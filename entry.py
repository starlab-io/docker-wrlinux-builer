#!/usr/bin/python3

"""
This entry point sets supplemental group(s) in a more flexible way than
crops/poky, and in a way that works with our GitLab runners. We can't
statically set docker container groups through the GitLab runner's config,
unfortunately, so we need to do so dynamically on container startup.

We will add groups of a few files and directories (kvm, sstate cache,
etc.)
"""

import os
import sys
import pwd
import shlex

def set_environment(uid):
    try:
        ent = pwd.getpwuid(uid)
    except KeyError:
        os.environ.pop('HOME', '')
    else:
        os.environ['HOME'] = ent.pw_dir
        os.environ['SHELL'] = ent.pw_shell

def gather_supplemental_groups():
    groups = set(os.getgroups())
    groups.add(os.getgid())

    # Gather groups based on interesting files/dirs
    extras = [
        os.getcwd(),
        '/dev/kvm',
        '$SSTATE_DIR',
        '/var/lib/sstate',
        '$CI_PROJECT_DIR',
        '$STARLAB_LAYERS',
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
        return
    groups = gather_supplemental_groups()
    os.setgroups(groups)

def exec_command(command):
    cmd = [ os.environ.get('SHELL', '/bin/bash') ]
    if command:
        cmd.append('-c')
        cmd.append(' '.join(shlex.quote(a) for a in command))
    os.execv(cmd[0], cmd)

def main():
    set_credentials()
    exec_command(sys.argv[1:])

if __name__ == '__main__':
    main()
