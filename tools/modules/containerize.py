# ------------------------------------------------------------------------
# Copyright 2022 IBM Corp. All Rights Reserved.
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

""" Calls to external tools """


# Global modules

# Local modules

from modules.command  import CmdShell
from modules.fail     import fail
from modules.nfstools import Overlays
from modules.ocp      import Ocp

# Public methods


def copyHdb(ctx):
    """ Copy snapshot of HANA DB to NFS server (automation option) """
    print(_genHeader1(f"Copying snapshot of HANA DB '{ctx.cf.refsys.hdb.sidU}'"
                      f" to NFS server '{ctx.cf.nfs.host.name}'"))
    cmd = f'time {ctx.cf.build.repo.root}/tools/nfs-hdb-copy'
    cmd += ctx.ar.commonArgsStr
    _runCmd(cmd)


def buildImages(ctx):
    """ Build images for all flavors (automation option) """
    for flavor in ctx.config.getImageFlavors():
        print(_genHeader1(f"Building image for flavor '{flavor}'"))
        cmd = f'time {ctx.cf.build.repo.root}/tools/image-build'
        cmd += f' -f {flavor}'
        cmd += ctx.ar.commonArgsStr
        _runCmd(cmd)


def pushImages(ctx):
    """ Push images for all flavors to OCP (automation option) """
    for flavor in ctx.config.getImageFlavors():
        print(_genHeader1(f"Pushing image for flavor '{flavor}'"))
        cmd = f'time {ctx.cf.build.repo.root}/tools/image-push'
        cmd += f' -f {flavor}'
        cmd += ctx.ar.commonArgsStr
        _runCmd(cmd)


def setupOverlayShare(ctx, overlayUuid=None, out=True):
    """ Setup an overlay share on NFS server (automation option) """
    if out:
        print(_genHeader1('Setting up overlay share'))
    cmd = f'time {ctx.cf.build.repo.root}/tools/nfs-overlay-setup'
    if overlayUuid:
        cmd += f' -u {overlayUuid}'
    cmd += ctx.ar.commonArgsStr
    overlayUuid = _runCmd(cmd).out
    if out:
        print(overlayUuid)
    return overlayUuid


def createDeploymentFile(ctx, overlayUuid, out=True):
    """ Create deployment description file (automation option) """
    if out:
        print(_genHeader1('Creating deployment description file'))
    cmd = f'time {ctx.cf.build.repo.root}/tools/ocp-deployment'
    cmd += ' --gen-yaml'
    cmd += f' -u {overlayUuid}'
    cmd += ctx.ar.commonArgsStr
    deploymentFile = _runCmd(cmd).out
    if out:
        print(deploymentFile)
    return deploymentFile


def startDeployment(ctx, deploymentFile=None, out=True):
    """ Start deployment using deployment file (automation option) """
    if out:
        print(_genHeader1(f"Starting deployment using file '{deploymentFile}'"))
    if not deploymentFile:
        deploymentFile = ctx.ar.deployment_file
    ocp = Ocp(ctx)
    ocp.ocApply(deploymentFile, printRunTime=True)
    del ocp


def listOverlayShares(ctx):
    """ List all overlay shares on NFS server (manual option) """
    # print(_genHeader1('List of existing overlay shares:'))
    cmd = f'time {ctx.cf.build.repo.root}/tools/nfs-overlay-list'
    cmd += ctx.ar.commonArgsStr
    return _runCmd(cmd).out


def tearDownOverlayShare(ctx, overlayUuid, out=True):
    """ Tear down an overlay share on NFS server (manual option) """
    overlayUuid = getOverlayUuid(ctx, overlayUuid)
    if out:
        print(_genHeader1(f'Tearing down overlay share {overlayUuid}'))
    cmd = f'{ctx.cf.build.repo.root}/tools/nfs-overlay-teardown'
    cmd += f' -u {overlayUuid}'
    cmd += ctx.ar.commonArgsStr
    _runCmd(cmd)


def stopDeployment(ctx, deploymentFile=None, out=True):
    """ Stop deployment using deployment file (manual option) """
    if not deploymentFile:
        deploymentFile = ctx.ar.deployment_file
    if out:
        print(_genHeader1(f"Stopping deployment using file '{deploymentFile}'"))
    ocp = Ocp(ctx)
    ocp.ocDelete(deploymentFile, printRunTime=True)
    del ocp

# Private Methods


def _genHeader(header, lineChar):
    """ Generate header string (generic) """
    return lineChar*60+'\n'+header+'\n'+lineChar*60


def _genHeader1(header):
    """ Generate header string (level 1 header) """
    return _genHeader(header, '=')


def _genHeader2(header):
    """ Generate header string (level 2 header) """
    return _genHeader(header, '-')


def getOverlayUuid(ctx, overlayUuid):
    """ Get overlay UUID from parameter or cli argument.
        Exit, if no overlay UUID can be determined """
    if not overlayUuid:
        if ctx.ar.overlay_uuid:
            overlayUuid = ctx.ar.overlay_uuid
        else:
            fail("Please specify an overlay share UUID via option '-u'")

    return Overlays(ctx).find(overlayUuid).uuid


def _runCmd(cmd):
    result = CmdShell().run(cmd)
    if result.rc != 0:
        msg = ''
        msg += f"Command '{cmd}' failed"
        msg += f'\n  stdout: >>>{result.out}<<<'
        msg += f'\n  stderr: >>>{result.err}<<<'
        msg += f'\n  rc: {result.rc}'
        fail(msg)
    return result
