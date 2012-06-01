"""
tests.test_main
~~~~~~~~~~~~~~~

Test the main interface
"""
import lxc4u
import fudge
from fudge.inspector import arg

@fudge.patch('lxc4u.LXC')
def test_create(fake_lxc_class):
    """Simple test create"""
    fake_lxc_class.expects('create').with_args('name', service=arg.any()).returns("test")
    assert lxc4u.create('name') == 'test'

@fudge.patch('lxc4u.LXC')
def test_create_with_overlays(fake_lxc_class):
    """Simple test create"""
    fake_lxc_class.expects('create_with_overlays').with_args('name', 'test1', 
            ['overlay'], service=arg.any()).returns("test")
    assert lxc4u.create('name', base='test1', overlays=['overlay'])

@fudge.patch('lxc4u.LXCManager')
def test_lxc_manager_get(fake_manager):
    """Get an LXC container"""
    fake_manager.expects('get').with_args('name').returns('LXC')
    assert lxc4u.get('name') == 'LXC'

@fudge.patch('lxc4u.LXCManager')
def test_lxc_manager_list(fake_manager):
    """List LXC Containers"""
    fake_manager.expects('list').returns('LXC_LIST')
    assert lxc4u.list() == 'LXC_LIST'

@fudge.patch('lxc4u.LXCManager')
def test_lxc_manager_start(fake_manager):
    """Start an LXC and return the object"""
    fake_lxc = fake_manager.expects('get').with_args('name').returns_fake()
    fake_lxc.expects('start')
    assert lxc4u.start('name')
