#-*-coding: utf-8-*-

from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPRequest
from tornado.options import options
from functools import wraps
from tornado import escape
import tornado.ioloop
import base64
import time
import datetime
import json
from math import exp

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


formula = lambda x: 2 ** 10 / (1 + pow(exp(1), -(x - 2 ** 7) / 2 ** 5))


def loop_call(delta=60 * 1000):
    def wrap_loop(func):
        @wraps(func)
        def wrap_func(*args, **kwargs):
            func(*args, **kwargs)
            tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timeelta(milliseconds=delta),
                wrap_func)
        return wrap_func
    return wrap_loop


def sync_loop_call(delta=60 * 1000):
    """
    Wait for func down then process add_timeout
    """
    def wrap_loop(func):
        @wraps(func)
        @gen.coroutine
        def wrap_func(*args, **kwargs):
            options.logger.info("function %r start at %d" %
                                (func.__name__, int(time.time())))
            try:
                yield func(*args, **kwargs)
            except Exception, e:
                options.logger.error("function %r error: %s" %
                                     (func.__name__, e))
            options.logger.info("function %r end at %d" %
                                (func.__name__, int(time.time())))
            tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(milliseconds=delta),
                wrap_func)
        return wrap_func
    return wrap_loop


class TornadoDataRequest(HTTPRequest):
    def __init__(self, url, **kwargs):
        super(TornadoDataRequest, self).__init__(url, **kwargs)
        self.auth_username = options.username
        self.auth_password = options.password
        self.user_agent = "Tornado-data"


@gen.coroutine
def GetPage(url):
    client = AsyncHTTPClient()
    request = TornadoDataRequest(url, method='GET')
    try:
        response = yield client.fetch(request)
    except HTTPError, e:
        response = e
    raise gen.Return(response)


@gen.coroutine
def PutPage(url, body):
    client = AsyncHTTPClient()
    request = TornadoDataRequest(url, method='PUT', body=body)
    try:
        response = yield client.fetch(request)
    except HTTPError, e:
        response = e
    raise gen.Return(response)


@gen.coroutine
def PatchPage(url, body):
    client = AsyncHTTPClient.configurable_default()()
    request = TornadoDataRequest(url, method="PATCH", body=body)
    try:
        response = yield client.fetch(request)
    except HTTPError, e:
        response = e
    raise gen.Return(response)


@gen.coroutine
def commit(url, message, data):
    resp = yield GetPage(url)
    if resp.code == 200:
        resp = escape.json_decode(resp.body)
        sha = resp["sha"]
        body = json.dumps({
            "message": message,
            "content": base64.b64encode(json.dumps(data)),
            "committer": {"name": "cloudaice", "email": "cloudaice@163.com"},
            "sha": sha
        })
        resp = yield PutPage(url, body)
        raise gen.Return(resp)
    else:
        raise gen.Return(resp)


@gen.coroutine
def update_file(gist_url, filename, data):
    try:
        body = json.dumps({
            "description": "update file at %s" %
                           datetime.datetime.utcfromtimestamp(time.time()),
            "files": {
                filename: {
                    "content": json.dumps(data, indent=4, separators=(',', ': '))
                }
            }
        })
    except Exception, e:
        options.logger.error("Error: %s" % e)
    resp = yield PatchPage(gist_url, body)
    raise gen.Return(resp)
