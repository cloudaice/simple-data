#-*-coding: utf-8-*-
import urllib
from tornado import escape
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
#from tornado.options import parse_config_file
from tornado.options import options
import tornado.ioloop
from libs.client import GetPage, sync_loop_call, formula, update_file
from libs.geo import match_geoname, match_world_geoname
import time


#parse_config_file("config.py")
github_china = []
github_world = []
temp_github_world = []
temp_github_china = []
current_china_page = 1
current_world_page = 1

china_location_map = {}
china_map = {}
for city in options.city_list:
    china_map[city] = {"score": 0, "stateInitColor": 6}

world_location_map = {}
world_map = {}
for country_code in options.country_code_list:
    world_map[country_code] = {"score": 0, "staticInitColor": 6}


AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


def wash(users):
    user_names = []
    new_users = []
    for user in users:
        if user['login'] not in user_names:
            user_names.append(user['login'])
            new_users.append(user)
    return new_users

    
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
                "name": user["name"] or "Unknown",
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
        options.logger.error("get china user error on page %d, error code %d, %s" %
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
                "name": user["name"] or "Unknown",
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


@sync_loop_call(60 * 1000)
@gen.coroutine
def update_china_location():
    global china_location_map
    global china_map
    if not china_location_map:  # Fetch location_map file
        resp = yield GetPage(options.api_url + options.location_map_gist)
        if resp.code == 200:
            resp = escape.json_decode(resp.body)
            raw_url = resp['files']['location_map.json']['raw_url']
            resp = yield GetPage(raw_url)
            if resp.code == 200:
                china_location_map = escape.json_decode(resp.body)
            else:
                options.logger.error("Fetch raw data error %d, %s" %
                                     (resp.code, resp.message))
        else:
            options.logger.error("Get gist error %d, %s" % (resp.code, resp.message))
    else:  # update location_map file every hour
        if int(time.time()) % 36000 < 60:
            resp = yield update_file(options.api_url + options.location_map_gist,
                                     "location_map.json",
                                     china_location_map)
            if resp.code != 200:
                options.logger.error("update gists error %d, %s" % (resp.code, resp.message))

    temp_china_map = {}
    for city in options.city_list:
        temp_china_map[city] = {"score": 0, "stateInitColor": 6}

    for user in github_china:
        try:
            location = user["location"].lower()
            location = ','.join(location.strip().split())
        except Exception, e:
            options.logger.error("lower location error %s" % e)
            continue
        # because acording to geoname match china will match to shanghai
        if location == "china":
            continue
        if location in china_location_map:
            city = china_location_map[location]
        else:
            city = yield match_geoname(location)
        if city:
            temp_china_map[city]["score"] += 1
            china_location_map[location] = city
        else:
            options.logger.warning("location: %s can't match" % location)

    china_map = temp_china_map.copy()


@sync_loop_call(60 * 1000)
@gen.coroutine
def update_world_location():
    options.logger.info("start update world_location")
    global world_location_map
    global world_map
    if not world_location_map:  # get file into world_location_map
        resp = yield GetPage(options.api_url + options.world_location_map_gist)
        if resp.code == 200:
            resp = escape.json_decode(resp.body)
            raw_url = resp["files"]["world_location_map.json"]['raw_url']
            resp = yield GetPage(raw_url)
            if resp.code == 200:
                world_location_map = escape.json_decode(resp.body)
            else:
                options.logger.error("Fetch raw data error %d, %s" %
                                     (resp.code, resp.message))
        else:
            options.logger.error("Get gist error %d, %s" %
                                 (resp.code, resp.message))

    else:  # update world_location_map file every hour
        if int(time.time()) % 36000 < 60:
            resp = yield update_file(options.api_url + options.world_location_map_gist,
                                     "world_location_map.json",
                                     world_location_map)
            if resp.code != 200:
                options.logger.error("update gists error %d, %s" %
                                    (resp.code, resp.message))

    temp_world_map = {}
    for country_code in options.country_code_list:
        temp_world_map[country_code] = {"score": 0, "staticInitColor": 6}

    for user in github_world:
        if not user["location"]:
            continue
        try:
            location = user["location"].strip()
            location = ','.join(filter(lambda d: d,
                                ','.join(location.split()).split(',')))
        except Exception, e:
            options.logger.error("Error: %s" % e)
            continue
        if location in world_location_map:
            country_code = world_location_map[location]
        else:
            country_code = yield match_world_geoname(location)
        if country_code:
            temp_world_map[country_code]["score"] += 1
            world_location_map[location] = country_code
        else:
            options.logger.warning("location: %s can't match" % location)

    world_map = temp_world_map.copy()


if __name__ == "__main__":
    update_china_user()
    update_world_user()
    update_china_location()
    update_world_location()
    tornado.ioloop.IOLoop.instance().start()
