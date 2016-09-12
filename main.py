#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2
import cgi

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class MainHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):#this allows us to create entity/table
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)#set created to be current time right now

class MainBlogPage(MainHandler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog "
                "ORDER BY created DESC LIMIT 5")

        self.render("viewpost.html", blogs = blogs)

class NewBlogPost(MainHandler):
    def get(self):
        self.render("newpost.html", title = "", body = "", error = "")


    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            b = Blog(title = title, body = body)
            key = b.put()
            _id = key.id()#gives id of just created blog post
            self.redirect("/blog/"+str(_id))
        else:
            error = "We need both a title and some content!"
            self.render("newpost.html", title = title, body = body, error = error)

class ViewPostHandler(MainHandler):
    def get(self, id):
        b = Blog.get_by_id(int(id))
        if b is not None:
            self.render("viewsinglepost.html", blog = b)
        else:
            error = "No post with that ID exists."
            self.response.write(error)

app = webapp2.WSGIApplication([
    webapp2.Route('/blog', handler =MainBlogPage),
    webapp2.Route('/newpost', handler =NewBlogPost),
    webapp2.Route('/blog/<id:\d+>', handler =ViewPostHandler)
], debug=True)
