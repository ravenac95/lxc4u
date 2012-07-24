import os
import json
from . import constants


class LXCMeta(object):
    """A dictionary like object that stores the metadata for an LXC"""

    @classmethod
    def load_from_file(cls, file_path):
        """Load the meta data given a file_path or empty meta data"""
        data = None
        if os.path.exists(file_path):
            data = json.loads(file_path)
        return cls(initial=data)

    def __init__(self, initial=None):
        initial = initial or {}
        self._metadata = initial.copy()

    def __getitem__(self, key):
        return self._metadata[key]

    def __setitem__(self, key, value):
        self._metadata[key] = value

    def get(self, key):
        return self._metadata[key]

    def set(self, key, value):
        self._metadata[key] = value

    def as_dict(self):
        return self._metadata.copy()

    def bind(self, lxc):
        """Bind to an LXC"""
        return BoundLXCMeta.bind_to_lxc(lxc, self)

    def bind_and_save(self, lxc):
        """Binds metadata to an LXC and saves it"""
        bound_meta = self.bind(lxc)
        bound_meta.save()
        return bound_meta


class BoundLXCMeta(object):
    """An LXCMeta wrapper that binds it to an LXC"""

    @classmethod
    def bind_to_lxc(cls, lxc, meta):
        return cls(lxc, meta)

    def __init__(self, lxc, meta):
        self._lxc = lxc
        self._meta = meta

    def __getitem__(self, key):
        return self._meta[key]

    def __setitem__(self, key, value):
        self._meta[key] = value

    def save(self):
        meta_file_path = self._lxc.path(constants.LXC_META_FILENAME)
        meta_file = open(meta_file_path, 'w')

        json_string = json.dumps(self._meta.as_dict())

        meta_file.write(json_string)
        meta_file.close()

    def as_dict(self):
        return self._meta.as_dict()
        return self._meta.as_dict()
