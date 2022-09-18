from flask import Flask , render_template ,request,flash, redirect, url_for,jsonify,Response,abort
from flask_wtf import FlaskForm
from wtforms import RadioField,StringField,SubmitField,PasswordField,IntegerField,ValidationError,TextAreaField
from wtforms.validators import DataRequired,EqualTo,Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin ,login_user , LoginManager,login_required,logout_user,current_user, user_accessed
from datetime import datetime
from flask_ckeditor import CKEditor
from flask_ckeditor import CKEditorField
from werkzeug.security import generate_password_hash, check_password_hash
from flask_share import Share


# init the app
app = Flask(__name__)
# make a share content
share = Share(app)

# add ckeditor
ckeditor = CKEditor(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # for romove cache browser
#new mysql db
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:password123456789@localhost/blogger"

#create secret key - to secure form information between flask and web through csrf token
app.config['SECRET_KEY'] = "this is secret key and hashed"

# init database
db = SQLAlchemy(app)
# migrate used for newer version and apply it to db
migrate = Migrate(app,db)

@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response

# init flask login
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

# lookup for logged user in database
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id)) 

######################################################################################

#     Models 

######################################################################################

# create db model for user 
class Users(db.Model,UserMixin):
   id = db.Column(db.Integer, primary_key = True)
   username = db.Column(db.String(20),nullable=False , unique=True)
   name = db.Column(db.String(100),nullable= False)
   email = db.Column(db.String(120),nullable=False , unique=True)
   phone = db.Column(db.Integer,nullable=True,default=None)
   job = db.Column(db.String(10),nullable=False)
   description = db.Column(db.Text(500),nullable=True,default="No Description Provided")
   date_added = db.Column(db.DateTime ,default= datetime.utcnow)
   profile_pic = db.Column(db.String(400),nullable=True)
   # create password
   pass_hash = db.Column(db.String(128))
#    user can have many posts
   posts = db.relationship('Posts',backref='author') #reference to class
   #    user can have many comments
   comments = db.relationship('Comments',backref='commenter') #reference to class
 #    user can have many comments
   photos = db.relationship('Photos',backref='photo') #reference to class


#    create property for hash algorithm and check password 
   @property
   def password(self):
       raise AttributeError('password incorrect .. not a reachable attribute.')
    
    # generate password hash
   @password.setter
   def password(self,password):
    #    set password hash
     self.pass_hash =generate_password_hash(password)

   def verify_pass(self,password):
      return check_password_hash(self.pass_hash,password)

   def get_json_data(self):
      return {
        "username": self.username,
        "fullname": self.name,
        "email": self.email,
        "phone": self.phone,
        "job": self.job,
        "About": self.description,
       }
   #create a String
   def __repr__(self):
       return '<Name %r>' % self.name


# create blog post model 
class Posts (db.Model):
    __searchable__ = ['title', 'content']
    id = db.Column(db.Integer,primary_key=True)
    # create banner image
    banner_img = db.Column(db.String(400),nullable=True)
    title = db.Column(db.String(255),unique=True, nullable=False)
    slug = db.Column(db.String(255),unique=True, nullable=False)
    content = db.Column(db.Text)
    status = db.Column(db.String(10),nullable=False,default="pending")
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime,default= datetime.utcnow())
    # create foreign key to link Users(refer to the primary key to the user)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id')) # call the database so its lowercase
    #    post can have many comments
    comments = db.relationship('Comments',backref='commenters') #reference to class
    views = db.Column(db.Integer,default=0)
    comment_count = db.Column(db.Integer,default=0)

    def __repr__(self):
        return '<Post:{}>'.format(self.title)

    @staticmethod
    def generate_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)

    def get_json_data(self):
      return {
        "author": self.author.name,
        "title": self.title,
        "slug": self.slug,
        "body": self.content,
        "date published": self.date_posted,
        "views": self.views,
        "comments count": self.comment_count,
       }

# set slug for the title of the post into database
db.event.listen(Posts.title, 'set',Posts.generate_slug, retval=False)

# create comment model so user can interact with any post
class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    # create foreign key to link Posts(refer to the primary key to the post)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    # create foreign key to link Users(refer to the primary key to the user)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id')) # call the database so its lowercase
    date_pub = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r' % self.message

    def get_json_data(self):
      return {
        "commenter": self.author.name,
        "message": self.message,
        "date published": self.date_pub,
        "post_id": self.commenters.id
       }

class Photos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    res_type = db.Column(db.String(20),nullable=False)
    res_status = db.Column(db.String(20),nullable=False)
    res_description = db.Column(db.Text,nullable=False)
    # create foreign key to link Users(refer to the primary key to the user)
    uploader_id = db.Column(db.Integer,db.ForeignKey('users.id')) # call the database so its lowercase
    # save image to database
    image_uploaded = db.Column(db.String(400),nullable=True)
    date_uploaded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    #create a String
    def __repr__(self):
       return '<Photos %r>' % self.id
################################################################

#         Forms

################################################################

#create flask form
class UserForm(FlaskForm):
    name = StringField("Name",validators=[DataRequired()]) # required field
    username = StringField("Username",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired()])
    phone = StringField("Phone",validators=[DataRequired()])
    job = RadioField("You Are ",validators=[DataRequired()],choices=[('patient','Patient'),('doctor','Doctor')],default='patient')
    description = TextAreaField("About Author") # unrequired field
    pass_hash =  PasswordField('password',validators=[DataRequired(),EqualTo('pass_hash2',message='passwords must match')])
    pass_hash2 = PasswordField('confirm password',validators=[DataRequired()] )
    submit = SubmitField("login")

# create login form
class LoginForm(FlaskForm):
    username= StringField("username",validators=[DataRequired()])
    password = PasswordField("password",validators=[DataRequired()])
    submit = SubmitField("Submit")


# create blog post form
class PostForm(FlaskForm):
    title= StringField("Blog Title", validators=[DataRequired()])
    # basic content
    # content= StringField("Content", validators=[DataRequired()], widget= TextArea())
    content= CKEditorField("Start Writing Here...", validators=[DataRequired()])
    author= StringField("Author")
    slug= StringField("Slug") # was data required
    submit = SubmitField("Submit", validators=[DataRequired()])


# create Search form
class SearchForm(FlaskForm):
    searched = StringField("What you are looking for?",validators=[DataRequired()])
    submit = SubmitField("Submit")


# pass stuf to nav bar(parent page)
@app.context_processor
def base():
    form =SearchForm()
    return dict(form=form)

################################################################

# routes

################################################################

@app.route('/')
def index():
    return render_template("index.html")

# create login form
@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # look up for the entered username in the database
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # check the password hash
            if check_password_hash(user.pass_hash,form.password.data):
                #  if they match , user login success
                login_user(user)
                flash("success")
                return redirect(url_for('upload'))
            else:
                flash("wrong password - try again")
        else:
             flash("user doesnt exist !!!! try again.....")
    return render_template("login.html",form=form)


# create logout route
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('logged out success')
    return redirect(url_for('login'))


@app.route('/register', methods= ['GET','POST'])
def register():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user= Users.query.filter_by(email = form.email.data).first()
        if user is None:
            # hash password
            hashed_pw = generate_password_hash(form.pass_hash.data,"sha256")
            user = Users(name = form.name.data, username= form.username.data, email= form.email.data , job = form.job.data,phone = form.phone.data
            ,pass_hash =hashed_pw,description= form.description.data)
            db.session.add(user) #add user to database
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.phone.data = ''
        form.username.data = ''
        form.email.data = ''
        form.job.data = 'patient'
        form.pass_hash.data = ''
        form.description.data = ''
        flash('user add successfully')
    # our_user = Users.query.order_by(Users.data_added)
    return render_template("register.html",
    form=form, 
    name=name )

# create blog post
@app.route('/add-post',methods=['GET','POST'])
# first way to lock page
# @login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        author = current_user.id
        post = Posts(title=form.title.data,content=form.content.data,author_id = author,slug=form.slug.data)

        #clear post form
        form.title.data =''
        form.content.data=''
        # form.author.data=''
        form.slug.data=''

        # add post to database
        db.session.add(post)
        db.session.commit()

        # return a message
        flash('Blog Post Added Successfully')

    # redirect to the web page
    return render_template("add_post.html",
    form=form)

# show posts
@app.route('/posts')
def posts():
    # Grab all the posts from the database
    posts= Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html",posts=posts)


# show individual blog post
@app.route('/posts/<int:id>')
def show_post(id):
    post = Posts.query.get_or_404(id)
    return render_template("show_post.html",post= post)


@app.route('/upload')
@login_required
def upload():
    return render_template("upload.html")

@app.route('/user-profile')
@login_required
def user_profile():
    return render_template("profile.html")

@app.route('/faq')
def faq():
    return render_template("faq.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/advices')
def advices():
    return render_template("advices.html")


# show individual blog post
@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html",post= post)



# edit blog post
@app.route('/post/edit/<int:id>',methods=['GET','POST'])
# first way to lock page
@login_required 
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    # if statement to determine if the user view the page or they click submit button
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.content = form.content.data
        post.slug = form.slug.data
        post.date_posted = datetime.today()
        # update database
        db.session.add(post)
        db.session.commit()

        # return flash message
        flash('Post updated successfully')

        return redirect(url_for('post', id=post.id))
    # check if it is the correct user
    if current_user.id == post.author_id:
        form.title.data = post.title
        # form.author.data = post.author
        form.content.data = post.content
        form.slug.data = post.slug
        return render_template('edit_post.html',form=form)
    else:
        flash('not authorized to edit this post!!!!')
        posts= Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html",posts=posts)

# delete blog post
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    if current_user.id == post_to_delete.author.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            # return a message and redirect
            flash('Blog Post was deleted')
            posts= Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html",posts=posts)
        except:
            # return flash error
            flash('database error ... try again')

            posts= Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html",posts=posts)
    else:
        # return flash error
            flash('not authorized to delete this post')

            posts= Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html",posts=posts)


# handle error page
# not found page error
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

# Method not allowed
@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("405.html"),405

#internal server error
@app.errorhandler(500)
def internal_server_err(e):
    return render_template("500.html"),500


# restful api
@app.route('/api',methods=['GET'])
def api_home():
    return jsonify({"message":"api_home"});





# Helpers
def validate_string(input):
    if input is None or not input.strip():
        return False
    return True


def validate_list_of_strings(list):
    for i in list:
        if not validate_string(i):
            return False
    return True

def get_value_from_dict(dict,key):
    if key not in dict:
        return None
    return dict[key]

def construct_response(status, message, data=None):
    return {
        "status": status,
        "message": message,
        "data": data
    }

if __name__ == "__main__":
    app.run(port=5000,debug= True)