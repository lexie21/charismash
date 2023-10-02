from flask_wtf import FlaskForm
from wtforms import (StringField,TextField,SubmitField)
from wtforms.validators import DataRequired

class GateKeeper(FlaskForm):
    question = StringField('What is the specific term ers use to denote an action of someone who is about to leave the firm?',validators=[DataRequired()])
    submit = SubmitField('Send it')
