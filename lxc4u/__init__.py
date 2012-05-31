from lxc import LXC
from service import LXCService

def create(*args):
    return LXC.create(*args)

def list_names(*args, **kwargs):
    return LXCService.list_names(*args, **kwargs)
