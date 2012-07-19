from lxc import (LXCManager, create_lxc, create_lxc_with_overlays)


def create(name, base=None, overlays=None, service=None):
    if base or overlays:
        return create_lxc_with_overlays(name,
                base, overlays, service=service)
    return create_lxc(name, service=service)


def get(name):
    return LXCManager.get(name)


def list():
    return LXCManager.list()


def start(name):
    lxc_obj = LXCManager.get(name)
    lxc_obj.start()
    return lxc_obj


def stop(name):
    lxc_obj = LXCManager.get(name)
    lxc_obj.stop()
    return lxc_obj
