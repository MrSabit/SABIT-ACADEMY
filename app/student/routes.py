from flask import render_template, flash, redirect, url_for, request
from datetime import datetime, timedelta
from flask_login import login_required, current_user
import os
import re
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from app import db
from app.student import bp
from app.student.forms import SubmissionForm
from app.models import Day, Lesson, Note, Assignment, Submission, User, Program

def sanitize_html_content(html_content):
    """Extract styles and body content from HTML while preserving functionality."""
    # Extract <style> tags from <head>
    style_matches = re.findall(r'<style[^>]*>(.*?)</style>', html_content, re.DOTALL | re.IGNORECASE)
    styles = ''.join(f'<style>{style}</style>' for style in style_matches)
    
    # Extract content between <body> tags
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
    if body_match:
        body_content = body_match.group(1)
    else:
        # If no body tags, remove html/head tags and keep everything else
        body_content = re.sub(r'</?html[^>]*>', '', html_content, flags=re.IGNORECASE)
        body_content = re.sub(r'</?head[^>]*>', '', body_content, flags=re.IGNORECASE)
        body_content = re.sub(r'</?title[^>]*>.*?</title>', '', body_content, flags=re.IGNORECASE | re.DOTALL)
    
    # Combine styles and body content
    return styles + body_content

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get submissions from the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    submissions = Submission.query.filter_by(user_id=current_user.id).filter(Submission.submitted_at >= thirty_days_ago).order_by(Submission.submitted_at).all()
    # Prepare data for chart
    chart_dates = []
    chart_scores = []
    for sub in submissions:
        if sub.score is not None:
            chart_dates.append(sub.submitted_at.strftime('%Y-%m-%d'))
            percentage = (sub.score / sub.assignment.max_score) * 100
            chart_scores.append(round(percentage, 2))
    return render_template('student/dashboard.html', submissions=submissions, chart_dates=chart_dates, chart_scores=chart_scores)

@bp.route('/notes')
@login_required
def list_notes():
    days = Day.query.order_by(Day.id).all()
    return render_template('student/notes.html', days=days, title="Notes")

@bp.route('/days/<int:day_id>')
@login_required
def view_day(day_id):
    day = Day.query.get_or_404(day_id)
    lessons = Lesson.query.filter_by(day_id=day_id).order_by(Lesson.id).all()
    programs = Program.query.filter_by(day_id=day_id).order_by(Program.id).all()
    return render_template('student/day_detail.html', day=day, lessons=lessons, programs=programs)

@bp.route('/lessons/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    notes = Note.query.filter_by(lesson_id=lesson_id).order_by(Note.created_at).all()
    html_content = None
    if lesson.html_file:
        try:
            with open(os.path.join('app', 'static', lesson.html_file), 'r', encoding='utf-8') as f:
                html_content = f.read()
                html_content = sanitize_html_content(html_content)
        except FileNotFoundError:
            html_content = "<p>HTML file not found.</p>"
    return render_template('student/lesson_detail.html', lesson=lesson, notes=notes, html_content=html_content)

@bp.route('/programs/<int:program_id>')
@login_required
def view_program(program_id):
    program = Program.query.get_or_404(program_id)
    code_content = None
    highlighted_code = None
    if program.python_file:
        try:
            with open(os.path.join('app', 'static', program.python_file), 'r', encoding='utf-8') as f:
                code_content = f.read()
                highlighted_code = highlight(code_content, PythonLexer(), HtmlFormatter(style='monokai', noclasses=True))
        except FileNotFoundError:
            highlighted_code = "<pre><code># Python file not found.</code></pre>"
    return render_template('student/program_detail.html', program=program, highlighted_code=highlighted_code)

@bp.route('/notes/<int:id>')
@login_required
def view_note(id):
    note = Note.query.get_or_404(id)
    return render_template('student/note_detail.html', note=note)

@bp.route('/assignments')
@login_required
def list_assignments():
    assignments = Assignment.query.order_by(Assignment.id.desc()).all()
    return render_template('student/assignments.html', assignments=assignments)

@bp.route('/assignments/<int:id>')
@login_required
def view_assignment(id):
    assignment = Assignment.query.get_or_404(id)
    submission = Submission.query.filter_by(user_id=current_user.id, assignment_id=id).first()
    return render_template('student/assignment_detail.html', assignment=assignment, submission=submission)

@bp.route('/assignments/<int:id>/submit', methods=['GET', 'POST'])
@login_required
def submit_assignment(id):
    assignment = Assignment.query.get_or_404(id)
    submission = Submission.query.filter_by(user_id=current_user.id, assignment_id=id).first()
    form = SubmissionForm()
    if form.validate_on_submit():
        if submission:
            submission.code_text = form.code_text.data
            submission.submitted_at = datetime.utcnow()
            flash('Your submission has been updated.')
        else:
            submission = Submission(user_id=current_user.id, assignment_id=id, code_text=form.code_text.data)
            db.session.add(submission)
            flash('Your submission has been received.')
        db.session.commit()
        return redirect(url_for('student.view_assignment', id=id))
    if submission:
        form.code_text.data = submission.code_text
    return render_template('student/submit_assignment.html', form=form, assignment=assignment)

@bp.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.filter(User.role != 'admin').order_by(User.total_score.desc()).all()
    return render_template('student/leaderboard.html', users=users)

@bp.route('/profile/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    # Get submissions from the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    submissions = Submission.query.filter_by(user_id=user.id).filter(Submission.submitted_at >= thirty_days_ago).order_by(Submission.submitted_at).all()
    # Prepare data for chart
    chart_dates = []
    chart_scores = []
    for sub in submissions:
        if sub.score is not None:
            chart_dates.append(sub.submitted_at.strftime('%Y-%m-%d'))
            percentage = (sub.score / sub.assignment.max_score) * 100
            chart_scores.append(round(percentage, 2))
    return render_template('student/profile.html', user=user, submissions=submissions, chart_dates=chart_dates, chart_scores=chart_scores)

@bp.route('/submission/<int:id>')
@login_required
def view_submission(id):
    submission = Submission.query.get_or_404(id)
    return render_template('student/submission_detail.html', submission=submission)