from blog import BlogHandler

class MainPage(BlogHandler):
    """A class that represent a RequestHandler
    of the main page of the project.
    """

    def get(self):
      self.write('Hello, Udacity!')
