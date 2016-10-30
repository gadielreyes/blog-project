import random
import hashlib

from string import letters

from google.appengine.ext import db

def make_salt(length = 5):
    """Make a random string with a given length

    Args:
        length (int): length of the string

    Returns:
        string: a string of concatenating the random letters
    """

    return ''.join(random.choice(letters) for x in xrange(length))

class User(db.Model):
    # A class that represent a User model in app engine datastore

    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = cls.users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = cls.make_pw_hash(name, pw)
        return User(parent = cls.users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and cls.valid_pw(name, pw, u.pw_hash):
            return u

    @classmethod
    def users_key(cls, group = 'default'):
        return db.Key.from_path('users', group)

    @classmethod
    def valid_pw(cls, name, password, h):
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
        return h == cls.make_pw_hash(name, password, salt)

    @classmethod
    def make_pw_hash(cls, name, pw, salt = None):
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
