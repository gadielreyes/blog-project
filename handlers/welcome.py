from blog import BlogHandler

class Welcome(BlogHandler):
    # A class that represent a RequestHandler for welcome page

    def get(self):
        if self.user:
            self.render('welcome.html', username = self.user.name, pagetitle = "Welcome")
        else:
            self.redirect('/signup')
