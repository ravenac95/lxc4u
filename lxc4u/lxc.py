import os
import shutil
from .service import LXCService
from .overlayutils import OverlayGroup
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
    lxc = LXC.with_meta(name, service, meta)
    return lxc


class LXC(object):
    """The standard LXC"""
    @classmethod
    def with_meta(cls, name, service, meta, save=False):
        lxc = cls(name, service)
        lxc.bind_meta(meta, save=save)
        return lxc

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
    initial_metadata = dict(type='LXCWithOverlays',
            overlay_group=overlay_group.metadata())
    meta = LXCMeta(initial=initial_metadata)
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

    def __init__(self, name, service, overlay_group):
        self._overlay_group = overlay_group
        super(LXCWithOverlays, self).__init__(name, service)

    def destroy(self):
        """Unmounts overlay and deletes it's own directory"""
        self._overlay_group.unmount()
        shutil.rmtree(self.path())


class LXCLoader(object):
    def __init__(self, types, service):
        self._types = types
        self._service = service

    def load(self, meta):
        lxc_type_name = meta['type']

        lxc_type_cls = self._types.get(lxc_type_name)
        if not lxc_type_cls:
            raise UnknownLXCType('LXC type "%s" is unknown' % lxc_type_name)
        return lxc_type_cls.with_meta(meta['name'], self._service, meta)


class LXCManager(object):
    @classmethod
    def list(cls, service=None):
        """Get's all of the LXC's and creates objects for them"""
        service = service or LXCService
        lxc_names = service.list_names()
        return map(lambda name: LXC(name, service=service), lxc_names)

    @classmethod
    def get(cls, name, service=None):
        return LXC.from_name(name, service=service)
