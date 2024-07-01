from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, IntegerField, SelectField, MultipleFileField
from wtforms.validators import DataRequired, Length, EqualTo, Email, InputRequired,  ValidationError
from TV_Display.models import User



class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Log in')


class LogoutForm(FlaskForm):
       submit = SubmitField(label='Logout')

class UploadFileForm(FlaskForm):
    file = MultipleFileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

class Uni_UploadForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Submit")

def validate_serial_number_length(form, field):
    if not (100 <= field.data <= 9999999):
        raise ValidationError('Serial number must be between 3 and 7 digits long.')
class TVSerialForm(FlaskForm):
    serial_number = IntegerField('Serial Number', validators=[DataRequired(), validate_serial_number_length])
    submit = SubmitField('Display')



class NewTVForm(FlaskForm):
    Serial_Number = IntegerField('Serial Number', validators=[DataRequired(), validate_serial_number_length])
    Location = StringField('Location', validators=[DataRequired()])
    User_id = SelectField('User', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add TV')

    def __init__(self, *args, **kwargs):
        super(NewTVForm, self).__init__(*args, **kwargs)
        self.User_id.choices = [(user.id, user.username) for user in User.query.order_by(User.username).all()]