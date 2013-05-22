#-*-coding: utf-8-*-
import datetime
import urllib
from tornado import escape
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
#from tornado.options import parse_config_file
from tornado.options import options
from functools import wraps
import tornado.ioloop
from libs.client import GetPage, sync_loop_call, formula


#parse_config_file("config.py")
github_china = []
github_world = []
temp_github_world = []
temp_github_china = []
current_china_page = 1
current_world_page = 1
AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


def wash(users):
    user_names = []
    new_users = []
    for user in users:
        if user['login'] not in user_names:
            user_names.append(user['login'])
            new_users.append(user)
    return new_users


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

    
@gen.coroutine
def contribute(login):
    resp = yield GetPage(options.contribution_url(login))
    if resp.code == 200:
        resp = escape.json_decode(resp.body)
        all_contribute = sum([day[1] for day in resp])
    else:
        all_contribute = 0
        options.logger.error("fetch contribution error %d, %s" %
                             (resp.code, resp.message))
    raise gen.Return(all_contribute)


@sync_loop_call(32 * 1000)
@gen.coroutine
def update_china_user():
    global github_china
    global current_china_page
    global temp_github_china
    options.logger.info("current page is %d" % current_china_page)
    resp = yield search_china(current_china_page)
    if resp.code == 200:
        resp = escape.json_decode(resp.body)
        users = resp["users"]
        for user in users:
            contributions = yield contribute(user["login"])
            temp_github_china.append({
                "login": user["login"],
                "name": user["name"],
                "location": user["location"],
                "gravatar": "http://www.gravatar.com/avatar/" + user["gravatar_id"]
                + urllib.urlencode({"s": 48}),
                "language": user["language"],
                "contributions": contributions,
                "followers": user["followers"],
                "score": contributions + formula(user["followers"])
            })
        temp_github_china = wash(temp_github_china)
        current_china_page += 1
        if len(github_china) < len(temp_github_china):
            github_china = temp_github_china[:]
            github_china = sorted(github_china, key=lambda d: d['score'], reverse=True)
    elif resp.code == 422:
        github_china = temp_github_china[:]
        github_china = sorted(github_china, key=lambda d: d['score'], reverse=True)
        temp_github_china = []
        current_china_page = 1
        options.logger.info("china loop end")
    else:
        options.logger.error("get chine user error on page %d, error code %d, %s" %
                             (current_china_page, resp.code, resp.message))


@sync_loop_call(64 * 1000)
@gen.coroutine
def update_world_user():
    global github_world
    global current_world_page
    global temp_github_world
    options.logger.info("current page is %d" % current_world_page)
    resp = yield search_world(current_world_page)
    if resp.code == 200:
        resp = escape.json_decode(resp.body)
        users = resp["users"]
        for user in users:
            contributions = yield contribute(user["login"])
            temp_github_world.append({
                "login": user["login"],
                "name": user["name"],
                "location": user["location"],
                "gravatar": "http://www.gravatar.com/avatar/" + user["gravatar_id"]
                + urllib.urlencode({"s": 48}),
                "language": user["language"],
                "contributions": contributions,
                "followers": user["followers"],
                "score": contributions + formula(user["followers"])
            })
        temp_github_world = wash(temp_github_world)
        current_world_page += 1
        if len(github_world) < len(temp_github_world):
            github_world = temp_github_world[:]
            github_world = sorted(github_world, key=lambda d: d['score'], reverse=True)

    elif resp.code == 422:
        github_world = temp_github_world[:]
        github_world = sorted(github_world, key=lambda d: d['score'], reverse=True)
        temp_github_world = []
        current_world_page = 1
        options.logger.info("world loop end")
    else:
        options.logger.error("get world user error on page %d, error code %d, %s" %
                             (current_world_page, resp.code, resp.message))


@gen.coroutine
def search_china(page):
    url = options.api_url + "/legacy/user/search/location:china?start_page=" + str(page) + "&sort=followers&order=desc"
    resp = yield GetPage(url)
    options.logger.info("search china %s" % url)
    raise gen.Return(resp)

    
@gen.coroutine
def search_world(page):
    url = options.api_url + "/legacy/user/search/followers:>0?start_page=" + str(page) + "&sort=followers&order=desc"
    options.logger.info("search world %s" % url)
    resp = yield GetPage(url)
    raise gen.Return(resp)


if __name__ == "__main__":
    update_china_user()
    update_world_user()
    tornado.ioloop.IOLoop.instance().start()
