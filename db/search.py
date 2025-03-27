import time
import tinydb
from tinydb import Query

from db import files as dbfiles
from db import users as dbusers
from db import posts as dbposts

from datetime import datetime, timedelta
from dateutil import parser

import markdown



def parse_date(date):
    if date == "today"      : date = (datetime.now() - timedelta(days =   0)).strftime("%Y-%m-%d")
    if date == "yesterday"  : date = (datetime.now() - timedelta(days =   1)).strftime("%Y-%m-%d")
    if date == "week"       : date = (datetime.now() - timedelta(days =   7)).strftime("%Y-%m-%d")
    if date == "yesterweek" : date = (datetime.now() - timedelta(days =  14)).strftime("%Y-%m-%d")
    if date == "month"      : date = (datetime.now() - timedelta(days =  30)).strftime("%Y-%m-%d")
    if date == "yestermonth": date = (datetime.now() - timedelta(days =  61)).strftime("%Y-%m-%d")
    if date == "year"       : date = (datetime.now() - timedelta(days = 365)).strftime("%Y-%m-%d")
    if date == "yesteryear" : date = (datetime.now() - timedelta(days = 731)).strftime("%Y-%m-%d")
    #print(date, int(parser.parse(date).timestamp()))
    return int(parser.parse(date).timestamp())


#parse_date("Mar 26, 2025")
#parse_date("2021")
#parse_date("1/1/2021")
#parse_date("3-26-25")
#parse_date("today")
#parse_date("yesterday")




def post_filter_generator(tags_in, tags_out, before, after, user_in, user_out):
    queries = []

    if tags_in != None:
        queries.append(Query().tags.test(lambda tags: set(tags).issuperset(tags_in)))
        
    if tags_out != None:
        queries.append(Query().tags.test(lambda tags: not any(tag in tags for tag in tags_in)))
        
    if before   != None: queries.append(Query().time < before)
    if after    != None: queries.append(Query().time >= after)
    if user_in  != None: queries.append(Query().user == user_in)
    if user_out != None: queries.append(Query().user != user_out)

    query = None
    for q in queries:
        if query is None:
            query = q
        else:
            query &= q

    if query is None:
        query = Query().user.test(lambda _: True)

    return query





def post_sorter(posts, sort_type):
    if sort_type == "date" or sort_type == "newest":
        sorted_posts = sorted(posts, key=lambda post: post['time'], reverse=True)
    elif sort_type == "oldest":
        sorted_posts = sorted(posts, key=lambda post: post['time'], reverse=False)
    else:
        sorted_posts = sorted(posts, key=lambda post: post['time'], reverse=True)

    return sorted_posts



import traceback

def get_posts(db, query):
    try: return _get_posts(db, query)
    except Exception as e: 
        #print(str(e))
        traceback.print_exc()
        return []



def adjust_posts(db, posts):
    #file_table = db.table('files')
    for post in posts:
        files = dbfiles.get_files_from_hashes(db, post['files'])
        post.update({'tags': set(post['tags'])})
        post.update({'files': files})
        post.update({'html': markdown.markdown(post['text'],
            extensions=['markdown.extensions.nl2br'])})

    return posts




def _get_posts(db, query):

    tokens = query.split(' ')

    if len(tokens) == 1 and tokens[0] == '':
        tokens = []

    #print(tokens)
    old_tokens = tokens
    tokens = []
    for token in old_tokens:
        if token != '':
            tokens.append(token)

    tags_in  = None
    tags_out = None
    before   = None
    after    = None
    user_in  = None
    user_out = None
    sort     = None
    start    = None
    end      = None

    #print("===================================")
    #print("===================================")
    #print(tokens)

    for token in tokens:
        #try:
        invert = False
        if token[0] == '-':
            token = token[1:]
            invert = True
        
        if ':' in token:
            mode, token = token.split(':')
        else:
            mode = 'tag'

        if not invert:
            if mode == 'tag':
                if tags_in is None: tags_in = []
                tags_in.append(token)
                
            elif mode == 'before': before  = parse_date(token)
            elif mode == 'after':  after   = parse_date(token)
            elif mode == 'user':   user_in = token
            elif mode == '_start': start   = token
            elif mode == '_end':   end     = token

        else:
            if mode == 'tag':
                if tags_out is None: tags_out = []
                tags_out.append(token)

            #elif mode == 'before': after    = parse_date(token)
            #elif mode == 'after' : before   = parse_date(token)
            elif mode == 'user'  : user_out = token

        if mode == 'sort':
            sort = token
                
        #except Exception as e:
        #    traceback.print_exc()

    post_table = db.table('posts')
    #file_table = db.table('files')
    
    posts = post_table.search(post_filter_generator(tags_in, tags_out, before, after, user_in, user_out))

    #for post in posts:
    #    files = dbfiles.get_files_from_hashes(db, post['files'])
    #    post.update({'files': files})

    #for post in post_sorter(posts, sort):
    #    print(post)

    adjust_posts(db, posts)

    sorted_posts = post_sorter(posts, sort)

    if end is not None:
        sorted_posts = sorted_posts[:int(end)]

    if start is not None:
        sorted_posts = sorted_posts[int(start):]
    
    return sorted_posts




import random
import string
import time


def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def gen_random_posts(db, count):
    all_tags = [generate_random_string(random.randint(3, 8)) for _ in range(20)]
    for i in range(count):
        user = {'username':generate_random_string(10)}
        tag_count = random.randint(1, 10)
        tags = set(random.sample(all_tags, tag_count))
        time_over = time.time() - random.randint(0, 30*24*60*60)
        dbposts.add_post(db, user, generate_random_string(50), [], tags, time_over)



from db import helpers
db = helpers.load_db()

#gen_random_posts(db, 100)

#get_posts(db, "")
#print("\n\n\n\n")
#get_posts(db, "after:today _end:5")
#get_posts(db, "after:yesterday _end:5")
#get_posts(db, "after:yesterday 3uvpR _end:5")
#get_posts(db, "sort:newest 3uvpR LdQU5 4BH")
#get_posts(db, "sort:oldest 3uvpR LdQU5 4BH")
#print()




# filters
# -------------
# before:10-10-1
#       :today
#       :month
#       :yesterday
# after:10-10-1
#      :today (beginning of)
#      :month (beginning of 30 days ago)
#      :yesterday (beginning of yesterday)
# tag: (implicit)
# user:
# _start:0
# _end:10
# 
# 
# sort:newest,
# sort:oldest,
# sort:rating
