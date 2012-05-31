import fudge
import lxc4u

@fudge.patch('subwrap.run', 'lxc4u.lxc.LXCService')
def test_create_a_container(fake_run, fake_service):
    from lxc4u.lxc import LXC
    fake_service.expects('create').with_args('test1', template='ubuntu')
    test1_lxc = lxc4u.create('test1')

    assert isinstance(test1_lxc, LXC), "test1_lxc isn't an LXC instance"

#@fudge.patch('subwrap.run', 'overlay4u')
#def test_create_a_container_with_overlay(fake_run):
#    fake_overlay4u.expects('mount')
#
#    test1_overlay_lxc = lxc4u.create('test1_overlay', base='test1',
#            overlays=['path_to_overlay_dir'])

class TestRealContainers(object):
    """Collection of tests that should only be run on a testing rig"""
    def setup():
        pass
