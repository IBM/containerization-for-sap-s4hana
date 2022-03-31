# ------------------------------------------------------------------------
# Copyright 2020, 2022 IBM Corp. All Rights Reserved.
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

""" Helper tools """


# Global modules

# Standard library modules

import contextlib
import datetime
import getpass
import logging
import os
import shutil
import socket
import types
import traceback
import yaml

# Non-standard library modules

import termcolor


# Local modules

from modules.command    import (
    CmdShell,
    CmdSsh
)
from modules.exceptions import RpmFileNotFoundException
from modules.fail       import fail
from modules.quantity   import Quantity
from modules.nfstools     import (
    getOverlayBase,
    getValidNfsServerAddress
)

# Functions


@contextlib.contextmanager
def pushd(newDir):
    """ Change directory and go back to previous directory when context is left """
    # See https://stackoverflow.com/a/13847807
    oldDir = os.getcwd()
    logging.debug(f"Current directory: '{oldDir}'")
    os.chdir(newDir)
    logging.debug(f"Changed directory to: '{os.getcwd()}'")
    try:
        yield
    finally:
        os.chdir(oldDir)
        logging.debug(f"Changed directory back to: '{os.getcwd()}'")


def strBold(strVal):
    """ Return string with bold attribute """
    return termcolor.colored(strVal, attrs=['bold'])


def readInput(prompt, default, emptyOk, hidden, confirm):
    """ Read string value from stdin """
    # pylint: disable=too-many-branches

    # Get input function

    if hidden:
        inputFunc = getpass.getpass
    else:
        inputFunc = input

    # Build prompt

    if emptyOk:
        prompt = f'{prompt} - <CTRL-D> for empty value'

    if default or emptyOk:
        # Display default value if it was supplied
        # or display '' as default if input can be empty

        if hidden:
            defaultPrint = '<hidden>'
        else:
            defaultPrint = f"'{default}'"

        prompt = f"{prompt} (default: {defaultPrint})"

    prompt += ': '

    # Read input

    first = True

    while True:
        # Confirm loop - confirm input if required
        # Repeat until same input was entered two times

        while True:
            # Input loop - read input
            # Repeat until input fulfills all requirements

            try:
                inputRead = inputFunc(prompt)

                if not inputRead:
                    inputRead = default

            except EOFError:
                # <CTRL-D> was hit

                inputRead = ''
                print()

            if inputRead or emptyOk:
                break  # Exit input loop

            print(strBold('NON-EMPTY VALUE REQUIRED!'))

        if hidden and confirm:
            # Confirm is only considered for hidden input

            if first:
                # Input was read for the first time
                # Save input for confirmation and adapt prompt

                inputReadSaved = inputRead
                promptSaved = prompt
                prompt = f'(Confirm) {prompt}'
                first = False

            else:
                # Input was read for the second time
                # Exit if first and second input are equal
                # othewise restart from beginning

                if inputRead == inputReadSaved:
                    break  # Exit confirm loop

                print(strBold("ENTERED VALUES DON'T MATCH!"))

                prompt = promptSaved
                first = True
        else:
            # No confirm necessary

            break  # Exit confirm loop

    return inputRead


def getExecPath(execName, doFail=True):
    """ Get path of executable """
    execPath = shutil.which(execName)
    if not execPath:
        if doFail:
            fail(f"Did not find executable '{execName}'")
        else:
            logging.warning(f"Did not find executable '{execName}'")
    else:
        logging.info(f"Using '{execPath}' as '{execName}'")
    return execPath


def getTimestamp(withDecorator):
    """ Get a current time stamp with time zone indicator and optional decorator """
    timestamp = datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S (%Z)')
    if withDecorator:
        timestamp = '-'*20 + timestamp + '-'*20
    return timestamp


def genFileFromTemplate(templatePath, outFilePath, params):
    """ Generate file from template replacing parameters enclosed in "{{...}} """
    content = instantiateTemplate(templatePath, params)
    # pylint: disable=invalid-name, unspecified-encoding
    try:
        with open(outFilePath, 'w') as fh:
            print(content, file=fh)
    except IOError:
        fail(f"Error writing to file {outFilePath}")


def instantiateTemplate(templatePath, params):
    """ Instantiate a template file replacing parameters enclosed in "{{...}} """
    # pylint: disable=invalid-name, unspecified-encoding
    try:
        with open(templatePath, 'r') as fh:
            content = fh.read()
        for (k, v) in params.items():
            content = content.replace('{{'+k+'}}', v)
    except IOError:
        fail(f"Error reading from file {templatePath}")
    return content


def instantiateYamlTemplate(templatePath, params):
    """ Instantiate a YAML template file replacing parameters enclosed in "{{...}}
        and return a python object of the instantiated template """
    return yaml.load(instantiateTemplate(templatePath, params), Loader=yaml.Loader)


def getBuildHost():
    """ Get a host object representing the (local) build user """
    return types.SimpleNamespace(**{
        'name': socket.gethostname(),
        'ip':   socket.gethostbyname(socket.gethostname())
    })


def getBuildUser(ctx):
    """ Get a user object representing the (local) build user """
    return types.SimpleNamespace(**{
        'name':     getpass.getuser(),
        'password': '',
        'sshid':    ctx.cr.build.user.sshid
    })


def getHomeDir(ctx, hname, user):
    """ Get the absolute path of the home directory of user.name@hname """
    res = CmdSsh(ctx, hname, user).run('pwd')
    if res.rc != 0:
        logging.debug(f"Could not determine the home directory of '{user.name@hname}'")
        return ''
    return res.out


def getNumRunningSapProcs(ctx, instance):
    """ Get number of running SAP processes for a given instance """
    sidU   = getattr(ctx.cf.refsys, instance).sidU
    instno = getattr(ctx.cf.refsys, instance).instno
    host   = getattr(ctx.cf.refsys, instance).host.name
    user   = getattr(ctx.cr.refsys,  instance).sidadm

    cmd = f'/usr/sap/{sidU}/SYS/exe/hdb/sapcontrol -nr {instno}'
    cmd += ' -function GetProcessList | grep GREEN | wc -l'
    out = CmdSsh(ctx, host, user).run(cmd).out
    return out


def refSystemIsStandard(ctx):
    """ Returns true in case the reference system is a standard system, false otherwise """
    return ctx.cf.refsys.nws4.host.name == ctx.cf.refsys.hdb.host.name


def isRepoAccessible(repository):
    """ Returns True if repository is accessible, otherwise False """
    if repository == "":
        return True

    cmd = f'dnf repolist --enabled | grep {repository}'
    out = CmdShell().run(cmd).out
    if out != "":
        logging.debug(f'Access to repository {repository} is enabled')
        return True
    logging.debug(f'Cannot access repository {repository}')
    return False


def getSpsLevelHdb(cmdSsh, sidU, instno):
    """ Return SPS Level of HANA DB """
    hdbInstDir = f'/usr/sap/{sidU}/HDB{instno}'
    cmd = f'{hdbInstDir}/HDB version | grep version:'
    # Output of HDB version | grep version: looks like
    # version:             2.00.053.00.1605092543
    # SPS Level in this case : "053"
    version  = cmdSsh.run(cmd).out.split()[1]
    spsLevel = version.split(".")[2]
    return int(spsLevel)


def getRpmFileForPackage(packageName, path):
    """ Return filename for specified package """

    # do not use fail function here, cause verify-config uses this function too
    if os.path.exists(path):
        pathContent = os.listdir(path)
        if len(pathContent) < 1:
            raise RpmFileNotFoundException(path, packageName, 'is empty.')
        cmd = 'rpm -qp --queryformat "%{NAME}" '
        for file in pathContent:
            if os.path.isfile(path + '/' + file):
                # check if rpm is found
                packageNameFromRpm = CmdShell().run(cmd + path + '/' + file).out
                if packageNameFromRpm == packageName:
                    return file
    else:
        raise RpmFileNotFoundException(path, packageName, 'does not exist.')
    raise RpmFileNotFoundException(path, packageName,
                                   'does not contain a matching rpm package file.')


def getDistributionFromRefSystem(ctx, flavor):
    """ Get Distribution from host  """
    host = getattr(ctx.cf.refsys, flavor).host.name
    user = getattr(ctx.cf.refsys, flavor).sidadm
    out  = CmdSsh(ctx, host, user).run('grep -w ID /etc/os-release | cut -d "=" -f2').out
    return out.split('"')[1]


def ocpMemoryResourcesValid(ctx):
    """ validates memory resources """
    containerTypes = list(ctx.cf.ocp.containers.__dict__)
    for containerType in containerTypes:
        if containerType == 'init':
            continue

        if areContainerMemResourcesValid(ctx.cf.ocp, containerType):
            continue

        print("The specified 'limits' value is less than the "
              f"requested for container {containerType}")
        return False
    return True


def areContainerMemResourcesValid(ocp, containerType):
    """ True if limits.memory >= requests.memory  """
    containers = getattr(ocp.containers, containerType)
    limits   = containers.resources.limits.memory
    requests = containers.resources.requests.memory

    return Quantity(limits) >= Quantity(requests)


def _hostUser1IsHostUser2(host1, user1, host2, user2):
    """ Return true if the first host and user are the same as the second host and user """
    return host1.ip == host2.ip and user1.name == user2.name


def helperIsBuild(ctx):
    """ Return true if the helper host and user are the same as the build machine host and user """
    return _hostUser1IsHostUser2(ctx.cf.ocp.helper.host, ctx.cr.ocp.helper.user,
                                 getBuildHost(), getBuildUser(ctx))


def helperIsNfs(ctx):
    """ Return true if the helper host and user are the same as the NFS server host and user """
    return _hostUser1IsHostUser2(ctx.cf.ocp.helper.host, ctx.cr.ocp.helper.user,
                                 ctx.cf.nfs.host, ctx.cr.nfs.user)


def getSAPPfparValue(cmdSsh, sidU, instanceType, parameter):
    """ Return the value of a SAP Profile or environment parameter """
    if "$(" in parameter:
        parameter = parameter[2:-1]

    exeDir = getInstanceExe(sidU, instanceType)
    cmd = f"{exeDir}/sappfpar name={sidU} {parameter}"
    # sappfpar does not set rc!
    return cmdSsh.run(cmd).out


def getInstanceExe(sidU, instanceType):
    """ Return exe directory for instance """
    exeDir = f"/usr/sap/{sidU}/SYS/exe"
    if instanceType == "hdb":
        exeDir += "/hdb"
    elif instanceType == "nws4":
        exeDir += "/run"
    else:
        exeDir = ""
    return exeDir


def getCallingToolName():
    """ returns name of the tool which was called """
    return traceback.format_stack()[0].split(',')[0].split(' ')[3].split('"')[1]


def getParmsForDeploymentYamlFile(ctx, deployment):
    """ returns parms for creating the deployment description file """
    return {
        # The OCP project name
        'PROJECT': ctx.cf.ocp.project,

        # OCP deployment name
        'DEPLOYMENT_NAME': deployment.appName,

        # Overlay Uuid
        'OVERLAY_UUID': deployment.overlayUuid,

        # Last part of the init image repository name
        'INIT_IMAGE_NAME_SHORT': ctx.cf.images.init.names.short,

        # Last part of the NWS4 image repository name
        'NWS4_IMAGE_NAME_SHORT': ctx.cf.images.nws4.names.short,

        # Last part of the HDB image repository name
        'HDB_IMAGE_NAME_SHORT': ctx.cf.images.hdb.names.short,

        # Name of the ASCS container
        'NWS4_ASCS_CONTAINER_NAME': ctx.cf.ocp.containers.ascs.name,

        # Name of the DI container
        'NWS4_DI_CONTAINER_NAME': ctx.cf.ocp.containers.di.name,

        # Name of the HDB container
        'HDB_CONTAINER_NAME': ctx.cf.ocp.containers.hdb.name,

        # Name of the service account
        'SERVICE_ACCOUNT_NAME': ctx.cf.ocp.sa.name,

        # --- Parameters for NWS4 Image ---

        # SAPSID of the Netweaver S/4 SAP System
        'NWS4_SAPSID': ctx.cf.refsys.nws4.sidU,

        # Host name of the original Netweaver S/4 SAP System
        'NWS4_PQHN': ctx.cf.refsys.nws4.host.name,

        # Domain name of the original Netweaver S/4 SAP System
        'NWS4_FQHN': ctx.cf.refsys.nws4.sapfqdn,

        # -- Parameters for ASCS Instance ---

        # Instance number of the Netweaver S/4 SAP System ASCS Instance
        'NWS4_ASCS_INSTNO': ctx.cf.refsys.nws4.ascs.instno,

        # Profile name of ASCS Instance, optional. If empty, default is used
        'NWS4_ASCS_PROFILE': ctx.cf.refsys.nws4.ascs.profile,

        # Memory request for ASCS container
        'ASCS_REQUESTS_MEMORY': ctx.cf.ocp.containers.ascs.resources.requests.memory,

        # Memory limit for ASCS container
        'ASCS_LIMITS_MEMORY': ctx.cf.ocp.containers.ascs.resources.limits.memory,

        # -- Parameters for DI Instance --

        # Instance number of the Netweaver S/4 SAP System Dialog Instance
        'NWS4_DI_INSTNO': ctx.cf.refsys.nws4.di.instno,

        # Profile name of DI Instance, optional. If empty, default is used
        'NWS4_DI_PROFILE': ctx.cf.refsys.nws4.di.profile,

        # Secret name
        'NWS4_DI_DBCREDENTIALS_SECRET': ctx.cf.ocp.containers.di.secret,

        # Memory request for DI container
        'DI_REQUESTS_MEMORY': ctx.cf.ocp.containers.di.resources.requests.memory,

        # Memory limit for DI container
        'DI_LIMITS_MEMORY': ctx.cf.ocp.containers.di.resources.limits.memory,

        # --- Parameters for HDB Image ---

        # Rename HDB Host
        'HDB_RENAME_HOST': ctx.cf.refsys.hdb.rename,

        # SAPSID of the HANA DB System
        'HDB_SAPSID': ctx.cf.refsys.hdb.sidU,

        # Instance number of the HANA DB System
        'HDB_INSTNO': ctx.cf.refsys.hdb.instno,

        # Host name of the original HANA DB System
        'HDB_PQHN': ctx.cf.refsys.hdb.host.name,

        # Host name of the target HANA DB System
        'HDB_TARGET_HOST': ctx.cf.refsys.nws4.host.name,

        # Directory under which the shared directory of the HANA instance is located
        'HDB_BASE': ctx.cf.refsys.hdb.base.shared,

        # Directory under which the data directory of the HANA database is located
        'HDB_BASE_DATA': ctx.cf.refsys.hdb.base.data,

        # Directory under which the log directory of the HANA database is located
        'HDB_BASE_LOG': ctx.cf.refsys.hdb.base.log,

        # Memory request for HDB container
        'HDB_REQUESTS_MEMORY': ctx.cf.ocp.containers.hdb.resources.requests.memory,

        # Memory limit for HDB container
        'HDB_LIMITS_MEMORY': ctx.cf.ocp.containers.hdb.resources.limits.memory,

        # -- Parameters for mounting HANA DB database file systems --

        # IP address of the NFS server
        'NFS_INTRANET_IP': getValidNfsServerAddress(ctx),

        # Parent dir on NFS Server
        'NFS_PARENT_DIR': getOverlayBase(ctx, deployment.overlayUuid),
    }
