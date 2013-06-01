#-*-coding: utf-8-*-
import os
import json
import datetime
from tornado import web
from tornado import gen
from tornado import escape
from tornado.web import asynchronous
from tornado.options import parse_command_line, options, parse_config_file
import tornado.ioloop
import tornado.log
from tornado.websocket import WebSocketHandler
from libs.geo import GeoFetch
from tornado.httpclient import AsyncHTTPClient
from test import Get

github_data = {}
parse_config_file("config.py")
parse_config_file("settings.py")

import workers


class ApiHandler(web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(ApiHandler, self).__init__(*args, **kwargs)
        super(ApiHandler, self).set_header('Content-Type', 'application/json; charset=UTF-8')
        
    def prepare(self):
        """do something before request comming"""
        #options.logger.debug(self.request)
        pass

    def on_finish(self):
        """do something after response to client like logging"""
        #options.logger.debug("finish request.")
        pass


class ChinaMapHandler(WebSocketHandler):
    handlers = 0

    def open(self):
        ChinaMapHandler.handlers += 1
        options.logger.info("The numbers of chinamaps sockets is %d" %
                            ChinaMapHandler.handlers)
        self.callback = None
        message = []
        self.write_message(json.dumps(message))

    def on_message(self, message):
        options.logger.info('recieved message from chinamap')
        message = escape.json_decode(message)
        self.check(message)

    def check(self, message):
        china_map = workers.china_map.copy()

        for city in china_map:
            if china_map[city]['score'] > 0 and china_map[city]['score'] < 5:
                china_map[city]['stateInitColor'] = 5
            elif china_map[city]['score'] >= 5 and china_map[city]['score'] < 10:
                china_map[city]['stateInitColor'] = 4
            elif china_map[city]['score'] >= 10 and china_map[city]['score'] < 50:
                china_map[city]['stateInitColor'] = 3
            elif china_map[city]['score'] >= 50 and china_map[city]['score'] < 100:
                china_map[city]['stateInitColor'] = 2
            elif china_map[city]['score'] >= 100 and china_map[city]['score'] < 200:
                china_map[city]['stateInitColor'] = 1
            elif china_map[city]['score'] >= 200:
                china_map[city]['stateInitColor'] = 0

        if message == china_map:
            self.callback = tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(milliseconds=500),
                lambda: self.check(message))
        else:
            options.logger.info("send message to chinamap...")
            self.write_message(json.dumps(china_map))
            
    def on_close(self):
        ChinaMapHandler.handlers -= 1
        if self.callback:
            options.logger.warning("remove chinamap callback")
            tornado.ioloop.IOLoop.instance().remove_timeout(self.callback)


class WorldMapHandler(WebSocketHandler):
    handlers = 0

    def open(self):
        WorldMapHandler.handlers += 1
        options.logger.info("The numbers of worldmaps sockets is %d " %
                            WorldMapHandler.handlers)
        self.callback = None
        message = []
        self.write_message(json.dumps(message))

    def on_message(self, message):
        options.logger.info("recieved message from worldmap")
        message = escape.json_decode(message)
        self.check(message)

    def check(self, message):
        world_map = workers.world_map.copy()

        for country_code in world_map:
            if world_map[country_code]["score"] > 0 and world_map[country_code]["score"] < 5:
                world_map[country_code]["stateInitColor"] = 5
            elif world_map[country_code]["score"] >= 5 and world_map[country_code]["score"] < 10:
                world_map[country_code]["stateInitColor"] = 4
            elif world_map[country_code]["score"] >= 10 and world_map[country_code]["score"] < 50:
                world_map[country_code]["stateInitColor"] = 3
            elif world_map[country_code]["score"] >= 50 and world_map[country_code]["score"] < 100:
                world_map[country_code]["stateInitColor"] = 2
            elif world_map[country_code]["score"] >= 100 and world_map[country_code]["score"] < 200:
                world_map[country_code]["stateInitColor"] = 1
            elif world_map[country_code]["score"] >= 200:
                world_map[country_code]["stateInitColor"] = 0
        if message == world_map:
            self.callback = tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(milliseconds=500),
                lambda: self.check(message))
        else:
            options.logger.info("send message to worldmap")
            self.write_message(json.dumps(world_map))

    def on_close(self):
        WorldMapHandler.handlers -= 1
        if self.callback:
            options.logger.warning("remove worldmap timeout...")
            tornado.ioloop.IOLoop.instance().remove_timeout(self.callback)
            

class GithubChinaHandler(WebSocketHandler):
    @asynchronous
    @gen.coroutine
    def post(self):
        self.write(json.dumps(workers.github_china, indent=4, separators=(',', ': ')))
        self.finish()


class GithubWorldHandler(ApiHandler):
    @asynchronous
    @gen.coroutine
    def post(self):
        self.write(json.dumps(workers.github_world, indent=4, separators=(',', ': ')))
        self.finish()
            

class MainHandler(web.RequestHandler):
    @asynchronous
    def get(self):
        self.render("index.html")


class AboutHandler(web.RequestHandler):
    @asynchronous
    def get(self):
        self.render("about.html")


class ChinaSocketbHandler(WebSocketHandler):
    handlers = 0

    def open(self):
        ChinaSocketbHandler.handlers += 1
        options.logger.info(" The numbers of china sockets is %d" %
                            ChinaSocketbHandler.handlers)
        self.callback = None
        self.write_message(json.dumps(workers.github_china))

    def on_message(self, message):
        options.logger.info('recieved message from china')
        message = escape.json_decode(message)
        self.check(message)

    def check(self, message):
        if message == workers.github_china:
            self.callback = tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(milliseconds=500),
                lambda: self.check(message))
        else:
            options.logger.info("send message to china...")
            self.write_message(json.dumps(workers.github_china))

    def on_close(self):
        ChinaSocketbHandler.handlers -= 1
        if self.callback:
            options.logger.warning("remove china users callback")
            tornado.ioloop.IOLoop.instance().remove_timeout(self.callback)
        

class WorldSocketbHandler(WebSocketHandler):
    handlers = 0

    def open(self):
        WorldSocketbHandler.handlers += 1
        options.logger.info("The numbers of world sockets is %d" %
                            WorldSocketbHandler.handlers)
        self.callback = None
        self.write_message(json.dumps(workers.github_world))

    def on_message(self, message):
        options.logger.info("recieved message from world")
        message = escape.json_decode(message)
        self.check(message)

    def check(self, message):
        if message == workers.github_world:
            self.callback = tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(milliseconds=500),
                lambda: self.check(message))
        else:
            options.logger.info("send message to world...")
            self.write_message(json.dumps(workers.github_world))

    def on_close(self):
        WorldSocketbHandler.handlers -= 1
        if self.callback:
            options.logger.warning("remove world users callback")
            tornado.ioloop.IOLoop.instance().remove_timeout(self.callback)


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'template'),
    "debug": options.debug
}

handlers = [
    (r"/", MainHandler),
    (r"/socketchina", ChinaSocketbHandler),
    (r"/socketworld", WorldSocketbHandler),
    (r"/githubchina", GithubChinaHandler),
    (r"/githubworld", GithubWorldHandler),
    (r"/chinamap", ChinaMapHandler),
    (r"/worldmap", WorldMapHandler),
    (r"/about", AboutHandler),
    (r"/favicon.ico", web.StaticFileHandler, dict(path=settings["static_path"])),
]

app = web.Application(handlers, **settings)
workers.update_china_user()
workers.update_world_user()
workers.update_china_location()
workers.update_world_location()

if __name__ == "__main__":
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
