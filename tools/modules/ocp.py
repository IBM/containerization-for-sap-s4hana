# ------------------------------------------------------------------------
# Copyright 2021 IBM Corp. All Rights Reserved.
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

import logging


# Local modules

from modules.command import (
    CmdShell,
    Command
)
from modules.fail    import fail


# Functions

def ocLogin(ctx, user):
    """ Log into an OpenShift cluster with given user """
    cmd = 'oc login'
    cmd += ' --insecure-skip-tls-verify=true'
    cmd += f' https://api.{ctx.cf.ocp.domain}:6443'
    cmd += f' -u {user.name}'
    cmd += f' -p {user.password}'

    out = CmdShell().run(cmd).out

    if not (out.startswith('Logged into') or out.startswith('Login successful')):
        fail('oc login failed')

    return out


def podmanOcpRegistryLogin(ctx):
    """ Log into the default registry of an OpenShift cluster """

    ocLogin(ctx, ctx.cr.ocp.user)

    cmd = 'podman login'
    cmd += ' --tls-verify=false'
    cmd += ' -u $(oc whoami) -p $(oc whoami --show-token)'
    cmd += f' default-route-openshift-image-registry.apps.{ctx.cf.ocp.domain}'
    out = CmdShell().run(cmd).out
    if not out.startswith('Login Succeeded!'):
        fail('podman login failed')


def containerRun(ctx, containerName, command, rcOk=(0,)):
    """ Run a command in a running container of given flavor """

    logging.debug(f'rcOk >>>{rcOk}<<<')

    podName = getPodName(ctx)

    if not podName:
        res = Command.buildResult('', 'Cannot get pod name', 1, rcOk=(1,))

    else:
        # Don't need an ocLogin() since getPodName() already performed one
        res = CmdShell().run(f'oc exec -it {podName} -c {containerName} -- {command} ', rcOk=rcOk)

    return res


def getContainerName(ctx, containerFlavor):
    """ Get name of the container for a specific flavor """
    return getattr(ctx.cf.ocp.containers, containerFlavor).name


def getPodName(ctx):
    """ Get the name of the pod in which our current deployment is running """
    return _getPodProperty(ctx, 'name', '.metadata.name')


def getPodStatus(ctx):
    """ Get the status of a pod in which our current deployment is running """
    return _getPodProperty(ctx, 'status', '.status.phase')


def getWorkerIp(ctx):
    """ Get the cluster IP address of the worker node on which the SAP system is running """
    return _getPodProperty(ctx, 'worker IP', '.status.hostIP')


def _getPodProperty(ctx, propertyName, propertySelector):
    """ Get a property of the pod in which our current deployment is running """

    podProperty = ''
    appName = f'soos-{ctx.cf.refsys.nws4.sidL}'

    ocLogin(ctx, ctx.cr.ocp.user)

    res = CmdShell().run(
        f'oc get pods --selector="app={appName}"'
        + ' -o template --template "{{range .items}}{{' + propertySelector + '}}{{end}}"'
    )

    if res.rc == 0:
        podProperty = res.out.strip()
        logging.debug(f"Pod property '{propertyName}': '{podProperty}'")

    else:
        logging.debug(f"Could not get pod property '{propertyName}'"
                      f" for app '{appName}' (reason: {res.err})")

    return podProperty
