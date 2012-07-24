from nose.tools import raises
from mock import Mock, patch, ANY, MagicMock
from lxc4u.lxc import *


@patch('lxc4u.lxc.LXCService')
def test_create_a_container(mock_service):
    test1_lxc = create_lxc('test1')

    # Assertions
    message = "test1_lxc isn't an LXC instance"
    assert isinstance(test1_lxc, LXC) == True, message
    mock_service.create.assert_called_with('test1', template='ubuntu')


def test_create_lxc_with_meta():
    mock_service = Mock()
    mock_meta = Mock()

    lxc = LXC.with_meta('name', mock_service, mock_meta)

    mock_meta.bind.assert_called_with(lxc)
    assert lxc.meta == mock_meta.bind.return_value


def test_create_lxc_with_meta_and_save():
    mock_service = Mock()
    mock_meta = Mock()

    # Save the meta data
    lxc = LXC.with_meta('name', mock_service, mock_meta, save=True)

    mock_meta.bind_and_save.assert_called_with(lxc)
    assert lxc.meta == mock_meta.bind_and_save.return_value


@raises(LXCHasNoMeta)
def test_lxc_without_meta():
    lxc = LXC('name', None)
    lxc.meta


class TestLXC(object):
    def setup(self):
        self.mock_service = Mock()
        self.mock_meta = Mock()
        self.lxc = LXC.with_meta('name', self.mock_service, self.mock_meta)

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


class TestCreateLXCWithOverlay(object):
    def setup(self):
        self.lxc_service_patch = patch('lxc4u.lxc.LXCService')
        self.mkdir_patch = patch('os.mkdir')
        self.overlay_group_patch = patch('lxc4u.lxc.OverlayGroup')
        self.lxc_meta_patch = patch('lxc4u.lxc.LXCMeta')

        self.mock_service = self.lxc_service_patch.start()
        self.mock_mkdir = self.mkdir_patch.start()
        self.mock_overlay_group_cls = self.overlay_group_patch.start()
        self.mock_meta_cls = self.lxc_meta_patch.start()

        self.mock_service.lxc_path.return_value = '/tmp/'

    def teardown(self):
        self.lxc_service_patch.stop()
        self.mkdir_patch.stop()
        self.overlay_group_patch.stop()
        self.lxc_meta_patch.stop()

    def test_with_simple_overlay(self):
        test1_overlay_lxc = create_lxc_with_overlays('test1_overlay',
                base='test1', overlays=['overlay_path'])

        # Assertions
        self.mock_overlay_group_cls.create.assert_called_with(
                '/tmp/test1_overlay', '/tmp/test1',
                ['overlay_path'])

        mock_meta = self.mock_meta_cls.return_value

        message = "test1_lxc_overlay isn't an LXC instance"

        assert isinstance(test1_overlay_lxc, LXCWithOverlays) == True, message

        mock_meta.bind_and_save.assert_called_with(test1_overlay_lxc)

    def test_with_many_overlays(self):
        """Test with multiple layers of overlay."""
        test1_overlay_lxc = create_lxc_with_overlays('test1_overlay',
                base='test1', overlays=['overlay1_path', 'overlay2_path'])

        # Assertions
        self.mock_overlay_group_cls.create.assert_called_with(
                '/tmp/test1_overlay', '/tmp/test1',
                ['overlay1_path', 'overlay2_path'])

        message = "test1_lxc_overlay isn't an LXC instance"
        assert isinstance(test1_overlay_lxc, LXCWithOverlays) == True, message


class TestLXCWithOverlay(object):
    def setup(self):
        self.mock_overlay_group = Mock()
        self.mock_service = Mock()

        self.lxc_with_overlay = LXCWithOverlays('name', self.mock_service,
                self.mock_overlay_group)

    @patch('shutil.rmtree')
    def test_destroy(self, mock_remove):
        self.lxc_with_overlay.destroy()

        # Assertions
        self.mock_overlay_group.unmount.assert_called_with()
        mock_remove.assert_called_with(self.mock_service.lxc_path.return_value)


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


def test_initialize_lxc_loader():
    LXCLoader(None, None)


# Utility function
def side_effect_map(**map_dict):
    return lambda a: map_dict[a]


class TestLXCLoader(object):
    def setup(self):
        self.mock_lxc_type1 = Mock()
        self.mock_lxc_type2 = Mock()
        self.mock_service = Mock()
        self.loader = LXCLoader({
            'type1': self.mock_lxc_type1,
            'type2': self.mock_lxc_type2,
        }, self.mock_service)

    def test_loader_load(self):
        # Setup Mocks
        meta1 = dict(type='type1', name='name1')
        meta2 = dict(type='type2', name='name2')

        # Run Test1
        lxc1 = self.loader.load(meta1)
        # Run Test2
        lxc2 = self.loader.load(meta2)

        # Assertions
        self.mock_lxc_type1.with_meta.assert_called_with('name1', ANY, meta1)
        assert lxc1 == self.mock_lxc_type1.with_meta.return_value

        self.mock_lxc_type2.with_meta.assert_called_with('name2', ANY, meta2)
        assert lxc2 == self.mock_lxc_type2.with_meta.return_value

    @raises(UnknownLXCType)
    def test_loader_load_fails(self):
        meta = dict(type='type3', name='name')
        self.loader.load(meta)
