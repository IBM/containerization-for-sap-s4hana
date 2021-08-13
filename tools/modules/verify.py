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

""" Verify settings in configuration YAML file (helper functions) """


# Global modules

# None


# Local modules

from modules.command    import (
    CmdShell,
    CmdSsh
)
from modules.constants  import getConstants
from modules.exceptions import RpmFileNotFoundException
from modules.ocp        import ocLogin
from modules.tools      import (
    refSystemIsStandard,
    areContainerMemResourcesValid,
    getRpmFileForPackage,
    strBold,
    getHdbCopySshCommand
)


# Functions for formatting the output

def showMsgOk(text):
    """ print text with header """
    print("[Ok   ] " + text)


def showMsgErr(text):
    """ print text with header """
    print('[' + strBold('Error') + '] ' + text)


def showMsgInd(text):
    """ print text with header """
    print("[.....] " + text)


# Classes

class Verify():
    """ Verify various configuration settings """

    def __init__(self, ctx):

        self._ctx = ctx

        self._cmdSshNfs  = CmdSsh(ctx, ctx.cf.nfs.host.name, ctx.cr.nfs.user,
                                  reuseCon=False)
        self._cmdSshNws4 = CmdSsh(ctx, ctx.cf.refsys.nws4.host.name, ctx.cr.refsys.nws4.sidadm,
                                  reuseCon=False)
        self._cmdSshHdb  = CmdSsh(ctx, ctx.cf.refsys.hdb.host.name, ctx.cr.refsys.hdb.sidadm,
                                  reuseCon=False)

    # Public methods

    def verify(self):
        """ Verify various configuration settings """

        success = True

        success = self._verifyOcp()                  and success
        success = self._verifyImages()               and success
        success = self._verifyNws4()                 and success
        success = self._verifyHdb()                  and success
        success = self._verifyNfs()                  and success
        success = self._verifySapSystem()            and success
        success = self.verifyNfsToHdbSshConnection() and success

        return success

    def verifyNfsToHdbSshConnection(self, doPrint=True):
        """ Verify SSH connection from NFS host to HDB host """
        hdbUser = self._ctx.cr.refsys.hdb.sidadm
        hdbHost = self._ctx.cf.refsys.hdb.host

        testSsh, testSshSecrets = getHdbCopySshCommand(self._ctx, withLogin=True, reuseCon=False)

        # set dummy command
        testSsh = testSsh + " true"

        result = self._cmdSshNfs.run(testSsh, testSshSecrets)

        success = result.rc == 0

        if doPrint:

            nfsUser = self._ctx.cr.nfs.user
            nfsHost = self._ctx.cf.nfs.host.name

            if success:
                showMsgOk(f"SSH connection to HDB host '{hdbHost.name}' "
                          f"from NFS host '{nfsHost}' was successful.")
            else:
                showMsgErr(f"Cannot establish ssh connection '{nfsUser.name}@{nfsHost}"
                           f" → '{hdbUser.name}@{hdbHost.ip}' ('{hdbUser.name}@{hdbHost.name}').")
                showMsgInd(f"Error message: '{result.out}'")
                showMsgInd("Check the ssh connection"
                           f" '{nfsUser.name}@{nfsHost}' → '{hdbUser.name}@{hdbHost.ip}'.")

        return success

    # Private methods

    def _verifyOcp(self):
        """ Verify OCP settings """
        # pylint: disable=too-many-statements

        def isDomainNameValid(loginAnsw):
            return 'no such host' not in loginAnsw

        def isCredentialsValid(loginAnsw):
            condFail1 = (loginAnsw.startswith('Login failed')
                         and 'Verify you have provided correct credentials' in loginAnsw)
            condFail2 = not (loginAnsw.startswith('Logged into')
                             or loginAnsw.startswith('Login successful'))
            return not (condFail1 or condFail2)

        def isProjectValid(project):
            # Assumes that an 'oc login' has been performed beforehand
            cmd = f'oc get project {project} -o custom-columns=NAME:.metadata.name --no-headers'
            # The command behaves as follows:
            # - If the project exists in the OpenShift cluster its name is printed to stdout.
            # - If it does not exist nothing is printed to stdout and an error message is printed
            #   to stderr
            return project in CmdShell().run(cmd).out

        def areResourcesValid(ocp, containerType):
            return areContainerMemResourcesValid(ocp, containerType)

        def isSecretExisting(secret):
            # Assumes that an 'oc login' has been performed beforehand
            cmd = f'oc describe secret {secret}'
            out = CmdShell().run(cmd).err
            return not out.startswith('Error from server')

        def verifySetup(ocp, loginAnsw):
            success = True
            if isDomainNameValid(loginAnsw):
                showMsgOk("OCP domain name is valid.")
                if isCredentialsValid(loginAnsw):
                    showMsgOk("OCP user and password are valid.")
                    if isProjectValid(ocp.project):
                        showMsgOk("OCP project is valid.")
                    else:
                        showMsgErr(f"OCP project '{ocp.project}' does not exist.")
                        success = False
                else:
                    showMsgErr(f"OCP user '{user.name}' and/or password are invalid.")
                    success = False
            else:
                showMsgErr(f"OCP domain name '{ocp.domain}' is invalid.")
                success = False

            return success

        def verifyResources(ocp):
            success = True
            for containerType in self._ctx.config.getContainerFlavors():
                if containerType == 'init':
                    continue
                if areResourcesValid(ocp, containerType):
                    showMsgOk("OCP memory resources for container type "
                              f"'{containerType}' are valid.")
                else:
                    showMsgErr(f"OCP memory limit for container type '{containerType}' "
                               f"is less than the value specified for requested memory.")
                    success = False
            return success

        def verifySecret(ocp):
            success = True
            if not refSystemIsStandard(self._ctx):
                secret = ocp.containers.di.secret
                if secret:
                    if isSecretExisting(secret):
                        showMsgOk(f"OCP secret '{secret}' exists.")
                    else:
                        showMsgErr(f"Specified OCP secret '{secret}' "
                                   "was not found in OCP cluster.")
                        showMsgInd("Make sure the secret exists and is "
                                   "created in the right project.")
                        success = False
                else:
                    showMsgErr("Reference system is a distributed system.")
                    showMsgInd("You must specify the name of an OCP secret in the config.yaml file")
                    showMsgInd("containing the information about the "
                               "SAP HANA DB user and password.")
                    success = False

            return success

        ocp     = self._ctx.cf.ocp
        user    = self._ctx.cr.ocp.user

        success = verifySetup(ocp, ocLogin(self._ctx, user))
        success = success and verifyResources(ocp)
        success = success and verifySecret(ocp)

        return success

    def _verifyImages(self):
        """ verify Settings for images """

        def _isRpmFileForPackageAvailable(packageName, path):
            try:
                getRpmFileForPackage(packageName, path)
                return True
            except RpmFileNotFoundException as exp:
                print(exp.errorText)
                return False

        def _getImageTypes(ctx):
            return list(ctx.cf.images.__dict__)

        success = True

        defaultPackagesDir = getConstants().defaultPackagesDir

        for flavor in _getImageTypes(self._ctx):
            if flavor == "init":
                continue
            packages = getattr(self._ctx.cf.images, flavor).packages
            for package in packages:
                if package.dnfInstallable:
                    showMsgOk(f"Package {package.packageName} installable via dnf install.")
                else:
                    if _isRpmFileForPackageAvailable(package.packageName, defaultPackagesDir):
                        showMsgOk(f"Package {package.packageName} installable via rpm.")
                    else:
                        showMsgErr(f"Package {package.packageName} not found "
                                   "in {defaultPackagesDir}.")
                        success = False
        return success

    def _verifyNfs(self):
        """ Verify NFS settings """
        nfs     = self._ctx.cf.nfs
        user    = self._ctx.cr.nfs.user
        success = True

        if self._isHostNameValid(self._cmdSshNfs):
            showMsgOk("NFS host is valid.")
            if self._isUserValid(self._cmdSshNfs):
                showMsgOk("NFS user is valid.")
            else:
                showMsgErr(f"NFS user '{user.name}' is invalid "
                           f"or ssh is not set up correctly.")
                showMsgInd(f"Check first the existence of '{user.name}' on '{nfs.host.name}'.")
                showMsgInd(f"If exists, check the ssh connection by executing: "
                           f"ssh {user.name}@{nfs.host.name}")
                success = False
        else:
            showMsgErr(f"NFS host '{nfs.host.name}' is invalid.")
            success = False

        return success

    def _verifyNws4(self):
        """ Verify settings for reference system component 'nws4' """
        return self._verifyRefSys('nws4', self._cmdSshNws4)

    def _verifyHdb(self):
        """ Verify settings for reference system component 'hdb' """
        success = self._verifyRefSys('hdb', self._cmdSshNws4)
        if success:
            if self._isHdbBaseDirValid():
                showMsgOk("HDB base directory is valid.")
            else:
                showMsgErr(f"HDB base directory '{self._ctx.cf.refsys.hdb.base}' is invalid.")
                success = False

        return success

    def _verifyRefSys(self, component, cmdSsh):
        """ Verify settings for given component' """
        compUp   = component.upper()
        sidU     = getattr(self._ctx.cf.refsys, component).sidU
        hostname = getattr(self._ctx.cf.refsys, component).host.name
        user     = getattr(self._ctx.cr.refsys, component).sidadm
        success  = True

        if self._isHostNameValid(cmdSsh):
            showMsgOk(f"{compUp} host is valid.")
            if self._isUserValid(cmdSsh):
                showMsgOk(f"{compUp} user is valid.")
                if self._isSidInUsrSapServices(cmdSsh, sidU):
                    showMsgOk(f"{compUp} SAP system ID is valid.")
                else:
                    showMsgErr(f"{compUp} SAP system ID is invalid.")
                    success = False
            else:
                showMsgErr(f"{compUp} user '{user.name}' is invalid "
                           f"or ssh is not set up correctly.")
                showMsgInd(f"Check first the existence of '{user.name}' on '{hostname}'.")
                showMsgInd(f"If exists, check the ssh connection by executing: "
                           f"ssh {user.name}@{hostname}")
                success = False
        else:
            showMsgErr(f"{compUp} host '{hostname}' is invalid.")
            success = False

        return success

    def _verifySapSystem(self):
        """ Verify SAP system setup """
        success = True
        if refSystemIsStandard(self._ctx):
            if not self._ctx.cf.refsys.nws4.host.name == self._ctx.cf.refsys.hdb.host.name:
                success = False
                showMsgErr(f"The HANADB database '{self._ctx.cf.refsys.hdb.sidU}' "
                           "must run on the same host as the NWS4 SAP System.")

        if not self._isHdbSidInDefaultPfl():
            showMsgErr("You must not use a different HANADB SAP System "
                       f"than specified for the NWS4 SAP System '{self._ctx.cf.refsys.nws4.sidU}'.")
            success = False
        return success

    def _isHostNameValid(self, cmdSsh):
        out = self._checkSshLogin(cmdSsh)
        return 'Could not resolve hostname' not in out

    def _isUserValid(self, cmdSsh):
        out = self._checkSshLogin(cmdSsh)
        return 'Permission denied' not in out and 'Connection reset' not in out

    def _checkSshLogin(self, cmdSsh):
        return cmdSsh.run('true').err

    def _isSidInUsrSapServices(self, cmdSsh, sidU):
        out = cmdSsh.run(f' grep {sidU} /usr/sap/sapservices | wc -l').err
        return not out.startswith('0')

    def _isDirValid(self, cmdSsh, directory):
        out = cmdSsh.run(f' ls {directory}').err
        return 'No such file or directory' not in out

    def _isHdbBaseDirValid(self):
        out = self._cmdSshHdb.run(f' ls {self._ctx.cf.refsys.hdb.base}').out
        return 'data' in out and 'log' in out and 'shared' in out

    def _isHdbSidInDefaultPfl(self):
        defaultPfl = f'/usr/sap/{self._ctx.cf.refsys.nws4.sidU}/SYS/profile/DEFAULT.PFL'
        out = self._cmdSshNws4.run(f' grep dbs/hdb/dbname {defaultPfl}').out
        return self._ctx.cf.refsys.hdb.sidU in out


class VerifyOcp():
    """ Verify various ocp settings """

    def __init__(self, ctx):

        self._ctx = ctx
        ocLogin(ctx, ctx.cr.ocp.admin)
        self._workerNodes = CmdShell().run(
            'oc get nodes'
            + ' --selector="node-role.kubernetes.io/worker"'
            + " -o template --template"
            + " '{{range .items}}{{.metadata.name}}{{"+r'"\n"'+"}}{{end}}'"
        ).out.split()

    # Public methods

    def verify(self):
        """ Verify various ocp settings """

        success = True
        success = self._verifySccForProject()        and success
        success = self._verifyOcpServiceAccount()    and success
        if not self._workerNodes:
            showMsgErr("Could not retrieve list of worker nodes.")
            showMsgInd("SELinux and pid limit settings cannot be verified!")
            success = False
        else:
            success = self._verifySeLinux()          and success
            success = self._verifyPidLimit()         and success
        return success

    # Private methods
    def _runSshJumpCmd(self, worker, cmd):
        ctx = self._ctx
        innerSshCmd =  'ssh'
        if ctx.cr.ocp.helper.user.sshid:
            innerSshCmd += ' -i {ctx.cr.ocp.helper.user.sshid}'
        innerSshCmd += ' -o StrictHostKeyChecking=no'
        innerSshCmd += f' core@{worker} {cmd}'

        helperHost  = ctx.cf.ocp.helper.host
        helperUser  = ctx.cr.ocp.helper.user

        res = CmdSsh(ctx, helperHost.name, helperUser, reuseCon=False).run(innerSshCmd)

        rval = res.out

        if res.rc != 0:
            showMsgErr(f"Could not execute SSH command on worker node '{worker}'"
                       f" as user '{helperUser.name}' on helper node '{helperHost.name}'")
            showMsgInd(f"({res.err})")
            rval = 'SSH CONNECT ERROR'

        return rval

    def _verifySccForProject(self):
        ocp = self._ctx.cf.ocp

        out = CmdShell().run(
            'oc adm policy who-can use scc anyuid'
            " -o template --template='{{range .groups}}{{.}}{{"+r'"\n"'+"}}{{end}}'"
        ).out.split()

        if f'system:serviceaccounts:{ocp.project}' in out:
            showMsgOk("Security Context Constraint 'anyuid' is valid.")
            return True

        showMsgErr(f"Project '{ocp.project}' does not have "
                   "the 'anyuid' Security Context Constraint permission.")
        showMsgInd("Logon as kube:admin and execute:")
        showMsgInd("      oc adm policy add-scc-to-group anyuid"
                   f' "system:serviceaccounts:{ocp.project}"\n')
        return False

    def _verifyOcpServiceAccount(self):
        ocp = self._ctx.cf.ocp

        out = CmdShell().run(
            'oc adm policy who-can use scc hostmount-anyuid'
            " -o template --template='{{range .users}}{{.}}{{"+r'"\n"'+"}}{{end}}'"
        ).out.split()

        if f'system:serviceaccount:{ocp.project}:{ocp.project}-sa' in out:
            showMsgOk("Security Context Constraint 'hostmount-anyuid' is valid.")
            return True

        showMsgErr(f"Service account {ocp.project}-sa does not have "
                   "the 'hostmount-anyuid' Security Context Constraint.")
        showMsgInd("Logon as kube:admin, create the service account and execute:")
        showMsgInd("         oc adm policy add-scc-to-user hostmount-anyuid"
                   f' "system:serviceaccount:{ocp.project}:{ocp.project}-sa"\n')
        return False

    def _verifySeLinux(self):
        success = True
        for worker in self._workerNodes:
            enforceState = self._runSshJumpCmd(worker, 'getenforce')
            if enforceState in ('Permissive', 'Disabled'):
                showMsgOk(f"SELinux setting for worker {worker} is valid.")
            else:
                showMsgErr(f"Invalid SELinux setting '{enforceState}' for worker {worker}.")
                success = False
        return success

    def _verifyPidLimit(self):
        success = True
        for worker in self._workerNodes:
            pidsLimit = self._runSshJumpCmd(worker, 'crio config | grep pids_limit')
            pidsLimit = int(pidsLimit.split('=')[1])
            if pidsLimit >= 8192:
                showMsgOk(f"CRI-O pids_limit setting for worker {worker} is valid.")
            else:
                showMsgErr(f"CRI-O pids_limit setting for worker {worker} "
                           "is too low, must be >= 8192.")
                success = False
        return success
