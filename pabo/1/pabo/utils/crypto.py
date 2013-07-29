# coding: u8


__all__ = ['SimpleCrypto']


class SimpleCrypto(object):
    u'''
    >>> key = '我是key'  # or key = u'我是key'
    >>> simple = SimpleCrypto(key)
    >>> text = u'你好，世界.'  # or text = '你好，世界.'
    >>> s1 = simple.encrypt(text)
    >>> s1
    '022c2803dcd884131402291e01ece945'
    >>> s2 = simple.decrypt(s1)
    >>> s2 == text
    True
    '''

    def __init__(self, key):
        '''key可以是任何字符串，也可以是中文'''
        if isinstance(key, unicode):
            key = key.encode('u8')
        # 将key的长度增加到30
        if len(key) < 30:
            _key, key, i, l = key, [], 30, len(key)
            while i:
                key.append(_key[i % l])
                i -= 1
            key = ''.join(key)

        self._key = map(ord, key)
        self._l = len(key)

    def encrypt(self, s):
        if isinstance(s, unicode):
            s = s.encode('u8')
        else:
            s = str(s)
        b = bytearray(s)
        for i in range(len(b)):
            b[i] ^= self._key[i % self._l]
        return str(b).encode('hex')

    def decrypt(self, s):
        b = bytearray(s.decode('hex'))
        for i in range(len(b)):
            b[i] ^= self._key[i % self._l]
        return str(b).decode('u8')


if __name__ == '__main__':
    simple = SimpleCrypto('你好，我是key')
    # 测试所有的unicode
    for char in xrange(0x10ffff):
        break
        cn = unichr(char)
        s1 = simple.encrypt(cn)
        s2 = simple.decrypt(s1)
        if cn != s2:
            print cn

    import doctest
    doctest.testmod()
