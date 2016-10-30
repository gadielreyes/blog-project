import time

from blog import BlogHandler
from models.post import Post

class DeletePost(BlogHandler):
    # A class that represent a RequestHandler for deleteing a post

    def get(self, post_id):
        post = Post.get_by_id(post_id)

        if self.user:
            if post.is_owner(self.user):
                post.delete()
                time.sleep(1)
                self.redirect('/blog')
            else:
                error = "You can only delete your posts."
                self.render("editpost.html",
                            post = post,
                            subject = post.subject,
                            content = post.content,
                            error = error,
                            pagetitle = "Edit Post")
        else:
            self.render("login-form.html",
                        pagetitle = "Login",
                        error = "You have to be logged in to delete posts.")
