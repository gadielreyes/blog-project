import hmac
import webapp2

from common.tools import Tools
from models.user import User

secret = 'S0m3S3cr3tM3ss4g31h0p3n0B0dyC4nSp0t'

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
        return Tools.render_str(template, **params)

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