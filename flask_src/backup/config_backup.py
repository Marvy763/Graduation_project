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
from .config_api import user_bp,posts_bp,comments_bp,photos_bp
import os

# init the app
app = Flask(__name__)
# make a share content
share = Share(app)
# init marshmallow schema
ma = Marshmallow(app)
# add ckeditor
ckeditor = CKEditor(app)



# init database
db.init_app(app)

# migrate used for newer version and apply it to db
migrate = Migrate(app,db)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # for romove cache browser
#new mysql db
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:password123456789@localhost/blogger"

#create secret key - to secure form information between flask and web through csrf token
app.config['SECRET_KEY'] = "be9b4a636529564ce506e0f599632cc0"
# create jwt secret key
app.config['JWT_SECRET_KEY'] = "1b3f5642e42df31d7d58781a4861312a"

# app.config.from_mapping(
#             SECRET_KEY= os.environ.get("SECRET_KEY"),
#             SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DB_URI"),
#             SQLALCHEMY_TRACK_MODIFICATIONS=False,
#             JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),


#             # SWAGGER={
#             #     'title': "Bookmarks API",
#             #     'uiversion': 3
#             # }
#         )

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
app.register_blueprint(photos_bp)

from config_api import *
from config_web import *




