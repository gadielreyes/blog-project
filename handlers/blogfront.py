from blog import BlogHandler
from models.post import Post

class BlogFront(BlogHandler):
    # A class that represent a RequestHandler for front page of the blog

    def get(self):
        posts = Post.all().order('-created')
        self.render('front.html', posts = posts, pagetitle="Blog")
