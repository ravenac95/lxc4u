from .lxc import (LXCManager, create_lxc, create_lxc_with_overlays,
        LXCWithOverlays, LXC, UnmanagedLXC, LXCLoader)
from .service import LXCService


def default_setup():
    """The default setup for lxc4u"""
    service = LXCService
    lxc_types = dict(LXC=LXC, LXCWithOverlays=LXCWithOverlays,
            __default__=UnmanagedLXC)
    loader = LXCLoader(lxc_types, service)
    manager = LXCManager(loader, service)
    return LXCAPI(manager=manager, service=service)


class LXCAPI(object):
    def __init__(self, manager=None, service=None):
        self._service = service
        self._manager = manager

    def create(self, name, base=None, overlays=None):
        if base or overlays:
            return create_lxc_with_overlays(name,
                    base, overlays, service=self._service)
        return create_lxc(name, service=self._service)

    def start(self, name):
        lxc = self._manager.get(name)
        lxc.start()
        return lxc

    def stop(self, name):
        lxc = self._manager.get(name)
        lxc.stop()
        return lxc

    def get(self, name):
        return self._manager.get(name)

    def list(self):
        return self._manager.list()
