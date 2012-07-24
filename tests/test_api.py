"""
tests.test_api
~~~~~~~~~~~~~~~

Test the api interface
"""
from lxc4u.api import *
from mock import Mock, patch


class TestLXCAPI(object):
    def setup(self):
        # Setup Patches
        self.create_lxc_patch = patch('lxc4u.api.create_lxc')
        self.create_lxc_with_overlays_patch = patch(
                'lxc4u.api.create_lxc_with_overlays')

        # Setup Mocks
        self.mock_create_lxc = self.create_lxc_patch.start()
        self.mock_create_lxc_with_overlays = \
                self.create_lxc_with_overlays_patch.start()
        self.mock_manager = Mock()
        self.mock_service = Mock()

        # Setup object under test
        self.api = LXCAPI(self.mock_manager, self.mock_service)

    def teardown(self):
        self.create_lxc_patch.stop()
        self.create_lxc_with_overlays_patch.stop()

    def test_create(self):
        name = 'name'

        lxc = self.api.create(name)

        self.mock_create_lxc.assert_called_with(name,
                service=self.mock_service)
        assert lxc == self.mock_create_lxc.return_value

    def test_create_with_overlays(self):
        name = 'name'
        base = 'base'
        overlays = ['ov1', 'ov2']

        lxc = self.api.create(name, base=base, overlays=overlays)

        self.mock_create_lxc_with_overlays.assert_called_with(name,
                base, overlays, service=self.mock_service)
        assert lxc == self.mock_create_lxc_with_overlays.return_value

    def test_get(self):
        name = 'name'

        lxc = self.api.get(name)

        assert lxc == self.mock_manager.get.return_value

    def test_list(self):
        lxc_list = self.api.list()

        assert lxc_list == self.mock_manager.list.return_value

    def test_start(self):
        name = 'name'

        lxc = self.api.start(name)

        self.mock_manager.get.assert_called_with(name)
        mock_lxc = self.mock_manager.get.return_value
        mock_lxc.start.assert_called_with()
        assert lxc == mock_lxc

    def test_stop(self):
        name = 'name'

        lxc = self.api.stop(name)

        self.mock_manager.get.assert_called_with(name)
        mock_lxc = self.mock_manager.get.return_value
        mock_lxc.stop.assert_called_with()
        assert lxc == mock_lxc
