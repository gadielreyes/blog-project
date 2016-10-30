from blog import BlogHandler
from models.post import Post

class EditPost(BlogHandler):
    # A class that represent a RequestHandler for a edit post page

    def get(self, post_id):
        post = Post.get_by_id(post_id)

        if not post:
            self.error(404)
            return

        subject = self.request.get('subject')
        content = self.request.get('content')
        error = self.request.get('error')

        if self.user:
            if post.user.key().id() == self.user.key().id():
                if error:
                    self.render("editpost.html",
                                post = post,
                                subject = subject,
                                content = content,
                                error = error,
                                pagetitle = "Edit Post")
                else:
                     self.render("editpost.html",
                                post = post,
                                subject = post.subject,
                                content = post.content,
                                pagetitle = "Edit Post")
            else:
                error = "You can only edit your posts."
                self.render("editpost.html",
                            post = post,
                            subject = post.subject,
                            content = post.content,
                            error = error,
                            pagetitle = "Edit Post")
        else:
            self.render("login-form.html",
                        pagetitle = "Login",
                        error = "You have to be logged in to edit posts.")

    def post(self, post_id):
        if not self.user:
            self.render("login-form.html",
                        pagetitle = "Login",
                        error = "You have to be logged in to create new posts.")

        post = Post.get_by_id(post_id)
        subject = self.request.get('subject')
        content = self.request.get('content')

        if not post:
            self.error(404)
            return

        if post.user.key().id() != self.user.key().id():
            error = "You can only edit your posts."
            self.render("editpost.html",
                        post = post,
                        subject = post.subject,
                        content = post.content,
                        error = error,
                        pagetitle = "Edit Post")

        if subject and content:
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            error = "subject and content must be filled, please!"
            self.render("editpost.html",
                        post = post,
                        subject = subject,
                        content = content,
                        error = error)