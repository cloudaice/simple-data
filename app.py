#-*-coding: utf-8-*-
from math import exp
import os
import json
import datetime
import base64
import logging
from tornado import escape
from tornado import web
from tornado import gen
from tornado import httpclient
from tornado.httpclient import HTTPError
from tornado.httpserver import HTTPServer
from tornado.web import asynchronous
from tornado.options import parse_command_line, options, parse_config_file
from functools import wraps
import tornado.ioloop
import tornado.log
from addr import searchpage
#import config


github_data = {}
parse_config_file("config.py")

formula = lambda x: 2 ** 11 / (1 + pow(exp(1), -(x - 2 ** 8) / 2 ** 6))
logger = logging.getLogger("tornado-data")


def loop_call(delta=60 * 1000):
    def wrap_loop(func):
        @wraps(func)
        def wrap_func(*args, **kwargs):
            func(*args, **kwargs)
            tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(milliseconds=delta), wrap_func)
        return wrap_func
    return wrap_loop

    
@loop_call(5 * 1000)
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
    users_stats = sorted(users_stats, key=lambda d: d["contributions"] + formula(d["followers"]), reverse=True)
    users_stats = filter(lambda u: 'china' in u['location'].lower(), users_stats)
    github_data["users_stats"] = users_stats
    github_data["languages_stats"] = languages_stats


class BaseHandler(web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)

    def prepare(self):
        """do something before request comming"""
        #logger.debug(self.request)
        pass

    def on_finish(self):
        """do something after response to client like logging"""
        #logger.debug("finish request.")
        pass


class TornadoDataRequest(httpclient.HTTPRequest):
    def __init__(self, url, **kwargs):
        super(TornadoDataRequest, self).__init__(url, **kwargs)
        self.method = "GET"
        self.auth_username = options.username
        self.auth_password = options.password
        self.user_agent = "Tornado-data"


@gen.coroutine
def GetPage(url):
    client = httpclient.AsyncHTTPClient()
    request = TornadoDataRequest(url)
    response = yield client.fetch(request)
    raise gen.Return(response)


class MainHandler(web.RequestHandler):
    @asynchronous
    def get(self):
        self.render("index.html")


class AboutHandler(web.RequestHandler):
    @asynchronous
    def get(self):
        self.render("about.html")
        

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
        request = TornadoDataRequest(searchpage(2))
        resp = yield client.fetch(request)
        self.write(resp.body)
        self.finish()


class FetchUserHandler(web.RequestHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        client = httpclient.AsyncHTTPClient()
        request = TornadoDataRequest("https://github.com/users/cloudaice/contributions_calendar_data")
        resp = yield client.fetch(request)
        self.write(resp.body)
        self.finish()


class GithubCiHandler(web.RequestHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        global remote_users_file
        #client = httpclient.AsyncHTTPClient()
        #request = TornadoDataRequest("https://api.github.com/repos/cloudaice/simple-data/contents/test1.md")
        #future = client.fetch(request)
        try:
            resp = yield GetPage("https://api.github.com/repos/cloudaice/simple-data/contents/test1.md")
        except HTTPError, e:
            if e.code == "404":
                pass  # Create this file
            else:
                raise e
        resp = escape.json_decode(resp.body)
        sha = resp['sha']
        client = httpclient.AsyncHTTPClient()
        request = httpclient.HTTPRequest(
            "https://api.github.com/repos/cloudaice/simple-data/contents/test.md",
            method="PUT",
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            auth_username=options.username,
            auth_password=options.password,
            user_agent="Tornado-Data",
            body=json.dumps({
                "message": "update users.json",
                "content": base64.b64encode(
                    json.dumps(
                        {"name": "cloudaice", "type": "test"},
                        indent=4,
                        separators=(',', ': ')
                    )
                ),
                "committer": {"name": "cloudaice", "email": "cloudaice@163.com"},
                "sha": sha
            })
        )
        resp = yield client.fetch(request)
        if resp.error:
            print resp.error
        resp = escape.json_decode(resp.body)
        if isinstance(resp, dict):
            self.write(json.dumps(resp, indent=4, separators=(',', ': ')))
        else:
            self.write("Failed")
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


class Application(web.Application):
    def __init__(self, *arhs):
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), 'static'),
            'template_path': os.path.join(os.path.dirname(__file__), 'template'),
            "debug": True
        }

        handlers = [
            (r"/", MainHandler),
            (r"/about", AboutHandler),
            (r"/love", LoveHandler),
            (r"/github", GithubHandler),
            (r"/githubpage", GithubPageHandler),
            (r"/githubci", GithubCiHandler),
            (r"/user", FetchUserHandler),
            (r"/favicon.ico", web.StaticFileHandler, dict(path=settings["static_path"])),
        ]

        web.Application.__init__(self, handlers, **settings)  # 这里不可以使用`super(Application, self)`
        

if __name__ == "__main__":
    parse_command_line()
    logger.debug("debug")
    logger.error("error")
    logger.info("info")
    logger.warning("warning")
    get_raw_data()

    app = HTTPServer(Application())
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
