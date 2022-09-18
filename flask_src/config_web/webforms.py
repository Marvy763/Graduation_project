
################################################################

#         Forms

################################################################
# import libraries
from flask_wtf import FlaskForm
from wtforms import  TextAreaField,RadioField,StringField,SubmitField,PasswordField,IntegerField,ValidationError,TextAreaField
from wtforms.validators import DataRequired,EqualTo,Length,Email
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField
from wtforms.fields.html5 import TelField

#create flask form
class UserForm(FlaskForm):
    name = StringField("Name",validators=[DataRequired(),Length(min=3, max=25)]) # required field
    username = StringField("Username",validators=[DataRequired(),Length(min=2, max=25)])
    email = StringField("Email",validators=[DataRequired()])
    phone = StringField("Phone",validators=[DataRequired()])
    job = RadioField("You Are ",validators=[DataRequired()],choices=[('patient','Patient'),('doctor','Doctor')],default='patient')
    description = TextAreaField("About Author") # unrequired field
    pass_hash =  PasswordField('password',validators=[DataRequired(),EqualTo('pass_hash2',message='passwords must match')])
    pass_hash2 = PasswordField('confirm password',validators=[DataRequired()] )
    submit = SubmitField("login")

    def validate_image(form, field):
        if field.data:
            field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)

#create flask form
class UserProfileForm(FlaskForm):
    profile_pic = FileField("Profile Pic.")
    name = StringField("Name",validators=[DataRequired(),Length(min=3, max=25)]) # required field
    username = StringField("Username",validators=[DataRequired(),Length(min=2, max=25)])
    email = StringField("Email",validators=[DataRequired()])
    phone = StringField("Phone",validators=[DataRequired()])
    job = StringField("You Are ",validators=[DataRequired()])
    description = TextAreaField("About Author") # unrequired field
    submit = SubmitField("update profile")

# create login form
class LoginForm(FlaskForm):
    username= StringField("username",validators=[DataRequired()])
    password = PasswordField("password",validators=[DataRequired()])
    submit = SubmitField("Submit")


# create blog post form
class PostForm(FlaskForm):
    banner_img = FileField("Upload Banner")
    title= StringField("Blog Title", validators=[DataRequired()])
    # basic content
    # content= StringField("Content", validators=[DataRequired()], widget= TextArea())
    content= CKEditorField("Start Writing Here...", validators=[DataRequired()])
    author= StringField("Author")
    # slug= StringField("Slug") # was data required
    submit = SubmitField("Submit")



# create Search form
class SearchForm(FlaskForm):
    searched = StringField("What you are looking for?",validators=[DataRequired()])
    submit = SubmitField("Submit")



# create comment Form
class CommentForm(FlaskForm):
    message = TextAreaField("Leave a Comment ...",validators=[DataRequired()])
    submit = SubmitField("Send")



# create upload Form
class UploadForm(FlaskForm):
    file_predict = FileField(validators=[DataRequired()])
    submit = SubmitField("predict")



# create change password form
class ChangePasswordForm(FlaskForm):
    old_pwd = PasswordField('Old Password',validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Confirm Password',validators=[DataRequired()])
    submit = SubmitField("update new password")



    