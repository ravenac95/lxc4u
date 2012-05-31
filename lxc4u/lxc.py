from utils import call_command

class LXC(object):
    @classmethod
    def create(cls, name, template="ubuntu"):
        call_command(['lxc-create', '-t', template, '-n',
            name])
        return cls(name)

    def __init__(self, name, *args, **kwargs):
        self.name = name

    def start(self):
        """Starts the LXC container as a daemon"""
        call_command(['lxc-start', '-n', self.name, '-d'])

    def stop(self):
        """Stops the LXC container"""
        call_command(['lxc-stop', '-n', self.name])
