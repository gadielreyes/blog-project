import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), '../templates')
static_dir = os.path.join(os.path.dirname(__file__), '../static')
jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader([template_dir, static_dir]),
    autoescape = True)

class Tools():
    # A class with common methods to be used in the blog

    @classmethod
    def blog_key(cls, name = 'default'):
        return db.Key.from_path('blogs', name)

    @classmethod
    def render_str(cls, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
