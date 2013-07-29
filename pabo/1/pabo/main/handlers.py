# coding:utf-8

import logging
import json

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.web import authenticated

from pabo.main import settings, g, urls, ctrl
import pabo.utils as utils


class BaseHandler(tornado.web.RequestHandler):
    def render(self, path, **kwargs):
        g.render.render(self, path, **kwargs)

    def macro(self, path):
        return g.render.macro(path)

    def get_current_user(self):
        return self.get_secure_cookie(
            settings.COOKIE_INFO, {}).get('loggedin', None)

    def set_secure_cookie(self, name, value, expires_days=30, **kwargs):
        if name.endswith('.j'):
            value = json.dumps(value)
        if value is not None:
            value = g.cryptor.encrypt(value)
        self.parent.set_secure_cookie(name, value, expires_days, **kwargs)

    def get_secure_cookie(self, name, default=None, value=None, max_days=31):
        value = self.parent.get_secure_cookie(name, value, max_days)
        if value is not None:
            value = g.cryptor.decrypt(value)
            if name.endswith('.j'):
                value = json.loads(value)
        return value if value is not None else default

    def input(self, name, default=None, strip=True):
        return self.parent.get_argument(name, default, strip)

    @property
    def parent(self):
        return super(BaseHandler, self)

    def prepare(self):
        # 禁止别人用iframe包含本站的内容
        self.set_header('X-Frame-Options', 'SAMEORIGIN')

        # 下面的应该写在on_finish方法中
        # 但是sae上面的tornado2.1.1没有on_finish方法,只能写在prepare中了
        if settings.DEBUG:
            # kvdb本地客户端不能实时保存文件, _save()方法是修改了kvdb.py源码后
            # 的函数,将libs/kvdb.py(此文件可删除)中的_save()函数复制到sae的
            # kvdb.py中即可
            try:
                import sae.kvdb
                sae.kvdb._save()
            except AttributeError:
                pass


class Editor(BaseHandler):
    @authenticated
    def get(self):
        self.render('admin_editor.html')


class GetSelectClasses(BaseHandler):
    '''获取所有分类组成的select控件html代码(用于发表文章页面,添加分类后刷新)'''
    @authenticated
    def get(self):
        self.write(self.macro('admin_widgets.html').classes_select(
            ctrl.get_all_classes(), ajax=True))


class CronKvdbBackup(BaseHandler):
    '''kvdb备份'''
    def get(self):
        ctrl.save_kvdb_2_storage()


class Home(BaseHandler):
    def get(self, page_num=None):
        app = g.kv.get(settings.K_SITE_INFO)['app']
        if page_num is None:
            page_num = 1
        page_num = int(page_num)
        offset = (page_num - 1) * app
        self.render('home.html',
                articles=ctrl.get_all_articles(offset=offset, limit=app),
                page_num=page_num, app=app)


class Rss(BaseHandler):
    '''rss/sitemap'''
    def get(self):
        info = g.site_info()
        need_abs = not info['rss_full']
        rss = utils.rss_gen(
                title=info['title'],
                host=self.request.protocol + '://' + self.request.host,
                description=info['description'],
                articles=ctrl.get_all_articles(limit=50, need_abs=need_abs))
        self.set_header('Content-Type', 'text/xml')
        self.write(rss)


class Archives(BaseHandler):
    '''文章归档(以分类归档)'''
    def get(self, cid=None, page_num=None):
        if cid is None:
            # 归档首页
            self.render('archives.html', classes=ctrl.get_all_classes())
        else:
            app = g.kv.get(settings.K_SITE_INFO)['app']
            if page_num is None:
                page_num = 1
            page_num = int(page_num)
            offset = (page_num - 1) * app
            self.render('archives.html',
                    articles=ctrl.get_all_articles(
                        offset=offset, limit=app, need_abs=True, cid=cid),
                    page_num=page_num, app=app, cid=cid)


class Login(BaseHandler):
    def get(self):
        if self.current_user:
            self.redirect(g.admin_url)
        else:
            self.render('login.html', action=g.login_url)

    def post(self):
        next_page = g.login_url
        admin = g.kv.get(settings.K_ADMIN_INFO)
        if admin is not None:
            name = self.input('username', '')
            pwd = self.input('password', '', strip=False)
            pwd = utils.md5(pwd + settings.COOKIE_SECRET)
            if admin['name'] == name and pwd == admin['pwd']:
                # 登录成功，设置cookie
                cookie = self.get_secure_cookie(settings.COOKIE_INFO, {})
                cookie['loggedin'] = True
                self.set_secure_cookie(
                    settings.COOKIE_INFO, cookie, settings.COOKIE_INFO_TIMEOUT)
                next_page = g.site_info()['admin']['default']
        self.redirect(next_page)


class Stats(BaseHandler):
    '''后台统计信息'''
    @authenticated
    def get(self):
        self.render('admin_stats.html', articles_cnt=ctrl.get_articles_count())


class Classes(BaseHandler):
    '''后台分类管理'''
    @authenticated
    def get(self):
        if self.request.path.endswith('.json'):
            self.write(self.macro('admin_widgets.html').classes_table(
                ctrl.get_all_classes(), ajax=True))
        else:
            self.render('admin_classes.html', classes=ctrl.get_all_classes())

    @authenticated
    def post(self, op=None):
        ret = ctrl._od()
        if op == 'add':
            cls = self.input('cls')
            if not cls:
                ret.msg = u'请输入分类名称'
            else:
                ret = ctrl.add_cls(cls)
        elif op == 'rename':
            cid = self.input('id')
            if cid == settings.DEFAULT_CLS:
                ret.msg = u'不能修改默认分类'
            else:
                new_name = self.input('new')
                ret = ctrl.rename_cls(cid, new_name)
        elif op == 'del':
            cid = self.input('id')
            if cid == settings.DEFAULT_CLS:
                ret.msg = u'不能删除默认分类'
            else:
                ret = ctrl.del_cls(cid)
        self.write(ret)


class AddArticle(BaseHandler):
    '''发表文章'''
    @authenticated
    def get(self):
        self.render('admin_add_article.html', classes=ctrl.get_all_classes())


class Articles(BaseHandler):
    '''后台文章管理'''
    @authenticated
    def get(self, page_num=None):
        app = g.kv.get(settings.K_SITE_INFO)['app']
        total_num=(ctrl.get_articles_count() - 1) / app + 1
        if page_num is None:
            self.render('admin_manage_articles.html',
                    cur_num=1,
                    total_num=total_num,
                    articles=ctrl.get_all_articles(need_abs=True))
        else:
            self.write(self.macro('admin_widgets.html').manage_articles(
                    ctrl.get_all_articles(
                        (int(page_num) - 1) * app, need_abs=True),
                    page_num, total_num))

    @authenticated
    def post(self, op):
        ret = ctrl._od()
        if op in ['add', 'mod']:
            title = self.input('title')
            md = self.input('md')
            cid = self.input('cls')
            if not all((title, md, cid)):
                ret.msg = u'标题、内容以及分类均不能为空'
            elif op == 'add':
                ret = ctrl.add_article(title, md, cid)
            else:
                aid = self.input('id')
                ret = ctrl.mod_article(title, md, cid, aid)
        elif op == 'del':
            ret = ctrl.del_article(self.input('id'))
        self.write(ret)


class RefreshArticle(BaseHandler):
    '''后台文章管理'''
    @authenticated
    def get(self, aid):
        self.write(self.macro('admin_widgets.html').box(
            ctrl.get_article(aid, need_abs=True), ajax=True))


class Friends(BaseHandler):
    ''''友链'''
    @authenticated
    def get(self):
        self.render('admin_friends.html')

    @authenticated
    def post(self, op):
        ret = ctrl._od()
        if op == 'mod':
            raw = self.input('raw')
            link = self.input('link')
            name = self.input('name')
            if not all((name, link, raw)):
                ret.msg = u'友链标题和链接不能为空'
            else:
                #ret = ctrl.mod_friends_links(raw, link, name)
                ret = ctrl.manage_links(op, link, name, raw)
        elif op == 'del':
            #ret = ctrl.del_friend_link(self.input('link'))
            ret = ctrl.manage_links(op, raw=self.input('raw'))
        elif op == 'add':
            link = self.input('link')
            name = self.input('name')
            if not all((name, link)):
                ret.msg = u'友链标题和链接不能为空'
            else:
                #ret = ctrl.add_friend_link(link, name)
                ret = ctrl.manage_links(op, link, name)
        self.write(ret)


class EditArticle(BaseHandler):
    '''修改文章'''
    @authenticated
    def get(self, aid):
        article = ctrl.get_article(aid, need_md=True)
        if article is None:
            self.redirect('/404')
        else:
            self.render('admin_editor.html', article=article,
                    classes=ctrl.get_all_classes())


class KvManager(BaseHandler):
    '''kvdb管理界面'''
    @authenticated
    def get(self):
        self.render('admin_kv.html', info=g.kv.get_info())

    @authenticated
    def post(self, op):
        if op == 'searchprefix':
            q = self.input('prefix', '')
            self.write({'data': ctrl.kv_search_prefix(q)})
        elif op == 'del':
            pass
        elif op == 'mod':
            pass
        elif op == 'clear':
            pass


class Attachments(BaseHandler):
    '''附件(图片)管理'''
    @authenticated
    def get(self, offset=None):
        if offset is None:
            self.render('admin_attachments.html',
                    imgs=ctrl.get_imgs())
        else:
            self.write(self.macro('admin_widgets.html').imgs_wall(
                ctrl.get_imgs(offset=offset), ajax=True).strip())


class Image(BaseHandler):
    '''取某个图片'''
    def get(self, w=None, h=None, key=None):
        import datetime
        ct = key.rsplit('.', 1)[1].replace('jpg', 'jpeg')
        self.set_header('Last-Modified', datetime.datetime(2013, 1, 1))
        cache_time = 86400 * 365 * 10
        self.set_header('Expires', datetime.datetime.now() +\
                datetime.timedelta(seconds=cache_time))
        self.set_header('Cache-Control', 'max-age=' + str(cache_time))
        self.set_header('Content-Type', 'image/%s' % ct)
        if self.request.headers.get('If-Modified-Since') is not None:
            self.set_status(304)
        else:
            if w is None:
                key = settings.K_IMG % key
            else:
                key = settings.K_IMG_WXH % (w, h, key)
            img_data = g.kv.get(str(key)) or utils.guid()
            self.write(img_data)


class Settings(BaseHandler):
    '''后台设置'''
    @authenticated
    def get(self):
        import glob
        import os.path as osp

        def _(admin_or_normal):
            _dir = osp.join(settings.TEMPLATE_DIR, admin_or_normal)
            _themes = glob.glob(osp.join(_dir, '*'))
            l = len(_dir)
            names = map(lambda p: p[l:].strip('/'), _themes)
            return dict(zip(names, names))

        links = {}
        for nav in g.kv.get(settings.K_SITE_INFO)['admin']['navs']:
            if 'sub' in nav:
                for sub in nav['sub']:
                    links[sub['link']] = sub['label']
            else:
                links[nav['link']] = nav['label']

        self.render('admin_settings.html',
                get=g.kv.get, themes=_('normal'), admin_themes=_('admin'),
                links=links)

    @authenticated
    def post(self, op):
        '''更改设置'''
        ret = ctrl._od()
        if op == 'admin':
            name = self.input('name')
            pwd = self.input('pwd', strip=False)
            confirm = self.input('confirm', strip=False)
            email = self.input('email')
            if not all((name, pwd, email)):
                ret.msg = u'请填写所有字段'
            elif pwd != confirm:
                ret.msg = u'两次密码不一致'
            else:
                ret = ctrl.mod_admin_info(name, pwd, email)
        elif op == 'site':
            _yesno = {'on': True, 'off': False}
            login_url = self.input('login_url', g.login_url)
            title = self.input('title', 'Pabo Blog')
            subtitle = self.input('subtitle', '')
            kw = self.input('kw', '')
            desc = self.input('desc', '')
            theme = self.input('theme', 'default')
            admin_theme = self.input('admin_theme', 'default')
            author_name = self.input('author_name', 'author')
            author_intro = self.input('author_intro', '')
            app = self.input('app', g.kv.get(settings.K_SITE_INFO)['app'])
            links_preview = _yesno[self.input('links_preview', 'off')]
            show_login = _yesno[self.input('show_login', 'off')]
            rss_full = _yesno[self.input('rss_full', 'off')]
            baidu_statistics = self.input('baidu_statistics', '')
            default_page = self.input('default_page', '/admin/stats')
            try:
                app = int(app)
                if not 5 <= app <= 20:
                    raise KeyError
            except KeyError:
                ret.msg = u'每页显示文章数量必须是一个5~20间的数字'
            else:
                if not login_url.startswith('/'):
                    ret.msg = u'登录网址必须以/开头'
                else:
                    ret = ctrl.mod_site_info(**locals())
        self.write(ret)


class Article(BaseHandler):
    '''查看某个文章'''
    def get(self, url):
        if url.startswith('admin/'):
            # 后台管理员管理文章页面的网址是直接用的aid
            aid = url.split('/')[1]
        else:
            import pabo.utils.tinyurl as tinyurl
            try:
                aid = tinyurl.decode_url(url)
            except ValueError:
                self.redirect('/404')
                return
        article = ctrl.get_article(aid, need_abs=False)
        if article is None:
            self.redirect('/404')
        else:
            self.render('article.html', article=article)


class DelImage(BaseHandler):
    '''删除某个图片'''
    @authenticated
    def post(self):
        key = self.input('key', '')
        if len(key) < 32:
            return
        ctrl.del_img(key)


class UploadImage(BaseHandler):
    '''上传图片'''
    @authenticated
    def post(self):
        myfile = self.request.files['pic'][0]
        if not utils.is_img_by_ext(myfile.filename):
            self.write(ctrl._od(msg=u'只能上传bmp、jpg、gif以及png格式的图片'))
        else:
            self.write(ctrl.save_img_by_ext(myfile))


class Logout(BaseHandler):
    @authenticated
    def get(self):
        self.clear_cookie(settings.COOKIE_INFO)
        self.redirect('/')


class Application(tornado.web.Application):
    def __init__(self):
        us = []
        env = globals()
        for route in urls.urls:
            if len(route) > 2:
                continue
            url, handler_name = route
            handler = env.get(handler_name, None)
            if handler is not None:
                us.append((url, handler))
            else:
                logging.warning('`{0}` not found'.format(handler_name))
        tornado.web.Application.__init__(self, us, **settings.TORNADO_SETTINGS)


application = Application()
