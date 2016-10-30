import time

from blog import BlogHandler
from models.post import Post
from models.like import Like
from common.tools import Tools

class LikePost(BlogHandler):
    # A class that represent a RequestHandler to like a post

    def get(self, post_id):
        post = Post.get_by_id(post_id)

        if not post:
            self.error(404)
            return

        if self.user:
            if post.is_owner(self.user):
                error = "You can not like your own post."
                self.render("likepost.html", error=error)
            else:
                like = post.likes.filter('user =', self.user).get()

                if like:
                    self.redirect('/blog')
                else:
                    l = Like(parent=Tools.blog_key(), post = post, user = self.user)
                    l.put()
                    time.sleep(1)
                    self.redirect('/blog')
        else:
            self.render("login-form.html",
                        pagetitle = "Login",
                        error = "You have to be logged in to like posts.")
