#coding:utf-8

from pabo.main import g


__doc__ = 'url中有-的为ajax请求; 以.json结尾的url说明此请求要求返回json格式'
__all__ = ['urls']


a = g.admin_url
c = '/cron'
urls = [
    # 普通用户可访问到的网址
    # 导航
    (r'/', 'Home'),
    (r'/page/(\d+)', 'Home'),
    (r'/archives', 'Archives'),
    (r'/messages', 'GuestMessage'),
    (r'/rss', 'Rss'),
    #(r'/about', 'About'),
    (g.login_url, 'Login'),
    (r'/logout', 'Logout'),
    # 某个文章
    (r'/article/(admin/\d+)', 'Article'),
    (r'/article/([0-9a-z]{5,})', 'Article'),
    # 显示某个图片
    (r'/img(?:/(\d+)x(\d+))?/(\w{32}\.(?:png|bmp|jpg|gif))', 'Image'),
    # 归档
    (r'/archives/([1-9a-zA-Z])/page/(\d+)', 'Archives'),

    # cron
    # 备份kvdb到storage中
    (c + r'/kvdbbackup', 'CronKvdbBackup'),

    # admin可访问的网址(为每个网址加上前缀)
    # 导航
    (a + r'/stats', 'Stats'),
    (a + r'/classes', 'Classes'),
    (a + r'/article/add', 'AddArticle'),
    (a + r'/articles/manage', 'Articles'),
    (a + r'/attachments', 'Attachments'),
    (a + r'/friends', 'Friends'),
    (a + r'/settings', 'Settings'),
    #(a + r'/me', 'Me'),
    # 编辑器
    (a + r'/editor', 'Editor'),
    # 修改文章
    (a + r'/edit/article/(\d+)', 'EditArticle'),
    # 分类
    (a + r'\.(add|rename|del)\.cls\.json', 'Classes'),
    (a + r'\.get\.select\.classes\.json', 'GetSelectClasses'),
    (a + r'\.get\.classes\.json', 'Classes'),
    # 文章
    (a + r'\.(add|mod|del)\.article\.json', 'Articles'),
    # 文章列表
    (a + r'\.get\.articles\.page\.(\d+)', 'Articles'),
    # 刷新文章列表中的某个文章
    (a + r'\.get\.article\.box\.(\d+)', 'RefreshArticle'),
    # 友链
    (a + r'\.(add|mod|del)\.link\.json', 'Friends'),
    # 图片
    (a + r'\.upload\.img\.json', 'UploadImage'),  # 上传图片
    # 批量获取图片
    (a + r'\.get\.imgs\.marker\.(\w{32}\.(?:png|gif|bmp|jpg))', 'Attachments'),
    (a + r'\.del\.img', 'DelImage'),  # 删除图片
    # kvdb管理界面
    (a + r'/kv', 'KvManager'),
    (a + r'\.kv\.(searchprefix|del|mod|clear)\.json', 'KvManager'),
    # 后台
    (a + r'\.mod\.(admin|site)\.info\.json', 'Settings'),
]
