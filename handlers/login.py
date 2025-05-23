import flask

from handlers import copy
from db import posts, users, helpers
from db import search as dbsearch

blueprint = flask.Blueprint("login", __name__)

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

@blueprint.route('/login', methods=['POST'])
def login():
    """Log in the user.

    Using the username and password fields on the form, create, delete, or
    log in a user, based on what button they click.
    """
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
        if users.delete_user(db, username, password):
            resp.set_cookie('username', '', expires=0)
            resp.set_cookie('password', '', expires=0)
            flask.flash('User {} deleted successfully!'.format(username), 'success')

    return resp

@blueprint.route('/logout', methods=['POST'])
def logout():
    """Log out the user."""
    db = helpers.load_db()

    resp = flask.make_response(flask.redirect(flask.url_for('login.loginscreen')))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('password', '', expires=0)
    return resp




def user_login_gate():
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    if username is None and password is None:
        return False, flask.redirect(flask.url_for('login.loginscreen'))
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('Invalid credentials. Please try again.', 'danger')
        return False, flask.redirect(flask.url_for('login.loginscreen'))
    return True, None


def get_my_user():
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    db = helpers.load_db()
    return users.get_user(db, username, password)



@blueprint.route('/')
def index():
    """Serves the main feed page for the user."""
    db = helpers.load_db()

    # make sure the user is logged in
    ok, ret = user_login_gate()
    if not ok: return ret

    user = get_my_user()
    friends = users.get_user_friends(db, user)

    # get the posts for feed
    sorted_posts = dbsearch.get_posts(db, "sort:newest _end:50")

    return flask.render_template('home.html', title=copy.title,
            subtitle=copy.subtitle, user=user, username=user['username'],
            friends=friends, posts=sorted_posts)




@blueprint.route('/plain/<path>')
def plain(path):
    db = helpers.load_db()

    # make sure the user is logged in
    ok, ret = user_login_gate()
    if not ok: return ret

    return flask.render_template(path+'.html')




@blueprint.route('/self/<path>')
def self(path):
    db = helpers.load_db()
    
    # make sure the user is logged in
    ok, ret = user_login_gate()
    if not ok: return ret

    myuser = get_my_user()
    friends = users.get_user_friends(db, myuser)

    return flask.render_template(path+'.html', myuser=myuser, friends=friends)


@blueprint.route('/user/<username>/<path>')
def user(username, path):
    db = helpers.load_db()
    
    # make sure the user is logged in
    ok, ret = user_login_gate()
    if not ok: return ret

    myuser = get_my_user()
    user = get_user_safe(db, username)

    return flask.render_template(path+'.html', myuser=myuser, user=user)
