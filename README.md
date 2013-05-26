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

    Formula = lambda x: 2 ** 10 / (1 + pow(exp(1), -(x - 2 ** 7) / 2 ** 5))

![formula](http://data.cloudaice.com/static/img/formula.jpg)


Score:

    Score = Formula(followers) + Contributions

首先抓取followers排名前1000的用户，然后再使用公式计算Score值。对folloers有一定依赖，
但主要看contributions。



TODO
----

+ 完善Github用户所在地分析

+ 增加世界范围内用户分布地图



应用地址
--------

[data.cloudaice.com](http://data.cloudaice.com)。


**注**: 如果打不开，请使用梯子。



更新日志
-------

####2013-05-25

+ 替换原来的ajax，使用websocket传输数据
+ 修改部分页面显示

####2013-05-26

+ 使用`geonames.org`进行模糊地名匹配
+ 修复没有`name`显示为空的bug
