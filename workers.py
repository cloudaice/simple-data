#-*-coding: utf-8-*-
import json
import datetime
import base64
from tornado import escape
from tornado import gen
from tornado import httpclient
from tornado.httpclient import HTTPError
from tornado.httpclient import AsyncHTTPClient
from tornado.options import options, parse_config_file
from functools import wraps
import tornado.ioloop


parse_config_file("config.py")
fetch_user_id = None
fetch_new_user_id = None
remote_users_file = None
AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


class TornadoDataRequest(httpclient.HTTPRequest):
    def __init__(self, url, **kwargs):
        super(TornadoDataRequest, self).__init__(url, **kwargs)
        self.auth_username = options.username
        self.auth_password = options.password
        self.headers = {
            'Content-Type': 'application/json; charset=UTF-8'
        },
        self.headers = {}
        self.user_agent = "Tornado-data"


def loop_call(delta=60 * 1000):
    def wrap_loop(func):
        @wraps(func)
        def wrap_func(*args, **kwargs):
            func(*args, **kwargs)
            tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(milliseconds=delta), wrap_func)
        return wrap_func
    return wrap_loop


@gen.coroutine
def GetPage(url):
    client = AsyncHTTPClient()
    request = TornadoDataRequest(url, method='GET')
    response = yield client.fetch(request)
    raise gen.Return(response)


@gen.coroutine
def PutPage(url, body):
    client = AsyncHTTPClient()
    request = TornadoDataRequest(url, method='PUT', body=body)
    response = yield client.fetch(request)
    raise gen.Return(response)

    
@gen.coroutine
def loop_fetch_new_user():
    global fetch_new_user_id
    global remote_users_file
    if fetch_new_user_id is None:
        try:
            resp = yield GetPage(options.fetch_new_user_id_url)  # should do some error process
        except HTTPError, e:
            options.logger.error("fetch new user id error", e.code, e.message)
            raise e
        resp = escape.json_decode(resp.body)
        content = base64.b64decode(resp["content"])  # 解码base64
        try:
            fetch_new_user_id = escape.json_decode(content)  # 解成dict类型
        except ValueError:
            options.logger.warning("decode fetch_new_user_id error")
            fetch_new_user_id = {"id": 0}
        options.logger.info(json.dumps(fetch_new_user_id, indent=4, separators=(',', ': ')))
    if remote_users_file is None:
        try:
            resp = yield GetPage(options.users_url)
        except HTTPError, e:
            options.logger.error("fetch users error", e.code, e.message)
            raise e
        resp = escape.json_decode(resp.body)
        content = base64.b64decode(resp["content"])
        try:
            remote_users_file = escape.json_decode(content)
        except ValueError:
            remote_users_file = {}
        print json.dumps(remote_users_file, indent=4, separators=(',', ': '))
    client = AsyncHTTPClient()
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
            datetime.timedelta(milliseconds=2 * 1000),
            loop_fetch_new_user)


@loop_call(30 * 1000)
@gen.coroutine
def commit_fetch_new_user():
    global remote_users_file
    global fetch_new_user_id
    if remote_users_file and fetch_new_user_id:
        client = AsyncHTTPClient()
        request = TornadoDataRequest("https://api.github.com/repos/cloudaice/simple-data/contents/users.json")
        resp = yield client.fetch(request)
        resp = escape.json_decode(resp.body)
        sha = resp["sha"]
        print sha
        client = AsyncHTTPClient()
        request = httpclient.HTTPRequest(
            "https://api.github.com/repos/cloudaice/simple-data/contents/users.json",
            method="PUT",
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            auth_username=options.username,
            auth_password=options.password,
            user_agent="Tornado-Data",
            body=json.dumps({
                "message": "update users.json",
                "content": base64.b64encode(
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
        print "resp return"
        if resp.error:
            print resp.error
        resp = escape.json_decode(resp.body)
        print json.dumps(resp, indent=4, separators=(',', ': '))
        client = AsyncHTTPClient()
        request = TornadoDataRequest("https://api.github.com/repos/cloudaice/simple-data/contents/fetch_new_user_id.json")
        resp = yield client.fetch(request)
        resp = escape.json_decode(resp.body)
        sha = resp["sha"]
        print sha
        client = AsyncHTTPClient()
        request = httpclient.HTTPRequest(
            "https://api.github.com/repos/cloudaice/simple-data/contents/fetch_new_user_id.json",
            method="PUT",
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            auth_username=options.username,
            auth_password=options.password,
            user_agent="Tornado-Data",
            body=json.dumps({
                "message": "update fetch_new_user_id.json",
                "content": base64.b64encode(
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

if __name__ == "__main__":
    loop_fetch_new_user()
    commit_fetch_new_user()
    tornado.ioloop.IOLoop.instance().start()
