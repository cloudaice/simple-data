#-*-coding: utf-8-*-
import os
import json
from tornado import web
from tornado import gen
from tornado import httpclient
from tornado.web import asynchronous
from tornado.options import parse_command_line, options, parse_config_file
import tornado.ioloop
import tornado.log
import workers


github_data = {}
parse_config_file("config.py")
parse_config_file("settings.py")

city_list = [
    "heilongjiang", "jilin", "liaoning", "hebei", "shandong", "jiangsu", "zhejiang", "anhui",
    "henan", "shanxi", "shanxii", "gansu", "hubei", "jiangxi", "fujian", "hunan", "guizou",
    "sichuan", "yunnan", "qinghai", "hainan", "shanghai", "chongqing", "tianjin", "beijing", "ningxia",
    "neimenggu", "guangxi", "xinjiang", "xizang", "guangdong", "xianggang", "taiwan", "aomen"]

country_list = [
    'United Arab Emirates', 'Afghanistan', 'Albania', 'Armenia', 'Angola', 'Argentina', 'Austria',
    'Australia', 'Azerbaijan', 'Bosnia and Herzegovina', 'Bangladesh', 'Belgium', 'Burkina Faso',
    'Bulgaria', 'Burundi', 'Benin', 'Brunei Darussalam', 'Plurinational State of Bolivia', 'Brazil',
    'Bhutan', 'Botswana', 'Belarus', 'Belize', 'Canada', 'The Democratic Republic of the Congo',
    'Central African Republic', 'Congo', 'Switzerland', 'Ivory Coast', 'Chile', 'Cameroon', 'China',
    'Colombia', 'Costa Rica', 'Cuba', 'Cyprus', 'Czech Republic', 'Germany', 'Djibouti', 'Denmark',
    'Dominican Republic', 'Algeria', 'Ecuador', 'Estonia', 'Egypt', 'Western Sahara', 'Eritrea',
    'Spain', 'Ethiopia', 'Finland', 'Fiji', 'Falkland Islands (Malvinas)', 'France', 'Gabon',
    'United Kingdom', 'Georgia', 'French Guiana', 'Ghana', 'Greenland', 'Gambia', 'Guinea',
    'Equatorial Guinea', 'Greece', 'Guatemala', 'Guinea-Bissau', 'Guyana', 'Honduras', 'Croatia',
    'Haiti', 'Hungary', 'Indonesia', 'Ireland', 'Israel', 'India', 'Iraq', 'Islamic Republic of Iran',
    'Iceland', 'Italy', 'Jamaica', 'Jordan', 'Japan', 'Kenya', 'Kyrgyzstan', 'Cambodia',
    'Democratic People\u2019s Republic of Korea', 'Republic of Korea', 'Kuwait', 'Kazakhstan',
    'Lao People\u2019s Democratic Republic', 'Lebanon', 'Sri Lanka', 'Liberia', 'Lesotho', 'Lithuania',
    'Luxembourg', 'Latvia', 'Libyan Arab Jamahiriya', 'Morocco', 'Republic of Moldova', 'Madagascar',
    'The Former Yugoslav Republic of Macedonia', 'Mali', 'Myanmar', 'Mongolia', 'Mauritania', 'Malawi',
    'Mexico', 'Malaysia', 'Mozambique', 'Namibia', 'New Caledonia', 'Niger', 'Nigeria', 'Nicaragua',
    'Netherlands', 'Norway', 'Nepal', 'New Zealand', 'Oman', 'Panama', 'Peru', 'Papua New Guinea',
    'Philippines', 'Pakistan', 'Poland', 'Puerto Rico', 'Occupied Palestinian Territory', 'Portugal',
    'Paraguay', 'Qatar', 'Romania', 'Serbia', 'Russian Federation', 'Rwanda', 'Saudi Arabia',
    'Solomon Islands', 'Sudan', 'Sweden', 'Svalbard and Jan Mayen', 'Slovakia', 'Sierra Leone',
    'Senegal', 'Somalia', 'Suriname', 'El Salvador', 'Syrian Arab Republic', 'Swaziland', 'Chad',
    'Togo', 'Thailand', 'Tajikistan', 'Timor-Leste', 'Turkmenistan', 'Tunisia', 'Turkey',
    'Province of China Taiwan', 'United Republic of Tanzania', 'Ukraine', 'Uganda', 'United States',
    'Uruguay', 'Uzbekistan', 'Bolivarian Republic of Venezuela', 'Viet Nam', 'Vanuatu', 'Yemen',
    'South Africa', 'Zambia', 'Zimbabwe']


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


class TornadoDataRequest(httpclient.HTTPRequest):
    def __init__(self, url, **kwargs):
        super(TornadoDataRequest, self).__init__(url, **kwargs)
        self.method = "GET"
        self.auth_username = options.username
        self.auth_password = options.password
        self.user_agent = "Tornado-data"


class ChinaMapHandler(ApiHandler):
    @asynchronous
    @gen.coroutine
    def post(self):
        china_map = {}
        for city in city_list:
            china_map[city] = {"score": 0, "stateInitColor": 6}

        for user in workers.github_china:
            try:
                location = user["location"].lower()
            except Exception, e:
                options.logger.error("location error: %s" % e)
                continue
            for city in city_list:
                if "hangzhou" in location:
                    china_map["zhejiang"]["score"] += 1
                    break
                if "harbin" in location:
                    china_map['heilongjiang']["score"] += 1
                    break
                if city in location:
                    china_map[city]['score'] += 1
                    break

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

        self.write(json.dumps(china_map, indent=4, separators=(',', ': ')))

                
class WorldMapHandler(ApiHandler):
    @asynchronous
    @gen.coroutine
    def post(self):
        world_map = {}
        for country in country_list:
            world_map[country] = {"score": 0, "stateInitColor": 6}
        for user in workers.github_world:
            try:
                location = user["location"].lower()
            except Exception, e:
                options.logger.error("location error: %s" % e)
                continue
            for country in country_list:
                if country in location:
                    world_map[country]["score"] += 1
                    break
        top_score = max([world_map[country]["score"] for country in world_map])
        capture = top_score / 6
        if capture == 0:
            capture = 1
        for country in world_map:
            world_map[country]["stateInitColor"] = 6 - world_map[country]["score"] / capture
        
        self.write(json.dumps(world_map, indent=4, separators=(',', ': ')))


class GithubChinaHandler(ApiHandler):
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
        

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'template'),
    "debug": False
}

handlers = [
    (r"/", MainHandler),
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

if __name__ == "__main__":
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
