# from flask_src.models import Users,Posts,Photos,Comments
from flask_marshmallow import Marshmallow
from marshmallow import pre_load,Schema, fields, ValidationError, validate,validates_schema
import json
from datetime import datetime
from flask_src.constants.http_status_codes import HTTP_400_BAD_REQUEST
from flask import Response
from flask_src.databases import Users,Posts,Comments,db


##### SCHEMAS #####


# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError("Data not provided.")

def must_not_alphnumeric(data):
    if not data.isalnum() or " " in data:
        return Response(
            response= json.dumps({'error': "Username should be alphanumeric, also no spaces"}),
            status = HTTP_400_BAD_REQUEST,
            mimetype = 'application/json')

def is_accept(value):
  if len(str(value)) != 10:
     raise ValidationError("Invalid phone input. Must be 11 number.")

def is_phone(value):
    if len(value.replace(" ", "")) != 11:
        raise ValidationError("invalid phone number. phone number must contain of 11 number.")

def validate_phone(value):
    if value[0:2] != '01':
        raise ValidationError("invalid phone number. phone number must start of '01'")

# create list of strings to specify user job
JOB = ['patient','doctor','admin']
# create list of string to show the status of post
STATUS = ['pending','accepted']

# User Schema 
class UserSchema(Schema):
     # id is "read-only"
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True,validate=[validate.Length(min=4),must_not_alphnumeric,must_not_be_blank])
    name = fields.Str(required=True,validate=[validate.Length(min=3)])
    email = fields.Str(required=True,validate=[validate.Email(),must_not_be_blank])
     # password is "write-only"
    pwd_hash=fields.Str(load_only=True,required=True,validate=[validate.Length(min=6,max=8),must_not_be_blank])
    pwd_hash2=fields.Str(load_only=True,required=True,validate=[validate.Length(min=6,max=8),must_not_be_blank])
    phone = fields.Str(required=True,validate=[is_accept,must_not_be_blank,is_phone,validate_phone])
    job = fields.Str(required=True,validate=[validate.OneOf(JOB),must_not_be_blank])
    description = fields.Str(required=False,missing='No Description Provided')
    date_added = fields.DateTime(dump_only=True,missing=datetime.utcnow())
    profile_pic = fields.Raw(type='file',missing='default-pic.png',required=False)# must be validate to allowed extensions


    class Meta:
       ordered = True
       model = Users


    @validates_schema
    def validate_numbers(self, data, **kwargs):
        if data["pwd_hash"] != data["pwd_hash2"]:
            raise ValidationError("passwords must match")


    @pre_load
    def delete_none_values(self, in_data, **kwargs):
        """Delete all None values so they get filled out with their 'missing' parameters."""
        to_delete = []
        for key, value in in_data.items():
            if value is None:
                # can't delete dict values on the fly, it produces an error
                to_delete.append(key)
        for key in to_delete:
            del in_data[key]
        return in_data


# User Schema 
class UserEditSchema(Schema):
     # id is "read-only"
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True,validate=[validate.Length(min=4),must_not_alphnumeric,must_not_be_blank])
    name = fields.Str(required=True,validate=[validate.Length(min=3)])
    email = fields.Str(required=True,validate=[validate.Email(),must_not_be_blank])
    phone = fields.Int(required=True,validate=[is_accept,must_not_be_blank])
    job = fields.Str(required=True,validate=[validate.OneOf(JOB),must_not_be_blank])
    description = fields.Str(required=False,missing='No Description Provided')
    date_added = fields.DateTime(dump_only=True,missing=datetime.utcnow())
    profile_pic = fields.Raw(type='file',missing='default-pic.png',required=False)# must be validate to allowed extensions


    class Meta:
       ordered = True


    @pre_load
    def delete_none_values(self, in_data, **kwargs):
        """Delete all None values so they get filled out with their 'missing' parameters."""
        to_delete = []
        for key, value in in_data.items():
            if value is None:
                # can't delete dict values on the fly, it produces an error
                to_delete.append(key)
        for key in to_delete:
            del in_data[key]
        return in_data

class PostSchema(Schema):
    id =fields.Int(dump_only=True)
    banner_img=fields.Raw(type='file',missing=None,required=False,default='default_banner_img.png')# must be validate to allowed extensions
    title=fields.Str(required=True,validate=must_not_be_blank)
    slug=fields.Str(dump_only=True) 
    content=fields.Str(required=True,validate=must_not_be_blank)
    status=fields.Str(required=False,missing='pending',validate=[validate.OneOf(STATUS)])
    date_posted=fields.DateTime(dump_only=True,default=datetime.utcnow())
    author = fields.Nested(UserSchema,validate=must_not_be_blank)
    views = fields.Int(required=False,default=0)
    date_posted = fields.DateTime(dump_only=True,default=datetime.utcnow())


    class Meta:
       ordered = True
       model=Posts

    @pre_load
    def delete_none_values(self, in_data, **kwargs):
        """Delete all None values so they get filled out with their 'missing' parameters."""
        to_delete = []
        for key, value in in_data.items():
            if value is None:
                # can't delete dict values on the fly, it produces an error
                to_delete.append(key)
        for key in to_delete:
            del in_data[key]
        return in_data


class CommentSchema(Schema):
    id =fields.Int(dump_only=True)
    message= fields.Str(required=True)
    # post = fields.Nested(PostSchema, validate=[must_not_be_blank])
    # commenter =fields.Nested(UserSchema, validate=[must_not_be_blank])
    commenter = fields.Nested(lambda: UserSchema(only=("id", "username")))
    date_pub = fields.DateTime(dump_only=True,default=datetime.utcnow())

    class Meta:
       ordered = True
       # model=Comments



    @pre_load
    def delete_none_values(self, in_data, **kwargs):
        """Delete all None values so they get filled out with their 'missing' parameters."""
        to_delete = []
        for key, value in in_data.items():
            if value is None:
                # can't delete dict values on the fly, it produces an error
                to_delete.append(key)
        for key in to_delete:
            del in_data[key]
        return in_data



class PhotoSchema(Schema):
    id =fields.Int(dump_only=True)
    res_type=fields.Str(data_key="Type",dump_only=True)
    res_status=fields.Str(data_key="Status",dump_only=True)
    res_desc=fields.Str(data_key="Description",dump_only=True)
    date_uploaded=fields.DateTime(data_key="Uploaded at ",dump_only=True,default=datetime.utcnow())
    uploaded_img = fields.Raw(type="file",required=True) #may take dump_only= true cause we take it from db
    uploader = fields.Nested(UserSchema,validate=must_not_be_blank)

    class Meta:
       ordered = True


# create search schema
class SearchSchema(Schema):
    word = fields.Str(data_key='word',required=True,validate=[validate.Length(min=1),must_not_be_blank])


# create login schema
class LoginSchema(Schema):
    username = fields.Str(required=True,validate=[validate.Length(min=4),must_not_alphnumeric,must_not_be_blank])
    pwd_hash=fields.Str(load_only=True,required=True,validate=[validate.Length(min=6,max=8),must_not_be_blank])


# create change password schema
class ChangePasswordSchema(Schema):
    old_pwd = fields.Str(load_only=True,required=True,validate=[validate.Length(min=6,max=8),must_not_be_blank])
    pwd_hash=fields.Str(load_only=True,required=True,validate=[validate.Length(min=6,max=8),must_not_be_blank])
    pwd_hash2=fields.Str(load_only=True,required=True,validate=[validate.Length(min=6,max=8),must_not_be_blank])


    @validates_schema
    def validate_numbers(self, data, **kwargs):
        if data["pwd_hash"] != data["pwd_hash2"]:
            raise ValidationError("passwords must match")


#### DEFINITIONS FOR SCHEMAS ####

user_schema = UserSchema()
users_schema = UserSchema(many=True)

user_edit_schema = UserEditSchema()

post_schema = PostSchema()
posts_schema = PostSchema(many=True)


comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)


photo_schema = PhotoSchema()
photos_schema = PhotoSchema(many=True)


search_schema = SearchSchema()

user_login_schema = LoginSchema()

change_pass_schema = ChangePasswordSchema()
