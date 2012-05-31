import fudge
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

@fudge.patch('subwrap.run')
def do_service_list_names(ls_str, expected, fake_run):
    fake_resp = fake_run.expects_call().with_args(['lxc-ls']).returns_fake()
    fake_resp.has_attr(std_out=ls_str)
    lxc_list = LXCService.list_names()
    assert lxc_list == expected

@fudge.patch('subwrap.run')
def test_service_create(fake_run):
    fake_run.expects_call()
    LXCService.create('something')

@fudge.patch('subwrap.run')
def test_service_start(fake_run):
    fake_run.expects_call()
    LXCService.start('something')

@fudge.patch('subwrap.run')
def test_service_stop(fake_run):
    fake_run.expects_call()
    LXCService.stop('something')

@fudge.patch('subwrap.run')
def test_service_info(fake_run):
    fake_resp = fake_run.expects_call().returns_fake()
    fake_resp.has_attr(std_out="state:   RUNNING\npid:    12345")
    info = LXCService.info('something')
    assert info == {"state": "RUNNING", "pid": "12345"}

def test_many_service_info():
    tests = [
        ("state:   RUNNING\npid:    12345", {"state": "RUNNING", "pid": "12345"}),
        ("state:   STOPPED\npid:    -1", {"state": "STOPPED", "pid": "-1"}),
    ]
    for info_str, expected in tests:
        yield do_service_info, info_str, expected

@fudge.patch('subwrap.run')
def do_service_info(info_str, expected, fake_run):
    fake_resp = fake_run.expects_call().returns_fake()
    fake_resp.has_attr(std_out=info_str)
    info = LXCService.info("something")
    assert info == expected
