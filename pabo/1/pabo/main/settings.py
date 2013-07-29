# coding:utf-8

import os
import os.path as osp
import inspect

import pabo


DEBUG = 'SERVER_SOFTWARE' not in os.environ
DEBUG = True


if DEBUG:
    import logging
    logging.getLogger().setLevel(logging.DEBUG)


# 静态文件设置
PABO_PATH = osp.dirname(osp.abspath(inspect.getfile(pabo)))
STATIC_DIR = osp.join(PABO_PATH, 'static')
TEMPLATE_DIR = osp.join(PABO_PATH, 'templates')


# tornado设置
COOKIE_SECRET = 'debug' if DEBUG else 'cu)X\r >pL?NZ~R=<aH\x0cj1l[h(6龙卷风'
TORNADO_SETTINGS = {
    'autoescape': True,
    'cookie_secret': COOKIE_SECRET,
    'debug': DEBUG,
    'login_url': '/404',
    'static_path': STATIC_DIR,
    'static_url_prefix': '/assets/',
    #'xsrf_cookies': True,
}


# kvdb设置[所有值不要超过4M] .j结尾的说明是json字符串
K_ART_HTML = 'a:hm:%s'  # 文章内容的html
K_ART_MD = 'a:md:%s'  # 文章内容的markdown
K_ART_META = 'a:mt:%s'  # 文章的meta信息，如标题、发表日期等
# K_ART_EN_URL = 'a:en:%s'  # 文章的英文网址,值为文章id(a:en:i-am-url => 6)
# K_ART_PY_URL = 'a:py:%s'  # 文章的拼音网址,值为文章id(a:py:wo-shi-url => 6)
K_ART_ABS = 'a:abs:%s'  # 文章摘要的html

# 所有文章的分类信息:
#  {'分类id': '分类名称', ...}
K_ART_CLS = 'a:cls'

# 文章索引，这是一个只包含数字字母的字符串，第i个数据可通过`K_ART_MD % i`来取到
# 其md数据，K_ARTS值的长度为已发表文章的篇数，越往后说明文章越新.
# 如值为'0Z8i9K'说明共发了6篇文章，其中第0篇文章的已被删除，第1篇文章属于Z分类.
# 注1: 由于kvdb中值不能超过4M，所以能够保存4M篇文章.
# 注2: 每位的字母或数字代表此文章所属分类的id, 0代表此文章已经被删除,
# 故最多只能保存61个分类[1-9a-zA-Z]
K_ARTS = 'articles'

K_ADMIN_INFO = 'admin'  # 用户名和密码等信息
K_SITE_INFO = 'site:info'  # 网站信息，如标题，关键字，主题样式等
K_STATS_INFO = 'stats:info'  # 网站统计信息,如pv, ip计数等等

K_IMG = 'img:fs:%s'  # 图片fullsize原图大小
K_IMG_WXH = 'img:%sx%s:%s'  # 指定大小的图片
K_IMG_160X120 = K_IMG_WXH % (160, 120, '%s')  # 图片(160 x 120大小)

DEL_INDEX = '0'  # 索引中的'0'代表此文章已经删除
DEFAULT_CLS = '1'  # 默认分类的id为'1'


COOKIE_INFO = 'info.j'  # 存放用户是否已经登录等cookie信息
COOKIE_INFO_TIMEOUT = 20  # 过期时间天数


KVDB_FILE_MAX_SIZE = 4 * 1024 * 1024  # kvdb最大保存的数据大小


del inspect, osp, pabo
