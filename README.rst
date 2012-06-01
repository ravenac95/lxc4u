lxc4u - Tools for dealing with LXC in ubuntu
============================================

Warning! This is still a work in progress.

Provides tools for managing LXC in Ubuntu 12.04 and Ubuntu 12.04 Containers.
Other containers are not supported (yet?)

- Starts ephemeral containers using overlayfs
- For Ubuntu 12.04 containers, it can specify a static IP address
- Can handle multiple overlayfs layers to run an ephemeral container
- Can specify a startup command

Mostly working examples
-----------------------

Create a container named ``test1``::
    
    import lxc4u

    test1_lxc = lxc4u.create('test1')

    # Start the container
    test1_lxc.start()

Create a container that overlays ``test1``::
    
    import lxc4u
    
    test1_overlay_lxc = lxc4u.create('test1_overlay', base='test1',
                                    overlays=['overlay_path'])

    # Start the container
    test1_overlay_lxc.start()

Create a container with multiple overlays of ``test1``. The right most overlay
is the upper most overlay directory::
    
    import lxc4u
    
    test1_overlay_lxc = lxc4u.create('test1_overlay', base='test1',
                                overlays=['overlay1_path', 'overlay2_path'])

    # Start the container
    test1_overlay_lxc.start()

Possible interface examples
---------------------------

These examples have not yet been implemented. Soon!

Starting a container named ``test1``. This assumes lxc is properly configured
in your system::
    
    import lxc4u

    # Start container
    test1_lxc = lxc4u.start('test1')

    # Stop container
    test1_lxc.stop()
    # or lxc4u.stop('test1')

Starting an ephemeral container using test1 as a base::

    import lxc4u

    # Start container
    test1_ephemeral_lxc = lxc4u.start('test1', ephemeral=True)

    # Stop container
    test1_ephemeral_lxc.stop()

Starting an ephemeral container using test1 with static network settings::
    
    import lxc4u
    
    network_settings = dict(
        ip="10.0.3.5",
        gateway="10.0.3.1",
        netmask="255.255.255.0",
        network="10.0.3.0",
    )
        
    # Start container
    test1_ephemeral_lxc = lxc4u.start('test1', ephemeral=True, 
                                    static_network=network_settings)

    # Stop container
    test1_ephemeral_lxc.stop()

Starting an ephemeral container using with a startup command (must be available
on the container's path)::
    
    import lxc4u

    # Start container
    test1_ephemeral_lxc = lxc4u.start('test1', ephemeral=True,
                        startup_command="/usr/local/bin/somecommand")
    
    # Stop container
    test1_ephemeral_lxc.stop()
