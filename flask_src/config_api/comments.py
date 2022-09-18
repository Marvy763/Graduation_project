######################################################
##   comments routes
######################################################
# import libraries
from flask import Blueprint,Response,request
from flask_jwt_extended import get_jwt_identity,jwt_required
from marshmallow import ValidationError
from flask_src.databases import Users,Posts,Comments,db
from flask_src.constants.http_status_codes import HTTP_200_OK,HTTP_400_BAD_REQUEST,HTTP_201_CREATED,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_422_UNPROCESSABLE_ENTITY,HTTP_204_NO_CONTENT,HTTP_404_NOT_FOUND
from .Schema import comment_schema,comments_schema
import json
from datetime import datetime
# from database import db




# define comments blueprint -- to group users' comments url routes
comments_bp = Blueprint("comments",__name__,url_prefix='/api/v1/comments')



# NOTE: authenticate correct uer and admin to access delete comment


@comments_bp.route('/test',methods=['GET'])
def test_api():
    return {"message":"sucess route"}



# edit comment
@comments_bp.route('/edit/<int:pk>',methods=['PUT','PATCH'])
@jwt_required
def edit_comment(pk):

    current_user = get_jwt_identity()

    if not request.get_json():
            return Response(
                   response = json.dumps({"message": "No input data provided"}),
                   status = HTTP_400_BAD_REQUEST,
                   mimetype = 'application/json'
                   )


    try:
        user_info = Users.query.filter_by(id=current_user).first()
    except Exception as ex:
        return Response(
                    response= json.dumps({
                        'error':'user database error',
                        'Exception': f'{ex}'}),
                    status=HTTP_500_INTERNAL_SERVER_ERROR,
                    mimetype='application/json'
                    )

    json_data = request.get_json()

    # Validate and deserialize input
    try:
        data = comment_schema.load(json_data)
    except ValidationError as err:
        return err.messages, HTTP_422_UNPROCESSABLE_ENTITY


    try:
        comment_data = Comments.query.filter_by(id=pk).first()

        if comment_data:

            # check if correct user
            if comment_data.author_id == current_user or user_info.job == 'admin':

                msg = data['message']

                
                comment_data.message = msg
                comment_data.date_posted = datetime.today()
                # apply changes to database
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
                    'message':'comment not found'
                    }),
                status=HTTP_404_NOT_FOUND,
                mimetype='application/json')
    except Exception as ex:
        return Response(
            response= json.dumps({
                'error':' comment edit database error',
                'Exception': f'{ex}'}),
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            mimetype='application/json'
            )
    comment_result = comment_schema.dump(Comments.query.get(comment_data.id))
    return Response(
        response= json.dumps({
            'message' : 'comment edited successfully',
            'result': comment_result
            }),
        status= HTTP_201_CREATED,
        mimetype='application/json'

        )





# delete comment
@comments_bp.route('/delete/<int:pk>',methods=["DELETE"])
@jwt_required
def delete_comment(pk):

    current_user = get_jwt_identity()


    try:
        comment_info = Comments.query.filter_by(id=pk).first()
    except:
        return Response(
                    response= json.dumps({'error':'post database error'}),
                    status=HTTP_500_INTERNAL_SERVER_ERROR,
                    mimetype='application/json'
                    )
   
    if not comment_info:
         return Response(
            response= json.dumps({
                'message': 'comment not found'
                }),
            status=HTTP_404_NOT_FOUND,
            mimetype='application/json')

    # check if correct user
    if comment_info.author_id == current_user:
        try:
            db.session.delete(comment_info)
            db.session.commit()
        except:
             return Response(
                response= json.dumps({
                    'error': 'delete comment error'
                    }),
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                mimetype='application/json')

        return Response(
            response= json.dumps({
                'message':'comment deleted successfully.'
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
