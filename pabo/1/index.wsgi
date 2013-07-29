# coding: u8

# 一定要先调用setup.init()
import pabo.main.setup as setup
setup.init()


import pabo.main.handlers as handlers


__all__ = ['application']
application = handlers.application
