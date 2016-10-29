import os
import re
import random
import hashlib
import hmac
import time
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
static_dir = os.path.join(os.path.dirname(__file__), 'static')
jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader([template_dir, static_dir]),
    autoescape = True)

secret = 'S0m3S3cr3tM3ss4g31h0p3n0B0dyC4nSp0t'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    """Make a given value more secure

    Args:
        val (str): the value to make secure

    Returns:
        string: value|hash of the value
    """

    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    """Check if the secure val has not been changed

    Args:
        secure_val (str): a secure value

    Returns:
        string: The return value. the value if it's secure.
        None otherwise.
    """

    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class BlogHandler(webapp2.RequestHandler):
    """A that represent a RequestHandler class with common functions
    to be used in all pages
    """

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

class MainPage(BlogHandler):
    """A class that represent a RequestHandler
    of the main page of the project.
    """

    def get(self):
      self.write('Hello, Udacity!')

##### user stuff
def make_salt(length = 5):
    """Make a random string with a given length

    Args:
        length (int): length of the string

    Returns:
        string: a string of concatenating the random letters
    """

    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    """Make a password secure

    Args:
        name (str): the name of the user
        pw (str): the password of the user
        salt (str): the random letters of the hash if created

    Returns:
        string: hash,salt is the format returned
    """

    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    """Check is a password is valid

    Args:
        name (str): name of the user
        password (str): password of the user
        h (str): password hashed with the salt

    Results:
        bool: The return value. True if valid password.
        False otherwise.
    """

    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    # A class that represent a User model in app engine datastore

    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

    def is_post_owner(self, post_id):
        """Verify if the current user is the owner of a given post id

        Args:
            post_id (int): id of the post

        Returns:
            bool: The return value. True for being the owner of the post,
            None otherwise.
        """
        post = get_post(post_id)
        if post.owner_id == self.key().id():
            return True

    def is_comment_owner(self, comment_id):
        """Verify if the current user is the owner of a given comment id

        Args:
            comment_id (int): id of the comment

        Returns:
            bool: The return value. True for being the owner of the comment,
            None otherwise.
        """
        comment = get_comment(comment_id)
        if comment.owner_id == self.key().id():
            return True

##### blog stuff
def get_post(post_id):
    """Get a post for a given id

    Args:
        post_id (int): id of the post

    Returns:
        Object: The return value. the post founded, None otherwise.
    """

    key = db.Key.from_path('Post', int(post_id), parent=blog_key())
    post = db.get(key)
    if post:
        return post

def get_comment(comment_id):
    """Get a comment for a given id

    Args:
        comment_id (int): id of the comment

    Returns:
        Object: The return value. the comment founded, None otherwise.
    """

    key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
    comment = db.get(key)
    if comment:
        return comment

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    # A class representing a Post model in app engine datastore

    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    owner_id = db.IntegerProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def get_likes(self):
        likes = db.GqlQuery("SELECT * FROM Like WHERE post_id = %s" % self.key().id())
        if likes:
            return likes.count(100000000)
        else:
            return 0

class Comment(db.Model):
    # A class representing a Comment model in app engine datastore

    post_id = db.IntegerProperty(required = True)
    owner_id = db.IntegerProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def get_owner_name(self, comment_id):
        comment = get_comment(comment_id)
        u = User.by_id(comment.owner_id)
        if u:
            return u.name

class Like(db.Model):
    # A class representing a Like model in app engine datastore

    post_id = db.IntegerProperty(required = True)
    user_id = db.IntegerProperty(required = True)
    liked_on = db.DateTimeProperty(auto_now_add = True)

class BlogFront(BlogHandler):
    # A class that represent a RequestHandler for front page of the blog

    def get(self):
        posts = Post.all().order('-created')
        self.render('front.html', posts = posts, pagetitle="Blog")

class PostPage(BlogHandler):
    # A class that represent a RequestHandler for a single post

    def get(self, post_id):
        post = get_post(post_id)
        comments = db.GqlQuery("SELECT * FROM Comment "
                                            "WHERE post_id = %s "
                                            "ORDER BY created DESC" % post_id)

        if not post:
            self.error(404)
            return

        self.render("permalink.html",
                    post = post,
                    comments = comments,
                    pagetitle = "Post Page")

    def post(self, post_id):
        content = self.request.get('content')

        post = get_post(post_id)

        if content and post_id:
            c = Comment(parent = blog_key(),
                        post_id = int(post_id),
                        owner_id = self.user.key().id(),
                        content = content)
            c.put()
            self.redirect('/blog/%s' % str(post_id))
        else:
            self.render("permalink.html", post = post)

class NewPost(BlogHandler):
    # A class that represent a RequestHandler for a new post page

    def get(self):
        if self.user:
            self.render("newpost.html", pagetitle="New Post")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')
        user_id = self.user.key().id()

        if subject and content and user_id:
            p = Post(parent = blog_key(),
                    subject = subject,
                    content = content,
                    owner_id = user_id)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html",
                        subject = subject,
                        content = content,
                        error = error)

class EditPost(BlogHandler):
    # A class that represent a RequestHandler for a edit post page

    def get(self, post_id):
        post = get_post(post_id)

        subject = self.request.get('subject')
        content = self.request.get('content')
        error = self.request.get('error')

        if self.user:
            if self.user.is_post_owner(post_id):
                if error:
                    self.render("editpost.html",
                                subject = subject,
                                content = content,
                                id = post_id,
                                error = error,
                                pagetitle = "Edit Post")
                else:
                     self.render("editpost.html",
                                subject = post.subject,
                                content = post.content,
                                id = post_id,
                                pagetitle = "Edit Post")
            else:
                error = "You can only edit your posts."
                self.render("editpost.html",
                    subject = post.subject,
                    content = post.content,
                    id = post_id,
                    error = error,
                    pagetitle = "Edit Post")
        else:
            self.redirect('/login')

    def post(self, post_id):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post = get_post(post_id)
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            error = "subject and content must be filled, please!"
            self.render("editpost.html",
                        subject = subject,
                        content = content,
                        id = post_id,
                        error = error)

class DeletePost(BlogHandler):
    # A class that represent a RequestHandler for deleteing a post

    def get(self, post_id):
        post = get_post(post_id)

        if self.user:
            if self.user.is_post_owner(post_id):
                post.delete()
                self.redirect('/blog')
            else:
                error = "You can only delete your posts."
                self.render("editpost.html",
                            subject = post.subject,
                            content = post.content,
                            id = post_id,
                            error = error,
                            pagetitle = "Edit Post")
        else:
            self.redirect('/login')

class EditComment(BlogHandler):
    # A class that represent a RequestHandler for the edit comment page

    def get(self, comment_id):
        comment = get_comment(comment_id)

        content = self.request.get('content')
        error = self.request.get('error')

        if self.user:
            if self.user.is_comment_owner(comment_id):
                if error:
                    self.render('editcomment.html',
                                content = content,
                                id = comment_id,
                                error = error,
                                post_id = comment.post_id,
                                pagetitle = "Edit Comment")
                else:
                    self.render('editcomment.html',
                                content = comment.content,
                                id = comment_id,
                                post_id = comment.post_id,
                                pagetitle = "Edit Comment")
            else:
                error = "You can only edit your comments."
                self.render('editcomment.html',
                            content = comment.content,
                            id = comment_id,
                            error = error,
                            post_id = comment.post_id,
                            pagetitle = "Edit Comment")
        else:
            self.redirect('/login')

    def post(self, comment_id):
        if not self.user:
            self.redirect('/blog')

        content = self.request.get('content')

        if content:
            comment = get_comment(comment_id)
            comment.content = content
            comment.put()
            self.redirect('/blog/%s' % str(comment.post_id))
        else:
            error = "content must be filled, please!"
            self.render('editcomment.html',
                        content = content,
                        id = comment_id,
                        error = error)

class DeleteComment(BlogHandler):
    # A class that represent a RequestHandler for deleting a comment

    def get(self, comment_id):
        comment = get_comment(comment_id)

        if self.user:
            if self.user.is_comment_owner(comment_id):
                comment.delete()
                self.redirect('/blog/%s' % comment.post_id)
            else:
                error = "You can only delete your comments."
                self.render("editcomment.html",
                            content = comment.content,
                            id = comment_id,
                            error = error)
        else:
            self.redirect('/login')

class LikePost(BlogHandler):
    # A class that represent a RequestHandler to like a post

    def get(self, post_id):
        post = get_post(post_id)

        if self.user:
            user_id = self.user.key().id()

            if self.user.is_post_owner(post_id):
                error = "You can not like your own post."
                self.render("likepost.html", error=error)
            else:
                like = db.GqlQuery("SELECT * FROM Like WHERE"
                                    " post_id = %s AND user_id = %s"
                                    % (post_id, user_id)).get()
                if like:
                    self.redirect('/blog')
                else:
                    l = Like(parent=blog_key(), post_id = int(post_id), user_id = int(user_id))
                    l.put()
                    time.sleep(1)
                    self.redirect('/blog')
        else:
            self.redirect('/login')

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):
    # A class that represent a RequestHandler for signup page

    def get(self):
        self.render("signup-form.html", pagetitle="Signup")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self):
            #make sure the user doesn't already exist
            u = User.by_name(self.username)
            if u:
                msg = 'That user already exists.'
                self.render('signup-form.html', error_username = msg, pagetitle = "Signup")
            else:
                u = User.register(self.username, self.password, self.email)
                u.put()

                self.login(u)
                self.redirect('/welcome')

class Login(BlogHandler):
    # A class that represent a RequestHandler for login page

    def get(self):
        self.render('login-form.html', pagetitle="Login")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(BlogHandler):
    # A class that represent a RequestHandler for login out a user

    def get(self):
        self.logout()
        self.redirect('/blog')

class Welcome(BlogHandler):
    # A class that represent a RequestHandler for welcome page

    def get(self):
        if self.user:
            self.render('welcome.html', username = self.user.name, pagetitle = "Welcome")
        else:
            self.redirect('/signup')

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
