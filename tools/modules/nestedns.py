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

""" Implementation of nested namespaces based on types.SimpleNamespace """


# Global modules

import argparse
import types


# Local modules

# None


# Functions

def objToNestedNs(obj):
    """ Convert an object into a (potentially) nested namespaces """

    if isinstance(obj, dict):
        nnObj = {}
        for k, v in obj.items():  # pylint: disable=invalid-name
            nnObj[k] = objToNestedNs(v)
        nestedNs = types.SimpleNamespace(**nnObj)

    elif isinstance(obj, list):
        nestedNs = []
        for i in obj:
            nestedNs.append(objToNestedNs(i))

    else:
        nestedNs = obj

    return nestedNs


def nestedNsToObj(nestedNs, hideSecrets=True):
    """ Convert a (potentially) nested namespaces into an object """

    if isinstance(nestedNs, (types.SimpleNamespace, argparse.Namespace)):
        hideList = []
        if hideSecrets:
            hideList += ['password']
        obj = {}
        for k in vars(nestedNs).keys():
            if k in hideList:
                obj[k] = '<hidden>'
            else:
                obj[k] = nestedNsToObj(getattr(nestedNs, k), hideSecrets)

    elif isinstance(nestedNs, list):
        obj = []
        for child in nestedNs:
            obj.append(nestedNsToObj(child, hideSecrets))

    else:
        obj = nestedNs

    return obj
