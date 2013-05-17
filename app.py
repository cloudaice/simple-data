#-*-coding: utf-8-*-
from math import exp
import os
import time
import json
import base64
from tornado import escape
from tornado import web
from tornado import gen
from tornado import httpclient
from tornado.httpserver import HTTPServer
from tornado.web import asynchronous
from tornado.options import parse_command_line, options, parse_config_file
import tornado.ioloop
import tornado.log
from addr import searchpage
from libs.client import GetPage, PutPage, PatchPage, sync_loop_call


github_data = {}
parse_config_file("config.py")

formula = lambda x: 2 ** 11 / (1 + pow(exp(1), -(x - 2 ** 8) / 2 ** 6))


@sync_loop_call(5 * 1000)
@gen.coroutine
def get_raw_data():
    """
    Every 5 seconds will fetch github.com
    """
    options.logger.info("start fetch %d" % int(time.time()))
    global github_data
    resp = yield GetPage("https://api.github.com/gists/4524946")
    if resp.code == 200:
        print resp.headers["X-RateLimit-Limit"]
        print resp.headers["X-RateLimit-Remaining"]
        options.logger.info("fetch gists sunccess")
        resp = escape.json_decode(resp.body)
        users_url = resp["files"]["github-users-stats.json"]["raw_url"]
        languages_url = resp["files"]["github-languages-stats.json"]["raw_url"]
        users, languages = yield [GetPage(users_url),
                                  GetPage(languages_url)]
        if users.code == 200 and languages.code == 200:
            if "X-RateLimit-Remaining" in languages.headers:
                print languages.headers["X-RateLimit-Remaining"]
            if "X-RateLimit-Remaining" in users.headers:
                print users.headers["X-RateLimit-Remaining"]
            users_stats = escape.json_decode(users.body)
            languages_stats = escape.json_decode(languages.body)
            users_stats = sorted(users_stats,
                                 key=lambda d: d["contributions"] + formula(d["followers"]),
                                 reverse=True)
            users_stats = filter(lambda u: 'china' in u['location'].lower(), users_stats)
            github_data["users_stats"] = users_stats
            github_data["languages_stats"] = languages_stats
            options.logger.info("fetch users and languages success")
        else:
            options.logger.error("%d, %r" % (users.code, users.message))
            options.logger.error("%d, %r" % (languages.code, languages.message))
    else:
        options.logger.error("%d, %r" % (resp.code, resp.message))
    gen.Return()


class ApiHandler(web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(ApiHandler, self).__init__(*args, **kwargs)
        super(ApiHandler, self).set_header('Content-Type', 'application/json; charset=UTF-8')
        
    def prepare(self):
        """do something before request comming"""
        #options.logger.debug(self.request)
        pass

    def on_finish(self):
        """do something after response to client like logging"""
        #options.logger.debug("finish request.")
        pass


class TornadoDataRequest(httpclient.HTTPRequest):
    def __init__(self, url, **kwargs):
        super(TornadoDataRequest, self).__init__(url, **kwargs)
        self.method = "GET"
        self.auth_username = options.username
        self.auth_password = options.password
        self.user_agent = "Tornado-data"


class GithubPageHandler(web.RequestHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        resp = yield GetPage(searchpage(2))
        if resp.code == 200:
            self.write(resp.body)
        else:
            self.write("%d, %r" % (resp.code, resp.message))
        self.finish()


class FetchUserHandler(ApiHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        resp = yield GetPage(options.contribution_url("cloudaice"))
        if resp.code == 200:
            resp = escape.json_decode(resp.body)
            self.write(json.dumps(resp, indent=4, separators=(",", ": ")))
        else:
            self.write("%d, %r" % (resp.code, resp.message))
        self.finish()


class GithubCiHandler(ApiHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        global remote_users_file
        resp = yield GetPage(options.api_url + "/repos/cloudaice/simple-data/contents/test.md")
        if resp.code == 404:
            options.logger.info("fetch file 404")
            self.write("%d, %r" % (resp.code, resp.message))
        elif resp.code == 200:
            resp = escape.json_decode(resp.body)
            sha = resp['sha']
            url = options.api_url + "/repos/cloudaice/simple-data/contents/test.md"
            body = json.dumps({
                "message": "update test",
                "content": base64.b64encode(
                    json.dumps(
                        {"name": "cloudaice", "type": "testmd"},
                        indent=4,
                        separators=(',', ': ')
                    )
                ),
                "committer": {"name": "cloudaice", "email": "cloudaice@163.com"},
                "sha": sha
            })
            resp = yield PutPage(url, body)
            if resp.code == 200:
                resp = escape.json_decode(resp.body)
                if isinstance(resp, dict):
                    self.write(json.dumps(resp, indent=4, separators=(',', ': ')))
                    options.logger.info("file %s size %d commit success" %
                                        (resp["content"]["name"], resp["content"]["size"]))
                else:
                    self.write("Failed")
            else:
                self.write("%d, %r" % (resp.code, resp.message))
        else:
            self.write(resp.message)
        self.finish()


class GithubHandler(ApiHandler):
    @asynchronous
    @gen.coroutine
    def post(self):
        global github_data
        if 'users_stats' not in github_data:
            users_stats = []
        else:
            users_stats = github_data["users_stats"]
        #languages_stats = github_data["languages_stats"]
        self.write(json.dumps(users_stats, indent=4, separators=(',', ': ')))
        self.finish()


class GithubEiHandler(ApiHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        body = json.dumps({
            "description": "update users file",
            "files": {
                "users": {
                    "content": "hello world"
                }
            }
        })
        resp = yield PatchPage(options.users_url, body)
        if resp.code == 200:
            resp = escape.json_decode(resp.body)
            self.write(json.dumps(resp, indent=4, separators=(',', ':')))
        else:
            options.logger.error("update gist error")
            self.write("%d %s" % (resp.code, resp.message))
            

class MainHandler(web.RequestHandler):
    @asynchronous
    def get(self):
        self.render("index.html")


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'template'),
    "debug": False
}


class AboutHandler(web.RequestHandler):
    @asynchronous
    def get(self):
        self.render("about.html")
        

class Application(web.Application):
    def __init__(self, *arhs):
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), 'static'),
            'template_path': os.path.join(os.path.dirname(__file__), 'template'),
            "debug": False
        }

        handlers = [
            (r"/", MainHandler),
            (r"/about", AboutHandler),
            (r"/github", GithubHandler),
            (r"/githubpage", GithubPageHandler),
            #(r"/githubci", GithubCiHandler),
            #(r"/githubei", GithubEiHandler),
            (r"/user", FetchUserHandler),
            (r"/favicon.ico", web.StaticFileHandler, dict(path=settings["static_path"])),
        ]

        web.Application.__init__(self, handlers, **settings)  # 这里不可以使用`super(Application, self)`
        

if __name__ == "__main__":
    parse_command_line()
    get_raw_data()
    app = HTTPServer(Application())
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
