import os
from .service import LXCService
from .overlayutils import OverlayGroup
from . import constants
from .meta import LXCMeta


class LXCAlreadyStarted(Exception):
    def __init__(self, name):
        message = 'LXC named "%s" is already running' % name
        super(LXCAlreadyStarted, self).__init__(message)


class LXCDoesNotExist(Exception):
    def __init__(self, name):
        message = 'LXC named "%s" does not exist' % name
        super(LXCDoesNotExist, self).__init__(message)


class LXCHasNoMeta(Exception):
    def __init__(self, name):
        message = 'LXC named "%s" has no BoundLXCMeta' % name
        super(LXCHasNoMeta, self).__init__(message)


class UnknownLXCType(Exception):
    pass


def create_lxc(name, template='ubuntu', service=None):
    """Factory method for the generic LXC"""
    service = service or LXCService
    service.create(name, template=template)
    meta = LXCMeta(initial=dict(type='LXC'))
    lxc = LXC.with_meta(name, service, meta, save=True)
    return lxc


class LXC(object):
    """The standard LXC"""
    @classmethod
    def with_meta(cls, name, service, meta, save=False):
        lxc = cls(name, service)
        lxc.bind_meta(meta, save=save)
        return lxc

    @classmethod
    def from_meta(cls, name, service, meta):
        return cls.with_meta(name, service, meta)

    def __init__(self, name, service):
        self.name = name
        self._service = service
        self._meta = None

    def start(self):
        """Start this LXC"""
        if self.status == 'RUNNING':
            raise LXCAlreadyStarted(self.name)
        self._service.start(self.name)

    def stop(self):
        """Stop this LXC"""
        self._service.stop(self.name)

    def destroy(self):
        self._service.destroy(self.name)

    @property
    def status(self):
        info = self._service.info(self.name)
        return info['state']

    @property
    def pid(self):
        info = self._service.info(self.name)
        return int(info['pid'])

    def path(self, *join_paths):
        return self._service.lxc_path(self.name, *join_paths)

    def __repr__(self):
        return '<%s "%s">' % (self.__class__.__name__, self.name)

    @property
    def meta(self):
        meta = self._meta
        if not meta:
            raise LXCHasNoMeta(self.name)
        return meta

    def bind_meta(self, meta, save=False):
        if save:
            self._meta = meta.bind_and_save(self)
        else:
            self._meta = meta.bind(self)


def create_lxc_with_overlays(name, base, overlays, overlay_temp_path=None,
        service=None):
    """Creates an LXC using overlays.

    This is a fast process in comparison to LXC.create because it does not
    involve any real copying of data.
    """
    service = service or LXCService
    # Check that overlays has content
    if not overlays:
        raise TypeError("Argument 'overlays' must have at least one item")

    # Get the system's LXC path
    lxc_path = service.lxc_path()
    # Calculate base LXC's path
    base_path = os.path.join(lxc_path, base)
    # Calculate the new LXC's path
    new_path = os.path.join(lxc_path, name)

    # Create the new directory if it doesn't exist
    if not os.path.exists(new_path):
        os.mkdir(new_path)

    overlay_group = OverlayGroup.create(new_path, base_path, overlays)
    initial_meta = dict(type='LXCWithOverlays',
            overlay_group=overlay_group.meta())
    meta = LXCMeta(initial=initial_meta)
    return LXCWithOverlays.with_meta(name, service, meta, overlay_group,
            save=True)


class UnmanagedLXCError(Exception):
    pass


class UnmanagedLXC(LXC):
    """An LXC that was created without lxc4u metadata"""
    def destroy(self, force=False):
        """UnmanagedLXC Destructor.

        It requires force to be true in order to work. Otherwise it throws an
        error.
        """
        if force:
            super(UnmanagedLXC, self).destroy()
        else:
            raise UnmanagedLXCError('Destroying an unmanaged LXC might not '
                'work. To continue please call this method with force=True')


class LXCWithOverlays(LXC):
    """An LXC that has an overlay group"""
    @classmethod
    def with_meta(cls, name, service, meta, overlay_group, save=False):
        lxc = cls(name, service, overlay_group)
        lxc.bind_meta(meta, save=save)
        return lxc

    @classmethod
    def from_meta(cls, name, service, meta):
        overlay_group_meta = meta.get('overlay_group')
        overlay_group = OverlayGroup.from_meta(overlay_group_meta)
        return cls.with_meta(name, service, meta, overlay_group)

    def __init__(self, name, service, overlay_group):
        self._overlay_group = overlay_group
        super(LXCWithOverlays, self).__init__(name, service)

    def destroy(self):
        """Unmounts overlay and deletes it's own directory"""
        self._overlay_group.destroy()


class LXCLoader(object):
    def __init__(self, types, service):
        self._types = types
        self._service = service

    def load(self, name, meta):
        lxc_type_name = meta.get('type', constants.DEFAULT_LXC_TYPE_KEY)

        lxc_type_cls = self._types.get(lxc_type_name)
        if not lxc_type_cls:
            raise UnknownLXCType('LXC type "%s" is unknown' % lxc_type_name)
        return lxc_type_cls.from_meta(name, self._service, meta)


class LXCManager(object):
    """Manages the currently available LXCs"""
    def __init__(self, loader, service):
        self._service = service
        self._loader = loader

    def list(self):
        """Get's all of the LXC's and creates objects for them"""
        service = self._service

        lxc_names = service.list_names()
        lxc_list = []
        for name in lxc_names:
            lxc = self.get(name)
            lxc_list.append(lxc)
        return lxc_list

    def get(self, name):
        """Retrieves a single LXC by name"""
        lxc_meta_path = self._service.lxc_path(name,
                constants.LXC_META_FILENAME)
        meta = LXCMeta.load_from_file(lxc_meta_path)
        lxc = self._loader.load(name, meta)
        return lxc
