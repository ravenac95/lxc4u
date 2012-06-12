import fudge
import testkit
from nose.tools import raises
from lxc4u.overlayutils import *

class TestCreatingOverlayGroup(object):
    def setup(self):
        patch_context = fudge.patch('lxc4u.lxc.LXCService', 'overlay4u.mount',
                'os.mkdir', 'tempfile.mkdtemp')
        context_user = testkit.ContextUser(patch_context)
        self.fake_service, self.fake_mount, self.fake_mkdir, self.fake_mkdtemp = context_user.enter()
        self.fake_service.provides('lxc_path').returns('/tmp/')
        self.fake_mkdir.is_a_stub()
        self.fake_mkdtemp.is_callable().returns('sometemp_location')
        self.context_user = context_user

    def teardown(self):
        self.context_user.exit()

    @fudge.test
    def test_create_simple_group(self):
        self.fake_mount.expects_call().with_args('/point', '/low_dir', 'overlay_path')

        group = OverlayGroup.create('/point', '/low_dir', ['overlay_path'])


    @fudge.test
    def test_create_group_with_multiple_overlays(self):
        (self.fake_mount.expects_call()
                .with_args('sometemp_location',
                    '/low_dir', 'overlay1_path').next_call()
                .with_args('/point', 
                    'sometemp_location', 'overlay2_path'))
        group = OverlayGroup.create('/point', '/low_dir',
                ['overlay1_path', 'overlay2_path'])

    @raises(TypeError)
    @fudge.test
    def test_create_group_fails_no_overlays(self):
        OverlayGroup.create('/point', '/low_dir', [])

def test_overlay_group_unmount():
    fake_ov1 = fudge.Fake()
    fake_ov2 = fudge.Fake()
    fake_ov1.expects('unmount')
    fake_ov2.expects('unmount')

    test_group = OverlayGroup('/end', '/start', [
        fake_ov1,
        fake_ov2,
    ])
    test_group.unmount()
