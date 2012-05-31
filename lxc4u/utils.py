import subwrap
from lxc import LXC

class LXCService(object):
    @classmethod
    def list_names(cls):
        """Lists all known LXC names"""
        response = subwrap.run(['lxc-ls'])
        output = response.std_out
        return map(str.strip, output.splitlines())

    def create(cls, *args, **kwargs):
        """Creates an LXC"""
        container = LXC.create(*args, **kwargs)
        return container
