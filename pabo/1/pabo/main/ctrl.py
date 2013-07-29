# coding: utf-8

from pabo.main import settings, g
from pabo.utils import ObjectDict
import pabo.utils as utils


kv = g.kv


###########################################################################
#                                  辅助函数                               #
###########################################################################


def _check_kvdb_error(od, **kwargs):
    '''检查是否kvdb出错'''
    if od.err:
        od.msg = u'数据库(KVDB)错误，请稍后再试。'
    else:
        od.pop('msg')
        od.update(kwargs)
    return od


def _od(err=True, msg=''):
    return ObjectDict(err=err, msg=msg)


###########################################################################
#                                   分类管理                              #
###########################################################################


def _cls_exists(name, default=None):
    '''判断是否已经存在某个分类'''
    values = (default or kv.get(settings.K_ART_CLS) or '').itervalues()
    return u'分类[ %s ]已存在.' % name if name in values else False


def add_cls(name):
    '''添加分类'''
    import string

    ret = _od()
    default = kv.get(settings.K_ART_CLS)
    table = set(
            (string.digits + string.letters).replace(settings.DEL_INDEX, '')
            )  # 除去0

    exists = set(default.iterkeys())
    rest = table - exists

    if not rest:
        ret.msg = u'分类个数已经达到上限, 添加失败。'
    else:
        exists = _cls_exists(name, default)
        if exists:
            ret.msg = exists
        else:
            cid = rest.pop()
            default[cid] = name
            ret.err = not kv.set(settings.K_ART_CLS, default)
            _check_kvdb_error(ret, cid=cid)
    return ret


def get_all_classes():
    '''查询所有分类'''
    counter = get_all_classes_count()
    for cid, name in kv.get(settings.K_ART_CLS).iteritems():
        yield {'cid': cid, 'name': name, 'num': counter[cid]}


def get_all_classes_count():
    '''得到每个分类下有多少文章'''
    from collections import Counter
    arts = kv.get(settings.K_ARTS) or ''
    return Counter(arts)


def del_cls(cid):
    '''删除分类'''
    ret = _od()
    default = kv.get(settings.K_ART_CLS)
    if default.pop(cid, None) is not None:
        ret.err = not kv.set(settings.K_ART_CLS, default)
        _check_kvdb_error(ret)
        # 将所有属于此分类的文章自动归类到'默认分类'中去
        arts = kv.get(settings.K_ARTS) or ''
        arts = arts.replace(cid, settings.DEFAULT_CLS)
        kv.set(settings.K_ARTS, arts)
    return ret


def rename_cls(cid, new_name):
    '''重命名分类'''
    ret = _od()
    default = kv.get(settings.K_ART_CLS)
    exists = _cls_exists(new_name, default)
    if exists:
        ret.msg = exists
    else:
        default[cid] = new_name
        ret.err = not kv.set(settings.K_ART_CLS, default)
        _check_kvdb_error(ret)
    return ret


###########################################################################
#                                  图片管理                               #
###########################################################################


def save_img_by_ext(myfile):
    '''保存上传的图片到kvdb中'''
    ret = _od()
    ct, img_binary = myfile.filename.lower().rsplit('.', 1)[1], myfile.body
    if len(img_binary) > settings.KVDB_FILE_MAX_SIZE:
        ret.msg = u'图片大小不能超过4M'
        return ret
    url = str('%s.%s' % (utils.md5(img_binary), ct))
    ret.err = not kv.set(settings.K_IMG % url, img_binary)

    # 生成160 ｘ 120大小的图片,后台图片管理预览用
    img_160x120 = utils.resize_img(img_binary, 160, 120, ct)
    kv.set(settings.K_IMG_160X120 % url, img_160x120)

    return _check_kvdb_error(ret, url='/img/%s' % url)


def get_imgs(offset=None, limit=6):
    '''返回所有的图片'''
    if offset is not None:
        offset = settings.K_IMG % offset
    prefix = settings.K_IMG.replace('%s', '')
    l = len(prefix)
    ret = []
    for k in kv.getkeys_by_prefix(prefix, limit=limit, marker=offset):
        ret.append(k[l:])
    return ret


def del_img(key):
    '''删除图片'''
    key = str(key)
    kv.delete(settings.K_IMG % key)
    kv.delete(settings.K_IMG_160X120 % key)


###########################################################################
#                                  文章管理                               #
###########################################################################


def _get_abstract(md):
    '''从markdown中提取出摘要'''
    idx = md.find('<!--more-->')
    abs = (md if idx == -1 else md[:idx]).strip()
    return utils.md2html(abs)


def add_article(title, md, cid):
    '''添加文章'''
    arts = kv.get(settings.K_ARTS) or ''
    aid = len(arts)
    kv.set(settings.K_ARTS, arts + cid)
    kv.set(settings.K_ART_MD % aid, md)
    kv.set(settings.K_ART_HTML % aid, utils.md2html(md))
    meta = {'datetime': utils.now(), 'title': title}
    kv.set(settings.K_ART_META % aid, meta)
    kv.set(settings.K_ART_ABS % aid, _get_abstract(md))
    return ''


def mod_article(title, md, cid, aid):
    '''修改文章'''
    aid = int(aid)
    arts = kv.get(settings.K_ARTS)
    arts = list(arts)
    arts[aid] = cid
    arts = ''.join(arts)
    kv.set(settings.K_ARTS, arts)
    kv.set(settings.K_ART_MD % aid, md)
    kv.set(settings.K_ART_HTML % aid, utils.md2html(md))
    meta = kv.get(settings.K_ART_META % aid)
    meta['title'] = title
    kv.set(settings.K_ART_META % aid, meta)
    kv.set(settings.K_ART_ABS % aid, _get_abstract(md))
    return ''


def get_all_articles(offset=0, limit=10, need_abs=False, need_md=False,
        cid=None):
    '''获取所有的文章列表, need_abs是否需要返回文章摘要, need_md是否返回md;
    如果给定了cid，那么只返回属于cid这个分类的文章
    '''
    arts = list(get_all_valid_aid(cid))[::-1][offset:]
    for aid in arts:
        article = get_article(aid, need_abs, need_md)
        if article is None:
            continue
        yield article
        # 如果limit为None，那么不限文章篇数(用于rss/sitemap中)
        if limit is not None:
            limit -= 1
            if limit == 0:
                break


def get_all_valid_aid(cid=None):
    '''将文章索引去除0，代表真实的文章索引'''
    arts = kv.get(settings.K_ARTS) or ''
    for aid, _cid in enumerate(arts):
        if cid is not None:
            if _cid == cid:
                yield aid
        elif _cid != settings.DEL_INDEX:
            yield aid


def get_articles_count():
    '''返回文章总数'''
    return len((kv.get(settings.K_ARTS) or '').replace(settings.DEL_INDEX, ''))


def del_article(aid):
    '''删除文章'''
    # 将文章索引分类标志置0,表示已删除
    aid = int(aid)
    arts = kv.get(settings.K_ARTS)
    arts = list(arts)
    arts[aid] = settings.DEL_INDEX
    arts = ''.join(arts)
    kv.set(settings.K_ARTS, arts)

    kv.delete(settings.K_ART_MD % aid)
    kv.delete(settings.K_ART_HTML % aid)
    kv.delete(settings.K_ART_META % aid)
    kv.delete(settings.K_ART_ABS % aid)

    return _od(err=False)


def get_article(aid, need_abs=True, need_md=False):
    '''返回一篇文章的数据'''
    aid = int(aid)
    arts = kv.get(settings.K_ARTS) or ''
    try:
        cid = arts[aid]
    except IndexError:
        return
    import pabo.utils.tinyurl as tinyurl
    try:
        url = tinyurl.encode_url(aid)
    except ValueError:
        return
    cls_name = kv.get(settings.K_ART_CLS)[cid]
    ret = {'meta': kv.get(settings.K_ART_META % aid),
            'aid': aid,
            'url': url,
            'cls_name': cls_name,
            'cid': cid,
            }
    need_html = True
    if need_abs:
        ret['abs'] = kv.get(settings.K_ART_ABS % aid)
        need_html = False
    if need_md:
        ret['md'] = kv.get(settings.K_ART_MD % aid)
        need_html = False
    if need_html:
        ret['html'] = kv.get(settings.K_ART_HTML % aid)
    return ret


###########################################################################
#                                  kvdb                                   #
###########################################################################


def kv_search_prefix(q, limit=100, marker=None):
    '''kvdb前缀搜索'''
    ret = []
    for k, v in kv.get_by_prefix(q, limit, marker):
        try:
            if isinstance(v, str):
                v.decode('u8')
        except UnicodeDecodeError:
            v = '[blob]'
        ret.append((k, v))
    return ret


def save_kvdb_2_storage():
    '''备份kvdb中的数据到storage'''
    return
    # TODO: 由于图片不能dumps,需要另行解决
    max_cnt = kv.get_info()['total_count']
    ret = {}
    for k, v in kv.get_by_prefix('', max_cnt):
        ret[k] = v
    import json
    ret = json.dumps(ret)
    # TODO 写进storage


###########################################################################
#                              友链管理                                   #
###########################################################################


def manage_links(op, link=None, name=None, raw=None):
    '''如果是del操作，那么执行pop;如果是add操作，那么添加即可;如果是mod操作，那
    么将旧的友链删除再添加新的友链(相当于先del再add)'''

    site_info = g.site_info()
    links = site_info['links']

    if op in ['del', 'mod']:
        links.pop(raw, None)
    # 不能把下面的if修改为elif
    if op in ['add', 'mod']:
        links[link] = name

    site_info['links'] = links
    kv.set(settings.K_SITE_INFO, site_info)
    return _od(err=False)


###########################################################################
#                                  后台管理                               #
###########################################################################


def mod_admin_info(name, pwd, email):
    '''修改管理员信息'''
    pwd = utils.md5(pwd + settings.COOKIE_SECRET)
    new = locals()
    info = kv.get(settings.K_ADMIN_INFO)
    info.update(new)
    kv.set(settings.K_ADMIN_INFO, info)
    return _od(err=False)


def mod_site_info(**kwargs):
    '''修改站点信息'''
    info = g.site_info()
    info['login_url'] = kwargs['login_url']
    info['title'] = kwargs['title']
    info['subtitle'] = kwargs['subtitle']
    info['keywords'] = kwargs['kw']
    info['description'] = kwargs['desc']
    info['theme'] = kwargs['theme']
    info['admin_theme'] = kwargs['admin_theme']
    info['author']['name'] = kwargs['author_name']
    info['author']['intro'] = kwargs['author_intro']
    info['app'] = kwargs['app']
    info['links_preview'] = kwargs['links_preview']
    info['show_login'] = kwargs['show_login']
    info['rss_full'] = kwargs['rss_full']
    info['baidu_statistics'] = kwargs['baidu_statistics']
    info['admin']['default'] = kwargs['default_page']
    kv.set(settings.K_SITE_INFO, info)
    return _od(err=False)
