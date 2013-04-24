import tornado.ioloop
import tornado.web
import os
from tornado.options import parse_command_line


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello world!")


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/favicon.ico", tornado.web.StaticFileHandler, dict(path=settings["static_path"])),
], **settings)


if __name__ == "__main__":
    parse_command_line()
    application.listen(18888)
    tornado.ioloop.IOLoop.instance().start()
