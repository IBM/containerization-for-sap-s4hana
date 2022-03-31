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

""" OCP quantities """

# pylint: disable=line-too-long
# See https://docs.openshift.com/container-platform/4.7/rest_api/objects/index.html#quantity-api-resource

# Global modules

import logging
import re


# Local modules

from modules.fail import fail


# Constants

_scale = {
    '':         1,

    'K':  1000**1,
    'M':  1000**2,
    'G':  1000**3,
    'T':  1000**4,
    'P':  1000**5,
    'E':  1000**6,

    'Ki': 1024**1,
    'Mi': 1024**2,
    'Gi': 1024**3,
    'Ti': 1024**4,
    'Pi': 1024**5,
    'Ei': 1024**6,
}


# Classes

class Quantity():
    """ OCP quantities """

    def __init__(self, quantityStr):

        self._quantityStr = quantityStr if quantityStr else '0'

        # Extract value and scale

        match = re.match(r'\s*(\d+)\s*(\S*)\s*', self._quantityStr)
        if not match:
            fail(f"Quantity '{self._quantityStr}' format is invalid")

        self._valueInt = int(match.groups()[0])
        self._scale    = match.groups()[1]
        self._checkScale()

        self._valueIntNormalized = self._valueInt * _scale[self._scale]

        logging.debug(f'({self._quantityStr}, {self._valueInt},'
                      f' {self._scale}, {self._valueIntNormalized})')

    def __str__(self):
        return self._quantityStr

    def __ge__(self, other):
        return self._valueIntNormalized >= other._valueIntNormalized

    def __lt__(self, other):
        return self._valueIntNormalized < other._valueIntNormalized

    def _checkScale(self):
        if self._scale not in _scale.keys():
            fail(f"Unknown scale '{self._scale}' in '{self._quantityStr}'")

    def valueIntScaled(self, scale):
        """ returns int value scaled to unit """
        if scale not in _scale.keys():
            fail(f"Unknown scale '{scale}' specified. Cannot continue.")
        return self._valueIntNormalized / _scale[scale]

    def valueIntNormalized(self):
        """ returns the value normed to bytes """
        return self._valueIntNormalized
