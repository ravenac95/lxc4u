"""
lxc4u.service
~~~~~~~~~~~~~

This contains the low level access layer to any of the lxc command line tools.
"""
import os
import subwrap


def split_info_line(line):
    return map(str.strip, line.split(':'))


class LXCService(object):
    """Low level access layer to the lxc tools"""
    @classmethod
    def list_names(cls):
        """Lists all known LXC names"""
        response = subwrap.run(['lxc-ls'])
        output = response.std_out
        return map(str.strip, output.splitlines())

    @classmethod
    def lxc_path(cls, *join_paths):
        """Returns the LXC path (default on ubuntu is /var/lib/lxc)"""
        response = subwrap.run(['lxc-ls', '-d'])
        output = response.std_out
        lxc_path = output.splitlines()[0]
        lxc_path = lxc_path.strip()
        return os.path.join(lxc_path, *join_paths)

    @classmethod
    def create(cls, name, template=None):
        """Creates an LXC"""
        command = ['lxc-create', '-n', name]
        if template:
            command.extend(['-t', template])
        subwrap.run(command)

    @classmethod
    def start(cls, name):
        """Starts an LXC as a daemon

        This cannot start an LXC as a non-daemon. That doesn't make sense.
        """
        command = ['lxc-start', '-n', name, '-d']
        subwrap.run(command)

    @classmethod
    def stop(cls, name):
        """Stops a running LXC"""
        command = ['lxc-stop', '-n', name]
        subwrap.run(command)

    @classmethod
    def destroy(cls, name):
        command = ['lxc-destroy', '-n', name]
        subwrap.run(command)

    @classmethod
    def info(cls, name, get_state=True, get_pid=True):
        """Retrieves and parses info about an LXC"""
        # Run lxc-info quietly
        command = ['lxc-info', '-n', name]
        response = subwrap.run(command)
        lines = map(split_info_line, response.std_out.splitlines())
        return dict(lines)
