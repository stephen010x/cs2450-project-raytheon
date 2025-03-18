# TODO:
#   - make file links redirect to pseudo name links to retain file name
#   - add file database stuff (name, user, date, etc)


import flask
import tinydb
import os
import db

# this is just to root out syntax errors in the module
# because they don't display properly otherwise
from db import files as ignore_me

#import os
#import random
#import string
#from flask import request, send_file


app = flask.Flask(__name__)


# I don't know why the other handlers don't require this
template_folder = "../templates"
blueprint = flask.Blueprint("upload_test", __name__, template_folder=template_folder)



# allright, the discarded filename at the end might be enough to spoof the name
@app.route('/file/<file_hash>/<file_name>')
def file(file_hash, file_name):
    #filepath = f'{DDIR}/{hash}'
    #if os.path.exists(filepath) and os.path.isfile(filepath):
    #    return flask.send_file(filepath)
    #else:
    #    flask.abort(404)
    mydb = db.helpers.load_db()
    entry = db.files.get_file(mydb, file_hash)

    if not os.path.exists(entry['path']):
        # TODO: implement later
        #db.files.delete_file(entry['hash'])
        flask.abort(404)
    
    if entry:
        return flask.send_file(entry['path'], download_name=file_name)
    else:
        flask.abort(404)



@app.route('/upload', methods=['POST'])
def upload():
    files = flask.request.files.getlist('files[]')
    mydb = db.helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = db.users.get_user(mydb, username, password)

    response_links = []

    for file in files:
        # add file to db, and retrieve entry for response
        entry = db.files.add_file(mydb, user, file)
        
        response_links.append({
            'hash' : entry['hash'],
            'name' : entry['name'],
            'ext'  : entry['ext'],
            'url'  : entry['url'],
            'user' : entry['user'],
            'time' : entry['time'],
        })

    # pickle list array to be sent back to client
    return flask.jsonify(message=response_links)



@blueprint.route('/upload_test')
def upload_test():
    return flask.render_template('upload_test.html')










########################
####                ####
####  GARBAGE CODE  ####
####                ####
########################





# @app.route('/upload', methods=['POST'])
# def upload():
    # files = flask.request.files.getlist('files[]')
# 
    # response_links = []
# 
    # for file in files:
        # # generate random file name to be stored for each file sent
        # extension = os.path.splitext(file.filename)[1]
        # filename = f'{random_string(8)}{extension}'
        # while os.path.exists(f'{DDIR}/{filename}'):
            # filename = f'{random_string(8)}{extension}'
            # 
        # file.save(f'{DDIR}/{filename}')
        # response_links.append(f'/file/{filename}')
# 
    # # pickles list array to be sent back to client
    # return flask.jsonify(message=response_links)




# @blueprint.route('/file/<filename>/')
# def file(filename):
    # with open(f'{DDIR}/{filename}') as file:
        # file_contents = file.read()
    # return flask.render_template('file.html', file_contents=file_contents)

# @app.route('/file/<filename>')
# def file(filename):
    # # the abspath will make it relative to the flask application rather than
    # # the directory.
    # #filepath = os.path.abspath(f'{DDIR}/{filename}')
    # filepath = f'{DDIR}/{filename}'
    # if os.path.exists(filepath) and os.path.isfile(filepath):
        # return flask.send_file(filepath) # , as_attachment=True
    # else:
        # flask.abort(404)
