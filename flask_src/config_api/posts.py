######################################################
##   posts routes
######################################################
# import libraries
from flask import Blueprint,request,Response
from flask_jwt_extended import get_jwt_identity,jwt_required
from marshmallow import ValidationError
from flask_src.constants.http_status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT,HTTP_201_CREATED,HTTP_401_UNAUTHORIZED,HTTP_422_UNPROCESSABLE_ENTITY,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_400_BAD_REQUEST
from .Schema import user_schema,post_schema,posts_schema,search_schema,comment_schema,comments_schema
# from models import Users,Posts
from flask_src.databases import Users,Posts,Comments,db
import json
from datetime import datetime
from sqlalchemy import or_
from flask_src.save import save_image


# define posts blueprint -- to group posts' url routes
posts_bp = Blueprint("posts",__name__,url_prefix='/api/v1/posts')


# NOTE: authenticate correct uer and admin to access delete,admin to accept post

# create post
@posts_bp.route('/add-post',methods=['POST'])
@jwt_required
def handle_posts():

    current_user = get_jwt_identity()


    try:
        user_info = Users.query.filter_by(id=current_user).first()
    except:
        return Response(
                    response= json.dumps({'error':'user database error'}),
                    status=HTTP_500_INTERNAL_SERVER_ERROR,
                    mimetype='application/json'
                    )



    # check authorization to add post
    if user_info.job == 'doctor' or user_info.job == 'admin':

        
        views= 0
        title = request.form['title']
        content = request.form['content']
        banner_img = request.files['banner_img']

        Thanks=''
   
        if user_info.job == 'doctor':
            status = 'pending'
            Thanks = 'Your post has been submited.  post will be published after approval of admin'
        else:
            status = 'accepted'
            Thanks = 'Your post has been submited and published successfully.'


        # check if banner_img exist:
        if banner_img:
            # save img
            pic_name,path = save_image(banner_img)
            # add to database
            post_data=Posts(title=title,content=content,banner_img=pic_name)
        else:
            post_data = Posts(title=title,content=content,status=status,banner_img=banner_img,views=views)


        try:
            # post_data = Posts(title=title,content=content,status=status,author_id = current_user,views=views)

            # add post to database
            db.session.add(post_data)
            db.session.commit()
        except Exception as ex:
            return Response(
                response= json.dumps({
                    'error':' post add database error',
                    'Exception':f'{ex}'}),
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                mimetype='application/json'
                )
        post_result = post_schema.dump(Posts.query.get(post_data.id))
        return Response(
            response= json.dumps({
                'message' : f"{Thanks}",
                'result': post_result
                }),
            status= HTTP_201_CREATED,
            mimetype='application/json'

            )
    else:
        return Response(
                response= json.dumps({'message':'You are not authorized to access '}),
                status=HTTP_401_UNAUTHORIZED,
                mimetype='application/json'
                )


           
# get user' pending posts
@posts_bp.route('/my-posts/<int:pk>',methods=['GET'])
@jwt_required
def user_post(pk):
    user_info = Users.query.get(pk)

    

    if not user_info:
        return Response(
            response= json.dumps({
                'message':'user not found.'
                }),
            status=HTTP_404_NOT_FOUND,
            mimetype='application/json')
    if user_info.job == 'doctor':
        # using GET method 
        # current_user = get_jwt_identity()
        # paginate posts
        # get the page of the record
        # if the user does not send the page who just defaults to send page no.one
        # but if user enter the page that's return that page we queried by
        page = request.args.get('page',1,type=int)

        # limit our posts in page - limit query
        per_page = request.args.get('per_page',5,type=int)

        try:
            # load all posts to user that is user has created
            posts_data = Posts.query.filter_by(author_id = pk,status='pending').paginate(page=page,per_page=per_page)
            # the return data has many keys : items (all posts) ,page ,pages ,next ,prev ,has_next ,has_prev and so on.
        except:
            return Response(
                    response= json.dumps({'error':'show post database error'}),
                    status=HTTP_500_INTERNAL_SERVER_ERROR,
                    mimetype='application/json'
                    )

        if not posts_data:

            # if there is no post created yet
            return Response(
                response= json.dumps({
                    'message': 'there is no post created yet.'
                    }),
                status = HTTP_204_NO_CONTENT,
                mimetype='application/json'
                )


        # Serialize the queryset
        result = posts_schema.dump(posts_data.items,many=True)

        meta = {
        'page': posts_data.page,
        'pages':posts_data.pages,
        'total_count':posts_data.total,
        'prev_page': posts_data.prev_num,
        'next_page': posts_data.next_num,
        'has_next': posts_data.has_next, # Boolean - means if there next pages after the current page
        'has_prev': posts_data.has_prev, # Boolean - means if there prev pages before the current page
        }

        return Response(
            response= json.dumps({
                'data': result,
                'meta':meta
                }),
            status = HTTP_200_OK,
            mimetype='application/json'
            )
    else:
        return Response(
            response= json.dumps({
                'message':'you are not authorized to access'
                }),
            status = HTTP_401_UNAUTHORIZED,
            mimetype= 'application/json')


# get all posts
@posts_bp.route("/", methods=["GET"])
def get_posts():

    # if the user does not send the page who just defaults to send page no.one
    # but if user enter the page that's return that page we queried by
    page = request.args.get('page',1,type=int)

    # limit our posts in page - limit query
    per_page = request.args.get('per_page',5,type=int)
    try:
        posts_data = Posts.query.filter_by(status='accepted').paginate(page=page,per_page=per_page)

    except Exception as ex:
        return Response(
            response= json.dumps({
                'error':'show all posts database error',
                'Exception':f'{ex}'}),
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            mimetype='application/json'
        )

    meta = {
            'page': posts_data.page,
            'pages':posts_data.pages,
            'total_count':posts_data.total,
            'prev_page': posts_data.prev_num,
            'next_page': posts_data.next_num,
            'has_next': posts_data.has_next, # Boolean - means if there next pages after the current page
            'has_prev': posts_data.has_prev, # Boolean - means if there prev pages before the current page
           }

    if not posts_data:
        return Response(
        response= json.dumps({}),
        status=HTTP_204_NO_CONTENT,
        mimetype='application/json'
        )

    result = posts_schema.dump(posts_data.items, many=True)
    

    return Response(
        response= json.dumps({
            'all pages': {
            'data':result,
            'meta':meta}
            }),
        status= HTTP_200_OK,
        mimetype='application/json'
        )


# get trend posts
@posts_bp.route("/top", methods=["GET"])
def get_top_posts():

    # if the user does not send the page who just defaults to send page no.one
    # but if user enter the page that's return that page we queried by
    page = request.args.get('page',1,type=int)

    # limit our posts in page - limit query
    per_page = request.args.get('per_page',5,type=int)
    try:
        posts_data = Posts.query.filter_by(status='accepted').order_by(Posts.views.desc()).paginate(page=page,per_page=per_page)

    except Exception as ex:
        return Response(
            response= json.dumps({
                'error':'show top posts database error',
                'Exception':f'{ex}'}),
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            mimetype='application/json'
        )

    meta = {
            'page': posts_data.page,
            'pages':posts_data.pages,
            'total_count':posts_data.total,
            'prev_page': posts_data.prev_num,
            'next_page': posts_data.next_num,
            'has_next': posts_data.has_next, # Boolean - means if there next pages after the current page
            'has_prev': posts_data.has_prev, # Boolean - means if there prev pages before the current page
           }

    if not posts_data.items:
        return Response(
        response= json.dumps({}),
        status=HTTP_204_NO_CONTENT,
        mimetype='application/json'
        )

    
    top_results = posts_schema.dump( posts_data.items,many=True)

    return Response(
        response= json.dumps({
            'trending':top_results,
            'meta':meta
            }),
        status= HTTP_200_OK,
        mimetype='application/json'
        )
    

# get all pending posts
@posts_bp.route("/pending-posts", methods=["GET"])
@jwt_required
def get_pending_posts():
    current_user = get_jwt_identity()

    user_info = Users.query.filter_by(id=current_user).first()

    if user_info.job == 'admin':
        # if the user does not send the page who just defaults to send page no.one
        # but if user enter the page that's return that page we queried by
        page = request.args.get('page',1,type=int)

        # limit our posts in page - limit query
        per_page = request.args.get('per_page',5,type=int)
        try:
            posts_data = Posts.query.filter_by(status='pending').paginate(page=page,per_page=per_page)

        except Exception as ex:
            return Response(
                response= json.dumps({
                    'error':'show all posts database error',
                    'Exception':f'{ex}'}),
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                mimetype='application/json'
            )

        meta = {
                'page': posts_data.page,
                'pages':posts_data.pages,
                'total_count':posts_data.total,
                'prev_page': posts_data.prev_num,
                'next_page': posts_data.next_num,
                'has_next': posts_data.has_next, # Boolean - means if there next pages after the current page
                'has_prev': posts_data.has_prev, # Boolean - means if there prev pages before the current page
               }

        if not posts_data:
            return Response(
            response= json.dumps({}),
            status=HTTP_204_NO_CONTENT,
            mimetype='application/json'
            )

        result = posts_schema.dump(posts_data.items, many=True)
        

        return Response(
            response= json.dumps({
                'all pages': {
                'data':result,
                'meta':meta}
                }),
            status= HTTP_200_OK,
            mimetype='application/json'
            )
    else:
        return Response(
                response= json.dumps({
                'message':"you are not authorized to access."
                }),
            status= HTTP_401_UNAUTHORIZED,
            mimetype='application/json'
            )

# get individual post
@posts_bp.route("/<string:slug>",methods=['GET'])
def get_post(slug):

    # current_user = get_jwt_identity()
    # posts_data = Posts.query.filter_by(author_id=current_user,slug=slug).first()
    posts_data = Posts.query.filter_by(slug=slug).first()
    if not posts_data:
        return Response(
            response= json.dumps({
                'message': 'Post not found'
                }),
            status=HTTP_404_NOT_FOUND,
            mimetype='application/json')
    comments_data = Comments.query.filter_by(post_id=posts_data.id).order_by(Comments.date_pub.desc()).all()
    posts_data.views = posts_data.views + 1
    db.session.commit()
    post_result = post_schema.dump(posts_data)

    if comments_data is None:
         return Response(
            response= json.dumps({
                'posts' : post_result,
                'total_comments': len(comments_data),
                'comments': 'there is no comment added yet . Be first comment.'
                }),
            status= HTTP_200_OK,
            mimetype='application/json'

            )
    else:
        comments_result = comments_schema.dump(comments_data)
        return Response(
            response= json.dumps({
                'post' : post_result,
                'total_comments': len(comments_data),
                'comments': comments_result
                }),
            status= HTTP_201_CREATED,
            mimetype='application/json'

            )

# make admin publish posts
@posts_bp.route('/check/<int:id>', methods=['POST','GET'])
@jwt_required
def check(id):
    post = Posts.query.get(id)
    current_user = get_jwt_identity()

    user_info = Users.query.filter_by(id=current_user).first()

    if user_info.job == 'admin':
        # check if post exist
        if post:
            if post.status == 'pending':
                try:
                    post.status = 'accepted'
                    db.session.commit()
                    return Response(
                    response= json.dumps({
                        'message':"post published successfully"
                        }),
                    status = HTTP_200_OK,
                    mimetype='application/json')
                except:
                    return Response(
                    response= json.dumps({
                        'message':"check post error"
                        }),
                    status = HTTP_500_INTERNAL_SERVER_ERROR,
                    mimetype='application/json')
            else:
                try:
                    return Response(
                    response= json.dumps({
                        'message':"post already published"
                        }),
                    status = HTTP_200_OK,
                    mimetype='application/json')
                except:
                    return Response(
                    response= json.dumps({
                        'message':"check post error"
                        }),
                    status = HTTP_500_INTERNAL_SERVER_ERROR,
                    mimetype='application/json')
        else:
            return Response(
                response= json.dumps({
                    'message':"post not found"
                    }),
                status = HTTP_404_NOT_FOUND,
                mimetype='application/json')


# add comment to current post 
@posts_bp.route('/<string:slug>',methods=['POST'])
@jwt_required
def add_comment(slug):
    # get current user
    current_user = get_jwt_identity()
    # get current post
    post_info = Posts.query.filter_by(slug=slug,status='accepted').first()

    if not request.get_json():
            return Response(
                   response = json.dumps({"message": "No input data provided"}),
                   status = HTTP_400_BAD_REQUEST,
                   mimetype = 'application/json'
                   )

    json_data = request.get_json()

    # Validate and deserialize input
    try:
        data = comment_schema.load(json_data)
    except ValidationError as err:
        return err.messages, HTTP_422_UNPROCESSABLE_ENTITY

    msg = data["message"]

    try:
        comment_data = Comments(author_id=current_user,post_id = post_info.id,message=msg)

        # add post to database
        db.session.add(comment_data)
        db.session.commit()
    except Exception as ex:
        return Response(
            response= json.dumps({
                'error':' comment add database error',
                'Exception':f'{ex}'}),
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            mimetype='application/json'
            )
    comment_result = comment_schema.dump(comment_data)
    return Response(
        response= json.dumps({
            "message" : 'comment added successfully.',
            "result": comment_result
            }),
        status= HTTP_201_CREATED,
        mimetype='application/json'

        )


# search post
@posts_bp.route('/search',methods=['POST'])
def search():

    # if the user does not send the page who just defaults to send page no.one
    # but if user enter the page that's return that page we queried by
    page = request.args.get('page',1,type=int)

    # limit our posts in page - limit query
    per_page = request.args.get('per_page',5,type=int)

    if not request.get_json():
            return Response(
                   response = json.dumps({"message": "No input data provided"}),
                   status = HTTP_400_BAD_REQUEST,
                   mimetype = 'application/json'
                   )

    json_data = request.get_json()

    # Validate and deserialize input
    try:
        data = search_schema.load(json_data)
    except ValidationError as err:
        return err.messages, HTTP_422_UNPROCESSABLE_ENTITY

    searched_word = data['word']
    search_filter = Posts.query

    try:
        searched_data = search_filter.filter_by(status='accepted').filter(or_(Posts.content.like('%' + searched_word + '%' ),Posts.title.like('%' + searched_word + '%' ))).paginate(page=page,per_page=per_page)
    except Exception as ex:
        return Response(
            response=json.dumps({
                'message':'search error',
                'Exception':f'{ex}'
                }),
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            mimetype='application/json')


    if searched_data.items:
        search_result = posts_schema.dump(searched_data.items,many=True)
        meta = {
                'page': searched_data.page,
                'pages':searched_data.pages,
                'total_count':searched_data.total,
                'prev_page': searched_data.prev_num,
                'next_page': searched_data.next_num,
                'has_next': searched_data.has_next, # Boolean - means if there next pages after the current page
                'has_prev': searched_data.has_prev, # Boolean - means if there prev pages before the current page
               }

        return Response(
            response=json.dumps({
                'message':'Result found',
                'search':f'{searched_word}',
                'data': search_result,
                'meta':meta
                }),
            status=HTTP_200_OK,
            mimetype='application/json')
    else:
        return Response(
            response=json.dumps({
                'message':'Result not found'
                }),
            status=HTTP_404_NOT_FOUND,
            mimetype='application/json')


# edit post
@posts_bp.route('/edit/<int:pk>',methods=['PUT','PATCH'])
@jwt_required
def edit_post(pk):

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

    # check authorization to edit post
    if user_info.job == 'doctor' or user_info.job == 'admin':
        

        try:
            post_data = Posts.query.filter_by(id=pk).first()

            if post_data:

                # check if correct user
                if post_data.author_id == current_user or user_info.job == 'admin':

                    title = request.form['title']
                    content = request.form['content']
                    banner_img= request.files['banner_img']

                    # post_data.banner_img = img
                    post_data.title = title
                    post_data.content = content
                    post_data.date_posted = datetime.today()

                    # check if banner img exists
                    # check if the profile pic is exist 
                    if banner_img:
                        # save img
                        pic_name,path = save_image(banner_img)
                        # set image filename to database
                        post_data.profile_pic = pic_name
                        # apply changes to database
                        db.session.commit()
                    else:
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
                        'message':'post not found'
                        }),
                    status=HTTP_404_NOT_FOUND,
                    mimetype='application/json')
        except Exception as ex:
            return Response(
                response= json.dumps({
                    'error':' post edit database error',
                    'Exception': f'{ex}'}),
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                mimetype='application/json'
                )
        post_result = post_schema.dump(Posts.query.get(post_data.id))
        return Response(
            response= json.dumps({
                'message' : 'Post edited successfully',
                'result': post_result
                }),
            status= HTTP_201_CREATED,
            mimetype='application/json'

            )
    else:
        return Response(
                response= json.dumps({'message':'You are not authorized to access '}),
                status=HTTP_401_UNAUTHORIZED,
                mimetype='application/json'
                )





# delete post
@posts_bp.route('/delete/<int:pk>',methods=["DELETE"])
@jwt_required
def delete_post(pk):

    current_user = get_jwt_identity()


    try:
        post_info = Posts.query.filter_by(id=pk).first()
    except:
        return Response(
                    response= json.dumps({'error':'post database error'}),
                    status=HTTP_500_INTERNAL_SERVER_ERROR,
                    mimetype='application/json'
                    )
   
    if not post_info:
         return Response(
            response= json.dumps({
                'message': 'Post not found'
                }),
            status=HTTP_404_NOT_FOUND,
            mimetype='application/json')

    # check if correct user
    if post_info.author_id == current_user:
        try:
            db.session.delete(post_info)
            db.session.commit()
        except:
             return Response(
                response= json.dumps({
                    'error': 'delete post error'
                    }),
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                mimetype='application/json')

        return Response(
            response= json.dumps({
                'message':'post deleted successfully.'
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








