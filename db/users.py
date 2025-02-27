import tinydb
import bcrypt # Used to make hashed passwords
import re # Used to create strong passwords

def is_strong_password(password):
    #Check if password is strong: at least 8 chars, includes letters, numbers, and symbols
    if len(password) < 8:
        return False
    if not re.search(r"[A-Za-z]", password):  # Must have letters
        return False
    if not re.search(r"\d", password):  # Must have numbers
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # Must have symbols
        return False
    return True

def new_user(db, username, password):
    users = db.table('users')
    User = tinydb.Query()
    if users.get(User.username == username):
        return "Username already exists!" # Prevents Duplicate usernames
    
    # Enforce strong passwords
    if not is_strong_password(password):
        return "Password must be at least 8 characters long and contain a mix of letters, numbers, and symbols.", "danger"

    # Creates a hashed password to store in the database
    hashed_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user_record = {
            'username': username,
            'password': password,
            'friends': []
            }
    return "User {} created successfully!".format(username), "success"

def get_user(db, username, password):
    users = db.table('users')
    User = tinydb.Query()
    # Uses hashed password to access users from database
    user = users.get(User.username == username)
    if user:
        if bcrypt.checkpw(password.encode(), user['password'].encode()):
            return user
        else:
            return None # Return None if password is incorrect
    return None # return None if User does not exist

def get_user_by_name(db, username):
    users = db.table('users')
    User = tinydb.Query()
    return users.get(User.username == username)

def delete_user(db, username, password):
    users = db.table('users')
    User = tinydb.Query()
    return users.remove((User.username == username) &
            (User.password == password))

def add_user_friend(db, user, friend):
    users = db.table('users')
    User = tinydb.Query()
    if friend not in user['friends']:
        if users.get(User.username == friend):
            user['friends'].append(friend)
            users.upsert(user, (User.username == user['username']) &
                    (User.password == user['password']))
            return 'Friend {} added successfully!'.format(friend), 'success'
        return 'User {} does not exist.'.format(friend), 'danger'
    return 'You are already friends with {}.'.format(friend), 'warning'

def remove_user_friend(db, user, friend):
    users = db.table('users')
    User = tinydb.Query()
    if friend in user['friends']:
        user['friends'].remove(friend)
        users.upsert(user, (User.username == user['username']) &
                (User.password == user['password']))
        return 'Friend {} successfully unfriended!'.format(friend), 'success'
    return 'You are not friends with {}.'.format(friend), 'warning'

def get_user_friends(db, user):
    users = db.table('users')
    User = tinydb.Query()
    friends = []
    for friend in user['friends']:
        friends.append(users.get(User.username == friend))
    return friends
