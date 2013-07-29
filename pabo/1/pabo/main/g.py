# coding:utf-8

import os.path as osp

import pabo.main.settings as settings
from pabo.utils import template, crypto
from sae.kvdb import KVClient


__all__ = ['kv', 'render', 'cryptor', 'site_info', 'login_url']


kv = KVClient()

# 加密解密
cryptor = crypto.SimpleCrypto(settings.COOKIE_SECRET)
# 网站信息
site_info = lambda: kv.get(settings.K_SITE_INFO)
_site_info = site_info()
_theme = _site_info.get('theme', 'default')
_admin = _site_info.get('admin_theme', 'default')
admin_url = _site_info['admin']['url']
login_url = _site_info['login_url']


# jinja2
_extra = dict(
    site_info=site_info,
    settings=settings,
)
if settings.DEBUG:
    _extra.update(__builtins__)
render = template.PaboBlogRender(
    template_path=[
        osp.join(settings.TEMPLATE_DIR, 'normal', _theme),  # 普通模板
        osp.join(settings.TEMPLATE_DIR, 'admin', _admin)  # admin后台管理模板
    ],
    trim_blocks=True,
    auto_reload=settings.DEBUG,
    extra=_extra,
    extensions=['jinja2.ext.do'],
)
