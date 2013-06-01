Make Data Simple Beautiful
==========================


Github用户活跃度排名
--------------------

+ 中国大陆地区Github用户分布地图 

+ 世界范围内的Github用户分布地图

+ 中国大陆地区Github用户活跃度排名

+ 世界范围内Github用户活跃度排名



实现
----

+ Python Tornado 框架，利用gen模块的coroune异步抓取数据

+ 使用`Github API`搜索followers前1000的用户, 结合网页抓取获取用户信息。

+ 部署在heroku上



排名计算
-------

Formula:

    Formula = lambda x: 2 ** 10 / (1 + pow(exp(1), -(x - 2 ** 7) / 2 ** 5))

![formula](http://data.cloudaice.com/static/img/formula.jpg)


Score:

    Score = Formula(followers) + Contributions

首先抓取followers排名前1000的用户，然后再使用公式计算Score值。
因此folloers排名进不了前1000，根本不会进入到score计算阶段，
之后主要看contributions。



TODO
----

+ 完善Github用户所在地分析 (#已完成)

+ 增加世界范围内用户分布地图 (#已完成)

+ 点击地图某一块区域显示该区域的成员列表



应用地址
--------

[data.cloudaice.com](http://data.cloudaice.com)。


**注**: 由于heroku不支持websocket，因此在线服务版本始终为websocket以前的版本。
目前在寻找免费的支持websocket的云平台。

另外如果网站打不开，请使用梯子。



更新日志
-------

####2013-05-25

+ 替换原来的ajax，使用websocket传输数据
+ 修改部分页面显示

####2013-05-26

+ 使用`geonames.org`进行模糊地名匹配
+ 修复没有`name`显示为空的bug

####2013-05-31

+ 增加了世界范围内的分布显示
+ 增加模糊匹配缓存文件
+ 修改默认china匹配到上海的bug
