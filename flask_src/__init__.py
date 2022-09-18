# import important libraries
from flask import Flask 
from flask_login import LoginManager
from datetime import datetime
from flask_ckeditor import CKEditor
from flask_share import Share
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from .databases import db
from flask_migrate import Migrate
from .config_api import user_bp,posts_bp,comments_bp
import os


# init the app
app = Flask(__name__,instance_relative_config=True)
# make a share content
share = Share(app)
# init marshmallow schema
ma = Marshmallow(app)
# add ckeditor
ckeditor = CKEditor(app)

# UPLOAD_FOLDER = f'{os.path.dirname(os.path.abspath(__file__))}' + 'static\\uploaded_imgs\\'


# migrate used for newer version and apply it to db
migrate = Migrate(app,db)

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# # app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # for romove cache browser
# #new mysql db
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DB_URI")

# #create secret key - to secure form information between flask and web through csrf token
# app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
# # create jwt secret key
# app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

app.config.from_mapping(
            SECRET_KEY= os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),
            UPLOAD_FOLDER= os.environ.get('UPLOAD_FOLDER')

            # SWAGGER={
            #     'title': "Bookmarks API",
            #     'uiversion': 3
            # }
        )

db.app = app
# init database
db.init_app(app)


# to solve cach problem
@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response

# init flask login
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

# init flask jwt for api
jwt_manager = JWTManager(app)



# register blueprint for api
app.register_blueprint(user_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(comments_bp)
# app.register_blueprint(photos_bp)


from flask_src.config_api import *
from flask_src.config_web import *
