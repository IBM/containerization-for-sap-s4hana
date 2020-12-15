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

""" Verify settings in configuration YAML file (helper functions) """

# Global modules

# None

# Local modules

from modules.command import (
    CmdShell,
    CmdSsh
)
from modules.tools   import getOcLoginCmd


# Functions


def verifyOcp(ocp):
    """ Verify OCP settings """
    success = True
    out = _OcLoginTest(ocp)
    if _isOcpDomainNameValid(out):
        print(f'OCP domain name is valid.')
        if _isOcpCredentialsValid(out):
            print(f'OCP user and password are valid.')
            if _isOcpProjectValid(ocp):
                print(f'OCP project is valid.')
            else:
                print(f"OCP project '{ocp.project}' does not exist.")
                success = False
        else:
            print(f"OCP user '{ocp.user}' and/or password are invalid.")
            success = False
    else:
        print(f"OCP domain name '{ocp.domain}' is invalid.")
        success = False
    return success


def verifyNfs(nfs):
    """ Verify NFS settings """
    success = True
    if _isNfsHostNameValid(nfs):
        print(f'NFS host is valid.')
        if _isNfsUserNameValid(nfs):
            print(f'NFS user is valid.')
            if _isNfsCopyBaseDirValid(nfs):
                print(f'NFS copyBase is valid.')
            else:
                print(f"NFS copyBase '{nfs.copyBase}' is invalid.")
                success = False

            if _isNfsOverlayBaseDirValid(nfs):
                print(f'NFS overlayBase is valid.')
            else:
                print(f"NFS overlayBase '{nfs.overlayBase}' is invalid.")
                success = False
        else:
            print(f"NFS user '{nfs.user}' is invalid "
                  f'or ssh is not set up correctly.')
            print(f"Check first the existence of '{nfs.user}' on '{nfs.host}'.")
            print(f'If exists, check the ssh connection by executing: '
                  f'ssh {nfs.user}@{nfs.host}')
            success = False
    else:
        print(f"NFS host '{nfs.host}' is invalid.")
        success = False

    return success


def verifyNws4(nws4):
    """ Verify settings for flavor 'nws4' """
    success = True
    if _isNws4HostNameValid(nws4):
        print(f'NWS4 host is valid.')
        if _isNws4UserNameValid(nws4):
            print(f'NWS4 user is valid.')
            if _isNws4SidValid(nws4):
                print(f'NWS4 SAP system ID is valid.')
            else:
                print(f'NWS4 SAP system ID is invalid.')
                success = False
        else:
            print(f"NWS4 user '{nws4.user}' is invalid "
                  f'or ssh is not set up correctly.\n'
                  f"Check first the existence of '{nws4.user}' on '{nws4.host}'.\n"
                  f'If exists, check the ssh connection by executing: '
                  f'ssh {nws4.user}@{nws4.host}')
            success = False
    else:
        print(f"NWS4 host '{nws4.host}' is invalid.")
        success = False

    return success


def verifyHdb(hdb):
    """ Verify settings for flavor 'hdb' """
    success = True
    if _isHdbHostNameValid(hdb):
        print(f'HDB host is valid.')
        if _isHdbUserNameValid(hdb):
            print(f'HDB user is valid.')
            if _isHdbSidValid(hdb):
                print(f'HDB SAP system ID is valid.')
            else:
                print(f"HDB SAP system ID '{hdb.sid}' is invalid.")
                success = False
            if _isHdbBaseDirValid(hdb):
                print(f'HDB base directory is valid.')
            else:
                print(f"HDB base directory '{hdb.base}' is invalid.")
                success = False
        else:
            print(f"HDB user '{hdb.user}' is invalid "
                  f'or ssh is not set up correctly.\n'
                  f"Check first the existence of '{hdb.user}' on '{hdb.host}'.\n"
                  f'If exists, check the ssh connection by executing: '
                  f'ssh {hdb.user}@{hdb.host}')
            success = False
    else:
        print(f"HDB host '{hdb.host}' is invalid.")
        success = False

    return success


def verifySAPSystem(config, sysType="Central"):
    """ Verify SAP system setup """
    success = True
    if sysType == "Central":
        if not config.flavor.nws4.host == config.flavor.hdb.host:
            # TODO? Check ip-addresses?
            success = False
            print(f"Error: The HANADB database '{config.flavor.hdb.sid}' "
                  f'must run on the same host as the NWS4 SAP System.')

    if not _isHdbSidInDefaultPfl(config):
        print(f'Error: You must not use a different HANADB SAP System '
              f"than specified for the NWS4 SAP System '{config.flavor.nws4.sid}'.")
        success = False
    return success


def verifySshConnection(config):
    """ Verify SSH connection from NFS host to HDB host """
    success = True
    cmdSsh = CmdSsh(config.nfs.host, config.nfs.user)
    sourceDir = f'{config.flavor.hdb.user}@{config.flavor.hdb.host}:'
    sourceDir += f'{config.flavor.hdb.base}/data/{config.flavor.hdb.sid}/*'
    targetDir = f'~/{config.flavor.hdb.sid}'

    out = cmdSsh.run(f"rsync -avrn '{sourceDir}' '{targetDir}'").err
    if 'Connection reset' in out or 'Host key verification failed' in out:
        print(f"Cannot access '{config.flavor.hdb.host}' "
              f"from '{config.nfs.host}'.\n"
              f"Error message: '{out}'\n"
              f"Check the ssh connection between '{config.nfs.host}' "
              f"and '{config.flavor.hdb.host}'.")
        success = False
    else:
        print(f"SSH connection to HDB host '{config.flavor.hdb.host}' "
              f"from NFS host '{config.nfs.host}' was successful.")
    return success

# Private functions


def _isOcpDomainNameValid(out):
    return 'no such host' not in out


def _isOcpCredentialsValid(out):
    condFail1 = (out.startswith('Login failed')
                 and 'Verify you have provided correct credentials' in out)
    condFail2 = not (out.startswith('Logged into')
                     or out.startswith('Login successful'))
    return not (condFail1 or condFail2)


def _OcLoginTest(ocp):
    return CmdShell().run(getOcLoginCmd(ocp)).out


def _isOcpProjectValid(ocp):
    # Assumes that an 'oc login' has been performed beforehand
    cmd = f'oc get project {ocp.project}'
    out = CmdShell().run(cmd).err
    return not (out.startswith('No resources found.')
                and 'cannot get resource' in out
                and 'namespace' in out
                )


def _isNws4HostNameValid(nws4):
    return _isHostNameValid(nws4.host, nws4.user)


def _isNws4UserNameValid(nws4):
    return _isUserNameValid(nws4.host, nws4.user)


def _isNws4SidValid(nws4):
    return _isSidInUsrSapServices(nws4)


def _isHdbHostNameValid(hdb):
    return _isHostNameValid(hdb.host, hdb.user)


def _isHdbUserNameValid(hdb):
    return _isUserNameValid(hdb.host, hdb.user)


def _isHdbSidValid(hdb):
    return _isSidInUsrSapServices(hdb)


def _isHdbBaseDirValid(hdb):
    cmdSsh = CmdSsh(hdb.host, hdb.user)
    out = cmdSsh.run(f' ls {hdb.base}').out
    # TODO: validate if hdb.sid in hdb.base/log hdb.base/data and hdb.base/shared
    return 'data' in out and 'log' in out and 'shared' in out


def _isNfsHostNameValid(nfs):
    return _isHostNameValid(nfs.host, nfs.user)


def _isNfsUserNameValid(nfs):
    return _isUserNameValid(nfs.host, nfs.user)


def _isNfsCopyBaseDirValid(nfs):
    return _isNfsBaseValid(nfs.host, nfs.user, nfs.copyBase)


def _isNfsOverlayBaseDirValid(nfs):
    return _isNfsBaseValid(nfs.host, nfs.user, nfs.overlayBase)


def _isUserNameValid(host, user):
    out = _checkSshLogin(host, user)
    return 'Permission denied' not in out and 'Connection reset' not in out


def _isHostNameValid(host, user):
    out = _checkSshLogin(host, user)
    return 'Could not resolve hostname' not in out


def _checkSshLogin(host, user):
    cmd = f'ssh -o BatchMode=yes {user}@{host} exit'
    return CmdShell().run(cmd).err


def _isSidInUsrSapServices(parms):
    cmdSsh = CmdSsh(parms.host, parms.user)
    out = cmdSsh.run(f' grep {parms.sid} /usr/sap/sapservices | wc -l').err
    return not out.startswith('0')


def _isNfsBaseValid(host, user, base):
    cmdSsh = CmdSsh(host, user)
    out = cmdSsh.run(f' ls {base}').err
    return 'No such file or directory' not in out


def _isHdbSidInDefaultPfl(config):
    defaultPfl = f'/usr/sap/{config.flavor.nws4.sid}/SYS/profile/DEFAULT.PFL'
    cmdSsh = CmdSsh(config.flavor.nws4.host, config.flavor.nws4.user)
    out = cmdSsh.run(f' grep dbs/hdb/dbname {defaultPfl}').out
    return config.flavor.hdb.sid in out
