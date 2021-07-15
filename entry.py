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
import re

def set_environment(uid):
    try:
        ent = pwd.getpwuid(uid)
    except KeyError:
        os.environ.pop('HOME', '')
    else:
        os.environ['HOME'] = ent.pw_dir
        os.environ['SHELL'] = ent.pw_shell

def get_uid(user):
    m = re.fullmatch(r'(\d+):(\d+)', user)
    if m:
        uid = int(m.group(1))
        gid = int(m.group(2))
        return uid, gid

    try:
        uid = int(user)
        try:
            ent = pwd.getpwuid(uid)
            return uid, ent.pw_gid
        except KeyError:
            return uid, uid
    except ValueError:
        ent = pwd.getpwnam(user)
        return ent.pw_uid, ent.pw_gid

def gather_supplemental_groups(gid):
    groups = set(os.getgroups())
    groups.discard(0) # don't keep root by default
    groups.add(gid)

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

def set_credentials(user):
    if os.getuid() != 0:
        print("Cannot set credentials: not root")
        return
    uid, gid = get_uid(user)
    groups = gather_supplemental_groups(gid)

    set_environment(uid)
    os.setgroups(groups)
    if not os.environ.get('WRLINUX_ROOT'):
        os.setgid(gid)
        os.setuid(uid)

def exec_command(command):
    cmd = [ os.environ.get('SHELL', '/bin/bash') ]
    if command:
        cmd.append('-c')
        cmd.append(' '.join(shlex.quote(a) for a in command))
    os.execv(cmd[0], cmd)

def main():
    user = sys.argv[1]
    command = sys.argv[2:]
    set_credentials(user)
    exec_command(command)

if __name__ == '__main__':
    main()
