# ------------------------------------------------------------------------
# Copyright 2021, 2022 IBM Corp. All Rights Reserved.
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

""" Helper tools for Red Hat OpenShift Container Platform """


# Global modules

import os
import sys
import logging
import types
import yaml


# Local modules

from modules.command import (
    CmdShell,
    Command
)
from modules.nestedns import objToNestedNs
from modules.fail     import (
    fail,
    warn
)


# Classes

class Ocp():
    """ Helper tools for Red Hat OpenShift Container Platform """
    # pylint: disable=too-many-public-methods, too-many-instance-attributes, too-many-arguments

    def __init__(self, ctx, login="user", verify=False, setProject=True, logout=True, appName=None):

        self._ctx     = ctx
        self._ocp     = ctx.cf.ocp
        self._domain  = ctx.cf.ocp.domain
        self._admin   = ctx.cr.ocp.admin
        self._user    = ctx.cr.ocp.user
        self._project = ctx.cf.ocp.project
        self._appName = appName
        self._verify  = {"domain": True,
                         "creds": True,
                         "project": True}
        self._logout  = logout

        self._loginuser = self._user
        if login == "admin":
            self._loginuser = self._admin

        self._orgUser, self._userSwitch = self._setOrgUser()

        self._result = self.ocLogin(self._loginuser)
        if self._result.rc > 0:
            if not verify:
                fail(self._result.err, exitCode=4)
            else:
                self._verify["domain"] = self._isDomainValid(self._result)
                self._verify["creds"]  = self._isCredentialsValid(self._result)

        # Change to project
        result = self.setProject()
        if result.rc > 0:
            if not verify:
                if setProject:
                    fail(result.err)
                else:
                    warn(f"Could not set project '{self._project}'")
            else:
                self._verify["project"] = False

    def __del__(self):
        self._printSwitchUserMsg()

        if self._logout:
            self.ocLogout()
            if self._userSwitch:
                self.ocLogin(self._orgUser)


# Public functions

    def setAppName(self, appName):
        """ Set the application name """
        self._appName = appName

    def getAppName(self):
        """ Return the application name """
        return self._appName

    def ocWhoami(self):
        """ Get actual OpenShift user """
        result = CmdShell().run(
            'oc whoami'
        )
        if result.rc == 0:
            return result.out
        return ""

    def ocLogin(self, user=""):
        """ Log into an OpenShift cluster with given user """
        if not user:
            return self._result
        secrets = [user.password]
        return CmdShell().run(
            'oc login'
            ' --insecure-skip-tls-verify=true'
            f' https://api.{self._domain}:6443'
            f' -u {user.name}'
            ' -p :0:', secrets
        )

    def setProject(self):
        """ Set project """
        return CmdShell().run(
            f"oc project {self._project}"
        )

    def isProjectExisting(self):
        """ Does the specified oc project exist """
        res = CmdShell().run(f"oc get project {self._project}")
        return res.rc == 0

    def createProject(self):
        """ Create project  """
        print(f"creating project: {self._project}")
        return CmdShell().run(
            f"oc new-project {self._project}"
        )

    def ocLogout(self):
        """ Logout from OpenShift Cluster """
        return CmdShell().run(
            'oc logout').rc

    def isDomainValid(self):
        """ return True if valid domain is specified """
        return self._verify["domain"]

    def isCredentialsValid(self):
        """ return True if valid credentials are specified """
        return self._verify["creds"]

    def isProjectValid(self):
        """ return True if a valid project is specified """
        return self._verify["project"]

    def podmanOcpRegistryLogin(self):
        """ Log into the default registry of an OpenShift cluster """

        out = CmdShell().run(
            'podman login'
            ' --tls-verify=false'
            ' -u $(oc whoami) -p $(oc whoami --show-token)'
            f' default-route-openshift-image-registry.apps.{self._domain}'
        ).out

        if not out.startswith('Login Succeeded!'):
            fail('podman login failed')

    def containerRun(self, containerName, command, rcOk=(0,)):
        """ Run a command in a running container of given flavor """

        logging.debug(f'rcOk >>>{rcOk}<<<')

        podName = self.getPodName()

        if not podName:
            res = Command.buildResult('', 'Cannot get pod name', 1, rcOk=(1,))

        else:
            ocCmd = self._buildOcExecCmd(podName, containerName, command)
            res = CmdShell().run(ocCmd, rcOk=rcOk)
        return res

    def getContainerName(self, containerFlavor):
        """ Get name of the container for a specific flavor """
        return getattr(self._ocp.containers, containerFlavor).name

    def getPodName(self):
        """ Get the name of the pod in which our current deployment is running """
        return self._getPodProperty('name', '.metadata.name')

    def getPodStatus(self):
        """ Get the status of a pod in which our current deployment is running """
        return self._getPodProperty('status', '.status.phase')

    def getWorkerIp(self):
        """ Get the cluster IP address of the worker node on which the SAP system is running """
        return self._getPodProperty('worker IP', '.status.hostIP')

    def getWorkerName(self):
        """ Get the worker name of the worker node on which the SAP system is running """
        return self._getPodProperty('worker name', '.spec.nodeName')

    def getHdbConnectSecretUser(self):
        """ Get credentials currently stored in OCP secret of name ctx.cf.ocp.containers.di.secret

            Returns an object 'user' where

            - 'user.name'     holds the retrieved user name
            - 'user.password' holds the retrieved password

            in case of success

            Returns None in case of failure (also if ctx.cf.ocp.containers.di.secret is not defined)
        """

        secretName = self._ocp.containers.di.secret

        template = str(
            '{{(index (index .items 0).metadata.annotations'
            ' "kubectl.kubernetes.io/last-applied-configuration")}}'
        )

        res = CmdShell().run(
            f'oc get secret'
            f" --namespace '{self._project}'"
            f" --field-selector 'metadata.name={secretName}'"
            f" -o template --template '{template}'"
        )

        if res.rc == 0:
            try:
                secretData = yaml.load(res.out, Loader=yaml.Loader)['stringData']

                user = types.SimpleNamespace()
                user.name     = secretData['HDB_DBUSER']
                user.password = secretData['HDB_DBUSERPWD']

            except KeyError as kex:
                user = None
                logging.debug(
                    f"Could not evaluate secret data of OCP secret '{secretName}' ({kex})"
                )

        else:
            user = None
            logging.debug(f"Could not retrieve secret data from OCP secret '{secretName}'")

        return user

    def ocServiceAccountExists(self):
        """ Return True if Service Account exists for ocp-project """
        res =  CmdShell().run(
            "oc get sa"
            f" --namespace {self._project}"
            f" --field-selector 'metadata.name={self._ocp.sa.name}'"
            " -o custom-columns=NAME:.metadata.name"
            " --no-headers"
        )

        if not self._ocp.sa.name in res.out:
            return False
        return True

    def ocApply(self, file, printRunTime=False):
        """ Apply a configuration to a resource """

        cmd = f"oc apply -f {file}"
        if printRunTime:
            cmd = "time " + cmd
        res = CmdShell().run(cmd)

        if res.rc == 0:
            logging.debug(f"Configuration file {file} successfully applied")
        else:
            logging.debug(f"Error applying configuration file {file}")
        return res

    def ocDelete(self, file, printRunTime=False):
        """ Delete a configuration """

        cmd = f"oc delete -f {file}"
        if printRunTime:
            cmd = "time " + cmd
        res = CmdShell().run(cmd)

        if res.rc == 0:
            logging.debug(f"Configuration file {file} successfully removed")
        else:
            logging.debug(f"Error removing configuration file {file}")
        return res

    def containerLogin(self):
        """ Login to a container """
        podName = self.getPodName()

        if not podName:
            fail("Cannot get the name of the pod - check if the pod is started.")

        containerName = self.getContainerName(self._ctx.ar.container_flavor)

        self._printSwitchUserMsg(switchLogin=False)

        print(f"Logging into container '{containerName}' of pod '{podName}'", file=sys.stderr)
        os.execlp('oc', 'oc', 'exec', '-it', podName, '-c', containerName, '--', 'bash')

    def getProject(self):
        """ get the project name from OpenShift """
        res = CmdShell().run(
            f"oc get project {self._project}"
            " -o custom-columns=NAME:.metadata.name --no-headers"
        )

        if res.rc > 0:
            return ""
        return res.out

    def getSecret(self):
        """ get the secret from OpenShift """
        res = CmdShell().run(
            f"oc get secret --namespace {self._project}"
            f" --field-selector 'metadata.name={self._ocp.containers.di.secret}'"
            " -o custom-columns=NAME:.metadata.name --no-headers"
        )

        if res.rc > 0:
            return ""
        return res.out

    def getWorkerNodeList(self):
        """ get the list of worker nodes from OpenShift """
        res = CmdShell().run(
            'oc get nodes'
            ' --selector="node-role.kubernetes.io/worker"'
            " -o template --template"
            " '{{range .items}}{{.metadata.name}} {{end}}'"
        )

        if res.rc > 0:
            return []
        return res.out.split()

    def getServiceAccountListForScc(self, scc):
        """ get the list of service accounts for scc from OpenShift """

        tplList = {"anyuid": str('{{range .groups}}{{.}} {{end}}'),
                   "hostmount-anyuid": str('{{range .users}}{{.}} {{end}}')}

        template = tplList[scc]

        res = CmdShell().run(
            f"oc adm policy who-can use scc {scc} -o template"
            f" --template='{template}'"
            f" --namespace={self._project}"
        )

        if res.rc > 0:
            return []
        return res.out.split()

    def getNodePortList(self):
        """ Get the node ports on the worker node which can be used to connect to the SAP system """
        res =  CmdShell().run(
            f'oc get service {self._appName}-np'
            ' -o template --template "{{range .spec.ports}}{{.name}}:{{.nodePort}} {{end}}"'
        )

        if res.rc > 0:
            return []
        return res.out.split()

    def getAppNames(self):
        """ Get the deployment app names  """
        res = CmdShell().run(
            'oc get pods -o template --template "{{range .items}}{{.metadata.labels.app}} {{end}}"'
        )
        if res.rc > 0:
            return []
        return res.out.split()

    def serviceExists(self, serviceName):
        """ Returns True if the specified NodePort Service exists """
        res = CmdShell().run(
            f"oc get service {serviceName}"
        )
        return res.rc == 0

    def serviceDelete(self, serviceName):
        """ deletes the specified service """
        if self.serviceExists(serviceName):
            res = CmdShell().run(
                f"oc delete service {serviceName}"
            )
            print(res)

    # Private functions

    def _setOrgUser(self):
        userSwitch = True

        orgUserName = self.ocWhoami()

        if orgUserName == "kube:admin":
            orgUserName = "kubeadmin"

        # Check for known users
        if orgUserName == self._user.name:
            return self._user, userSwitch
        if orgUserName == self._admin.name:
            return self._admin, userSwitch

        userSwitch = False

        # ocp user not set before
        if orgUserName == "":
            return None, userSwitch

        return objToNestedNs({"name": orgUserName}), userSwitch

    def _getPodProperty(self, propertyName, propertySelector):
        """ Get a property of the pod in which our current deployment is running """

        podProperty = ''
        if not self._appName:
            fail("Internal error: appName not set")

        res = CmdShell().run(
            f'oc get pods --selector="app={self._appName}"'
            ' -o template --template "{{range .items}}{{' + propertySelector + '}}{{end}}"'
        )

        if res.rc == 0:
            podProperty = res.out.strip()
            logging.debug(f"Pod property '{propertyName}': '{podProperty}'")

        else:
            logging.debug(f"Could not get pod property '{propertyName}'"
                          f" for app '{self._appName}' (reason: {res.err})")

        return podProperty

    def _isDomainValid(self, result):
        return 'no such host' not in result.err

    def _isCredentialsValid(self, result):
        condFail1 = (
            result.out.startswith('Login failed') and
            'Verify you have provided correct credentials' in result.out
        )
        condFail2 = not (
            result.out.startswith('Logged into') or
            result.out.startswith('Login successful')
        )
        return not (condFail1 or condFail2)

    def _buildOcExecCmd(self, podName, containerName, command="bash"):
        return f'oc exec -it {podName} -c {containerName} -- {command} '

    def _printSwitchUserMsg(self, switchLogin=True):
        if not switchLogin:
            if not self._orgUser or self._orgUser.name != self._loginuser.name:
                print("Caution: after execution you will be logged on to your OpenShift Cluster "
                      f"as user {self._loginuser.name}!")
            return

        if self._logout:
            if not self._orgUser:
                return
            if self._orgUser.name not in (self._user.name, self._admin.name):
                print(f"Cannot automatically switch back to original user {self._orgUser.name}")
