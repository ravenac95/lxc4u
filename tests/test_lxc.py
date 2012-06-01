from nose.tools import raises
import fudge
from fudge.inspector import arg
import testkit
from lxc4u.lxc import *

@fudge.patch('lxc4u.lxc.LXCService')
def test_create_a_container(fake_service):
    fake_service.expects('create').with_args('test1', template='ubuntu')
    test1_lxc = LXC.create('test1')

    message = "test1_lxc isn't an LXC instance"
    assert isinstance(test1_lxc, LXC) == True, message

@fudge.patch('lxc4u.lxc.LXCService')
def test_container_from_name(fake_service):
    fake_service.expects('list_names').returns(['name'])
    test1_lxc = LXC.from_name('name')
    message = "test1_lxc isn't an LXC instance"
    assert isinstance(test1_lxc, LXC) == True, message

@raises(LXCDoesNotExist)
@fudge.patch('lxc4u.lxc.LXCService')
def test_container_from_name_does_not_exist(fake_service):
    fake_service.expects('list_names').returns([])
    LXC.from_name('name')

class TestLXC(object):
    def setup(self):
        self.fake_service = fudge.Fake('LXCService')
        self.lxc = LXC('name', service=self.fake_service)

    @fudge.test
    def test_start_container(self):
        self.fake_service.expects('start').with_args('name')
        self.fake_service.expects('info').returns({
            'state': 'STOPPED', 'pid': '-1'})
        self.lxc.start()

    @fudge.test
    def test_stop_container(self):
        self.fake_service.expects('stop').with_args('name')
        self.lxc.stop()

    @fudge.test
    def test_get_status(self):
        self.fake_service.expects('info').returns({
            'state': 'RUNNING', 'pid': '12345'})
        assert self.lxc.status == 'RUNNING'

    @fudge.test
    def test_get_pid(self):
        self.fake_service.expects('info').returns({
            'state': 'RUNNING', 'pid': '12345'})
        assert self.lxc.pid == 12345

    @fudge.test
    @raises(LXCAlreadyStarted)
    def test_start_container_that_is_already_running(self):
        self.fake_service.expects('info').returns({
            'state': 'RUNNING', 'pid': '12345'})
        self.lxc.start()

class TestLXCWithOverlay(object):
    def setup(self):
        patch_context = fudge.patch('lxc4u.lxc.LXCService', 'overlay4u.mount', 'os.mkdir', 'tempfile.mkdtemp')
        context_user = testkit.ContextUser(patch_context)
        self.fake_service, self.fake_mount, self.fake_mkdir, self.fake_mkdtemp = context_user.enter()
        self.fake_service.provides('lxc_path').returns('/tmp/')
        self.fake_mkdir.is_a_stub()
        self.fake_mkdtemp.expects_call().returns('sometemp_location')
        self.context_user = context_user

    def teardown(self):
        self.context_user.exit()
    
    @fudge.test
    def test_with_simple_overlay(self):
        self.fake_mount.expects_call().with_args('/tmp/test1_overlay', 
                '/tmp/test1', 'overlay_path')

        test1_overlay_lxc = LXC.create_with_overlays('test1_overlay',
                base='test1', overlays=['overlay_path'])
    
        message = "test1_lxc_overlay isn't an LXC instance"
        assert isinstance(test1_overlay_lxc, LXC) == True, message

    @fudge.test
    def test_with_many_overlays(self):
        """Test with multiple layers of overlay."""
        (self.fake_mount.expects_call()
                .with_args('sometemp_location',
                    '/tmp/test1', 'overlay1_path').next_call()
                .with_args('/tmp/test1_overlay', 
                    'sometemp_location', 'overlay2_path'))

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
