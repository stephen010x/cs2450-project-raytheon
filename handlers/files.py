import flask
import os
import random
import string
#from flask import request, send_file


DDIR = os.path.abspath(f'./files')


app = flask.Flask(__name__)


# I don't know why the other handlers don't require this
template_folder = "../templates"

blueprint = flask.Blueprint("upload_test", __name__, template_folder=template_folder)


# @blueprint.route('/file/<filename>/')
# def file(filename):
    # with open(f'{DDIR}/{filename}') as file:
        # file_contents = file.read()
    # return flask.render_template('file.html', file_contents=file_contents)

@app.route('/file/<filename>')
def file(filename):
    # the abspath will make it relative to the flask application rather than 
    # the directory.
    #filepath = os.path.abspath(f'{DDIR}/{filename}')
    filepath = f'{DDIR}/{filename}'
    if os.path.exists(filepath) and os.path.isfile(filepath):
        return flask.send_file(filepath) # , as_attachment=True
    else:
        flask.abort(404)



@app.route('/upload', methods=['POST'])
def upload():
    files = flask.request.files.getlist('files[]')

    response_links = []

    for file in files:
        # generate random file name to be stored for each file sent
        extension = os.path.splitext(file.filename)[1]
        filename = f'{random_string(8)}{extension}'
        while os.path.exists(f'{DDIR}/{filename}'):
            filename = f'{random_string(8)}{extension}'
            
        file.save(f'{DDIR}/{filename}')
        response_links.append(f'/file/{filename}')

    # pickles list array to be sent back to client
    return flask.jsonify(message=response_links)


@blueprint.route('/upload_test')
def upload_test():
    return flask.render_template('upload_test.html')

	
def random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string
