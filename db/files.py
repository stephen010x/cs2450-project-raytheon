import time
import tinydb
import os
import random
import string
import urllib
import types


DDIR = os.path.abspath(f'./files')


def random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def add_file(db, user, file):
    files = db.table('files')

    # determine unique file hash
    file_hash = random_string(8)
    while files.get(tinydb.Query()['hash'] == file_hash):
        file_hash = random_string(8)

    # determine remaning file properties
    file_name = file.filename
    file_ext = os.path.splitext(file_name)[1][1:]
    file_path = f'{DDIR}/{file_hash}.{file_ext}'
    file_url = f'/file/{file_hash}/{urllib.parse.quote(file_name)}'

    if not os.path.exists(DDIR):
	    os.makedirs(DDIR)

    # store file on server
    file.save(file_path)

    entry = {
        'hash' : file_hash,
        'name' : file_name,
        'ext'  : file_ext,
        'path' : file_path,
        'url'  : file_url,
        'user' : user['username'] if user else 'anonymous',
        'time' : time.time(),
    }
    files.insert(entry)
    
    # returns an object-like structure with the above properties
    return entry


# TODO: finish implementing this
# will also delete file, if it still exists
# def delete_file(db, file_hash):
    # files = db.table('files')
    # entry = get_file(db, file_hash)
    # key = list(files.search(tinydb.Query()['hash'] == file_hash)[0].keys())[0]
    # if (os.path.exists(entry['path'))):
        # delete file here
    # files.remove(query.key == key)
    # return


def get_file(db, file_hash):
    files = db.table('files')
    return files.get(tinydb.Query()['hash'] == file_hash)


def get_files(db, username, file_name=None):
    files = db.table('files')

    if file_name:
        return files.search(
            (tinydb.Query()['user'] == username) and
            (tinydb.Query()['name'] == file_name)
        )

    return files.search((tinydb.Query()['user'] == username))
