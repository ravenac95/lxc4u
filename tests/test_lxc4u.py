import fudge
import lxc4u

@fudge.patch('lxc4u.lxc.call_command')
def test_create_a_container(fake_call_command):
    from lxc4u.lxc import LXC
    fake_call_command.expects_call()
    test1_lxc = lxc4u.create('test1')

    assert isinstance(test1_lxc, LXC), "test1_lxc isn't an LXC instance"

class TestRealContainers(object):
    """Collection of tests that should only be run on a testing rig"""
    def setup():
        pass
