import flask

from handlers import copy
from db import posts, users, helpers, search
from db import search as dbsearch

blueprint = flask.Blueprint("account", __name__)

@blueprint.route('/create', methods=['POST'])
def create():
    return flask.render_template('new_account.html', title=copy.title,
            subtitle=copy.subtitle)

@blueprint.route('/loginscreen')
def loginscreen():
    """Present a form to the user to enter their username and password."""
    db = helpers.load_db()

    # First check if already logged in
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if username is not None and password is not None:
        if users.get_user(db, username, password):
            # If they are logged in, redirect them to the feed page
            flask.flash('You are already logged in.', 'warning')
            return flask.redirect(flask.url_for('login.index'))

    return flask.render_template('login.html', title=copy.title,
            subtitle=copy.subtitle)

@blueprint.route('/account', methods=['POST'])
def account():

    db = helpers.load_db()

    username = flask.request.form.get('username')
    password = flask.request.form.get('password')

    resp = flask.make_response(flask.redirect(flask.url_for('login.index')))
    resp.set_cookie('username', username)
    resp.set_cookie('password', password)

    submit = flask.request.form.get('type')
    if submit == 'Create':
        user, error = users.new_user(db, username, password)
        if user is None:
            resp.set_cookie('username', '', expires=0)
            resp.set_cookie('password', '', expires=0)
            #flask.flash('Username {} already taken!'.format(username), 'danger')
            flask.flash(error, 'danger')
            return flask.redirect(flask.url_for('login.loginscreen'))
        flask.flash('User {} created successfully!'.format(username), 'success')
    elif submit == 'Delete':
        # if users.delete_user(db, username, password):
        #     resp.set_cookie('username', '', expires=0)
        #     resp.set_cookie('password', '', expires=0)
        #     flask.flash('User {} deleted successfully!'.format(username), 'success')
        if not username or not password:
            flask.flash('Username and password are required to delete an account.', 'danger')
            return flask.redirect(flask.url_for('login.loginscreen'))

        if users.delete_user(db, username, password):
            resp.set_cookie('username', '', expires=0)
            resp.set_cookie('password', '', expires=0)
            flask.flash(f'User {username} deleted successfully!', 'success')
        else:
            flask.flash('Invalid username or password.', 'danger')


    return resp

@blueprint.route('/logout', methods=['POST'])
def logout():
    """Log out the user."""
    db = helpers.load_db()

    resp = flask.make_response(flask.redirect(flask.url_for('login.loginscreen')))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('password', '', expires=0)
    return resp

@blueprint.route('/')
def index():
    """Serves the main feed page for the user."""
    db = helpers.load_db()

    # make sure the user is logged in
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    if username is None and password is None:
        return flask.redirect(flask.url_for('login.loginscreen'))
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('Invalid credentials. Please try again.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # get the info for the user's feed
    friends = users.get_user_friends(db, user)
    #all_posts = []
    #for friend in friends + [user]:
    #    all_posts += posts.get_posts(db, friend)
    # sort posts
    #print(all_posts)
    #sorted_posts = sorted(all_posts, key=lambda post: post['time'], reverse=True)

    sorted_posts = dbsearch.get_posts(db, "sort:newest _end:50")

    return flask.render_template('home.html', title=copy.title,
            subtitle=copy.subtitle, user=user, username=username,
            friends=friends, posts=sorted_posts)


@blueprint.route('/profile')
def profile():
    db = helpers.load_db()
    username = flask.request.cookies.get('username')

    # Get user data
    user = users.get_user_by_name(db, username)
    if user is None:
        flask.flash('User not found.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # Get user-specific data
    post_list = search.get_posts(db, username)
    post_count = len(post_list)
    join_date = user.get('created_at')

    return flask.render_template('profile.html',
                                 username=username,
                                 join_date=join_date,
                                 post_count=post_count,
                                 posts=post_list)