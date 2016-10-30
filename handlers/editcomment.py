from blog import BlogHandler
from models.comment import Comment

class EditComment(BlogHandler):
    # A class that represent a RequestHandler for the edit comment page

    def get(self, comment_id):
        comment = Comment.get_by_id(comment_id)

        if not comment:
            self.error(404)
            return

        content = self.request.get('content')
        error = self.request.get('error')

        if self.user:
            if comment.user.key().id() == self.user.key().id():
                if error:
                    self.render('editcomment.html',
                                comment = comment,
                                content = content,
                                error = error,
                                pagetitle = "Edit Comment")
                else:
                    self.render('editcomment.html',
                                comment = comment,
                                content = comment.content,
                                pagetitle = "Edit Comment")
            else:
                error = "You can only edit your comments."
                self.render('editcomment.html',
                            comment = comment,
                            content = comment.content,
                            error = error,
                            pagetitle = "Edit Comment")
        else:
            self.render("login-form.html",
                        pagetitle = "Login",
                        error = "You have to be logged in to edit comments.")

    def post(self, comment_id):
        if not self.user:
            self.render("login-form.html",
                        pagetitle = "Login",
                        error = "You have to be logged in to edit comments.")

        comment = Comment.get_by_id(comment_id)
        content = self.request.get('content')

        if not comment:
            self.error(404)
            return

        if comment.user.key().id() != self.user.key().id():
            self.render("login-form.html",
                        pagetitle = "Login",
                        error = "You have to be logged in to edit comments.")

        if content:
            comment.content = content
            comment.put()
            self.redirect('/blog/%s' % str(comment.post.key().id()))
        else:
            error = "content must be filled, please!"
            self.render('editcomment.html',
                        comment = comment,
                        content = content,
                        error = error)
