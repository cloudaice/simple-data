#-*-coding: utf-8-*-
import os
import time
import json
from tornado import escape
from tornado import web
from tornado import gen
from tornado import httpclient
from tornado.web import asynchronous
from tornado.options import parse_command_line, options, parse_config_file
import tornado.ioloop
import tornado.log
from addr import searchpage
from libs.client import GetPage, sync_loop_call, formula
import workers


github_data = {}
parse_config_file("config.py")

city_list = ["heilongjiang", "jilin", "liaoning", "hebei", "shandong", "jiangsu",
             "zhejiang", "anhui", "henan", "shanxi", "shanxii", "gansu", "hubei",
             "jiangxi", "fujian", "hunan", "guizou", "sichuan", "yunnan", "qinghai",
             "hainan", "shanghai", "chongqing", "tianjin", "beijing", "ningxia",
             "neimenggu", "guangxi", "xinjiang", "xizang", "guangdong",
             "xianggang", "taiwan", "aomen"]


@sync_loop_call(60 * 1000)
@gen.coroutine
def get_raw_data():
    """
    Every 5 seconds will fetch github.com
    """
    options.logger.info("start fetch %d" % int(time.time()))
    global github_data
    resp = yield GetPage("https://api.github.com/gists/4524946")
    if resp.code == 200:
        options.logger.info("fetch gists sunccess")
        if "X-RateLimit-Remaining" in resp.headers:
            options.logger.info("limit: %r" % resp.headers["X-RateLimit-Remaining"])
        resp = escape.json_decode(resp.body)
        users_url = resp["files"]["github-users-stats.json"]["raw_url"]
        languages_url = resp["files"]["github-languages-stats.json"]["raw_url"]
        users, languages = yield [GetPage(users_url),
                                  GetPage(languages_url)]
        if users.code == 200 and languages.code == 200:
            users_stats = escape.json_decode(users.body)
            languages_stats = escape.json_decode(languages.body)
            for user in users_stats:
                user["score"] = user["contributions"] + formula(user["followers"])
            users_stats = sorted(users_stats,
                                 key=lambda d: d['score'],
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


class GithubChinaHandler(ApiHandler):
    @asynchronous
    @gen.coroutine
    def post(self):
        self.write(json.dumps(workers.github_china, indent=4, separators=(',', ': ')))
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


class GithubWorldHandler(ApiHandler):
    @asynchronous
    @gen.coroutine
    def post(self):
        self.write(json.dumps(workers.github_world, indent=4, separators=(',', ': ')))
        self.finish()
            

class MainHandler(web.RequestHandler):
    @asynchronous
    def get(self):
        self.render("index.html")


class AboutHandler(web.RequestHandler):
    @asynchronous
    def get(self):
        self.render("about.html")
        

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'template'),
    "debug": True
}

handlers = [
    (r"/", MainHandler),
    (r"/github", GithubHandler),
    (r"/githubpage", GithubPageHandler),
    (r"/githubchina", GithubChinaHandler),
    (r"/githubworld", GithubWorldHandler),
    (r"/user", FetchUserHandler),
    (r"/about", AboutHandler),
    (r"/favicon.ico", web.StaticFileHandler, dict(path=settings["static_path"])),
]

app = web.Application(handlers, **settings)
get_raw_data()
workers.update_china_user()
workers.update_world_user()

if __name__ == "__main__":
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
