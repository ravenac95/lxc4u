"""
tests.test_as_root
~~~~~~~~~~~~~~~~~~

These are tests that must be run as root. They will be skipped by nose
automatically if you are not root.

These tests are meant to be as close to truly functional as possible. Take
extra caution when running these tests. If this is not a stable release please
do not run these tests in a production system.
"""
import tempfile
import shutil
import os
from nose.plugins.attrib import attr
from testkit import random_string, temp_directory
from testkit.data import ALPHAS_LOWER
from .utils import only_as_root
import lxc4u

def read_file_data(filepath):
    f = open(filepath)
    data = f.read()
    f.close()
    return data

@only_as_root
def test_create():
    """Create a new LXC"""
    # WARNING this test assumes that you're using /var/lib/lxc for 
    # lxc containers. If that is not correct please do not run this test
    # Create a random directory path for the test container
    container_path = tempfile.mkdtemp(dir="/var/lib/lxc")
    # Delete path that was created
    shutil.rmtree(container_path)
    # Get random name using temp directory path
    random_name = os.path.basename(container_path)
    try:
        # Create the new container
        lxc4u.create(random_name)
        # Assert that the new container was created at the correct path
        assert os.path.exists(container_path) == True, "Container not created"
        # Assert that it's a directory
        assert os.path.isdir(container_path) == True, "Container not a directory"
    finally:
        # Always delete the temp directory if it still exists
        if os.path.exists(container_path):
            if os.path.isdir(container_path):
                shutil.rmtree(container_path)
            else:
                os.remove(container_path)

#@only_as_root
#def test_create_with_overlay():
#    """Create a new LXC with a temp overlay"""
#    random_name = random_string(26, ALPHAS_LOWER)
#    # Create a random directory path for the test container
#    container_path = tempfile.mkdtemp(dir='/var/lib/lxc')
#    # Delete path that was created
#    shutil.rmtree(container_path)
#    # Get random name using temp directory path
#    random_name = os.path.basename(container_path)
#    with temp_directory() as temp_path:
#        try:
#            # FIXME it assumes you have an LXC named base
#            lxc4u.create(random_name, base="base", overlays=[temp_path])
#        finally:
#            if os.path.exists(container_path):
#                if os.path.isdir(container_path):
#                    shutil.rmtree(container_path)
#                else:
#                    os.remove(container_path)
#

