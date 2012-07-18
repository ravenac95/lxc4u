"""
tests.test_main
~~~~~~~~~~~~~~~

Test the main interface
"""
import lxc4u
from mock import patch, ANY

@patch('lxc4u.LXC')
def test_create(mock_lxc_cls):
    """Simple test create"""
    assert lxc4u.create('name') == mock_lxc_cls.create.return_value
    mock_lxc_cls.create.assert_called_with('name', service=ANY)

@patch('lxc4u.LXC')
def test_create_with_overlays(mock_lxc_cls):
    """Simple test create"""
    create_obj = mock_lxc_cls.create_with_overlays.return_value
    assert lxc4u.create('name', base='test1', 
            overlays=['overlay']) == create_obj
    mock_lxc_cls.create_with_overlays.assert_called_with('name', 'test1', 
            ['overlay'], service=ANY)

@patch('lxc4u.LXCManager')
def test_get(mock_manager):
    """Get an LXC container"""
    assert lxc4u.get('name') == mock_manager.get.return_value
    mock_manager.get.assert_called_with('name')

@patch('lxc4u.LXCManager')
def test_list(mock_manager):
    """List LXC Containers"""
    assert lxc4u.list() == mock_manager.list.return_value

@patch('lxc4u.LXCManager')
def test_start(mock_manager):
    """Start an LXC and return the object"""
    # Get mock_lxc from mock_manager
    mock_lxc = mock_manager.get.return_value

    assert lxc4u.start('name') == mock_lxc
    mock_manager.get.assert_called_with('name')
    mock_lxc.start.assert_called_with()

@patch('lxc4u.LXCManager')
def test_stop(mock_manager):
    """Stop an LXC and return the object"""
    mock_lxc = mock_manager.get.return_value

    assert lxc4u.stop('name') == mock_lxc
    mock_manager.get.assert_called_with('name')
    mock_lxc.stop.assert_called_with()
