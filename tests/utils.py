import os
from functools import wraps
from nose.plugins.skip import SkipTest

def only_as_root(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        euid = os.geteuid()
        if euid != 0:
            raise SkipTest("Sorry. Test requires root")
        return f(*args, **kwargs)
    return decorated_function
