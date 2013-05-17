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
from tornado.options import options, parse_config_file
from functools import wraps
import tornado.ioloop
from libs.client import GetPage, PutPage, PatchPage, sync_loop_call


parse_config_file("config.py")
fetch_user_id = None
fetch_new_user_id = None
remote_users_file = None
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
    global fetch_new_user_id
    global remote_users_file
    if fetch_new_user_id is None:
        resp = yield GetPage(options.fetch_new_user_id_url)
        if resp.code == 200:
            resp = escape.json_decode(resp.body)
            content = base64.b64decode(resp["content"])  # 解码base64
            try:
                fetch_new_user_id = escape.json_decode(content)  # 解成dict类型
            except ValueError:
                fetch_new_user_id = {"id": 0}
                options.logger.warning("decode fetch_new_user_id error")
        else:
            fetch_new_user_id = {"id": 0}
            options.logger.error("fetch new_user_id error %d %r" % (resp.code, resp.message))
    if remote_users_file is None:
        resp = yield GetPage(options.users_url)
        if resp.code == 200:
            resp = escape.json_decode(resp.body)
            users_raw_url = resp["files"]["users"]["raw_url"]
            resp = yield GetPage(users_raw_url)
            try:
                content = base64.b64decode(resp.body)
            except TypeError:
                options.logger.error("users is not base64 decode")
            try:
                content = zlib.decompress(content)
            except zlib.error:
                options.logger.error("users is not zlib decode")
            try:
                remote_users_file = escape.json_decode(content)
            except ValueError:
                remote_users_file = {}
                options.logger.warning("decode remote users file error")
        else:
            remote_users_file = {}
            options.logger.error("fetch users error %d %r" % (resp.code, resp.message))
    fetch_new_user_url = options.api_url + "/users?since=" + str(fetch_new_user_id["id"])
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
            if fetch_new_user_id["id"] < users_json[-1]["id"]:
                fetch_new_user_id["id"] = users_json[-1]["id"]
                options.logger.info("new user id is %d" % fetch_new_user_id["id"])
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
            tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(milliseconds=2 * 1000),
                loop_fetch_new_user)
    else:
        options.logger.error("fetch users error %d %r" % (resp.code, resp.message))
        tornado.ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(milliseconds=2 * 1000),
            loop_fetch_new_user)


@sync_loop_call(10 * 1000)
@gen.coroutine
def commit_fetch_new_user():
    global remote_users_file
    global fetch_new_user_id
    if remote_users_file and fetch_new_user_id:
        resp = yield GetPage(options.fetch_new_user_id_url)
        if resp.code == 200:
            print "fetch new user id ok"
            try:
                resp = escape.json_decode(resp.body)
            except Exception, e:
                print e
            try:
                content = base64.b64decode(resp["content"])
            except Exception, e:
                print e
            print "content is ok"
            try:
                old_fetch_new_user_id = escape.json_decode(content)
                print old_fetch_new_user_id
            except ValueError:
                options.logger.error("decode fetch new user id error")
                old_fetch_new_user_id = {"id": fetch_new_user_id["id"] - 5001}
        else:
            options.logger.error("when fetch new user id error %d, %r" %
                                 (resp.code, resp.message))
            old_fetch_new_user_id = {"id": fetch_new_user_id["id"] - 5001}

        if fetch_new_user_id["id"] - old_fetch_new_user_id["id"] > 200:
            print "start commit"
            try:
                content = zlib.compress(json.dumps(remote_users_file))
                print "zlib is ok"
            except Exception, e:
                print e
            print "update users file on %d" % fetch_new_user_id["id"]
            try:
                body = json.dumps({
                    "description": "update users file on %d" % fetch_new_user_id["id"],
                    "files": {
                        "users": {
                            "content": base64.b64encode(
                                zlib.compress(json.dumps(remote_users_file))
                            )
                        }
                    }
                })
                print "body"
            except Exception, e:
                print e
            print 'patch...'
            resp = yield PatchPage(options.users_url, body)
            if resp.code == 200:
                print 'patched'
                try:
                    resp = escape.json_decode(resp.body)
                except Exception, e:
                    print e
                #options.logger.info(json.dumps(resp, indent=4, separators=(',', ':')))
                options.logger.info("file %s size %d commit success" %
                                    (resp["files"]["users"]["filename"], resp["files"]["users"]["size"]))
                resp = yield GetPage(options.fetch_new_user_id_url)
                if resp.code == 200:
                    resp = escape.json_decode(resp.body)
                    sha = resp["sha"]
                    body = json.dumps({
                        "message": "update fetch_new_user_id.json on %d" % fetch_new_user_id["id"],
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
                    resp = yield PutPage(options.fetch_new_user_id_url, body)
                    if resp.code == 200:
                        resp = escape.json_decode(resp.body)
                        options.logger.info("file %s size %d commit success" %
                                            (resp["content"]["name"], resp["content"]["size"]))
                    else:
                        options.logger.error("when commit fetch new user id error %d, %r" %
                                             (resp.code, resp.message))
                else:
                    options.logger.error("fetch new user id error %d, %r" %
                                         (resp.code, resp.message))
            else:
                options.logger.error("update users file error %d, %r" %
                                     (resp.code, resp.message))
        else:
            options.logger.info("new user id %d is not 5000 more than old user id %d" %
                                (fetch_new_user_id["id"], old_fetch_new_user_id["id"]))
    else:
        options.logger.info("remote_user_file and fetch_new_user_id has not ready")
    raise gen.Return()

if __name__ == "__main__":
    loop_fetch_new_user()
    commit_fetch_new_user()
    tornado.ioloop.IOLoop.instance().start()
