import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import pymongo

from tornado.options import define, options
define("port", default=8000, type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
                #(r"/", PageHandler)),
                (r"/page/(\d+)$", PageHandler),
                (r"/blog/(\d{4}-\d{2}-\d{2})$", ArticleHandler),
                (r"/about", AboutHandler)
                ]
        settings = dict(
                template_path=os.path.join(os.path.dirname(__file__), "templates"),
                static_path=os.path.join(os.path.dirname(__file__), "static"),
                )
        connection = pymongo.Connection("localhost", 27017)
        self.db = connection.blog
        tornado.web.Application.__init__(self, handlers, debug=True, **settings)



class PageHandler(tornado.web.RequestHandler):

    def get(self, page):
        articles = self.application.db.articles
        page = int(page)
        page_count = articles.count() //10 +1
        if page > page_count:
            self.set_status(404)
            self.write("404")
        else:
            display = articles.find()[(page-1) * 10 : (page-1) * 10 + 9]
            self.render('page.html', display=display, page_count=page_count)


class AboutHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('about.html')


class ArticleHandler(tornado.web.RequestHandler):

    def get(self, date):

        articles = self.application.db.articles
        blog = articles.find_one({"date": date})
        if blog == None:
            self.set_status(404)
        else:
            self.render('blog.html', blog=blog)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
