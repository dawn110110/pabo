pabo
====


一个基于SAE的博客程序，使用tornado构建，数据完全使用SAE的KVDB进行存储。

启用SAE上面的kvdb后上传代码即可使用。


### 附加说明

* 前端使用html5, css3，bootstrap，jquery以及jquery-ui构建

* 后台使用Python 2.7及tornado 2.1.1构建

* 响应式布局

* 支持自定义主题，默认主题简洁轻快

* localStorage进行页面间数据共享


### 支持的功能有

* 文章分类归档

* 留言和文章评论(尚未完成)

* rss订阅

* 后台管理


其中`后台管理`包括博客`数据概览`、`文章管理`、`分类管理`、`附件管理`、`友链管理`、`站点信息设置`以及KVDB管理。


[前往DEMO站点](http://pabo.sinaapp.com/ ), 后台登录密码@a123456


以下是博客预览图及相关说明：

**后台管理概览**

![](https://github.com/Shu-Ji/pabo/raw/master/docs/imgs/stats.png )

**发表文章**

支持拖拽上传图片。

文章使用markdown书写。带有实时预览功能的markdown全屏编辑器。

![](https://github.com/Shu-Ji/pabo/raw/master/docs/imgs/add.png )

**分类管理**

添加与查看分类情况，在此页面添加分类后，在其他页面能够自动侦测到分类的变化，并自动根据变化后的分类情况进行相应处理。

![](https://github.com/Shu-Ji/pabo/raw/master/docs/imgs/cls.png )

**附件管理**

在这里管理所有上传的图片，复制图片网址，删除图片等。

![](https://github.com/Shu-Ji/pabo/raw/master/docs/imgs/atta.png )

**文章管理**

管理所有已经发布的文章，在这里显示文章标题，所属分类，发表时间，以及文章摘要。

![](https://github.com/Shu-Ji/pabo/raw/master/docs/imgs/manage.png )

**友链管理**

添加删除友链，支持预览友链。

![](https://github.com/Shu-Ji/pabo/raw/master/docs/imgs/friends.png )

**站点信息设置**

![](https://github.com/Shu-Ji/pabo/raw/master/docs/imgs/settings.png )

**响应式设计**

![](https://github.com/Shu-Ji/pabo/raw/master/docs/imgs/resp.png )

**博客首页**

![](https://github.com/Shu-Ji/pabo/raw/master/docs/imgs/home.png )

**归档**

![](https://github.com/Shu-Ji/pabo/raw/master/docs/imgs/archives.png )

**分类归档**

![](https://github.com/Shu-Ji/pabo/raw/master/docs/imgs/abs-archives.png )

**rss订阅**

![](https://github.com/Shu-Ji/pabo/raw/master/docs/imgs/rss.png )
