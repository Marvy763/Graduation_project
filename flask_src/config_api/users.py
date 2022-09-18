######################################################
##   user routes
######################################################
# import libraries
from flask import Blueprint,request,Response
from werkzeug.security import generate_password_hash,check_password_hash
from marshmallow import ValidationError
from flask_jwt_extended import jwt_refresh_token_required, get_jwt_identity,jwt_required, create_access_token, create_refresh_token
from flask_src.constants.http_status_codes import HTTP_500_INTERNAL_SERVER_ERROR,HTTP_422_UNPROCESSABLE_ENTITY,HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from .Schema import user_edit_schema,user_schema,users_schema,user_login_schema,change_pass_schema
# from models import Users
from flask_src.databases import Users,Posts,Comments,db
import json
from flask_src.save import save_image



# define user blueprint -- to group users' url routes
user_bp = Blueprint("user",__name__,url_prefix='/api/v1/user')




# in real app, you would have strategy automatically refresh it
# so we don't ever get that token expired 
@user_bp.route('/test',methods=['GET'])
def test_api():
    return {"message":"sucess route"}


@user_bp.route('/register',methods=['POST'])
def register():


    if not request.get_json():
        return Response(
               response = json.dumps({"message": "No input data provided"}),
               status = HTTP_400_BAD_REQUEST,
               mimetype = 'application/json'
               )
    
    json_data = request.get_json()

   

    # Validate and deserialize input
    try:
        data = user_schema.load(json_data)
    except ValidationError as err:
        return err.messages, HTTP_422_UNPROCESSABLE_ENTITY

        # assign load input to variables
    username,name,email,pwd_hash,phone,job,description,profile_pic = data["username"],data['name'],data["email"],data["pwd_hash"],data["phone"],data["job"],data["description"],data["profile_pic"]

        # check input email if already taken
    if Users.query.filter_by(email=email).first() is not None:
        return Response(
               response = json.dumps({'error': "Email is taken"}),
               status = HTTP_409_CONFLICT,
               mimetype = 'application/json'
            )

        # check input username if already taken
    if Users.query.filter_by(username=username).first() is not None:
        return Response(
               response = json.dumps({'error': "Username is taken"}),
               status = HTTP_409_CONFLICT,
               mimetype = 'application/json'
            )

        # hash password to be saved in database
    pwd_hash = generate_password_hash(pwd_hash,"sha256")

    

    try:
        # save user to db
        user_data = Users(username=username,name=name, password=pwd_hash, 
            email=email,phone=phone,job=job,
            description=description)
        
        
        # apply changes to db
        db.session.add(user_data)
        db.session.commit()
    except Exception as ex:
        return Response(
            response= json.dumps({
                'error':'database error',
                'Exception':f'{ex}'}),
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            mimetype='application/json'
        )

    user_result = user_schema.dump(user_data)

    return Response(
                response = json.dumps({
                    'message': "User created",
                    'user': {
                        'username': user_result
                        }
                   }),
                status = HTTP_201_CREATED,
                mimetype = 'application/json'
               )





@user_bp.route('/login',methods=['POST'])
def login():

    if not request.get_json():
        return Response(
               response = json.dumps({"message": "No input data provided"}),
               status = HTTP_400_BAD_REQUEST,
               mimetype = 'application/json'
               )

    json_data = request.get_json()

    

    # Validate and deserialize input
    try:
        data = user_login_schema.load(json_data)
    except ValidationError as err:
        return err.messages, HTTP_422_UNPROCESSABLE_ENTITY


    # assign load input to variable 
    username,pwd_hash = data['username'], data['pwd_hash']

    try:
        user_data = Users.query.filter_by(username=username).first()
    except:
        return Response(
                    response= json.dumps({'error':'database error'}),
                    status=HTTP_500_INTERNAL_SERVER_ERROR,
                    mimetype='application/json'
                    )


    # look up for the entered username in the database
    if user_data:
        is_pass_correct = check_password_hash(user_data.pass_hash, pwd_hash)
        # check the password hash
        if is_pass_correct:
            refresh = create_refresh_token(identity=user_data.id)
            access = create_access_token(identity=user_data.id)

            user_result = user_schema.dump(user_data)

            return Response(
               response = json.dumps({
                'message':'user logged in successfully',
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'info': user_result
                }

            }),
               status = HTTP_200_OK,
               mimetype = 'application/json'
               )
        else:
            return Response(
               response = json.dumps({
                'error': 'Wrong password - try again'}),
               status = HTTP_400_BAD_REQUEST,
               mimetype = 'application/json'
               )

    return Response(
               response = json.dumps({'error': 'Wrong credentials'}),
               status = HTTP_401_UNAUTHORIZED,
               mimetype = 'application/json'
               )




# get current user info
@user_bp.route('/profile/<int:pk>',methods=['GET'])
def get_profile(pk):

    try:
        user_data = Users.query.filter_by(id=pk).first()
    except Exception as ex:
        return Response(
            response= json.dumps({
                'error':'database error',
                'Exception': f'{ex}'}),
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            mimetype='application/json'
        )

    if user_data:
        user_result = user_schema.dump(user_data)

        return Response(
           response = json.dumps({'user':user_result}),
           status = HTTP_200_OK,
           mimetype = 'application/json'
           )
    else:
        return Response(
            response= json.dumps(
                {
                'message':'user not found'
                }),
            status=HTTP_404_NOT_FOUND,
            mimetype='application/json')



# refresh token authentication for logged user
@user_bp.route('/token/refresh',methods=['GET'])
# @jwt_required(refresh=True)
@jwt_refresh_token_required
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return Response(
        response= json.dumps({
            'access': access
            }),
        status= HTTP_200_OK,
        mimetype='application/json'

        )


# change password
@user_bp.route('/change-password/<int:pk>',methods=['POST'])
@jwt_required
def change_password(pk):

    current_user=get_jwt_identity()

    if not request.get_json():
        return Response(
               response = json.dumps({"message": "No input data provided"}),
               status = HTTP_400_BAD_REQUEST,
               mimetype = 'application/json'
               )

    json_data = request.get_json()

    

    # Validate and deserialize input
    try:
        data = change_pass_schema.load(json_data)
    except ValidationError as err:
        return err.messages, HTTP_422_UNPROCESSABLE_ENTITY


    old_pwd,pwd_hash,pwd_hash2=data['old_pwd'],data['pwd_hash'],data['pwd_hash2']


    # lookup for user in db
    try:
        user_data = Users.query.filter_by(id=pk).first()
    except:
        return Response(
                    response= json.dumps({'error':'database error'}),
                    status=HTTP_500_INTERNAL_SERVER_ERROR,
                    mimetype='application/json'
                    )

    # check if correct user
    if current_user == user_data.id:

       # check if old password is correct
        is_pass_correct = check_password_hash(user_data.pass_hash, old_pwd)
        # check the password hash
        if is_pass_correct:
            # if correct add new hased password to db
            new_pwd = generate_password_hash(pwd_hash)
            user_data.pass_hash=new_pwd
            db.session.commit()
            return Response(
                response=json.dumps({
                    'message':'changed password successfully.'
                    }),
                status=HTTP_200_OK,
                mimetype='application/json')
        else:
            return Response(
               response = json.dumps({
                'error': 'Wrong password - try again'}),
               status = HTTP_400_BAD_REQUEST,
               mimetype = 'application/json'
               )
    else:
        return Response(
            response=json.dumps({
                'message':'you are not authorized to access.'
                }),
            status = HTTP_401_UNAUTHORIZED,
            mimetype='application/json')





# edit user
@user_bp.route('/edit/<int:pk>',methods=['PUT','PATCH'])
@jwt_required
def edit_user(pk):

    current_user = get_jwt_identity()

    # if not request.get_json():
    #         return Response(
    #                response = json.dumps({"message": "No input data provided"}),
    #                status = HTTP_400_BAD_REQUEST,
    #                mimetype = 'application/json'
    #                )


    try:
        user_info = Users.query.filter_by(id=pk).first()
    except Exception as ex:
        return Response(
                    response= json.dumps({
                        'error':'user database error',
                        'Exception': f'{ex}'}),
                    status=HTTP_500_INTERNAL_SERVER_ERROR,
                    mimetype='application/json'
                    )



    try:
        if user_info:

            # check if correct user
            if user_info.id == current_user or user_info.job == 'admin':

                

                username = request.form['username']
                name = request.form['name']
                email = request.form['email']
                phone = request.form['phone']
                description = request.form['description']
                profile_pic = request.files['profile_pic']

                if len(form.phone.data.replace(" ", "")) != 11:
                    return Response(
                        response= json.dumps({
                            "message":"invalid phone number. phone number must contain of 11 number.",
                            }),
                        status=HTTP_400_BAD_REQUEST,
                        mimetype="application/json")

                if form.phone.data[0:2] != '01':
                    return Response(
                        response= json.dumps({
                            "message":"invalid phone number. phone number must start of '01'"
                            }),
                        status=HTTP_400_BAD_REQUEST,
                        mimetype='application/json')


                user_info.username = username
                user_info.name = name
                user_info.email = email
                user_info.phone = phone
                user_info.description = description
                # user_info.profile_pic = profile_pic

                # check if the profile pic is exist 
                if profile_pic:
                    # save img
                    pic_name,path = save_image(profile_pic)
                    # set image filename to database
                    user_info.profile_pic = pic_name
                db.session.commit()
            else:
                return Response(
                    response= json.dumps({
                        'message':'you are not authorized to access.'
                        }),
                    status=HTTP_401_UNAUTHORIZED,
                    mimetype='application/json')
        else:
            return Response(
                response= json.dumps({
                    'message':'user not found'
                    }),
                status=HTTP_404_NOT_FOUND,
                mimetype='application/json')
    except Exception as ex:
        return Response(
            response= json.dumps({
                'error':' user edit database error',
                'Exception': f'{ex}'}),
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            mimetype='application/json'
            )
    user_result = user_edit_schema.dump(Users.query.get(user_info.id))
    return Response(
        response= json.dumps({
            'message' : 'user updated successfully',
            'result': user_result
            }),
        status= HTTP_201_CREATED,
        mimetype='application/json'

        )





# delete user
@user_bp.route('/delete/<int:pk>',methods=["DELETE"])
@jwt_required
def delete_user(pk):

    current_user = get_jwt_identity()


    try:
        user_info = Users.query.filter_by(id=pk).first()
    except:
        return Response(
                    response= json.dumps({'error':'user database error'}),
                    status=HTTP_500_INTERNAL_SERVER_ERROR,
                    mimetype='application/json'
                    )
   # check if user exists
    if not user_info:
         return Response(
            response= json.dumps({
                'message': 'user not found'
                }),
            status=HTTP_404_NOT_FOUND,
            mimetype='application/json')

    # check if correct user
    if  pk == current_user:
        if user_info.job == 'doctor' or user_info.job == 'admin':
            comments = Comments.query.filter_by(author_id=pk).all()
            # check if user commented 
            if comments:
                db.session.delete(comments)
            posts = Posts.dump.filter_by(author_id=pk).all()
            # check if the user posted posts
            if posts:
                db.session.delete(posts)
                # db.session.commit()
        try:
            db.session.delete(user_info)
            db.session.commit()
        except:
             return Response(
                response= json.dumps({
                    'error': 'delete user error'
                    }),
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                mimetype='application/json')

        return Response(
            response= json.dumps({
                'message':'user deleted successfully.'
                }),
            status=HTTP_200_OK,
            mimetype='application/json')
    else:
        return Response(
            response= json.dumps({
                'message':'you are not authorized to access.'
                }),
            status=HTTP_401_UNAUTHORIZED,
            mimetype='application/json')



# logout


