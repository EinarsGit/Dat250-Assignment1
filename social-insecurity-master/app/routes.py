from flask import render_template, flash, redirect, url_for
from flask_login import login_user, login_required, current_user, logout_user
from app import app, limiter, secure_query
from app.Security import User
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import string
import random


# this file contains all the different routes, and the logic for communicating with the database
# home page/login/registration
@app.route('/', methods=['GET', 'POST'])  # the methods mean that you can only get and post in this url
@app.route('/index', methods=['GET', 'POST'])
@limiter.limit('15 per minute')
def index():
    form = IndexForm()
    if current_user.is_authenticated:
        return redirect(url_for('stream', username=current_user.get_id()))

    if form.login.is_submitted() and form.login.submit.data:
        user = User.load_user(form.login.username.data)  # .data returns what it was typed in
        if user is None:
            flash('Sorry, wrong username or password!')
        elif check_password_hash(user.get_password(), form.login.password.data):
            login_user(user, form.login.remember_me.data)
            flash('Logged in successfully!')
            return redirect(url_for('stream', username=form.login.username.data))
        else:
            flash('Sorry, wrong username or password!')

    #elif form.register.is_submitted() and form.register.submit.data:
    elif form.register.validate_on_submit():
        hashed_password = generate_password_hash(form.register.password.data, method='pbkdf2:sha512', salt_length=8)

        if check_if_username_in_db(form.register.username.data) is None:
            secure_query('INSERT INTO Users (username, first_name, last_name, password) VALUES(?, ?, ?, ?);', [
                form.register.username.data, form.register.first_name.data, form.register.last_name.data, hashed_password])
            flash('Account successfully created! ')
            return redirect(url_for('index'))
        else:
            flash("This username isn't available. Please enter a username that isn't already taken!")
    return render_template('index.html', title='Welcome', form=form)


# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
@login_required #requires to be logged in
@limiter.limit('4 per second')
def stream(username):
    if username != current_user.get_id():
        return redirect(url_for('stream', username=current_user.get_id()))

    form = PostForm()
    user = secure_query('SELECT * FROM Users WHERE username= ?;', [username], one=True)
    if form.is_submitted():
        if form.content.data == "" and form.image.data.filename == "":
            # Checks if content and image is empty and return
            flash("Post content is empty!")
            return redirect(url_for('stream', username=username))

        filename = form.image.data.filename
        if form.image.data:
            # Checks if file type is allowed
            if form.image.data.filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                filename = current_user.get_id() + str(datetime.now().second) + randomString()
                path = os.path.join(app.config['UPLOAD_PATH'], filename)
                form.image.data.save(path)
            else:
                # Returns if upload requirements are not met
                flash("File type not supported")
                return redirect(url_for('stream', username=username))

        secure_query('INSERT INTO Posts (u_id, content, image, creation_time) VALUES(?, ?, ?, ?);', [
            user['id'], form.content.data, filename, datetime.now()])

    posts = secure_query('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id=?) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id=?) OR p.u_id=? ORDER BY p.creation_time DESC;',[
        user['id'], user['id'], user['id']])
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)

@app.route('/logout/')
@login_required
def logout():
    logout_user() #removes user id-session from cookies
    flash('You have successfully logged yourself out.')
    return redirect(url_for('index'))

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
@login_required
@limiter.limit('4 per second')
def comments(username, p_id):
    if username != current_user.get_id():
        return redirect(url_for('comments', username=current_user.get_id(), p_id=p_id))

    form = CommentsForm()
    if form.is_submitted():
        user = secure_query('SELECT * FROM Users WHERE username= ?;', [username], one=True)
        secure_query('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES(?, ?, ?, ?);', [p_id, user['id'], form.comment.data, datetime.now()])

    post = secure_query('SELECT * FROM Posts WHERE id=?;', [p_id], one=True)
    all_comments = secure_query('SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id=? ORDER BY c.creation_time DESC;', [p_id])
    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)

# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
@login_required
@limiter.limit('4 per second')
def friends(username):
    if username != current_user.get_id():
        return redirect(url_for('friends', username=current_user.get_id()))

    form = FriendsForm()
    user = secure_query('SELECT * FROM Users WHERE username= ?;', [username], one=True)

    if form.is_submitted():
        friend = secure_query('SELECT * FROM Users WHERE username= ?;', [form.username.data], one=True)
        if friend is None:
            flash('User does not exist')
        elif user['id'] == friend['id']:
            flash("You can't add yourself as a friend!")
        elif check_if_friend(user['id'], friend['id']) is not None:
            flash("This friend has already been added!")
        else:
            secure_query('INSERT INTO Friends (u_id, f_id) VALUES(?, ?);', [user['id'], friend['id']])

    all_friends = secure_query('SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id=? AND f.f_id!=? ;', [user['id'], user['id']])
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
@limiter.limit('5 per second')
def profile(username):
    form = ProfileForm()
    user = secure_query('SELECT * FROM Users WHERE username= ?;', [username], one=True)

    if username == current_user.get_id():
        if form.is_submitted():
            secure_query('UPDATE Users SET education= ?, employment= ? , music= ?, movie= ? , nationality= ? , birthday= ? WHERE username= ? ;', [
                form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username])
            return redirect(url_for('profile', username=username))
        else:
            return render_template('profile.html', title='profile', username=username, user=user, form=form)

    else:
        if check_if_username_in_db(username) is not None:
            return render_template('profile.html', title='profile', username=username, user=user)
        ## Don't need the form anymore, because it will not be used in this case
        else:
            flash('User does not exist')
            return redirect(url_for('profile', username=current_user.get_id()))


def check_if_username_in_db(username):
    return secure_query('SELECT * FROM Users WHERE username= ?;', [username], one=True)

def check_if_friend(user_id, id_tocheck):
    return secure_query('SELECT * FROM Friends WHERE u_id= ? and f_id = ?;', [user_id, id_tocheck], one=True)


def randomString(stringLength=30):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))