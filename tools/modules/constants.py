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

""" Constants """


# Global modules

import types


# Functions

def getConstants():
    """ Get constants """
    const = types.SimpleNamespace()

    # Constants for config.yaml file handling
    const.configCacheTimeout = 600  # seconds

    # optional packages to be installed depending on the SPS Level of the HANA DB

    compatSapPkg9 = types.SimpleNamespace()

    compatSapPkg9.minSpsLevel  = 50
    compatSapPkg9.maxSpsLevel  = 59
    # packageName is part of the package metadata, it is not the rpm filename
    compatSapPkg9.packageName  = "compat-sap-c++-9"
    compatSapPkg9.dependencies = ["libgomp"]
    compatSapPkg9.distribution = "rhel"
    compatSapPkg9.repository   = "rhel-8-for-ppc64le-sap-netweaver-rpms"

    compatSapPkg10 = types.SimpleNamespace()

    compatSapPkg10.minSpsLevel  = 60
    compatSapPkg10.maxSpsLevel  = 69
    # packageName is part of the package metadata, it is not the rpm filename
    compatSapPkg10.packageName  = "compat-sap-c++-10"
    compatSapPkg10.dependencies = ["libgomp"]
    compatSapPkg10.distribution = "rhel"
    compatSapPkg10.repository   = "rhel-8-for-ppc64le-sap-netweaver-rpms"

    const.optionalHdbPkgs = [compatSapPkg9, compatSapPkg10]

    # default location for packages to be downloaded
    const.defaultPackagesDir = "/tmp/soos/rpm-packages"

    # additional free space to be added for HANA DB
    const.additionalFreeSpaceHdbGiB = 5
    # minimum memory size of Dialog Instance Container
    const.minMemSizeDIGiB = 32

    # length of the uuid
    # uuid is used for overlay fs name, deployment file name and deployment app name
    const.uuidLen = 10

    # HA Proxy configuration file
    const.haproxyCfg = '/etc/haproxy/haproxy.cfg'

    # Constants for argument names
    const.argAdd             = 'add'
    const.argAppName         = 'app-name'
    const.argConfigFile      = 'config-file'
    const.argContainerFlavor = 'container-flavor'
    const.argCredsFile       = 'creds-file'
    const.argDeploymentFile  = 'deployment-file'
    const.argDumpContext     = 'dump-context'
    const.argGenDocGfm       = 'gen-doc-gfm'
    const.argGenYaml         = 'gen-yaml'
    const.argImageFlavor     = 'image-flavor'
    const.argList            = 'list'
    const.argLogFileDir      = 'logfile-dir'
    const.argLogLevel        = 'loglevel'
    const.argLogToTerminal   = 'log-to-terminal'
    const.argLoop            = 'loop'
    const.argNumber          = 'number'
    const.argOutputFile      = 'output-file'
    const.argOverlayUuid     = 'overlay-uuid'
    const.argRemove          = 'remove'
    const.argSleepTime       = 'sleep-time'
    const.argStart           = 'start'
    const.argStop            = 'stop'

    # Constants for different deployment types
    const.deployAll          = 'all'
    const.deployRunning      = 'running'
    const.deployDeployed     = 'deployed'
    const.deployNotDeployed  = 'not deployed'

    return const
