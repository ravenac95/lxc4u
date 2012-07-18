from nose.tools import raises
from mock import Mock, patch
import fudge
from fudge.inspector import arg
import testkit
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
        patch_context = fudge.patch('lxc4u.lxc.LXCService', 
                'os.mkdir', 'lxc4u.lxc.OverlayGroup')
        context_user = testkit.ContextUser(patch_context)
        self.fake_service, self.fake_mkdir, self.fake_overlay_group_cls = context_user.enter()
        self.fake_service.provides('lxc_path').returns('/tmp/')
        self.fake_mkdir.is_a_stub()
        self.context_user = context_user

    def teardown(self):
        self.context_user.exit()
    
    @fudge.test
    def test_with_simple_overlay(self):
        (self.fake_overlay_group_cls.expects('create')
                .with_args('/tmp/test1_overlay', '/tmp/test1', ['overlay_path'])
                .returns_fake())

        test1_overlay_lxc = LXC.create_with_overlays('test1_overlay',
                base='test1', overlays=['overlay_path'])
    
        message = "test1_lxc_overlay isn't an LXC instance"
        assert isinstance(test1_overlay_lxc, LXC) == True, message

    @fudge.test
    def test_with_many_overlays(self):
        """Test with multiple layers of overlay."""
        (self.fake_overlay_group_cls.expects('create')
                .with_args('/tmp/test1_overlay', '/tmp/test1', 
                    ['overlay1_path', 'overlay2_path'])
                .returns_fake())

        test1_overlay_lxc = LXC.create_with_overlays('test1_overlay',
                base='test1', overlays=['overlay1_path', 'overlay2_path'])
        message = "test1_lxc_overlay isn't an LXC instance"
        assert isinstance(test1_overlay_lxc, LXC) == True, message


@fudge.patch('lxc4u.lxc.LXCService')
def test_lxc_manager_list(fake_service):
    fake_service.expects('list_names').returns(['lxc1', 'lxc2'])
    lxc_list = LXCManager.list()
    for lxc in lxc_list:
        assert isinstance(lxc, LXC)

@fudge.patch('lxc4u.lxc.LXC')
def test_lxc_manager_get(fake_lxc_class):
    fake_lxc_class.expects('from_name').with_args('name', service=arg.any()).returns('LXC')
    assert LXCManager.get('name') == 'LXC'
