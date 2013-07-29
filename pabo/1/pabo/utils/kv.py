# coding:utf-8

from json import dumps, loads

from sae.kvdb import KVClient as Kv


__all__ = ['Client']


class Client(object):
    u'''不能从KVClient继承，因为sae线上的kvdb需要分配server，而本地的不需要,
    继承之后，在__init__的参数server不能正确传入
    '''
    def __init__(self, json_k_suffix, autosave=False):
        self._suffix = json_k_suffix
        self._autosave = autosave
        self.kv = Kv()

    def _do(self, key, value, func):
        if self._autosave:
            # kvdb在dev_server源码里面reload的时候不会保存数据到磁盘造成丢失，
            # 这里在调试模式下解决，线上环境时可删除，以提高运行速率
            try:
                import sae.kvdb
                import os
                yes = os.environ.get('sae.run_main', '1')
                os.environ['sae.run_main'] = yes
                sae.kvdb._save_cache()
            except AttributeError:
                pass
        return value if not key.endswith(self._suffix) else func(value)

    def get(self, key, default=None):
        '''如果是json数据，那么返回解析为python对象后的数据'''
        if isinstance(key, unicode):
            key = key.encode('u8')
        value = self._do(key, self.kv.get(key), loads)
        return value if value is not None else default

    def set(self, key, value, min_compress_len=0):
        '''如果是json数据，那么先将python对象转换为json字符串'''
        if isinstance(key, unicode):
            key = key.encode('u8')
        value = self._do(key, value, dumps)
        return self.kv.set(key, value, min_compress_len)

    def add(self, key, value, min_compress_len=0):
        '''如果是json数据，那么先将python对象转换为json字符串'''
        if isinstance(key, unicode):
            key = key.encode('u8')
        value = self._do(key, value, dumps)
        return self.kv.add(key, value, min_compress_len)
