import os
import tempfile
import overlay4u
from .service import LXCService

class LXCAlreadyStarted(Exception):
    def __init__(self, name):
        message = 'LXC named "%s" is already running' % name
        super(LXCAlreadyStarted, self).__init__(message)

class LXC(object):
    @classmethod
    def create(cls, name, template="ubuntu"):
        """Create a brand new LXC"""
        LXCService.create(name, template=template)
        return cls(name)

    @classmethod
    def create_with_overlays(cls, name, base, overlays, overlay_temp_path=None):
        """Creates an LXC using overlays. 
        
        This is a fast process in comparison to LXC.create because it does not
        involve any real copying of data.
        """
        # Check that overlays has content
        if not overlays:
            raise TypeError("Argument 'overlays' must have at least one item")

        # Get the system's LXC path
        lxc_path = LXCService.lxc_path()
        # Calculate base LXC's path
        base_path = os.path.join(lxc_path, base)
        # Calculate the new LXC's path
        new_path = os.path.join(lxc_path, name)

        # Create the new directory if it doesn't exist
        if not os.path.exists(new_path):
            os.mkdir(new_path)

        # Prime the loop
        current_lower = base_path
        # Loop through all but the final overlay
        for overlay in overlays[:-1]:
            # Create a temporary directory to handle the mount points for any
            # intermediate overlays
            temp_mount_point = tempfile.mkdtemp(dir=overlay_temp_path)
            # Mount that overlay
            overlay4u.mount(temp_mount_point, current_lower, overlay)
            # The new lower directory should be the temporary directory
            current_lower = temp_mount_point
        # Get the final overlay location
        overlay = overlays[-1]
        # Do the final mount point on the lxc_path using the name provided
        overlay4u.mount(new_path, current_lower, overlay)
        # Return the LXC object
        return cls(name)
    
    @classmethod
    def from_name(cls, name, service=None):
        # Seems redundant now, but I prefer this over calling the constructor
        # directly. This could improve later
        return cls(name, service=service)

    def __init__(self, name, service=None):
        self.name = name
        self._service = service or LXCService

    def start(self):
        """Start this LXC"""
        if self.status == 'RUNNING':
            raise LXCAlreadyStarted(self.name)
        self._service.start(self.name)
    
    def stop(self):
        """Stop this LXC"""
        self._service.stop(self.name)

    @property
    def status(self):
        info = self._service.info()
        return info['status']
    
    @property
    def pid(self):
        info = self._service.info()
        return int(info['pid'])
