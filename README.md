Make Data Simple Beautiful
==========================


Github用户活跃度排名
--------------------

+ 中国大陆地区Github用户活跃度排名

+ 世界Github用户排名

+ 中国大陆地区Github用户分布地图 



实现
----

+ Python Tornado 框架，利用gen模块的coroune异步抓取数据

+ 结合使用Github API 和网页抓取

+ 部署在heroku上



排名计算
-------

Formula:

    formula = lambda x: 2 ** 10 / (1 + pow(exp(1), -(x - 2 ** 7) / 2 ** 5))

![formula](http://data.cloudaice.com/static/img/formula.jpg)


Score:

    Score = Formula(followers) + Contributions

首先抓取followers排名前1000的用户，然后再使用公式计算Score值。对folloers有一定依赖，
主要看contributions。



TODO
----

+ 完善Github用户所在地分析

+ 增加世界范围内用户分布地图



应用网址
--------

[data.cloudaice.com](http://data.cloudaice.com)
