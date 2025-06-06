import flask

from db import posts, users, helpers

blueprint = flask.Blueprint("posts", __name__)

@blueprint.route('/post', methods=['POST'])
def post():
    """Creates a new post."""
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    post = flask.request.form.get('post')
    tags = flask.request.form.get('tags').replace(' ', '').split(',')
    files = flask.request.form.get('files').replace(' ', '').split(',')
    #print(post, tags, files)
    posts.add_post(db, user, post, files, tags)

    return flask.redirect(flask.url_for('login.index'))
