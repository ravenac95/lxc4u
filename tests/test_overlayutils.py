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
        overlay_group = OverlayGroup.create('/point', '/low_dir',
                ['overlay_path'])

        self.mock_mount.assert_called_with('/point', '/low_dir',
                'overlay_path')
        # Assert that the overlays are tracked correctly
        assert len(overlay_group) == 1

    def test_create_group_with_multiple_overlays(self):
        overlay_group = OverlayGroup.create('/point', '/base_dir',
                ['overlay1_path', 'overlay2_path'])

        calls = [
            call('sometemp_location', 'overlay1_path', 'overlay2_path'),
            call('/point', '/base_dir', 'sometemp_location'),
        ]
        self.mock_mount.assert_has_calls(calls)
        # Assert that the overlays are tracked correctly
        assert len(overlay_group) == 2

    def test_create_group_and_iterate(self):
        overlay_group = OverlayGroup.create('/point', '/low_dir',
                ['overlay1_path', 'overlay2_path'])

        for overlay in overlay_group:
            assert overlay == self.mock_mount.return_value

    @raises(TypeError)
    def test_create_group_fails_no_overlays(self):
        OverlayGroup.create('/point', '/low_dir', [])


@patch('overlay4u.get')
def test_overlay_group_from_meta(mock_overlay_get):
    # Setup
    fake_overlays = ['/over1', '/over2']
    fake_meta = ['/end', '/start', fake_overlays]

    # Run Test
    overlay_group = OverlayGroup.from_meta(fake_meta)

    # Assertions
    expected_calls = [
        call('/over1'),
        call('/over2'),
    ]
    mock_overlay_get.assert_has_calls(expected_calls)
    assert overlay_group.end_dir == '/end'
    assert overlay_group.start_dir == '/start'
    for overlay in overlay_group.overlays:
        assert overlay == mock_overlay_get.return_value


class TestOverlayGroup(object):
    def setup(self):
        self.mock_ov1 = Mock(name='overlay1')
        self.mock_ov2 = Mock(name='overlay2')
        self.mock_ov3 = Mock(name='overlay3')

        self.group = OverlayGroup('/end', '/start', [
            self.mock_ov1,
            self.mock_ov2,
            self.mock_ov3,
        ])

    def test_meta(self):
        meta = self.group.meta()

        assert meta == ['/end', '/start', [self.mock_ov1.mount_point,
                self.mock_ov2.mount_point, self.mock_ov3.mount_point]]

    @patch('shutil.rmtree')
    def test_destroy(self, mock_rmtree):
        self.group.destroy()

        calls = [
            call(self.mock_ov1.mount_point),
            call(self.mock_ov2.mount_point),
            call(self.mock_ov3.mount_point),
        ]
        mock_rmtree.assert_has_calls(calls)

        self.mock_ov1.unmount.assert_called_with()
        self.mock_ov2.unmount.assert_called_with()
        self.mock_ov3.unmount.assert_called_with()
