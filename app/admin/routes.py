from flask import render_template, abort, flash, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps
import os
from werkzeug.utils import secure_filename
from app import db
from app.admin import bp
from app.admin.forms import DayForm, LessonForm, NoteForm, AssignmentForm, SubmissionReviewForm, UserRoleForm, ProgramForm
from app.models import Day, Lesson, Note, Assignment, Submission, User, Program

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'teacher']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@bp.route('/days/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_day():
    form = DayForm()
    if form.validate_on_submit():
        day = Day(title=form.title.data)
        db.session.add(day)
        db.session.commit()
        flash('Day created successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_day.html', form=form)

@bp.route('/lessons/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_lesson():
    form = LessonForm()
    form.day_id.choices = [(day.id, day.title) for day in Day.query.all()]
    if form.validate_on_submit():
        lesson = Lesson(title=form.title.data, day_id=form.day_id.data)
        if form.html_file.data:
            filename = secure_filename(form.html_file.data.filename)
            upload_folder = os.path.join('app', 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            form.html_file.data.save(file_path)
            lesson.html_file = f'uploads/{filename}'
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson created successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_lesson.html', form=form)

@bp.route('/programs/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_program():
    form = ProgramForm()
    form.day_id.choices = [(day.id, day.title) for day in Day.query.all()]
    if form.validate_on_submit():
        program = Program(title=form.title.data, day_id=form.day_id.data)
        if form.python_file.data:
            filename = secure_filename(form.python_file.data.filename)
            upload_folder = os.path.join('app', 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            form.python_file.data.save(file_path)
            program.python_file = f'uploads/{filename}'
        db.session.add(program)
        db.session.commit()
        flash('Program created successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_program.html', form=form)

@bp.route('/notes/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_note():
    form = NoteForm()
    form.lesson_id.choices = [(lesson.id, lesson.title) for lesson in Lesson.query.all()]
    if form.validate_on_submit():
        note = Note(title=form.title.data, lesson_id=form.lesson_id.data, content=form.content.data)
        db.session.add(note)
        db.session.commit()
        flash('Note created successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_note.html', form=form)

@bp.route('/assignments/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_assignment():
    form = AssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(title=form.title.data, description=form.description.data, max_score=form.max_score.data)
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment created successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_assignment.html', form=form)

@bp.route('/submissions')
@login_required
@admin_required
def list_submissions():
    submissions = Submission.query.all()
    return render_template('admin/submissions.html', submissions=submissions)

@bp.route('/submissions/<int:id>/review', methods=['GET', 'POST'])
@login_required
@admin_required
def review_submission(id):
    submission = Submission.query.get_or_404(id)
    form = SubmissionReviewForm(assignment=submission.assignment)
    if form.validate_on_submit():
        old_score = submission.score or 0
        
        submission.score = form.score.data
        submission.feedback = form.feedback.data
        
        score_difference = submission.score - old_score
        submission.author.total_score = (submission.author.total_score or 0) + score_difference
        
        try:
            db.session.commit()
            flash('Submission has been reviewed and score updated.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating submission: {str(e)}', 'error')
        return redirect(url_for('admin.list_submissions'))
    elif request.method == 'GET':
        form.score.data = submission.score
        form.feedback.data = submission.feedback
    return render_template('admin/review_submission.html', title='Review Submission', submission=submission, form=form)

@bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@bp.route('/users/<int:id>/change_role', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_role(id):
    user = User.query.get_or_404(id)
    form = UserRoleForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.commit()
        flash(f'Role for {user.username} updated to {user.role}.', 'success')
        return redirect(url_for('admin.list_users'))
    elif request.method == 'GET':
        form.role.data = user.role
    return render_template('admin/change_role.html', form=form, user=user)

@bp.route('/reset_app', methods=['POST'])
@login_required
@admin_required
def reset_app():
    try:
        # Delete all submissions
        Submission.query.delete()
        # Delete all assignments
        Assignment.query.delete()
        # Delete all notes
        Note.query.delete()
        # Delete all programs
        Program.query.delete()
        # Delete all lessons
        Lesson.query.delete()
        # Delete all days
        Day.query.delete()
        # Delete all non-admin users
        User.query.filter(User.role != 'admin').delete()
        db.session.commit()
        flash('App has been reset successfully! All data except admin users has been cleared.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting app: {str(e)}', 'error')
    return redirect(url_for('admin.dashboard'))