# ------------------------------------------------------------------------
# Copyright 2020 IBM Corp. All Rights Reserved.
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

import types

# Functions


def getHdbSubDirs():
    """ Get SAP HANA database top-level subdirectories """
    return ['data', 'log']


def getHdbCopyBase(config):
    """ Get base directory where SAP HANA database snapshots are copied to """
    return f'{config.nfs.copyBase}/{config.flavor.hdb.host}/{config.flavor.hdb.sid.upper()}'


def getOverlayBase(config, uuid):
    """ Get base directory under which overlay file systems for container instances are created """
    return f'{config.nfs.overlayBase}/{uuid}'


def getOverlayDirs(config, subDir, uuid):
    """ Get directories used for overlay filesystem setup """
    # pylint: disable=bad-whitespace
    hdbSid  = config.flavor.hdb.sid.upper()
    baseDir = getOverlayBase(config, uuid)
    return types.SimpleNamespace(**{
        'base':   baseDir,
        'lower':  f'{getHdbCopyBase(config)}/{subDir}/{hdbSid}',
        'upper':  f'{baseDir}/{subDir}-upper/{hdbSid}',
        'work':   f'{baseDir}/{subDir}-work/{hdbSid}',
        'merged': f'{baseDir}/{subDir}/{hdbSid}'
    })
