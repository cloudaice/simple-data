#-*-coding: utf-8-*-
import json
import datetime
import base64
import zlib
from tornado import escape
from tornado import gen
#from tornado import httpclient
#from tornado.httpclient import HTTPError
from tornado.httpclient import AsyncHTTPClient
from tornado.options import parse_config_file
from tornado.options import options
from functools import wraps
import tornado.ioloop
from libs.client import GetPage, PatchPage


parse_config_file("config.py")
fetch_new_user_id = None
remote_users_file = None
last_users_file_num = 0  # 记录最后一个完整的文件的编号
AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


def loop_call(delta=60 * 1000):
    def wrap_loop(func):
        @wraps(func)
        def wrap_func(*args, **kwargs):
            func(*args, **kwargs)
            tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(milliseconds=delta),
                wrap_func)
        return wrap_func
    return wrap_loop

    
@gen.coroutine
def loop_fetch_new_user():
    global last_users_file_num
    global fetch_new_user_id
    global remote_users_file
    if remote_users_file is None:
        remote_users_file = {}
        fetch_new_user_id = last_users_file_num * options.user_file_interval  # 每个文件存储十万个用户信息
    fetch_new_user_url = options.api_url + "/users?since=" + str(fetch_new_user_id)
    resp = yield GetPage(fetch_new_user_url)
    if "X-RateLimit-Remaining" in resp.headers:
        options.logger.warning(resp.headers["X-RateLimit-Remaining"])
    if resp.code == 200:
        users_json = escape.json_decode(resp.body)
        if users_json == []:
            options.logger.info("no more users")
            tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(milliseconds=3600 * 1000),
                loop_fetch_new_user)
        else:
            users_json = sorted(users_json, key=lambda d: d["id"])
            if fetch_new_user_id < users_json[-1]["id"]:
                fetch_new_user_id = users_json[-1]["id"]
                options.logger.info("new user_id is %d" % fetch_new_user_id)
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
            now_file_num = fetch_new_user_id / options.user_file_interval
            if now_file_num > last_users_file_num:
                try:
                    update_users_file = {
                        key: remote_users_file[key] for key in remote_users_file
                        if key > (now_file_num - 1) * options.user_file_interval
                        and key < now_file_num * options.user_file_interval + 1}
                except KeyError, e:
                    print e
                    options.logger.error("update file %d KeyError in %r" % (now_file_num, e))
                resp = yield update_file(update_users_file, now_file_num)
                print "update..."
                if resp.code == 200:
                    print "200"
                    last_users_file_num = now_file_num
                    keys = remote_users_file.keys()
                    try:
                        for key in keys:
                            if key <= now_file_num * options.user_file_interval:
                                del remote_users_file[key]
                    except Exception, e:
                        print e
                    print "del..."
                    resp = escape.json_decode(resp.body)
                    filename = "users%d" % now_file_num
                    options.logger.info("file %s size %d update success" %
                                        (resp["files"][filename]["filename"],
                                         resp["files"][filename]["size"]))
                else:
                    options.logger.error("update users file error %d, %r" %
                                         (resp.code, resp.message))
                
            tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(milliseconds=1 * 1000),
                loop_fetch_new_user)
    else:
        options.logger.error("fetch users error %d %r" % (resp.code, resp.message))
        tornado.ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(milliseconds=2 * 1000),
            loop_fetch_new_user)


@gen.coroutine
def update_file(update_users_file, now_file_num):
    filename = "users%d" % now_file_num
    try:
        body = json.dumps({
            "description": "update users file  %d" % now_file_num,
            "files": {
                filename: {
                    "content": base64.b64encode(
                        zlib.compress(json.dumps(update_users_file))
                    )
                }
            }
        })
    except Exception, e:
        options.logger.error("process body error %d %s" % (e.code, e.message))
    resp = yield PatchPage(options.users_url, body)
    raise gen.Return(resp)

if __name__ == "__main__":
    loop_fetch_new_user()
    tornado.ioloop.IOLoop.instance().start()
