import tempfile
import overlay4u

class OverlayGroup(object):
    @classmethod
    def create(cls, end_dir, start_dir, overlays, overlay_temp_path=None):
        if not overlays:
            raise TypeError('overlays may not be an empty list')
        overlay_objects = []
        # Prime the loop
        current_lower = start_dir
        # Loop through all but the final overlay
        for overlay in overlays[:-1]:
            # Create a temporary directory to handle the mount points for any
            # intermediate overlays
            temp_mount_point = tempfile.mkdtemp(dir=overlay_temp_path)
            # Mount that overlay
            overlay_obj = overlay4u.mount(temp_mount_point,
                    current_lower, overlay)
            overlay_objects.append(overlay_obj)
            # The new lower directory should be the temporary
            # directory
            current_lower = temp_mount_point
        # Get the final overlay location
        overlay = overlays[-1]
        # Do the final mount point on the lxc_path using the name provided
        overlay4u.mount(end_dir, current_lower, overlay)
        return cls(end_dir, start_dir, overlay_objects)

    def __init__(self, end_dir, start_dir, overlays):
        self.end_dir = end_dir
        self.start_dir = start_dir
        self.overlays = overlays

    def unmount(self):
        for overlay in self.overlays:
            overlay.unmount()

    def metadata(self):
        """Data for loading later"""
        mount_points = []
        for overlay in self.overlays:
            mount_points.append(overlay.mount_point)
        return mount_points
