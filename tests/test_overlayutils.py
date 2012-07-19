from mock import Mock, patch, call
from nose.tools import raises
from lxc4u.overlayutils import *

class TestCreatingOverlayGroup(object):
    def setup(self):
        self.lxc_service_patch = patch('lxc4u.lxc.LXCService')
        self.mkdir_patch = patch('os.mkdir')
        self.mount_patch = patch('overlay4u.mount')
        self.mkdtemp_patch = patch('tempfile.mkdtemp')

        self.mock_service = self.lxc_service_patch.start()
        self.mock_mkdir = self.mkdir_patch.start()
        self.mock_mount = self.mount_patch.start()
        self.mock_mkdtemp = self.mkdtemp_patch.start()

        self.mock_service.lxc_path.return_value = '/tmp/'
        self.mock_mkdtemp.return_value = 'sometemp_location'


    def teardown(self):
        self.lxc_service_patch.stop()
        self.mkdir_patch.stop()
        self.mount_patch.stop()
        self.mkdtemp_patch.stop()

    def test_create_simple_group(self):
        OverlayGroup.create('/point', '/low_dir', ['overlay_path'])

        self.mock_mount.assert_called_with('/point', '/low_dir', 'overlay_path')


    def test_create_group_with_multiple_overlays(self):
        OverlayGroup.create('/point', '/low_dir',
                ['overlay1_path', 'overlay2_path'])

        calls = [
            call('sometemp_location', '/low_dir', 'overlay1_path'),
            call('/point', 'sometemp_location', 'overlay2_path'),
        ]
        self.mock_mount.assert_has_calls(calls)

    @raises(TypeError)
    def test_create_group_fails_no_overlays(self):
        OverlayGroup.create('/point', '/low_dir', [])


class TestOverlayGroup(object):
    def setup(self):
        self.mock_ov1 = Mock(name='overlay1')
        self.mock_ov2 = Mock(name='overlay2')

        self.group = OverlayGroup('/end', '/start', [
            self.mock_ov1,
            self.mock_ov2
        ])

    def test_unmount(self):
        self.group.unmount()

        self.mock_ov1.unmount.assert_called_with()
        self.mock_ov2.unmount.assert_called_with()
