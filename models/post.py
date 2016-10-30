from google.appengine.ext import db
from common.tools import Tools
from user import User

class Post(db.Model):
    # A class representing a Post model in app engine datastore

    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    user = db.ReferenceProperty(User, collection_name='posts')
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    @classmethod
    def get_by_id(cls, post_id):
        """Get a post for a given id

        Args:
            post_id (int): id of the post

        Returns:
            Object: The return value. the post founded, None otherwise.
        """

        key = db.Key.from_path('Post', int(post_id), parent=Tools.blog_key())
        post = db.get(key)
        if post:
            return post

    def is_owner(self, user):
        """Verify if the given user is the owner of te post

        Args:
            user (object): user object to verify

        Returns:
            bool: The return value. True for being the owner of the post,
            None otherwise.
        """
        if self.user.key().id() == user.key().id():
            return True


    def get_likes(self):
        likes = self.likes
        if likes:
            return likes.count(100000000)
        else:
            return 0
