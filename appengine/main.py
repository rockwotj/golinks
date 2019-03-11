from google.appengine.ext import ndb

import urllib
import webapp2
import re
import json

def valid_url(url):
    """See https://stackoverflow.com/a/7160778"""
    valid_url_regex = re.compile(
        r'^(?:http)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(valid_url_regex, url) is not None

class Golink(ndb.Model):
    path = ndb.StringProperty()
    redirect = ndb.StringProperty()

    @classmethod
    def get(cls, link):
        return cls.query(cls.path == link).get()

    @classmethod
    def find(cls, link):
        return cls.query(cls.path >= link, cls.path < (link + "\0"))

    @classmethod
    def all(cls):
        return cls.query().order(cls.path)

class VisitPage(webapp2.RequestHandler):
    def get(self):
        path = self.request.get('link')
        if path is None or path == '':
            return webapp2.redirect('/list')
        links = [l for l in Golink.find(path)]
        if len(links) == 0:
            return self.redirect('/edit?' + urllib.urlencode({'link':path}))
        elif len(links) == 1:
            return self.redirect(str(links[0].redirect))
        self.response.status = 400
        self.response.write("Too many links for {}: {}".format(path, links))

class EditPage(webapp2.RequestHandler):
    def get(self):
        path = self.request.get('link')
        redirect = ''
        if path is None or path == '':
            path = ''
        else:
            link = Golink.get(path)
            if link is not None:
                redirect = link.redirect
        self.response.write("""
        <form action="/edit" method="post">
          Path:<br>
          <input type="text" name="from" value="{}">
          <br>
          Redirect:<br>
          <input type="text" name="to" value="{}">
          <br><br>
          <input type="submit" value="Submit">
        </form>
        """.format(path, redirect))


    def post(self):
        path = self.request.get('from')
        redirect = self.request.get('to')
        if redirect is None or redirect == '':
            return self.delete_link(path)
        elif not valid_url(redirect):
            self.abort(400)
        elif path is None or path == '':
            self.abort(400)
        link = Golink.get(path)
        if link is None:
            link = Golink(path = path, redirect = redirect)
        else:
            link.redirect = redirect
        link.put()
        self.response.write("OK")

    def delete_link(self, path):
        if path is None or path == '':
            self.abort(400)
        link = Golink.get(path)
        if link is None:
            self.abort(404)
        link.key.delete()
        self.response.write("OK")

class ListPage(webapp2.RequestHandler):
    def get(self):
        links = Golink.all()
        self.response.write('<ul>')
        for l in links:
            visit = "/edit?" + urllib.urlencode({'link':l.path})
            self.response.write('<li><a href="{}">{}</a> is redirected to {}</li>'.format(visit, l.path, l.redirect))
        self.response.write('</ul>')

app = webapp2.WSGIApplication([
    ('/visit', VisitPage),
    ('/edit', EditPage),
    ('/list', ListPage),
])

