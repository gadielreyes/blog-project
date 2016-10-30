from google.appengine.ext import db
from post import Post
from post import User

class Like(db.Model):
    # A class representing a Like model in app engine datastore

    post = db.ReferenceProperty(Post, collection_name='likes')
    user = db.ReferenceProperty(User, collection_name='likes')
    liked_on = db.DateTimeProperty(auto_now_add = True)
