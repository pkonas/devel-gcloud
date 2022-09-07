# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerRangeField
from wtforms.validators import ValidationError, DataRequired
from app.models import User
from app.main import valve_opening

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
            
class ValveForm(FlaskForm):
    valve_opening = IntegerRangeField('Control valve opening', default=valve_opening.current_value)
    submit = SubmitField('Set')