from blog import BlogHandler
from models.comment import Comment

class DeleteComment(BlogHandler):
    # A class that represent a RequestHandler for deleting a comment

    def get(self, comment_id):
        comment = Comment.get_by_id(comment_id)

        if self.user:
            if comment.user.key().id() == self.user.key().id():
                comment.delete()
                self.redirect('/blog/%s' % comment.post.key().id())
            else:
                error = "You can only delete your comments."
                self.render("editcomment.html",
                            comment = comment,
                            content = comment.content,
                            error = error)
        else:
            self.render("login-form.html",
                        pagetitle = "Login",
                        error = "You have to be logged in to delete comments.")
