#-*-coding: utf-8-*-

from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPRequest
from tornado.options import options
from tornado import gen
from tornado import escape


AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


class GeoRequest(HTTPRequest):
    def __init__(self, url, **kwargs):
        super(GeoRequest, self).__init__(url, **kwargs)
        self.user_agent = "Tornado-data"
        self.auth_username = options.username


@gen.coroutine
def GeoFetch(keyword):
    client = AsyncHTTPClient()
    url = ("http://api.geonames.org/searchJSON?q=%s&maxRows=10&username=%s" %
           (keyword, options.username))
    request = GeoRequest(url)
    try:
        resp = yield client.fetch(request)
    except HTTPError, e:
        options.logger.error("fetch geoname error %d %s" % (e.code, e.message))
        resp = e
    raise gen.Return(resp)


def match_location(city, location):
    if not location:
        return False
    if (city in location or location in city):
        return True
    else:
        return False


@gen.coroutine
def match_geoname(location):
    matched_city = None
    for city in options.city_list:
        if match_location(city, location):
            matched_city = city
            break
    if matched_city is None:
        resp = yield GeoFetch(location)
        if resp.code == 200:
            resp = escape.json_decode(resp.body)
            for geo in resp.get("geonames", []):
                if matched_city:
                    break
                for city in options.city_list:
                    is_matched = match_location(
                        city, geo.get("adminName1", "NoName").lower())

                    if is_matched:
                        matched_city = city
                        break

    raise gen.Return(matched_city)


@gen.coroutine
def match_world_geoname(location):
    matched_country_code = None
    for country_code in options.country_code_list:
        if match_location(country_code, location):
            matched_country_code = country_code
            break
    if matched_country_code is None:
        resp = yield GeoFetch(location)
        if resp.code == 200:
            resp = escape.json_decode(resp.body)
            for geo in resp.get("geonames", []):
                if matched_country_code:
                    break
                for country_code in options.country_code_list:
                    if match_location(country_code, geo.get("countryCode", "NoName")):
                        matched_country_code = country_code
                        break

        else:
            options.logger.error("Error fetch geonames %d, %s" %
                                 (resp.code, resp.message))

    raise gen.Return(matched_country_code)
