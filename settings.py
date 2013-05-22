#-*-coding: utf-8 -*-
from tornado.options import define
import logging as logs


define("port", default=8000)

define("logger", logs.getLogger("Tornado-data"))

define("api_url", "https://api.github.com")

define("contribution_url",
       lambda user: "https://github.com/users/" + user + "/contributions_calendar_data")
