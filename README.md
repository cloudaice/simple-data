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
因此followers排名进不了前1000，根本不会进入到score计算阶段，
设计这样的计算公式的原因是考虑到followers在前期的增长含金量比较高，
而之后的增加主要是影响力因素，因此，如果你在github初露锋芒，
那么folloers的增加会导致score疯狂上涨。


地名匹配
--------

这是一个比较头痛的事情，也是花费时间最长的步骤。因为每个用户的地名都不一定提到关键省份，
例如在`hangzhou`的用户就习惯直接写`hangzhou`，而不会提及`zhejiang`。
因此这里需要能够模糊匹配的库。
后来在`http://www.geonames.org/`上找到开放接口，通过查询API可以得到简单的模糊匹配结果。
然后在内存中建立缓存，将匹配成功的地名分别update到Github的`gists`文件夹中。

+ [china_location_map](https://gist.github.com/cloudaice/5677947) 
+ [world_location_map](https://gist.github.com/cloudaice/5681176)


匹配不到的再通过手动添加映射。


运行
---

clone该项目，在项目的根目录下创建config.py文件，编辑内容如下:

    from tornado.options import define

    define("username", "your-github-username")
    define("password", "your-github-password")

在根目录下执行 `python app.py`，然后访问浏览器`localhost:8000`


TODO
----

+ ~~完善Github用户所在地分析~~ (#已完成)

+ ~~增加世界范围内用户分布地图~~ (#已完成)

+ 点击地图某一块区域显示该区域的成员列表

+ 迁移到openshift平台



Demo
--------

+ 中国用户分布图

![Github-china](http://cloudaice.com/images/Github-china.png)



+ 世界用户分布图

![Github-world](http://cloudaice.com/images/Github-world.png)


+ 应用地址

[data.cloudaice.com](http://data.cloudaice.com)。


**注**: 由于heroku不支持websocket，因此在线服务版本为ajax轮询版本。
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
