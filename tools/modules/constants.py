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

    compatSapPkg = types.SimpleNamespace()

    compatSapPkg.minSpsLevel  = 50
    compatSapPkg.maxSpsLevel  = 59
    # packageName is part of the package metadata, it is not the rpm filename
    compatSapPkg.packageName  = "compat-sap-c++-9"
    compatSapPkg.dependencies = ["libgomp"]
    compatSapPkg.distribution = "rhel"
    compatSapPkg.repository   = "rhel-8-for-ppc64le-sap-netweaver-rpms"

    const.optionalHdbPkgs = [compatSapPkg]

    # default location for packages to be downloaded
    const.defaultPackagesDir = "/tmp/soos/rpm-packages"

    # additional free space to be added for HANA DB
    const.additionalFreeSpaceHdbGiB = 5

    # minimum memory size of Dialog Instance Container
    const.minMemSizeDIGiB = 32

    return const
