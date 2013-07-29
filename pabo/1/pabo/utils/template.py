# coding: utf-8


class Render(object):
    def __init__(self, template_path, **kw):
        from jinja2 import Environment, FileSystemLoader

        extra = kw.pop('extra', [])
        self._env = Environment(loader=FileSystemLoader(template_path), **kw)
        self._env.globals.update(extra)

    def render(self, handler, path, **kw):
        # 将tornado中的传递给模板的隐式参数'转移'到jinja2中
        args = dict(
            #handler=handler,
            request=handler.request,
            #locale=handler.locale,
            #_=handler.locale.translate,
            loggedin=handler.current_user,
            static_url=handler.static_url,
            normal_static=self.normal_static(handler),
            admin_static=self.admin_static(handler),
            #xsrf_form_html=handler.xsrf_form_html,
            #reverse_url=handler.application.reverse_url
        )
        kw.update(args)
        #kw.update(handler.ui)

        handler.write(self._env.get_template(path).render(**kw))

    def normal_static(self, handler):
        raise NotImplementedError

    def admin_static(self, handler):
        raise NotImplementedError

    def macro(self, path):
        return self._env.get_template(path).module


class PaboBlogRender(Render):
    def __init__(self, template_path, **kw):
        super(PaboBlogRender, self).__init__(template_path, **kw)
        site_info = self._env.globals['site_info']()
        self._theme = 'themes/normal/%s' % site_info['theme']
        self._admin = 'themes/admin/%s' % site_info['admin_theme']

    def normal_static(self, handler):
        return lambda p: handler.static_url('%s/%s' % (self._theme, p))

    def admin_static(self, handler):
        return lambda p: handler.static_url('%s/%s' % (self._admin, p))
