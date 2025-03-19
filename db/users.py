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



# added this function for readability and organization
def hash_password(password):
    if password is None:
        return None
    # generate salt
    salt = bcrypt.gensalt()
    # hash password
    return bcrypt.hashpw(password.encode(), salt).decode('utf-8')


# added this function for readability and organization
def verify_password(passhash, password):
    if passhash is None or password is None:
        return None
    return bcrypt.checkpw(password.encode('utf-8'), passhash.encode('utf-8'))




# wait, is all this hashing done on server side???
# That isn't exactly top notch security. It should be done client side!
# Whatever...
def new_user(db, username, password):
    users = db.table('users')
    User = tinydb.Query()
    if users.get(User.username == username):
        return None, "Username already taken!" # Prevents Duplicate usernames
    
    # Enforce strong passwords
    if not is_strong_password(password):
        return None, "Password must be at least 8 characters long and contain a mix of letters, numbers, and symbols!"

    # Creates a hashed password to store in the database
    # I replaced this with a function for readability
    #hashed_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    passhash = hash_password(password)
    
    user_entry = users.insert({
            'username': username,
            #'password': password,
            'passhash' : passhash,
            'friends': []
        })

    if user_entry is None:
        return None, "Error creating user {}".format(username)
    else:
        return user_entry, "User {} created successfully!".format(username)




# Seriously though, if only the hashing could've been done clientside.
# It would probably need to be done in javascript if we did.
def get_user(db, username, password):
    users = db.table('users')
    User = tinydb.Query()
    user = users.get((User.username == username) & (User.passhash.exists()))

    if user is None: return None
    
    # if user:
        # if bcrypt.checkpw(password.encode(), user['password'].encode()):
            # return user
        # else:
            # return None # Return None if password is incorrect
    # return None # return None if User does not exist
    return user if verify_password(user['passhash'], password) else None
    




def get_user_by_name(db, username):
    users = db.table('users')
    User = tinydb.Query()
    return users.get(User.username == username)




def delete_user(db, username, password):
    users = db.table('users')
    User = tinydb.Query()
    
    # Jeez. Why wasn't hashing implemented to this function too???
    #return users.remove((User.username == username) &
    #        (User.password == password))

    if verify_password(user['passhash'], password):
        return users.remove((User.username == username) & (User.passhash.exists()))
    else:
        return None




def add_user_friend(db, user, friend):
    users = db.table('users')
    User = tinydb.Query()
    if friend not in user['friends']:
        if users.get(User.username == friend):
            user['friends'].append(friend)
            users.upsert(user, (User.username == user['username']) &
                    #(User.password == user['password']))
                    (User.passhash.exists()))
            return 'Friend {} added successfully!'.format(friend), 'success'
        return 'User {} does not exist.'.format(friend), 'danger'
    return 'You are already friends with {}.'.format(friend), 'warning'




def remove_user_friend(db, user, friend):
    users = db.table('users')
    User = tinydb.Query()
    if friend in user['friends']:
        user['friends'].remove(friend)
        users.upsert(user, (User.username == user['username']) &
                (User.passhash.exists()))
        return 'Friend {} successfully unfriended!'.format(friend), 'success'
    return 'You are not friends with {}.'.format(friend), 'warning'




def get_user_friends(db, user):
    users = db.table('users')
    User = tinydb.Query()
    friends = []
    for friend in user['friends']:
        friends.append(users.get(User.username == friend))
    return friends
