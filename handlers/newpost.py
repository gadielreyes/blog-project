from blog import BlogHandler
from models.post import Post
from common.tools import Tools

class NewPost(BlogHandler):
    # A class that represent a RequestHandler for a new post page

    def get(self):
        if self.user:
            self.render("newpost.html", pagetitle="New Post")
        else:
            self.render("login-form.html",
                        pagetitle = "Login",
                        error = "You have to be logged in to create new posts.")

    def post(self):
        if not self.user:
            self.render("login-form.html",
                        pagetitle = "Login",
                        error = "You have to be logged in to create new posts.")

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = Tools.blog_key(),
                    subject = subject,
                    content = content,
                    user = self.user)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html",
                        subject = subject,
                        content = content,
                        error = error)