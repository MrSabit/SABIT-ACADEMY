from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('', 'Select Role'), ('student', 'Student'), ('admin', 'Admin')], validators=[DataRequired()])
    admin_code = StringField('Admin Code (if Admin)', default='')
    profile_pic = FileField('Profile Picture (optional)')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_role(self, role):
        if role.data.lower() not in ['admin', 'student']:
            raise ValidationError('Role must be Admin or Student.')

    def validate_admin_code(self, admin_code):
        if self.role.data.lower() == 'admin' and admin_code.data != '!MADMIN':
            raise ValidationError('Invalid admin code.')

class ChangeProfilePicForm(FlaskForm):
    profile_pic = FileField('New Profile Picture')
    submit = SubmitField('Update Profile Picture')