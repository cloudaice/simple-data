#-*-coding: utf-8-*-
from math import exp
import os
import json
import base64
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
fetch_user_id = None
fetch_new_user_id = None
remote_users_file = None
define("port", default=8000)
strong = lambda x: 2 ** 11 / (1 + pow(exp(1), -(x - 2 ** 8) / 2 ** 6))


def searchpage(p):
    if p == 1:
        return "https://github.com/search?q=location:china&s=followers&type=Users"
    else:
        return "https://github.com/search?p=" + str(p) + "&q=location:china&s=followers&type=Users"


def loop_call(delta=60 * 1000):
    def wrap_loop(func):
        @wraps(func)
        def wrap_func(*args, **kwargs):
            func(*args, **kwargs)
            tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(milliseconds=delta), wrap_func)
        return wrap_func
    return wrap_loop


@gen.coroutine
def loop_fetch_new_user():
    global fetch_new_user_id
    global remote_users_file
    httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    if fetch_new_user_id is None:
        client = httpclient.AsyncHTTPClient()
        request = TornadoDataRequest("https://api.github.com/repos/cloudaice/simple-data/contents/fetch_new_user_id.json")
        resp = yield client.fetch(request)
        resp = escape.json_decode(resp.body)
        content = base64.decodestring(resp["content"])  # 解码base64
        fetch_new_user_id = escape.json_decode(content)  # 解成dict类型
        print json.dumps(fetch_new_user_id, indent=4, separators=(',', ': '))
    if remote_users_file is None:
        client = httpclient.AsyncHTTPClient()
        request = TornadoDataRequest("https://api.github.com/repos/cloudaice/simple-data/contents/users.json")
        resp = yield client.fetch(request)
        resp = escape.json_decode(resp.body)
        content = base64.decodestring(resp["content"])
        remote_users_file = escape.json_decode(content)
        print json.dumps(remote_users_file, indent=4, separators=(',', ': '))
    client = httpclient.AsyncHTTPClient()
    fetch_new_user_url = "https://api.github.com/users?since=" + str(fetch_new_user_id["id"])
    request = TornadoDataRequest(fetch_new_user_url)
    resp = yield client.fetch(request)
    users_json = escape.json_decode(resp.body)
    print json.dumps(users_json[-1], indent=4, separators=(', ', ': '))
    if users_json == []:
        print "no users_json"
        tornado.ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(milliseconds=3600 * 1000),
            loop_fetch_new_user)
    else:
        if fetch_new_user_id["id"] < users_json[-1]["id"]:
            fetch_new_user_id["id"] = users_json[-1]["id"]
        for user in users_json:
            if user["id"] not in remote_users_file:
                remote_users_file[user["id"]] = {
                    "login": user["login"],
                    "id": user["id"],
                    "gravatar": user["avatar_url"],
                    "name": "",
                    "location": "",
                    "followers": 0,
                    "contributions": 0,
                    "activity": 1
                }
        print json.dumps(fetch_new_user_id, indent=4, separators=(',', ': '))
        tornado.ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(milliseconds=1 * 1000),
            loop_fetch_new_user)


@loop_call(5 * 1000)
@gen.coroutine
def commit_fetch_new_user():
    global remote_users_file
    global fetch_new_user_id
    if remote_users_file and fetch_new_user_id:
        client = httpclient.AsyncHTTPClient()
        request = TornadoDataRequest("https://api.github.com/repos/cloudaice/simple-data/contents/users.json")
        resp = yield client.fetch(request)
        resp = escape.json_decode(resp.body)
        sha = resp["sha"]
        print sha
        client = httpclient.AsyncHTTPClient()
        request = httpclient.HTTPRequest(
            "https://api.github.com/repos/cloudaice/simple-data/contents/users.json",
            method="PUT",
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            auth_username=config.username,
            auth_password=config.password,
            user_agent="Tornado-Data",
            body=json.dumps({
                "message": "update users.json",
                "content": base64.encodestring(
                    json.dumps(
                        remote_users_file,
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
        print json.dumps(resp, indent=4, separators=(',', ': '))
        client = httpclient.AsyncHTTPClient()
        request = TornadoDataRequest("https://api.github.com/repos/cloudaice/simple-data/contents/fetch_new_user_id.json")
        resp = yield client.fetch(request)
        resp = escape.json_decode(resp.body)
        sha = resp["sha"]
        client = httpclient.AsyncHTTPClient()
        request = httpclient.HTTPRequest(
            "https://api.github.com/repos/cloudaice/simple-data/contents/fetch_new_user_id.json",
            method="PUT",
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            auth_username=config.username,
            auth_password=config.password,
            user_agent="Tornado-Data",
            body=json.dumps({
                "message": "update fetch_new_user_id.json",
                "content": base64.encodestring(
                    json.dumps(
                        fetch_new_user_id,
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
        print json.dumps(resp, indent=4, separators=(',', ': '))

    
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
        print resp.headers
        self.write(resp.body)
        self.finish()


class GithubCiHandler(web.RequestHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        client = httpclient.AsyncHTTPClient()
        request = TornadoDataRequest("https://api.github.com/repos/cloudaice/simple-data/contents/test.md")

        resp = yield client.fetch(request)
        resp = escape.json_decode(resp.body)
        sha = resp['sha']
        client = httpclient.AsyncHTTPClient()
        request = httpclient.HTTPRequest(
            "https://api.github.com/repos/cloudaice/simple-data/contents/test.md",
            method="PUT",
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            auth_username=config.username,
            auth_password=config.password,
            user_agent="Tornado-Data",
            body=json.dumps({
                "message": "test commit",
                "content": base64.encodestring("Hello world!!!"),
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


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'template'),
    "debug": True
}

get_raw_data()
loop_fetch_new_user()
commit_fetch_new_user()

app = web.Application([
    (r"/", MainHandler),
    (r"/about", AboutHandler),
    (r"/love", LoveHandler),
    (r"/github", GithubHandler),
    (r"/githubpage", GithubPageHandler),
    (r"/githubci", GithubCiHandler),
    (r"/user", FetchUserHandler),
    (r"/favicon.ico", web.StaticFileHandler, dict(path=settings["static_path"])),
], **settings)


if __name__ == "__main__":
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
