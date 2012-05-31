import subprocess

def call_command(*args, **kwargs):
    """A wrapper around subprocess.Popen. 

    At this time this is not at all useful, but it may lead to
    easier testing later, hence it's inclusion
    """
    subprocess.Popen(*args, **kwargs)
    
