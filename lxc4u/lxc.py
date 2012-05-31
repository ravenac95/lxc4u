from .service import LXCService

class LXC(object):
    @classmethod
    def create(cls, name, template="ubuntu"):
        LXCService.create(name, template=template)
        return cls(name)

    def __init__(self, name):
        self.name = name
