from nose.tools import raises
from mock import Mock, patch, ANY
from lxc4u.lxc import *

@patch('lxc4u.lxc.LXCService')
def test_create_a_container(mock_service):
    test1_lxc = LXC.create('test1')

    # Assertions
    message = "test1_lxc isn't an LXC instance"
    assert isinstance(test1_lxc, LXC) == True, message
    mock_service.create.assert_called_with('test1', template='ubuntu')

@patch('lxc4u.lxc.LXCService')
def test_container_from_name(mock_service):
    # Setup Return values
    mock_service.list_names.return_value = ['name']

    # Run Test
    test1_lxc = LXC.from_name('name')
    
    # Assertions
    message = "test1_lxc isn't an LXC instance"
    assert isinstance(test1_lxc, LXC) == True, message
    mock_service.list_names.assert_called_with()
    

@raises(LXCDoesNotExist)
@patch('lxc4u.lxc.LXCService')
def test_container_from_name_does_not_exist(mock_service):
    mock_service.list_names.return_value = []
    LXC.from_name('name')

class TestLXC(object):
    def setup(self):
        self.mock_service = Mock()
        self.lxc = LXC('name', service=self.mock_service)

    def test_start_container(self):
        # Setup Return Values
        self.mock_service.info.return_value = dict(state='STOPPED',
                pid='-1')

        # Run test
        self.lxc.start()

        # Assertions
        self.mock_service.start.assert_called_with('name')

    def test_stop_container(self):
        self.lxc.stop()

        # Assertions
        self.mock_service.stop.assert_called_with('name')

    def test_get_status(self):
        self.mock_service.info.return_value = dict(state='RUNNING', 
                pid='12345')
        assert self.lxc.status == 'RUNNING'

    def test_get_pid(self):
        self.mock_service.info.return_value = dict(state='RUNNING', 
                pid='12345')
        assert self.lxc.pid == 12345

    def test_path(self):
        path = self.lxc.path('hello')
        assert path == self.mock_service.lxc_path.return_value
        self.mock_service.lxc_path.assert_called_with('name', 'hello')


    @raises(LXCAlreadyStarted)
    def test_start_container_that_is_already_running(self):
        self.mock_service.info.return_value = dict(state='RUNNING', 
                pid='12345')
        self.lxc.start()

    def test_destroy(self):
        self.lxc.destroy()
        self.mock_service.destroy.assert_called_with('name')

class TestLXCWithOverlay(object):
    def setup(self):
        self.lxc_service_patch = patch('lxc4u.lxc.LXCService')
        self.mkdir_patch = patch('os.mkdir')
        self.overlay_group_patch = patch('lxc4u.lxc.OverlayGroup')

        self.mock_service = self.lxc_service_patch.start()
        self.mock_mkdir = self.mkdir_patch.start()
        self.mock_overlay_group_cls = self.overlay_group_patch.start()

        self.mock_service.lxc_path.return_value = '/tmp/'

    def teardown(self):
        self.lxc_service_patch.stop()
        self.mkdir_patch.stop()
        self.overlay_group_patch.stop()
    
    def test_with_simple_overlay(self):
        test1_overlay_lxc = LXC.create_with_overlays('test1_overlay',
                base='test1', overlays=['overlay_path'])

        # Assertions
        self.mock_overlay_group_cls.create.assert_called_with('/tmp/test1_overlay', '/tmp/test1',
                ['overlay_path'])

        message = "test1_lxc_overlay isn't an LXC instance"
        assert isinstance(test1_overlay_lxc, LXC) == True, message

    def test_with_many_overlays(self):
        """Test with multiple layers of overlay."""
        test1_overlay_lxc = LXC.create_with_overlays('test1_overlay',
                base='test1', overlays=['overlay1_path', 'overlay2_path'])
        
        # Assertions
        self.mock_overlay_group_cls.create.assert_called_with('/tmp/test1_overlay', '/tmp/test1',
                ['overlay1_path', 'overlay2_path'])

        message = "test1_lxc_overlay isn't an LXC instance"
        assert isinstance(test1_overlay_lxc, LXC) == True, message


@patch('lxc4u.lxc.LXCService')
def test_lxc_manager_list(mock_service):
    mock_service.list_names.return_value = ['lxc1', 'lxc2']
    lxc_list = LXCManager.list()
    for lxc in lxc_list:
        assert isinstance(lxc, LXC)
    assert len(lxc_list) == 2


@patch('lxc4u.lxc.LXC')
def test_lxc_manager_get(mock_lxc_cls):
    assert LXCManager.get('name') == mock_lxc_cls.from_name.return_value
    mock_lxc_cls.from_name.assert_called_with('name', service=ANY)
