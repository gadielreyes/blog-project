import webapp2

from google.appengine.ext import db
from common.tools import Tools
from models.post import Post
from models.user import User
from models.like import Like
from models.comment import Comment

from handlers.blog import BlogHandler
from handlers.blogfront import BlogFront
from handlers.postpage import PostPage
from handlers.newpost import NewPost
from handlers.editpost import EditPost
from handlers.deletepost import DeletePost
from handlers.editcomment import EditComment
from handlers.deletecomment import DeleteComment
from handlers.likepost import LikePost
from handlers.signup import Signup
from handlers.login import Login
from handlers.logout import Logout
from handlers.welcome import Welcome
from handlers.mainpage import MainPage

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/editpost/([0-9]+)', EditPost),
                               ('/blog/deletepost/([0-9]+)', DeletePost),
                               ('/blog/likepost/([0-9]+)', LikePost),
                               ('/blog/editcomment/([0-9]+)', EditComment),
                               ('/blog/deletecomment/([0-9]+)', DeleteComment),
                               ('/welcome', Welcome),
                               ('/signup', Signup),
                               ('/login', Login),
                               ('/logout', Logout),
                               ], debug=True)
