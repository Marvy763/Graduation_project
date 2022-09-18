
# import important libraries
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin 
from sqlalchemy import Enum
from datetime import datetime
from .database import db
from slugify import slugify
import uuid as uuid


##### MODELS #####


# create db model for user 
class Users(db.Model,UserMixin):
   id = db.Column(db.Integer, primary_key = True)
   username = db.Column(db.String(20),nullable=False , unique=True)
   name = db.Column(db.String(100),nullable= False)
   email = db.Column(db.String(120),nullable=False , unique=True)
   # phone = db.Column(db.String(20),nullable=True,default=None)
   phone = db.Column(db.String(20),nullable=True,default=None)
   job = db.Column(db.String, Enum('patient', 'doctor', 'user', name='job'), default='patient',nullable=False)
   description = db.Column(db.Text(500),nullable=True,default="No Description Provided")
   date_added = db.Column(db.DateTime ,default= datetime.utcnow)
   profile_pic = db.Column(db.String(400),nullable=True)
   # create password
   pass_hash = db.Column(db.String(128))
#    user can have many posts
   posts = db.relationship('Posts',backref='author', lazy="dynamic") #reference to class
   #    user can have many comments
   comments = db.relationship('Comments',backref='commenter', lazy="dynamic") #reference to class
 
   # photos = db.relationship('Photos',backref='photo', lazy="dynamic") #reference to class


   def __init__(self,name=None, username=None, password=None,email=None,phone=0, job='patient',description=None,profile_pic=None):
     self.name = name
     self.username = username
     self.pass_hash = password
     self.email = email
     self.phone = phone
     self.job = job
     self.description=description
     self.profile_pic=profile_pic


#    create property for hash algorithm and check password 
   # @property
   # def password(self):
   #     raise AttributeError('password incorrect .. not a reachable attribute.')
    
   #  # generate password hash
   # @password.setter
   # def password(self,password):
   #  #    set password hash
   #   self.pass_hash =generate_password_hash(password)

   def verify_pass(self,password):
      return check_password_hash(self.pass_hash,password)

   
   #create a String
   def __repr__(self):
       return '<Name %r>' % self.name


# create blog post model 
class Posts (db.Model):
    id = db.Column(db.Integer,primary_key=True)
    # create banner image
    banner_img = db.Column(db.String(400),nullable=True)
    title = db.Column(db.String(255),nullable=False)
    slug = db.Column(db.String(255),unique=True, nullable=False)
    content = db.Column(db.Text)
    status = db.Column(db.String, Enum('pending', 'accepted', name='status'),default="pending",nullable=False)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime,default= datetime.utcnow())
    # create foreign key to link Users(refer to the primary key to the user)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id')) # call the database so its lowercase
    #    post can have many comments
    comments = db.relationship('Comments',backref='commenters', lazy="dynamic") #reference to class
    views = db.Column(db.Integer,default=0)
    # comment_count = db.Column(db.Integer,default=0)

    def __repr__(self):
        return '<Post:{}>'.format(self.title)

    @staticmethod
    def generate_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            # generate unique id for slug 
            random = str(uuid.uuid1()) + '_' + value
            # generate hash to make it unique
            target.slug = slugify(random)

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




