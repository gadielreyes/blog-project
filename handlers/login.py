from blog import BlogHandler
from models.user import User

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
