from lxc import LXC, LXCManager

def create(name, base=None, overlays=None, service=None):
    if base or overlays:
        return LXC.create_with_overlays(name, 
                base, overlays, service=service)
    return LXC.create(name, service=service)

def get(name):
    return LXCManager.get(name)

def list():
    return LXCManager.list()

def start(name):
    lxc_obj = LXCManager.get(name)
    lxc_obj.start()
    return lxc_obj
