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
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader([template_dir, static_dir]),
                               autoescape = True)

secret = 'S0m3S3cr3tM3ss4g31h0p3n0B0dyC4nSp0t'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class BlogHandler(webapp2.RequestHandler):
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

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

class MainPage(BlogHandler):
  def get(self):
      self.write('Hello, Udacity!')

##### user stuff
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

def get_post(post_id):
    key = db.Key.from_path('Post', int(post_id), parent=blog_key())
    post = db.get(key)
    if post:
        return post

def get_comment(comment_id):
    key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
    comment = db.get(key)
    if comment:
        return comment

class User(db.Model):
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
        post = get_post(post_id)
        if post.owner_id == self.key().id():
            return True

    def is_comment_owner(self, comment_id):
        comment = get_comment(comment_id)
        if comment.owner_id == self.key().id():
            return True


##### blog stuff
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    owner_id = db.IntegerProperty()
    likes = db.IntegerProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class Comment(db.Model):
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

class BlogFront(BlogHandler):
    def get(self):
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts = posts)

class PostPage(BlogHandler):
    def get(self, post_id):
        post = get_post(post_id)
        comments = greetings = db.GqlQuery("SELECT * FROM Comment WHERE post_id = %s ORDER BY created DESC" % post_id)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post, comments = comments)

    def post(self, post_id):
        content = self.request.get('content')

        post = get_post(post_id)

        if content and post_id:
            c = Comment(parent = blog_key(), post_id = int(post_id), owner_id = self.user.key().id(), content = content)
            c.put()
            self.redirect('/blog/%s' % str(post_id))
        else:
            self.render("permalink.html", post = post)

class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')
        user_id = self.user.key().id()

        if subject and content and user_id:
            p = Post(parent = blog_key(), subject = subject, content = content, owner_id = user_id, likes = 0)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

class EditPost(BlogHandler):
    def get(self, post_id):
        post = get_post(post_id)

        subject = self.request.get('subject')
        content = self.request.get('content')
        error = self.request.get('error')

        if self.user:
            if self.user.is_post_owner(post_id):
                if error:
                    self.render("editpost.html", subject=subject, content=content, id=post_id, error=error)
                else:
                     self.render("editpost.html", subject=post.subject, content=post.content, id=post_id)
            else:
                error = "You can only edit your posts."
                self.render("editpost.html", subject=post.subject, content=post.content, id=post_id, error=error)
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
            self.render("editpost.html", subject=subject, content=content, id=post_id, error=error)


class DeletePost(BlogHandler):
    def get(self, post_id):
        post = get_post(post_id)

        if self.user:
            if self.user.is_post_owner(post_id):
                post.delete()
                self.redirect('/blog')
            else:
                error = "You can only delete your posts."
                self.render("editpost.html", subject=post.subject, content=post.content, id=post_id, error=error)
        else:
            self.redirect('/login')

class EditComment(BlogHandler):
    def get(self, comment_id):
        comment = get_comment(comment_id)

        content = self.request.get('content')
        error = self.request.get('error')

        if self.user:
            if self.user.is_comment_owner(comment_id):
                if error:
                    self.render('editcomment.html', content=content, id=comment_id, error=error)
                else:
                    self.render('editcomment.html', content=comment.content, id=comment_id)
            else:
                error = "You can only edit your comments."
                self.render('editcomment.html', content=comment.content, id=comment_id, error=error)
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
            self.render('editcomment.html', content=content, id=comment_id, error=error)

class DeleteComment(BlogHandler):
    def get(self, comment_id):
        comment = get_comment(comment_id)

        if self.user:
            if self.user.is_comment_owner(comment_id):
                comment.delete()
                self.redirect('/blog/%s' % comment.post_id)
            else:
                error = "You can only delete your comments."
                self.render("editcomment.html", content=comment.content, id=comment_id, error=error)
        else:
            self.redirect('/login')

class LikePost(BlogHandler):
    def get(self, post_id):
        post = get_post(post_id)
        if self.user:
            if self.user.is_post_owner(post_id):
                error = "You can not like your own post."
                self.render("likepost.html", error=error)
            else:
                likes = post.likes
                likes += 1
                post.likes = likes
                post.put()
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
    def get(self):
        self.render("signup-form.html")

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

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/welcome')

class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

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
    def get(self):
        self.logout()
        self.redirect('/blog')

class Welcome(BlogHandler):
    def get(self):
        if self.user:
            self.render('welcome.html', username = self.user.name)
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
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ], debug=True)
