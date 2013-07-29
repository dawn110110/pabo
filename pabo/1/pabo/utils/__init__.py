#coding:utf-8


def md5(s):
    import hashlib
    return hashlib.md5(s).hexdigest()


def now():
    '''得到当前日期时间的字符串'''
    import datetime
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def now_time_str():
    import time
    return str(int(time.time()))


def iter_callback(it, callback):
    '''为gen.Task时使用迭代器时的异步方法'''
    try:
        value = it.next()
    except StopIteration:
        value = None
    callback(value)


class ObjectDict(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return

    def __setattr__(self, name, value):
        self[name] = value


def is_img(ct):
    '''判断一个给定的content_type是不是图片(bmp, jpg, png, gif)'''
    return ct.lower() in ['image/png', 'image/bmp', 'image/jpeg', 'image/gif']


def is_img_by_ext(filename):
    return filename.lower().rsplit('.', 1)[1] in ['png', 'bmp', 'jpg', 'gif']


def guid():
    '''生成一个uuid的字符串'''
    import uuid
    return uuid.uuid4().hex


def md2html(md):
    '''markdown to html'''
    import re
    from pabo.libs import markdown2
    md = re.sub(r'(```\r\n[^`]*?\r\n```)', r'\r\n\r\n\1\r\n', md)
    return markdown2.markdown(md, True,
            extras={'fenced-code-blocks': None,
                'html-classes': {'code': 'prettyprint'}})


def resize_img(img_data, w, h, ext=None):
    ext = ext.replace('jpg', 'jpeg')
    try:
        import Image  # 本地
    except ImportError:
        from PIL import Image  # SAE
    import StringIO
    img = Image.open(StringIO.StringIO(img_data))
    img = img.resize((w, h), Image.ANTIALIAS)  # 滤镜输出，不然缩放质量很差
    f = StringIO.StringIO()
    img.save(f, ext)
    return f.getvalue()


def rss_gen(title, host, description, articles):
    '''生成rss'''
    import datetime
    from pabo.libs import PyRSS2Gen

    items = []
    for article in articles:
        item = PyRSS2Gen.RSSItem(
            title=article['meta']['title'],
            link=host + '/article/' + article['url'],
            description=article['abs'],
            #guid=article['url'],
            pubDate=article['meta']['datetime'])
        items.append(item)

    rss = PyRSS2Gen.RSS2(
            title=title,
            link=host + '/rss',
            description=description,
            items=items,
            lastBuildDate=datetime.datetime.now())
    return rss.to_xml(encoding='utf-8')
