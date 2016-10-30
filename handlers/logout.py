from blog import BlogHandler

class Logout(BlogHandler):
    # A class that represent a RequestHandler for login out a user

    def get(self):
        self.logout()
        self.redirect('/blog')
