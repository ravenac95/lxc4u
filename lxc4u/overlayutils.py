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
        overlay_obj = overlay4u.mount(end_dir, current_lower, overlay)
        overlay_objects.append(overlay_obj)
        return cls(end_dir, start_dir, overlay_objects)

    @classmethod
    def from_meta(cls, meta):
        end_dir = meta[0]
        start_dir = meta[1]
        overlay_mount_points = meta[2]
        overlay_objects = map(lambda a: overlay4u.get(a), overlay_mount_points)
        return cls(end_dir, start_dir, overlay_objects)

    def __init__(self, end_dir, start_dir, overlays):
        self.end_dir = end_dir
        self.start_dir = start_dir
        self.overlays = overlays

    def unmount(self):
        for overlay in self.overlays:
            overlay.unmount()

    def meta(self):
        """Data for loading later"""
        mount_points = []
        for overlay in self.overlays:
            mount_points.append(overlay.mount_point)
        return [self.end_dir, self.start_dir, mount_points]

    def __iter__(self):
        return iter(self.overlays)

    def __len__(self):
        return len(self.overlays)
