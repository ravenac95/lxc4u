from mock import Mock, patch, MagicMock
from lxc4u.meta import *


def test_initialize_lxc_meta():
    meta1 = LXCMeta()
    meta1['hello'] = 'hello'

    meta2 = LXCMeta(initial=dict(hello=123))

    assert meta1['hello'] == 'hello'
    assert meta2['hello'] == 123


@patch('__builtin__.open')
@patch('json.loads')
@patch('os.path.exists')
def test_meta_load_from_file(mock_exists, mock_loads, mock_open):
    # Setup Mocks
    mock_exists.return_value = True
    mock_loads.return_value = {}
    fake_path = 'path'

    # Run Test
    meta = LXCMeta.load_from_file(fake_path)

    # Assertions
    assert isinstance(meta, LXCMeta) == True


@patch('__builtin__.open')
@patch('json.loads')
@patch('os.path.exists')
def test_meta_load_from_file_with_no_file(mock_exists, mock_loads, mock_open):
    mock_exists.return_value = False
    fake_path = 'path'

    # Run Test
    meta = LXCMeta.load_from_file(fake_path)

    assert mock_loads.called == False, "Mock json was called for some reason"


class TestLXCMeta(object):
    def setup(self):
        metadata = dict(a=1, b=2, c=3, d='delta')
        self.metadata = metadata
        self.meta = LXCMeta(initial=metadata)



    def test_as_dict(self):
        assert self.meta.as_dict() == self.metadata

    @patch('lxc4u.meta.BoundLXCMeta')
    def test_bind(self, mock_bound_meta_cls):
        mock_lxc = Mock()

        self.meta.bind(mock_lxc)

        mock_bound_meta_cls.bind_to_lxc.assert_called_with(mock_lxc, self.meta)

    @patch('lxc4u.meta.BoundLXCMeta')
    def test_bind_and_save(self, mock_bound_meta_cls):
        self.meta.bind_and_save(None)

        mock_bound_meta_cls.bind_to_lxc.return_value.save.assert_called_with()


def test_initialize_bound_lxc_meta():
    fake_meta = dict(a=1, b=2, c=3)
    mock_lxc = Mock()

    bound_meta = BoundLXCMeta.bind_to_lxc(mock_lxc, fake_meta)
    bound_meta['hello'] = 'world'
    assert bound_meta['a'] == 1
    assert bound_meta['hello'] == 'world'


class TestBoundLXCMeta(object):
    def setup(self):
        mock_meta = MagicMock()
        mock_lxc = Mock()

        self.bound_meta = BoundLXCMeta.bind_to_lxc(mock_lxc, mock_meta)
        self.mock_meta = mock_meta
        self.mock_lxc = mock_lxc

    @patch('json.dumps', autospec=True)
    @patch('__builtin__.open', autospec=True)
    def test_save(self, mock_open, mock_dumps):
        mock_file = mock_open.return_value

        self.bound_meta.save()

        mock_open.assert_called_with(self.mock_lxc.path.return_value, 'w')
        mock_dumps.assert_called_with(self.mock_meta.as_dict.return_value)
        mock_file.write.assert_called_with(mock_dumps.return_value)
        mock_file.close.assert_called_with()

    def test_as_dict(self):
        self.bound_meta.as_dict()
        self.mock_meta.as_dict.assert_called_with()
