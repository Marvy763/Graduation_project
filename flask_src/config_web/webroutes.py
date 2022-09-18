
################################################################

# website routes

################################################################
from flask import render_template ,request,flash, redirect, url_for,jsonify,Response,abort
from flask_login import login_user,login_required,logout_user,current_user, user_accessed
from flask_src import app,db,login_manager
from .webforms import UserProfileForm,UserForm,LoginForm,PostForm,SearchForm,CommentForm,UploadForm,ChangePasswordForm
from flask_src.databases import Users,Posts,Comments,db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from sqlalchemy import or_
from flask_src.save import save_image,model
from flask_src.model import evaluation_model ,pred_info
import pickle

# from flask_src.predict import chestScanPrediction,pred_info
# lookup for logged user in database
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id)) 

# pass stuf to nav bar(parent page)
@app.context_processor
def base():
    form =SearchForm()
    return dict(form=form)


@app.route('/')
def index():
    # get top 3 posts
    top_posts = Posts.query.filter_by(status='accepted').order_by(Posts.views.desc()).all()
    # get 3 posts from blog
    posts= Posts.query.filter_by(status='accepted').order_by(Posts.date_posted.desc())
    return render_template("index.html",top_posts=top_posts,posts=posts)


# change password
@app.route('/change-password/<int:pk>',methods=['GET','POST'])
@login_required
def change_password(pk):

    change_pass_form = ChangePasswordForm()
    if change_pass_form.validate_on_submit():

        # lookup for user in db
        try:
            user_data = Users.query.filter_by(id=pk).first()
        except:
           flash('error in database, we try to fix it as soon as possible.','warning')

        # check if correct user
        if current_user.id == user_data.id:

           # check if old password is correct
            is_pass_correct = check_password_hash(user_data.pass_hash, change_pass_form.old_pwd.data)
            # check the password hash
            if is_pass_correct:
                # if correct add new hased password to db
                new_pwd = generate_password_hash(change_pass_form.password.data)
                user_data.pass_hash=new_pwd
                db.session.commit()
                flash('changed password successfully.','success')
            else:
               flash('old password is wrong - try again','error')
        else:
           flash('you are not authorized to access.','error')
    change_pass_form.old_pwd.data=''
    change_pass_form.password.data=''
    change_pass_form.confirm.data=''
    return render_template("edit_profile.html",change_pass_form=change_pass_form)




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
                flash("login success",'info')
                return redirect(url_for('upload'))
            else:
                flash("wrong password - try again",'error')
        else:
             flash("user doesnt exist !!!! try again.....",'error')
    return render_template("login.html",form=form)


# create logout route
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('logged out success','info')
    return redirect(url_for('login'))

# add user
@app.route('/register', methods= ['GET','POST'])
def register():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        # check if the user already exist in the database
        user1= Users.query.filter_by(email = form.email.data).first()
        user2= Users.query.filter_by(username = form.username.data).first()
        if user1:
            flash('Email already exist.','error')
            return render_template("register.html", form=form,
                name=name )
        if user2:
            flash('Username already exist.','error')
            return render_template("register.html", form=form,
                name=name )
            # try:
            # hash password

        if len(form.phone.data.replace(" ", "")) != 11:
            flash('invalid phone number. phone number must contain of 11 number.','error')
            return render_template("register.html", form=form,
                name=name )
        if form.phone.data[0:2] != '01':
            flash("invalid phone number. phone number must start of '01'",'error')
            return render_template("register.html", form=form,
                name=name )
# important
        if form.phone.data.isnumeric() == False:
            flash("invalid phone number. phone number must start of '01'",'error')
            return render_template("register.html", form=form,
                name=name )
        hashed_pw = generate_password_hash(form.pass_hash.data,"sha256")
        user = Users(name = form.name.data, username= form.username.data, email= form.email.data , job = form.job.data,phone = form.phone.data
        ,password =hashed_pw,description= form.description.data)
        db.session.add(user) #add user to database
        db.session.commit()
            # except:
            #     flash(f"User {form.username.data} is already registered.")
            #     return render_template("register.html",form=form,
            #     name=name )

        name = form.name.data
        form.name.data = ''
        form.phone.data = ''
        form.username.data = ''
        form.email.data = ''
        form.job.data = 'patient'
        form.pass_hash.data = ''
        form.description.data = ''
        flash('user add successfully','success')
        return redirect(url_for('login'))
    name = form.name.data
    form.name.data = ''
    form.phone.data = ''
    form.username.data = ''
    form.email.data = ''
    form.job.data = 'patient'
    form.pass_hash.data = ''
    form.description.data = ''
    return render_template("register.html", form = form,
            name=name )

    # # our_user = Users.query.order_by(Users.data_added)
    # return render_template("register.html",
    # form=form, 
    # name=name )

# edit user data
@app.route('/edit/<int:pk>',methods=['GET','POST'])
def edit_user(pk):
    id = current_user.id
    edit_user_form = UserProfileForm()
    name_to_update = Users.query.get_or_404(pk)
    if request.method == 'POST':
        if id == pk :
            # assign the entire image
            # name_to_update.profile_pic = edit_user_form.profile_pic.data
            name_to_update.name = edit_user_form.name.data
            name_to_update.email = edit_user_form.email.data
            name_to_update.username=edit_user_form.username.data
            name_to_update.phone=edit_user_form.phone.data
            name_to_update.job=edit_user_form.job.data
            
            name_to_update.description =edit_user_form.description.data

            # check for profile pic
            if  edit_user_form.profile_pic.data: 

                pic_name, path = save_image(edit_user_form.profile_pic.data)
                # set image filename to database
                name_to_update.profile_pic = pic_name

                try:
                    db.session.commit()
                    flash('user updated successfully!','success')
                    return render_template("edit_user.html",
                    id=id,
                    edit_user_form=edit_user_form,
                    name_to_update = name_to_update),200
                except :
                    flash('error in update .. failed','warning')
                    return render_template("edit_user.html",
                    id=id,
                    edit_user_form=edit_user_form,
                    name_to_update = name_to_update),500
            else:
                try:
                    db.session.commit()
                    flash('user updated successfully!','success')
                    return render_template("edit_user.html",
                    id=id,
                    edit_user_form=edit_user_form,
                    name_to_update = name_to_update),200
                except :
                    flash('error in update .. failed','warning')
                    return render_template("edit_user.html",
                    id=id,
                    edit_user_form=edit_user_form,
                    name_to_update = name_to_update),500
        else:
            flash('you are not authorized to update this user.','error')
            return render_template("edit_user.html"),400

    else:
        # show old data when user clicked
        return render_template("edit_user.html",
            id= id,
            edit_user_form=edit_user_form,
            name_to_update=name_to_update),200
    return render_template("edit_user.html"),200



# delete user
@app.route('/delete/<int:pk>')
@login_required
def delete(pk):
    id = current_user.id
    change_pass_form = ChangePasswordForm()
    name_to_delete = Users.query.get_or_404(pk)

    if id  == pk:
      if name_to_delete.job == 'doctor' or name_to_delete.job == 'admin':
            comments = Comments.query.filter_by(author_id=pk).all()
                # check if user commented 
            if comments:
                db.session.delete(comments)
            posts = Posts.dumps.filter_by(author_id=pk).all()
            # check if the user posted posts
            if posts:
                db.session.delete(posts)
                # db.session.commit()
      try:
            db.session.delete(name_to_delete)
            db.session.commit()

            flash('your account deleted successfully!!!','success')
            return redirect(url_for('login')),302
      except:
          flash('error in database - try again...')
          return render_template("edit_profile.html",change_pass_form=change_pass_form)
    else:
        flash('You are not Authorized To Delete That Post!','error')  
        change_pass_form= ChangePasswordForm()
        return render_template("edit_profile,html",change_pass_form=change_pass_form)



# create blog post
@app.route('/add-post',methods=['GET','POST'])
# first way to lock page
# @login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        author = current_user.id
        Thanks=''

        if current_user.job == 'doctor' or current_user.job == 'admin':

            # set status
            if current_user.job == 'doctor':
                status = 'pending'
                Thanks='Your post has been submited.  post will be published after approval of admin'
            else:
               status = 'accepted'
               Thanks = 'Your post has been submited and published successfully.'
            try: 

                
                if form.banner_img.data:
                    pic_name,path = save_image(form.banner_img.data)
                    post = Posts(status=status,title=form.title.data,content=form.content.data,author_id = author,banner_img=pic_name)
                else:
                    post = Posts(status=status,title=form.title.data,content=form.content.data,author_id = author,banner_img=form.banner_img.data)

              
                # add post to database
                db.session.add(post)
                db.session.commit()
            except:
                flash('database error','warning')
                abort(500)

            #clear post form
            form.title.data =''
            form.content.data=''
            # form.author.data=''
            # form.slug.data=''


            # return a message
            flash(f'{Thanks}','success')
            return redirect(url_for('posts'))
        else:
            flash('you are not authorized to access this page.','error')
            return redirect(url_for('posts'))

    # redirect to the web page
    return render_template("add_post.html",
    form=form)

# get posts
@app.route('/posts')
def posts():
    page = request.args.get('page',1,type=int)
    # Grab all the posts from the database
    posts= Posts.query.filter_by(status='accepted').order_by(Posts.date_posted.desc()).paginate(page=page,per_page=6)
    return render_template("posts.html",posts=posts)


# show individual blog post
@app.route('/posts/<string:slug>',methods=['GET','POST'])
def show_post(slug):
    # get selected post
    post = Posts.query.filter_by(slug=slug).first()
    if post.status == 'accepted':
        # increament views by 1 
        post.views=post.views +1
        db.session.commit() #push changes into databases
    # check if user do comment 
    comment_form = CommentForm()
    comment_edit_form = CommentForm()
    if request.method == "POST":
        if comment_form.validate_on_submit():

            try:
                comment_data = Comments(post_id=post.id,author_id=current_user.id,message=comment_form.message.data)
                db.session.add(comment_data)
                db.session.commit()
                flash('comment add successfully','success')
                comment_form.message.data=''
                # get all comments on that post
                comments = Comments.query.filter_by(post_id= post.id).order_by(Comments.date_pub.desc()).all()
                return render_template("show_post.html",post= post,comments=comments,comment_form=comment_form,comment_edit_form=comment_edit_form),200
            except:
                flash('error in database for commenting this post.','error')
                return redirect(request.url),500
    # get all comments on that post
    comments = Comments.query.filter_by(post_id= post.id).order_by(Comments.date_pub.desc()).all()
    return render_template("show_post.html",post= post,comments=comments,comment_form=comment_form,comment_edit_form=comment_edit_form),200


# edit comment
@app.route('/posts/comment/edit/<int:pk>',methods=['GET','POST'])
@login_required
def edit_comment(pk):
    # get comment to be updated
    comment = Comments.query.get_or_404(pk)
     # get selected post
    post = Posts.query.filter_by(slug=comment.commenters.slug).first()
    comment_edit_form=CommentForm()
    if request.method == 'POST':
        if comment_edit_form.validate_on_submit():
            if current_user.is_authenticated:
               comment.message = comment_edit_form.message.data
            try:
                db.session.add(comment)
                db.session.commit()
                flash('comment updated successfully','success')
                return redirect(url_for('show_post',slug=comment.commenters.slug))
            except:
                flash('error in database','warning')
             # get all comments on that post
    comments = Comments.query.filter_by(post_id= post.id).order_by(Comments.date_pub.desc()).all()
    return render_template("edit_comment.html",comment=comment,post= post,comments=comments,comment_edit_form=comment_edit_form),200

# delete comment
@app.route('/posts/comment/delete/<int:pk>')
@login_required
def delcomment(pk):
    # get the comment to be deleted
    comment = Comments.query.get_or_404(pk)
    slug = comment.commenters.slug
    try:
        db.session.delete(comment)   
        db.session.commit()     
        flash('comment deleted successfully.','success')
    except:
        flash('database error','error')
    return redirect(url_for('show_post',slug=slug))



# get top posts
@app.route('/posts/top',methods=['GET'])
def top_posts():
    page = request.args.get('page',1,type=int)
    posts = Posts.query.filter_by(status='accepted').order_by(Posts.views.desc()).paginate(page=page,per_page=6)
    return render_template("top_posts.html",posts=posts)

# get pending posts - for admin
@app.route('/admin/pending-posts')
@login_required
def pending_posts():
    page = request.args.get('page',1,type=int)
    posts = Posts.query.filter_by(status='pending').paginate(page=page,per_page=6)
    return render_template("pending_admin.html",posts=posts)

# get pending posts - for user
@app.route('/pending/<int:pk>',methods=['GET','POST'])
@login_required
def pending_posts_user(pk):
    user = Users.query.get_or_404(pk)
    id = current_user.id 
    page = request.args.get('page',1,type=int)
    posts = Posts.query.filter_by(status='pending',author_id=pk).order_by(Posts.date_posted.desc()).paginate(page=page,per_page=6)
    return render_template("pending_user.html",posts=posts)


# make admin publish posts
@app.route('/check/<int:id>', methods=['POST','GET'])
@login_required
def check(id):
    post = Posts.query.get_or_404(id)
    try:
        post.status = 'accepted'
        db.session.commit()
        flash("post publish successfully",'success')
    except:
        flash("database error",'warning')
    return redirect(url_for('pending_posts')) 


# create search bar
@app.route('/search',methods=['POST'])
def search():
    form =SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # get data from submitted form
        searched = form.searched.data
        # query the database
        # search by containing the word searched
        page = request.args.get('page',1,type=int)
        posts = posts.filter_by(status='accepted').filter(or_(Posts.content.like('%' + searched + '%' ),Posts.title.like('%' + searched + '%' )))
        # return all the results
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html",posts=posts,form=form,searched=searched)


# upload photo to model to be predicted
@app.route('/upload', methods=['GET'])
@login_required
def upload():
    form = UploadForm()
    return render_template("upload.html",form=form),200
    
# upload photo to model to be predicted
@app.route('/upload', methods=['POST'])
@login_required
def result():
    form = UploadForm()
    image,imgPath = save_image(form.file_predict.data)
    image= evaluation_model(imgPath)
    prediction = model.predict(image)
    result = pred_info(prediction[0])
    form.file_predict.data = ''
    return render_template("upload.html",form=form,result=result)

    # return render_template("upload.html",form=form),200



@app.route('/user-profile/<int:pk>')
def user_profile(pk):
    # get user information
    user = Users.query.get_or_404(pk)
    return render_template("profile.html",user=user)

@app.route('/faq')
def faq():
    return render_template("faq.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/advices')
def advices():
    return render_template("advices.html")


# edit blog post
@app.route('/posts/edit/<string:slug>', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    post = Posts.query.filter_by(slug=slug).first()
    if not post:
        abort(404)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        #post.author = form.author.data
        post.content = form.content.data

        # post.banner_img = form.banner_img.data

        if form.banner_img.data:
            pic_name, path = save_image(form.banner_img.data)
                # set image filename to database
            post.profile_pic = pic_name
            # Update Database
            db.session.add(post)
            db.session.commit()
            flash("Post Has Been Updated!",'success')
            return redirect(url_for('show_post', slug=post.slug))
        else:
            db.session.commit()
            flash("Post Has Been Updated!",'success')
            return redirect(url_for('show_post', slug=post.slug))
    
    if current_user.id == post.author_id or current_user.job == 'admin':
        form.title.data = post.title
        #form.author.data = post.author
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You Aren't Authorized To Edit This Post...",'error')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


# delete blog post
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.filter_by(status="accepted",id=id).first()
    if current_user.id == post_to_delete.author.id or current_user.job == 'admin':
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            # return a message and redirect
            flash('Blog Post was deleted','info')
            posts= Posts.query.order_by(Posts.date_posted.desc()).paginate(page=1,per_page=6)
            return render_template("posts.html",posts=posts)
            # return render_template("posts.html",posts=posts)
        except:
            # return flash error
            flash('database error ... try again','warning')

            posts= Posts.query.order_by(Posts.date_posted.desc()).paginate(page=1,per_page=6)
            return render_template("posts.html",posts=posts)
    else:
        # return flash error
            flash('not authorized to delete this post','error')

            posts= Posts.query.order_by(Posts.date_posted.desc()).paginate(page=1,per_page=6)
            return render_template("posts.html",posts=posts)

@app.route('/admin/posts/delete/<int:id>')
@login_required
def delete_post_admin(id):
    post_to_delete = Posts.query.get_or_404(id)
    if current_user.job == 'admin':
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            # return a message and redirect
            flash('Blog Post was deleted','info')
            posts= Posts.query.order_by(Posts.date_posted)
            return redirect(url_for('pending_posts'))
            # return render_template("posts.html",posts=posts)
        except:
            # return flash error
            flash('database error ... try again','warning')

            posts= Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html",posts=posts)
    else:
        # return flash error
            flash('not authorized to delete this post','error')

@app.route('/user/posts/delete/<int:id>')
@login_required
def delete_post_user(id):
    post_to_delete = Posts.query.filter_by(status="pending",id=id).first()
    if current_user.id == post_to_delete.author.id or current_user.job == 'admin':
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            # return a message and redirect
            flash('Blog Post was deleted','info')
            return render_template("pending_user.html",pk=current_user.id)
            # return render_template("posts.html",posts=posts)
        except:
            # return flash error
            flash('database error ... try again','warning')

            return render_template("pending_user.html",pk=current_user.id)

    else:
        # return flash error
            flash('not authorized to delete this post','error')

            return render_template("pending_user.html",pk=current_user.id)

 


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



# # restful api
# @app.route('/api',methods=['GET'])
# def api_home():
#     return jsonify({"message":"api_home"});