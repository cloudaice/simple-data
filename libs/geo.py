#-*-coding: utf-8-*-

from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.options import options
import workers
from tornado import gen
from tornado import escape


AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


@gen.coroutine
def GeoFetch(keyword):
    client = AsyncHTTPClient()
    url = "view-source:http://api.geonames.org/searchJSON?q=Xiaoshan,%20Zhejiang,%20China&maxRows=10&username=" + options.username
    try:
        resp = yield client.fetch(url)
    except HTTPError, e:
        options.logger.error("fetch geoname error %d %s" % (e.code, e.message))
        resp = e
    raise gen.Return(resp)


@gen.coroutine
def collect_geoname():
    china_map = {}
    for city in options.city_list:
        china_map[city] = {"score": 0, "stateInitColor": 6}
    for user in workers.github_china:
        try:
            location = user["location"].lower()
        except Exception, e:
            options.logger.error("location error: %s" % e)
            continue
        city = match_geoname(location)
        if city:
            china_map[city]['score'] += 1


def match_location(city, location):
    if (city in location or location in city):
        return True
    else:
        return False


@gen.coroutune
def match_geoname(location):
    matched_city = None
    for city in options.city_list:
        if match_location(city, location):
            matched_city = city
            break
    if matched_city is None:
        resp = yield GeoFetch(location)
        if resp.code == 200:
            resp = escape.json_encode(resp.body)
            for geo in resp.get("geonames", []):
                if matched_city is None:
                    for city in options.city_list:
                        if match_location(city, geo.get("adminName1", "NoAdminName")):
                            matched_city = city
                            break
    raise gen.Return(matched_city)
