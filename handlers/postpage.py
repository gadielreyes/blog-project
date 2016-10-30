from blog import BlogHandler
from models.post import Post
from common.tools import Tools
from models.comment import Comment

class PostPage(BlogHandler):
    # A class that represent a RequestHandler for a single post

    def get(self, post_id):
        post = Post.get_by_id(post_id)

        if not post:
            self.error(404)
            return

        self.render("permalink.html",
                    post = post,
                    pagetitle = "Post Page")

    def post(self, post_id):
        post = Post.get_by_id(post_id)

        content = self.request.get('content')

        if content and post_id:
            c = Comment(parent = Tools.blog_key(),
                        post = post,
                        user = self.user,
                        content = content)
            c.put()
            self.redirect('/blog/%s' % str(post_id))
        else:
            self.render("permalink.html", post = post)
