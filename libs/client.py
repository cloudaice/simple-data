#-*-coding: utf-8-*-

from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPRequest
from tornado.options import options
from functools import wraps
import tornado.ioloop
import time
import datetime

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


def sync_loop_call(delta=60 * 1000):
    """
    Wait for func down then process add_timeout
    """
    def wrap_loop(func):
        @wraps(func)
        @gen.coroutine
        def wrap_func(*args, **kwargs):
            try:
                yield func(*args, **kwargs)
            except:
                options.logger.error("function %r error" % func.__name__)
            options.logger.info("function %r end at %d" % (func.__name__, int(time.time())))
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
