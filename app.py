#-*-coding: utf-8-*-
from math import exp
import os
import json
from tornado import escape
import tornado.ioloop
from tornado import web
from tornado import gen
from tornado import httpclient
from tornado.web import asynchronous
from tornado.options import parse_command_line, options, define
import config
from functools import wraps
import datetime


github_data = {}
define("port", default=8000)
strong = lambda x: 2 ** 11 / (1 + pow(exp(1), -(x - 2 ** 8) / 2 ** 6))


def loop_call(delta=60 * 1000):
    def wrap_loop(func):
        @wraps(func)
        def wrap_func(*args, **kwargs):
            func(*args, **kwargs)
            tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(milliseconds=delta), wrap_func)
        return wrap_func
    return wrap_loop


@loop_call()
@gen.coroutine
def get_raw_data():
    """
    every 5 seconds will fetch github.com
    """
    global github_data
    httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    client = httpclient.AsyncHTTPClient()
    request = TornadoDataRequest("https://api.github.com/gists/4524946")
    resp = yield client.fetch(request)
    resp = escape.json_decode(resp.body)
    users_url = resp["files"]["github-users-stats.json"]["raw_url"]
    languages_url = resp["files"]["github-languages-stats.json"]["raw_url"]
    users, languages = yield [client.fetch(TornadoDataRequest(users_url)),
                              client.fetch(TornadoDataRequest(languages_url))]
    users_stats = escape.json_decode(users.body)
    languages_stats = escape.json_decode(languages.body)
    users_stats = sorted(users_stats, key=lambda d: d["contributions"] + strong(d["followers"]), reverse=True)
    users_stats = filter(lambda u: 'china' in u['location'].lower(), users_stats)
    github_data["users_stats"] = users_stats
    github_data["languages_stats"] = languages_stats


class TornadoDataRequest(httpclient.HTTPRequest):
    def __init__(self, url, **kwargs):
        super(TornadoDataRequest, self).__init__(url, **kwargs)
        self.method = "GET"
        self.auth_username = config.username
        self.auth_password = config.password
        self.user_agent = "Tornado-data"


class MainHandler(web.RequestHandler):
    @asynchronous
    def get(self):
        self.render("index.html")


class HelloHandler(web.RequestHandler):
    @asynchronous
    def get(self):
        self.write("Hello world!")


class LoveHandler(web.RequestHandler):
    @asynchronous
    def get(self):
        self.write("Love world!")


class GithubPageHandler(web.RequestHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        client = httpclient.AsyncHTTPClient()
        request = TornadoDataRequest("https://github.com/cloudaice")
        resp = yield client.fetch(request)
        self.write(resp.body)
        self.finish()


class GithubHandler(web.RequestHandler):
    @asynchronous
    @gen.coroutine
    def post(self):
        global github_data
        if 'users_stats' not in github_data:
            users_stats = []
        else:
            users_stats = github_data["users_stats"]
        #languages_stats = github_data["languages_stats"]
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.write(json.dumps(users_stats, indent=4, separators=(',', ': ')))
        self.finish()


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'template'),
    "debug": True
}

get_raw_data()

app = web.Application([
    (r"/", MainHandler),
    (r"/love", LoveHandler),
    (r"/github", GithubHandler),
    (r"/githubpage", GithubPageHandler),
    (r"/favicon.ico", web.StaticFileHandler, dict(path=settings["static_path"])),
], **settings)


if __name__ == "__main__":
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
