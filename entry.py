#!/usr/bin/python3

"""
This entry point sets up the user and group(s) in a more flexible way than
crops/poky.

If the current user is root, then we set our UID to match the owner of the
current working directory. We add the GID of the current working directory as
our primary group. We maintain all groups that might have been passed along
with --group-add when running the container.

We will add groups of a few other files and directories (kvm, sstate cache,
etc.)
"""

import os
import sys
import pwd

def set_environment(uid):
    try:
        ent = pwd.getpwuid(uid)
    except KeyError:
        os.environ.pop('HOME', '')
    else:
        os.environ['HOME'] = ent.pw_dir
        os.environ['SHELL'] = ent.pw_shell

def gather_supplemental_groups(gid):
    groups = set(os.getgroups())
    groups.add(os.getgid()) # keep if not root
    groups.discard(0) # don't keep root group by default
    groups.add(gid) # always keep final group

    # Gather groups based on interesting files/dirs
    extras = [
        '/dev/kvm',
        '$SSTATE_DIR',
        '/var/lib/sstate',
        '$CI_PROJECT_DIR',
    ]
    for e in extras:
        path = os.path.expandvars(e)
        try:
            groups.add(os.stat(path).st_gid)
        except FileNotFoundError:
            pass

    return sorted(groups)

def set_credentials():
    if os.getuid() != 0:
        return # not root, leave as is

    # Get final credentials
    stat = os.stat(os.getcwd())
    uid = stat.st_uid
    gid = stat.st_gid
    groups = gather_supplemental_groups(gid)

    set_environment(uid)

    # Set credentials
    os.setgroups(groups)
    os.setgid(gid)
    os.setuid(uid)

def exec_command(cmdline):
    if not cmdline:
        cmdline = [ os.environ.get('SHELL', '/bin/bash') ]
    os.execv(cmdline[0], cmdline)

def main():
    set_credentials()
    exec_command(sys.argv[1:])

if __name__ == '__main__':
    main()
