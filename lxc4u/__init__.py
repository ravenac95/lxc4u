from .api import default_setup

__all__ = ['create', 'start', 'stop', 'get', 'list']

__default__ = default_setup()

create = __default__.create
start = __default__.start
stop = __default__.stop
get = __default__.get
list = __default__.list
