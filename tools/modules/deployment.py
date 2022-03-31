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

""" Helper tools for multiple deployment handling """


# Global modules

import os
import time
import string
import random
import yaml


# Local modules
from modules.ocp          import Ocp
from modules.nestedns     import (objToNestedNs, nestedNsToObj)
from modules.fail         import fail

from modules.tools        import (
    ocpMemoryResourcesValid,
    instantiateYamlTemplate,
    refSystemIsStandard,
    getCallingToolName,
    getParmsForDeploymentYamlFile
)

from modules.containerize import (
    createDeploymentFile,
    setupOverlayShare,
    tearDownOverlayShare,
    startDeployment,
    stopDeployment
)

# Classes


class Deploy():
    """ Class for all deployment actions """

    def __init__(self, ctx, deploymentType = None, initDeployments= True):

        self._ctx            = ctx
        self._ocp            = Ocp(ctx)
        self._deploymentType = deploymentType
        if not deploymentType:
            self._deploymentType = ctx.cs.deployAll

        self._appName        = None
        self._deployments    = None

        if initDeployments:
            self._deployments = Deployments(ctx, self._ocp, deploymentType = self._deploymentType)

    def __del__(self):
        del self._ocp

    # Public functions

    def start(self):
        """ start a deployment """
        deploymentFile = self._ctx.ar.deployment_file
        if not deploymentFile:
            self._appName = self._deployments.getValidAppName()

            # check if deployment is already started
            if self._deployments.isDeployed(self._appName):
                fail(f"Deployment with app name '{self._appName}' already started.")

            # start the deployment
            deploymentFile = self._deployments.getDeploymentFile(self._appName)
        startDeployment(self._ctx, deploymentFile = deploymentFile)

    def stop(self, ignore = False):
        """ Stop a deployment """
        deploymentFile = self._ctx.ar.deployment_file

        if deploymentFile:
            self._appName = self._deployments.getAppNameFromFile(deploymentFile)
        else:
            self._appName = self._deployments.getValidAppName()

            # check if deployment is already stopped
            if not ignore:
                if self._deployments.isNotDeployed(self._appName):
                    fail(f"Deployment with app name '{self._appName}' not deployed.")

            # stop the deployment
            deploymentFile = self._deployments.getDeploymentFile(self._appName)
        stopDeployment(self._ctx, deploymentFile = deploymentFile)

        # wait for stopped
        self._waitForStopped(self._appName)

    def list(self):
        """ list deployments """
        self._appName = self._deployments.getValidAppName()
        deploymentsList = self._deployments.getAll()
        if len(deploymentsList) == 0:
            print("No deployments found.")
            return
        if self._appName:
            deployment = self._deployments.getDeployment(self._appName)
            deploymentsList = [deployment]

        self._printList(deploymentsList)
        return

    def genYaml(self, overlayUuid):
        """ generate the deployment description file """

        deployment = Deployment(self._ctx, overlayUuid=overlayUuid).get()

        if not ocpMemoryResourcesValid(self._ctx):
            fail("Fatal error. Stopping the deployment.")

        parms = getParmsForDeploymentYamlFile(self._ctx, deployment)

        templatePath = f'{self._ctx.cf.build.repo.root}/openshift/'
        serviceTemplate = f'{templatePath}/service-nodeport.yaml.template'
        deploymentTemplate = f'{templatePath}/deployment.yaml.template'

        serviceYamlPart    = instantiateYamlTemplate(serviceTemplate, parms)
        deploymentYamlPart = instantiateYamlTemplate(deploymentTemplate, parms)

        if refSystemIsStandard(self._ctx):
            # If the reference system is a standard system no OCP secret definition
            # for the HDB connect user is required
            # ->
            # Remove all OCP secret definition related environment variables
            # to avoid problems at deployment time in case no OCP secret was defined

            delEnvVars = ('SOOS_DI_DBUSER', 'SOOS_DI_DBUSERPWD')
            initContSpec = deploymentYamlPart['spec']['template']['spec']['initContainers'][0]
            initContSpec['env'] = [e for e in initContSpec['env'] if e['name'] not in delEnvVars]

            # Write deployment file

        try:
            # pylint: disable=unspecified-encoding
            with open(deployment.file, 'w') as oFh:
                print(yaml.dump(serviceYamlPart), file=oFh, end='')
                print('---', file=oFh)
                print(yaml.dump(deploymentYamlPart), file=oFh, end='')

            print(deployment.file)

        except IOError:
            fail(f"Error writing to file {deployment.file}")

    def add(self, number):
        """ generate new deployment(s) """
        # pylint: disable=unused-variable
        for i in range(number):
            deployment = Deployment(self._ctx).get()
            print(f"Generating deployment with uuid '{deployment.uuid}:'")
            print(f"- Application Name: '{deployment.appName}'")
            print(f"- Overlay Uuid    : '{deployment.overlayUuid}'")
            print(f"- Deployment File : '{deployment.file}'\n")
            overlayUuid = deployment.overlayUuid
            setupOverlayShare(self._ctx, overlayUuid=overlayUuid, out=False)
            createDeploymentFile(self._ctx, overlayUuid, out=False)
            startDeployment(self._ctx, deployment.file, out=False)

    def remove(self):
        """ Remove all deployment related objects """
        self._appName = self._deployments.getValidAppName()

        deployment  = self._deployments.getDeployment(self._appName)
        serviceName = self._deployments.getNodePortService(deployment.file)

        length  = len("- delete the Overlay Share with the overlay uuid ")
        length += len(f"'{deployment.overlayUuid}'")

        print("-"*length)
        print("WARNING: You are about to: ")
        print("-"*length)
        if self._deployments.isDeployed(deployment.appName):
            print(f"- stop the deployment '{deployment.appName}'")
        if self._deployments.serviceExists(serviceName):
            print(f"- delete the NodePort Service '{serviceName}'")
        print(f"- delete the Overlay Share with the overlay uuid '{deployment.overlayUuid}'")
        print(f"- delete the deployment file '{deployment.file}'")
        print()
        answer = input("Enter YES if you want to continue: ")
        print()

        if not answer == "YES":
            return

        # wait for deployment to be stopped
        if self._deployments.isDeployed(deployment.appName):
            print(f"Stopping deployment '{deployment.appName}'")
            stopDeployment(self._ctx, deployment.file, out=False)
            self._waitForStopped(deployment.appName)

        # deleting the NodePort Service
        print(f"Deleting the NodePort Service '{serviceName}'")
        self._deployments.serviceDelete(serviceName)

        if deployment.overlayUuid:
            print(f"Tearing down overlay share '{deployment.overlayUuid}'")
            tearDownOverlayShare(self._ctx, deployment.overlayUuid, out=False)

        # remove deployment file
        if os.path.exists(deployment.file):
            print(f"Removing deployment yaml file {deployment.file}")
            os.remove(deployment.file)

    # Private functions

    def _waitForStopped(self, appName):
        self._ocp.setAppName(appName)
        while True:
            print("Waiting for deployment to be stopped...")
            if not self._ocp.getPodStatus():
                return
            time.sleep(20)

    def _printList(self, deploymentsList):

        lenStatus      = 0
        lenAppName     = 0
        lenOverlayUuid = 0

        deploymentsList = self._sortList(deploymentsList)

        for deployment in deploymentsList:
            lenStatus = max(len(deployment.status), lenStatus)
            lenAppName = max(len(deployment.appName), lenAppName)
            lenOverlayUuid = max(len(deployment.overlayUuid), lenOverlayUuid)

        header = "Status" + " "*(lenStatus-len("Status")) + " "
        header += "App-Name" + " "*(lenAppName-len("App-Name")) + " "
        header += "OverlayUuid" + " "*(lenOverlayUuid-len("OverlayUuid"))

        print(header)
        print("="*len(header))
        for deployment in deploymentsList:
            print(f"{deployment.status}" + " "*(lenStatus - len(deployment.status)) + " " +
                  f"{deployment.appName}" + " "*(lenAppName - len(deployment.appName)) + " " +
                  f"{deployment.overlayUuid}")

    def _sortList(self, deployments):
        return sorted(deployments, key=lambda x: x.status, reverse=True)


class Deployments():
    """ Helper class for deployment list discovery """

    def __init__(self, ctx, ocp, deploymentType = None):

        self._ctx            = ctx
        self._ocp            = ocp
        self._deploymentType = deploymentType
        if deploymentType is None:
            self._deploymentType = self._ctx.cs.deployRunning
        self._all            = self._setAll()
        self._deployed       = self._setDeployed()
        self._undeployed     = self._setUndeployed()
        self._running        = self._setRunning()

    # Public functions

    def getValidAppName(self):
        """ returns valid application name """

        appNames = self.getAppNames()
        msg = self._getErrorMsg(appNames)

        if not self._ctx.ar.app_name:
            if self._deploymentType == self._ctx.cs.deployAll:
                return None

            if len(appNames) == 1:
                return appNames[0]

            fail(msg)

        # parts or full app-name specified as parameter
        match = None
        for appName in appNames:
            if self._ctx.ar.app_name in appName:
                if match:
                    fail(msg)
                match = appName
        if not match:
            fail(msg)
        return match

    def getAll(self):
        """ Return information of all deployments """
        return self._all

    def getUndeployed(self):
        """ Return information of all deployments which are not deployed """
        return self._undeployed

    def getDeployed(self):
        """ Return information of all deployments which are deployed in OCP """
        return self._deployed

    def getRunning(self):
        """ Return information about all deployments in running state """
        return self._running

    def getOverlayUuidForAppName(self, appName):
        """ Return overlayUuid for deployment """
        for deployment in self._all:
            if appName == deployment.appName:
                return deployment.overlayUuid
        return None

    def getDeploymentFile(self, appName):
        """ Return file name for deployment """
        return self._getDeploymentForAppName(appName).file

    def getAppNameFromFile(self, file):
        """ Return app name from given deployment """
        return self._getDeploymentFromFile(file).appName

    def getNodePortService(self, file):
        """ Return NodePort Service Name from given deployment """
        return self._getServiceNameFromFile(file)

    def isDeployed(self, appName):
        """ True if deployed """
        deployment = self._getDeploymentForAppName(appName)
        if deployment and deployment in self._deployed:
            return True
        return False

    def isNotDeployed(self, appName):
        """ True if not deployed """
        return not self.isDeployed(appName)

    def getAppNames(self):
        """ Return a list of all appNames """
        appNames = []

        deployments = self._getDeploymentsForType()

        for deployment in deployments:
            appNames.append(deployment.appName)
        return appNames

    def getDeployment(self, appName):
        """ returns deployment object for app name """
        return self._getDeploymentForAppName(appName)

    def serviceExists(self, serviceName):
        """ returns True if the nodePort service exists """
        return self._ocp.serviceExists(serviceName)

    def serviceDelete(self, serviceName):
        """ deletes the NodePort Service """
        self._ocp.serviceDelete(serviceName)

    # Private functions

    def _setAll(self):
        deploymentFiles = self._getDeploymentFiles()

        deployments = []

        for file in deploymentFiles:
            deployments.append(self._getDeploymentFromFile(file))

        return deployments

    def _setDeployed(self):
        deployments = []
        for appName in self._ocp.getAppNames():
            for deployment in self._all:
                if appName == deployment.appName:
                    self._ocp.setAppName(appName)
                    deployment.status = self._ocp.getPodStatus()
                    deployments.append(deployment)
        return deployments

    def _setRunning(self):
        deployments = []
        for deployment in self._deployed:
            if deployment.status  == "Running":
                deployments.append(deployment)
        return deployments

    def _setUndeployed(self):
        deployments = []
        for deployment in self._all:
            if not deployment in self._deployed:
                deployments.append(deployment)
        return deployments

    def _getDeploymentsForType(self):
        if self._deploymentType == self._ctx.cs.deployAll:
            return self._all
        if self._deploymentType == self._ctx.cs.deployDeployed:
            return self._deployed
        if self._deploymentType == self._ctx.cs.deployNotDeployed:
            return self._undeployed
        if self._deploymentType == self._ctx.cs.deployRunning:
            return self._running
        return None

    def _getDeploymentForAppName(self, appName):
        for deployment in self._getDeploymentsForType():
            if deployment.appName == appName:
                return deployment
        return None

    def _getFileNameForApp(self, appName):
        return self._getDeploymentForAppName(appName).file

    def _getDeploymentFiles(self):
        files = []
        for file in os.listdir(self._ctx.cf.build.repo.root):
            if 'deployment' in file and '.yaml' in file:
                if self._hasValidProject(file):
                    files.append(file)
        return files

    def _hasValidProject(self, file):
        deploymentYaml = self._getDeploymentYaml(file)
        project = objToNestedNs(deploymentYaml).metadata.namespace
        return project == self._ctx.cf.ocp.project

    def _getDeploymentYaml(self, file):
        return self._getYamlKind(file, "Deployment")

    def _getServiceYaml(self, file):
        return self._getYamlKind(file, "Service")

    def _getYamlKind(self, file, kind):
        # pylint: disable=unspecified-encoding
        with open(file, "r") as stream:
            try:
                yamlContent = yaml.safe_load_all(stream)
                for obj in yamlContent:
                    if obj['kind'] == kind:
                        return obj

            except yaml.YAMLError as exc:
                print(exc)
        return None

    def _getDeploymentFromFile(self, file):
        deploymentYaml = self._getDeploymentYaml(file)
        appName     = self._getAppNameFromYaml(deploymentYaml)
        overlayUuid = self._getOverlayUuidFromYaml(deploymentYaml)
        return Deployment(self._ctx,
                          appName=appName,
                          overlayUuid=overlayUuid,
                          file=file).get()

    def _getAppNameFromYaml(self, deploymentYaml):
        return objToNestedNs(deploymentYaml).metadata.labels.app

    def _getOverlayUuidFromYaml(self, deploymentYaml):
        return objToNestedNs(deploymentYaml).metadata.labels.overlayUuid

    def _getServiceNameFromFile(self, file):
        serviceYaml = self._getServiceYaml(file)
        return objToNestedNs(serviceYaml).metadata.name

    def _getCaller(self):
        # pylint: disable = too-many-boolean-expressions, too-many-return-statements
        caller = getCallingToolName()
        arguments = nestedNsToObj(self._ctx.ar)
        const = self._ctx.cs

        if const.argStart in arguments.keys() and self._ctx.ar.start:
            return f"{caller} --{self._ctx.cs.argStart}"
        if const.argStop in arguments.keys() and self._ctx.ar.stop:
            return f"{caller} --{self._ctx.cs.argStop}"
        if const.argAdd in arguments.keys() and self._ctx.ar.add:
            return f"{caller} --{self._ctx.cs.argAdd}"
        if const.argRemove in arguments.keys() and self._ctx.ar.remove:
            return f"{caller} --{self._ctx.cs.argRemove}"
        if const.argList in arguments.keys() and self._ctx.ar.list:
            return f"{caller} --{self._ctx.cs.argList}"
        if const.argGenYaml in arguments.keys() and self._ctx.ar.gen_yaml:
            return f"{caller} --{self._ctx.cs.argGenYaml}"
        return caller

    def _getErrorMsg(self, appNames):
        status = " running "
        noOfAppNames = len(appNames)

        if self._deploymentType == self._ctx.cs.deployNotDeployed:
            status = " stopped "
        else:
            status = " "

        msgHeader = "You specified a part of or a complete deployment application name,"
        if not self._ctx.ar.app_name:
            msgHeader = "You did not specify a part of or a complete deployment application name,"

        msgNumber = f"but no{status}deployment was found "
        msgCall   = ""
        appNameOut = ""
        caller = self._getCaller()

        if noOfAppNames > 1:
            msgCall = f"Call '{caller}' with one of the following arguments:\n"
            msgNumber = f"but more than one{status}deployment was found "
            for appName in appNames:
                appNameOut += f"    --{self._ctx.cs.argAppName} {appName}\n"
            msgCall += appNameOut

        msgLocation = "in your deployment description files."
        if self._deploymentType in [self._ctx.cs.deployDeployed, self._ctx.cs.deployRunning]:
            msgLocation = "in your OpenShift cluster project."

        msg = msgHeader + "\n" + msgNumber + msgLocation + "\n" + msgCall
        return msg


class Deployment():
    """ deployment object """
    # pylint: disable=too-many-arguments

    def __init__(self, ctx, appName=None, overlayUuid=None, file=None, status=None):
        self._ctx = ctx
        if not overlayUuid:
            self._uuid = self._genUuid()
            overlayUuid = self._genOverlayUuid()
        else:
            self._uuid = self._getSpecificUuid(overlayUuid)

        if not appName:
            appName = self._genAppName()

        if not file:
            file = self._genDeploymentFileName()

        if not status:
            status = 'Prepared'

        self._deployment =  {"appName":     appName,
                             "overlayUuid": overlayUuid,
                             "uuid":        self._uuid,
                             "file":        file,
                             "status":      status
                            }

    def get(self):
        """ return deployment object """
        return objToNestedNs(self._deployment)

    def getAsDict(self):
        """ return deployment object """
        return self._deployment

    def _getSpecificUuid(self, overlayUuid):
        return overlayUuid[-int(self._ctx.cs.uuidLen):]

    def _genUuid(self):
        uuidLen = self._ctx.cs.uuidLen
        seq = string.ascii_lowercase + string.digits
        return ''.join([random.choice(seq) for ch in range(uuidLen)])

    def _genOverlayUuid(self):
        overlayUuid  = f'{self._ctx.cr.ocp.user.name}'
        overlayUuid += f'-{self._ctx.cf.ocp.project}'
        overlayUuid += f'-{self._ctx.cf.refsys.hdb.host.name}'
        overlayUuid += f'-{self._ctx.cf.refsys.hdb.sidU}'
        overlayUuid += f'-{self._uuid}'
        return overlayUuid

    def _genAppName(self):
        appName  =  "soos-"
        appName += f"{self._ctx.cf.refsys.nws4.sidL}-"
        appName += f"{self._uuid}"
        return appName

    def _genDeploymentFileName(self):
        fileName  = f"soos-{self._ctx.cf.refsys.nws4.sidL}-"
        fileName += f"{self._uuid}-"
        fileName +=  "deployment.yaml"
        return fileName
