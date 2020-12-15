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

""" Helper tools """

# Global modules

import contextlib
import logging
import os
import sys
import types

# Local modules

from modules.command import (
    CmdShell,
    CmdSsh
)

# Functions


def nestedNamespace(obj):
    """ Convert an object into a (potentially) nested namespaces """
    if isinstance(obj, dict):
        for (k, v) in obj.items():  # pylint: disable=invalid-name
            obj[k] = nestedNamespace(v)
        nestedNs = types.SimpleNamespace(**obj)
    elif isinstance(obj, list):
        nestedNs = []
        for i in obj:
            nestedNs.append(nestedNamespace(i))
    else:
        nestedNs = obj
    return nestedNs


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


def genFileFromTemplate(templatePath, outFilePath, params):
    """ Generate file from template replacing parameters enclosed in "{{...}} """
    with open(templatePath, 'r') as fh:  # pylint: disable=invalid-name
        content = fh.read()
    for k in params.keys():
        content = content.replace('{{'+k+'}}', params[k])
    with open(outFilePath, 'w') as fh:  # pylint: disable=invalid-name
        print(content, file=fh)


def ocLogin(config):
    """ Log into an OpenShift cluster """
    cmd = getOcLoginCmd(config.ocp)
    out = CmdShell().run(cmd).out
    if not (out.startswith('Logged into') or out.startswith('Login successful')):
        logging.error('oc login failed')
        sys.exit(1)


def getOcLoginCmd(ocp):
    """ Generate OpenShift cluster login command """
    cmd = 'oc login'
    cmd += ' --insecure-skip-tls-verify=true'
    cmd += f' https://api.{ocp.domain}:6443'
    cmd += f' -u {ocp.user}'
    cmd += f' -p {ocp.password}'
    return cmd


def podmanOcpRegistryLogin(config):
    """ Log into the default registry of an OpenShift cluster """
    cmd = 'podman login'
    cmd += ' --tls-verify=false'
    cmd += ' -u $(oc whoami) -p $(oc whoami --show-token)'
    cmd += f' default-route-openshift-image-registry.apps.{config.ocp.domain}'
    out = CmdShell().run(cmd).out
    if not out.startswith('Login Succeeded!'):
        logging.error('podman login failed')
        sys.exit(1)


def getNumRunningSapProcs(config, flavor):
    """ Get number of running SAP processes for a given flavor """
    # pylint: disable=bad-whitespace
    sid    = getattr(config.flavor, flavor).sid
    host   = getattr(config.flavor, flavor).host
    user   = getattr(config.flavor, flavor).user
    instNo = getattr(config.flavor, flavor).instNo

    cmd = f'/usr/sap/{sid}/SYS/exe/hdb/sapcontrol -nr {instNo}'
    cmd += f' -function GetProcessList | grep GREEN | wc -l'
    out = CmdSsh(host, user).run(cmd).out
    return out


def getStatusOfPod(config):
    """ Get the status of a pod """
    ocLogin(config)
    cmdShell = CmdShell()
    cmdShell.run(f'oc project {config.ocp.project}')
    out = cmdShell.run(f'oc get pods | grep {config.flavor.nws4.sid.lower()}').out
    podStatus = ' '.join(out.split()).split()[2]
    return podStatus
