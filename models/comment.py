from google.appengine.ext import db
from common.tools import Tools
from user import User
from post import Post

class Comment(db.Model):
    # A class representing a Comment model in app engine datastore

    post = db.ReferenceProperty(Post, collection_name='comments')
    user = db.ReferenceProperty(User, collection_name='comments')
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    @classmethod
    def get_by_id(cls, comment_id):
        """Get a comment for a given id

        Args:
            comment_id (int): id of the comment

        Returns:
            Object: The return value. the comment founded, None otherwise.
        """

        key = db.Key.from_path('Comment', int(comment_id), parent=Tools.blog_key())
        comment = db.get(key)
        if comment:
            return comment

    def is_owner(self, user):
        """Verify if the give user is the owner of the comment

        Args:
            user (object): instance of an user objecrt

        Returns:
            bool: The return value. True for being the owner of the comment,
            None otherwise.
        """

        if self.user.key().id() == user.key().id():
            return True
