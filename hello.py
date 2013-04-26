#-*-coding: utf-8-*-
import os
import tornado.ioloop
import tornado.web
from tornado.options import parse_command_line


class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello world!")


class LoveHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Love world!")

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
}

app = tornado.web.Application([
    (r"/", HelloHandler),
    (r"/love", LoveHandler),
    (r"/favicon.ico", tornado.web.StaticFileHandler, dict(path=settings["static_path"])),
], **settings)


if __name__ == "__main__":
    parse_command_line()
    app.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
