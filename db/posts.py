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

    raise RuntimeError("Error: This get_posts is outdated. Get files using search API instead")

    dbposts = db.table('posts')
    Post = tinydb.Query()
    posts = dbposts.search(Post.user==user['username'])
    #print("====================")
    #print(post)
    #for post in posts:
    #    post['tags'] = set(post['tags'])
        
    return posts
