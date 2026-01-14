from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError

class DayForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Create Day')

class LessonForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    day_id = SelectField('Day', coerce=int, validators=[DataRequired()])
    html_file = FileField('HTML File', validators=[FileAllowed(['html'], 'HTML files only!')])
    submit = SubmitField('Create Lesson')

class ProgramForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    day_id = SelectField('Day', coerce=int, validators=[DataRequired()])
    python_file = FileField('Python File', validators=[FileAllowed(['py'], 'Python files only!')])
    submit = SubmitField('Create Program')

class NoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    lesson_id = SelectField('Lesson', coerce=int, validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Create Note')

class AssignmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    max_score = IntegerField('Max Score', validators=[DataRequired()])
    submit = SubmitField('Create Assignment')

class SubmissionReviewForm(FlaskForm):
    score = IntegerField('Score', validators=[DataRequired()])
    feedback = TextAreaField('Feedback')
    submit = SubmitField('Submit Review')

    def __init__(self, assignment=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assignment = assignment

    def validate_score(self, field):
        if self.assignment and field.data > self.assignment.max_score:
            raise ValidationError(f'Score cannot exceed the maximum score of {self.assignment.max_score}.')

class UserRoleForm(FlaskForm):
    role = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Update Role')