from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class SubmissionForm(FlaskForm):
    code_text = TextAreaField('Your Code', validators=[DataRequired()], render_kw={"rows": 20})
    submit = SubmitField('Submit')