import fudge
from mock import patch
from lxc4u.service import LXCService

def test_service_list_names():
    """Test list container names times"""
    tests = [
        ('lxc1\nlxc2\nlxc3\n', ['lxc1', 'lxc2', 'lxc3']),
        ('lxc4\nlxc5\n', ['lxc4', 'lxc5']),
        ('', []),
    ]
    for ls_str, expected in tests:
        yield do_service_list_names, ls_str, expected

@patch('subwrap.run')
def do_service_list_names(ls_str, expected, mock_run):
    # Setup Mocks
    mock_resp = mock_run.return_value
    mock_resp.std_out = ls_str
    mock_resp.has_attr(std_out=ls_str)
    
    # Run Test
    lxc_list = LXCService.list_names()

    # Assertions
    mock_run.assert_called_with(['lxc-ls'])
    assert lxc_list == expected

@patch('subwrap.run')
def test_service_create(mock_run):
    LXCService.create('something')
    mock_run.assert_any_calls()

@patch('subwrap.run')
def test_service_start(mock_run):
    LXCService.start('something')
    mock_run.assert_any_calls()

@patch('subwrap.run')
def test_service_stop(mock_run):
    LXCService.stop('something')
    mock_run.assert_any_calls()

@patch('subwrap.run')
def test_service_destroy(mock_run):
    LXCService.destroy('something')
    mock_run.assert_any_calls()

def test_service_info():
    tests = [
        ("state:   RUNNING\npid:    12345", {"state": "RUNNING", "pid": "12345"}),
        ("state:   STOPPED\npid:    -1", {"state": "STOPPED", "pid": "-1"}),
    ]
    for info_str, expected in tests:
        yield do_service_info, info_str, expected

@patch('subwrap.run')
def do_service_info(info_str, expected, mock_run):
    # Setup Mocks
    mock_resp = mock_run.return_value
    mock_resp.std_out = info_str

    # Run Test
    info = LXCService.info("something")

    # Assertions
    assert info == expected

@patch('subwrap.run')
def test_service_lxc_path(mock_run):
    mock_resp = mock_run.returnG_value
    mock_resp.std_out = '/var/lib/lxc\n'

    assert LXCService.lxc_path() == '/var/lib/lxc'
    assert LXCService.lxc_path('hello') == '/var/lib/lxc/hello'
