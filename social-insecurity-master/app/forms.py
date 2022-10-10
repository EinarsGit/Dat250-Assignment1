from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, DataRequired, Length, EqualTo, Regexp
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField
from wtforms.fields.html5 import DateField

# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields

class LoginForm(FlaskForm): # Nothing changed for LoginForm
    username = StringField('Username', render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm): # Added validators for each field
    first_name = StringField('First Name', validators=[InputRequired(message="Info: Name required"), Length(max=25)], render_kw={'placeholder': 'First Name'})
    last_name = StringField('Last Name', validators=[InputRequired(message="Info: Surname required"), Length(max=25)], render_kw={'placeholder': 'Last Name'})
    username = StringField('Username', validators=[InputRequired(message="Info: Username required"), Length(max=25), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Info: Username must contain only letters, numbers, dots or underscores. And must not start with a numeric.')], render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', validators=[DataRequired(message="Info: Password required"), Length(min=4, max=30, message="Info: The password bust be between 4 and 30 characters"), EqualTo('confirm_password', message='Info: Passwords do not match.'), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Info: Password must contain capital letters, numbers, dots or underscores')], render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired("Info: Confirmation needed")], render_kw={'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')

class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)

class PostForm(FlaskForm):
    content = TextAreaField('New Post', render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image')
    submit = SubmitField('Post')

class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', render_kw={'placeholder': 'What do you have to say?'})
    submit = SubmitField('Comment')

class FriendsForm(FlaskForm):
    username = StringField('Friend\'s username', render_kw={'placeholder': 'Username'})
    submit = SubmitField('Add Friend')

class ProfileForm(FlaskForm):
    education = StringField('Education', render_kw={'placeholder': 'Highest education'})
    employment = StringField('Employment', render_kw={'placeholder': 'Current employment'})
    music = StringField('Favorite song', render_kw={'placeholder': 'Favorite song'})
    movie = StringField('Favorite movie', render_kw={'placeholder': 'Favorite movie'})
    nationality = StringField('Nationality', render_kw={'placeholder': 'Your nationality'})
    birthday = DateField('Birthday')
    submit = SubmitField('Update Profile')
