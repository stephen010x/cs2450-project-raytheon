import time
import tinydb

def add_post(db, user, text, file_hashes=[], tags={}, time_override=None):
    posts = db.table('posts')
    posts.insert({
        'user': user['username'], 
        'text': text, 
        'time': time_override if time_override else time.time(),
        'files': file_hashes,
        'tags': list(tags),
    })

def get_posts(db, user):
    posts = db.table('posts')
    Post = tinydb.Query()
    post = posts.search(Post.user==user['username'])
    print(post)
    post['tags'] = set(post['tags'])
    return post
