import flask
import tinydb
import os
import db

from db import posts, users, helpers
from db import search as dbsearch
from handlers import copy


from datetime import datetime, timedelta
from dateutil import parser



def verify_login(username, password):
    db = helpers.load_db()
    #username = flask.request.cookies.get('username')
    #password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if username is None and password is None or not user:
        flask.flash('Invalid credentials. Please try again.', 'danger')
        return False
    return True




blueprint = flask.Blueprint("search", __name__)
@blueprint.route('/search')
def search():
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    
    # verify = verify_login(username, password)
    # if verify is False:
        # flask.flash('Invalid credentials. Please try again.', 'danger')
    # if not verify:
        # return flask.redirect(flask.url_for('login.loginscreen'))

    if not verify_login(username, password):
        return flask.redirect(flask.url_for('login.loginscreen'))

    user = users.get_user(db, username, password)

    # get the info for the user's feed
    #friends = users.get_user_friends(db, user)
    #all_posts = []
    #for friend in friends + [user]:
    #    all_posts += posts.get_posts(db, friend)
    # sort posts
    #sorted_posts = sorted(all_posts, key=lambda post: post['time'], reverse=True)

    query = flask.request.args.get('query')
    page = flask.request.args.get('page')

    try: 
        page = int(page)
        page_is_int = True
    except:
        page = None
        page_is_int = False

    per_page = 50

    print(page)

    if page is not None and page > 0:
        query += " _start:{} _end:{}".format((page-1)*per_page, page*per_page)

    queried_posts = dbsearch.get_posts(db, query)

    return flask.render_template('search.html', posts=queried_posts)
