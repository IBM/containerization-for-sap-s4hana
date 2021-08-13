# ------------------------------------------------------------------------
# Copyright 2020, 2021 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

""" Helper functions for overlay filesystem setup on the NFS server """


# Global modules

import os
import types
import uuid


# Local modules

from modules.command import CmdSsh
from modules.fail    import fail


# Functions

def getHdbSubDirs():
    """ Get SAP HANA database top-level subdirectories """
    return ['data', 'log']


def getHdbCopyBase(ctx):
    """ Get base directory where SAP HANA database snapshots are copied to """
    return f'{ctx.cf.nfs.bases.copy}/{ctx.cf.refsys.hdb.host.name}/{ctx.cf.refsys.hdb.sidU}'


def getOverlayBase(ctx, overlayUuid):
    """ Get base directory under which overlay file systems for container instances are created """
    return f'{ctx.cf.nfs.bases.overlay}/{overlayUuid}'


def getOverlayDirs(ctx, subDir, overlayUuid):
    """ Get directories used for overlay filesystem setup """

    hdbSid  = ctx.cf.refsys.hdb.sidU
    baseDir = getOverlayBase(ctx, overlayUuid)
    return types.SimpleNamespace(**{
        'base':   baseDir,
        'lower':  f'{getHdbCopyBase(ctx)}/{subDir}/{hdbSid}',
        'upper':  f'{baseDir}/{subDir}-upper/{hdbSid}',
        'work':   f'{baseDir}/{subDir}-work/{hdbSid}',
        'merged': f'{baseDir}/{subDir}/{hdbSid}'
    })


def getPersistenceDir(ctx, overlayUuid):
    """ Get name of persistence directory """
    baseDir = getOverlayBase(ctx, overlayUuid)
    return f'{baseDir}/persistence'


# Classes

class Overlay():
    """ Representation of an overlay filesystem share """

    @staticmethod
    def create(ctx):
        """ Create a new overlay filesystem share on the NFS server """

        cmdSsh = CmdSsh(ctx, ctx.cf.nfs.host.name, ctx.cr.nfs.user)

        overlayUuid  = f'{uuid.uuid1()}'
        overlayUuid += f'-{ctx.cr.ocp.user.name}'
        overlayUuid += f'-{ctx.cf.ocp.project}'
        overlayUuid += f'-{ctx.cf.refsys.hdb.host.name}'
        overlayUuid += f'-{ctx.cf.refsys.hdb.sidU}'

        # Making an overlay-fs NFS-mountable requires additional mount
        # options when establishing the overlay-fs; see also:
        #
        #   https://serverfault.com/questions/949892/nfs-export-an-overlay-of-ext4-and-btrfs
        #   https://www.kernel.org/doc/Documentation/filesystems/overlayfs.txt
        #
        # XXX NEEDED OPTIONS MAY DEPEND ON FILESYSTEM TYPE OF lower, work AND upper -
        #     THIS MAY VARY FROM CUSTOMER TO CUSTOMER

        # NFS specific mount options for each overlay file system

        nfsOpts = []
        # nfsOpts.append('comment=merge')
        nfsOpts.append('nfs_export=on')
        nfsOpts.append('index=on')
        # nfsOpts.append('redirect_dir=nofollow')
        # nfsOpts.append('xino=on')

        # Create the directory structure for each overlay file system,
        # establish the overlay fs and add a corresponding entry to /etc/exports

        exportOptsGeneric = ''
        exportOptsGeneric += 'rw'
        exportOptsGeneric += ',insecure'
        exportOptsGeneric += ',no_root_squash'
        exportOptsGeneric += ',sync'

        for subDir in getHdbSubDirs():
            ovld = getOverlayDirs(ctx, subDir, overlayUuid)

            cmdSsh.run(f'mkdir -p "{ovld.upper}" "{ovld.work}" "{ovld.merged}"')

            # Add to /etc/fstab for automatic mount after reboot
            # use noauto,x-systemd.automount to mount via systemd and automount

            fstabOpts = f'noauto,x-systemd.automount,{",".join(nfsOpts)},'
            fstabOpts += f'lowerdir={ovld.lower},upperdir={ovld.upper},workdir={ovld.work}'
            cmdSsh.run(f'echo "overlay {ovld.merged} overlay {fstabOpts} 0 0" >> /etc/fstab')

            mountCmd = f'mount {ovld.merged}'

            cmdSsh.run(mountCmd)

            # Need to make the file systems unique - otherwise rpc.mountd
            # will always offer the first mounted file system.

            exportOpts = exportOptsGeneric + f',fsid={uuid.uuid1()}'

            cmdSsh.run(f'echo "{ovld.merged} *({exportOpts})" >> /etc/exports')

        # Create the persistence directories

        persistenceDir = getPersistenceDir(ctx, overlayUuid)

        persistenceDirNws4 = f'{persistenceDir}/{ctx.cf.refsys.nws4.sidU}'

        cmdSsh.run(f'mkdir -p "{persistenceDirNws4}"')
        cmdSsh.run(f'chown {ctx.cf.refsys.nws4.sidadm.uid}:{ctx.cf.refsys.nws4.sidadm.gid}'
                   f' "{persistenceDirNws4}"')
        cmdSsh.run(f'chmod 755 "{persistenceDirNws4}"')

        persistenceDirHdb = f'{persistenceDir}/{ctx.cf.refsys.hdb.sidU}'

        cmdSsh.run(f'mkdir -p "{persistenceDirHdb}"')
        cmdSsh.run(f'chown {ctx.cf.refsys.hdb.sidadm.uid}:{ctx.cf.refsys.hdb.sidadm.gid}'
                   f' "{persistenceDirHdb}"')
        cmdSsh.run(f'chmod 755 "{persistenceDirHdb}"')

        cmdSsh.run(f'echo "{persistenceDir} *({exportOptsGeneric})" >> /etc/exports')

        # Export the overlay and persistence file systems

        cmdSsh.run('exportfs -ar')

        # Return the uuid of the created file systems

        return Overlays(ctx).find(overlayUuid)

    # Instance methods

    # pylint: disable=too-many-arguments

    def __init__(self, ctx, overlayUuid, creationDate, creationTime):
        """ Create an internal data structure representing an
            existing overlay filesystem share on the NFS server """

        self._ctx = ctx

        self.uuid = overlayUuid
        self.date = creationDate
        self.time = creationTime

        self._cmdSsh = CmdSsh(ctx, ctx.cf.nfs.host.name, ctx.cr.nfs.user)

    def __str__(self):
        return f"{self.uuid} ({self.date} {self.time})"

    def delete(self):
        """ Delete an overlay filesystem share on the NFS server """

        # Remove the entries for the overlay and persistence file systems from /etc/exports

        self._cmdSsh.run(f'sed -i.backup -e "/.*{self.uuid}.*/d" /etc/exports')

        # Remove the entries for the overlay and persistence file systems from /etc/fstab

        self._cmdSsh.run(f'sed -i.backup -e "/overlay .*{self.uuid}.*/d" /etc/fstab')

        # Remove the overlay file systems from the table of exported NFS file systems

        self._cmdSsh.run('exportfs -ar')

        # Tear down all overlay file systems

        for subDir in getHdbSubDirs():
            ovld = getOverlayDirs(self._ctx, subDir, self.uuid)
            self._cmdSsh.run(f'umount {ovld.merged}')
            self._cmdSsh.run(f'rm -rf {ovld.base}/{subDir}*/* 2>/dev/null')
            self._cmdSsh.run(f'rmdir -p {ovld.base}/{subDir}* 2>/dev/null')

        # Tear down the persistence file system

        persistenceDir = getPersistenceDir(self._ctx, self.uuid)

        self._cmdSsh.run(f'rm -rf {persistenceDir}/* 2>/dev/null')
        self._cmdSsh.run(f'rmdir -p {persistenceDir} 2>/dev/null')


class Overlays():
    """ Existing overlay file system shares """

    def __init__(self, ctx):

        cmdSsh = CmdSsh(ctx, ctx.cf.nfs.host.name, ctx.cr.nfs.user)
        lssCmd = f"ls -ladtr --time-style=long-iso {ctx.cf.nfs.bases.overlay}/*-*-*-*-*"

        self._overlays = []

        for line in cmdSsh.run(lssCmd, rcOk=(0, 1, 2)).out.split('\n'):
            if not line or line == '':
                continue
            (_d1, _d2, _d3, _d4, _d5, creationDate, creationTime, file) = line.split()
            self._overlays.append(
                Overlay(ctx, os.path.basename(file), creationDate, creationTime)
            )

    def get(self):
        """ Get list of existing overlay filesystem shares """
        return self._overlays

    def find(self, uuidPrefix):
        """ Find an existing overlay which matches a given UUID prefix """

        found = [ovl for ovl in self._overlays if ovl.uuid.startswith(uuidPrefix)]

        if len(found) < 1:
            fail(f"Found no matching overlay uuid for uuid prefix '{uuidPrefix}'")

        elif len(found) > 1:
            msg = f"Overlay uuid prefix '{uuidPrefix}' matches more than one uuid:\n"
            for ovl in found:
                msg += f'  {ovl}\n'
            fail(msg)

        return found[0]
