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

""" Configuration base operations """


# Global modules

import logging
import os
import pathlib
import sys
import types

import yaml


# Local modules

from modules.fail     import fail
from modules.messages import formatMessageList
from modules.nestedns import objToNestedNs
from modules.tools    import readInput


# Classes

class ConfigBase:
    """ Configuration bases operations """

    @staticmethod
    def cleanup(subtree):
        """ Set all items to <item.value>
            (drop item.description and item.required) """

        cleantree = {}

        for itemK, itemV in subtree.items():
            if isinstance(itemV, dict):
                if 'value' in itemV.keys():
                    cleantree[itemK] = itemV['value']
                else:
                    cleantree[itemK] = ConfigBase.cleanup(itemV)

        return cleantree

    def __init__(self, ctx, templateFile, instanceFile, create):
        self._ctx          = ctx
        self._templateFile = templateFile
        self._instanceFile = instanceFile

        if not hasattr(self, '_noFileMsg'):
            self._noFileMsg = f"Configuration file '{instanceFile}' does not exist"

        if create:
            self._instance = None
        else:
            self._instance = self._read(instanceFile)

    # Public functions

    def get(self):
        """ Get cleaned up configuration as nested namespace """
        return  objToNestedNs(self.getObj())

    def getObj(self):
        """ Get cleaned up configuration as nested dicts """
        if not self._instance:
            fail(self._noFileMsg)

        return ConfigBase.cleanup(self._instance)

    def create(self, hideDescriptions):
        """ Create new configuration from template """
        with open(self._templateFile, 'r') as tmplFh:
            self._instance = yaml.load(tmplFh.read(), Loader=yaml.Loader)
        self.edit(hideDescriptions)

    def edit(self, hideDescriptions):
        """ Edit existing configuration  """
        if not self._instance:
            fail(self._noFileMsg)

        pOps = types.SimpleNamespace()
        pOps.extend   = lambda path, key: f'{path}.{key}'
        pOps.envName  = lambda path: f"SOOS_{type(self).__name__}{path.replace('.', '_')}".upper()
        pOps.envValue = lambda path: os.getenv(pOps.envName(path))

        def getMsg(item, path, descs):
            printWidth = 70
            msg = '- '*int(printWidth/2) + '\n'
            msg += f'Parameter:   {path[1:]}\n'
            msg += f"Required:    {'yes' if item['required'] else 'no'}\n"
            msg += f'Environment: {pOps.envName(path)}'
            if descs and not hideDescriptions:
                msg += '\n'
                level = 0
                for desc in descs:
                    msg += f"\n{formatMessageList([desc], printWidth, '  ', level)}"
                    level += 1
            msg += '\n'
            return msg

        def getDefault(item, path):
            default = pOps.envValue(path)
            if not default:
                default = item['value'] if 'value' in item.keys() else ''
            if default is None:
                default = ''
            return default

        def setValueNonInteractive(item, path, descs):
            item['value'] = getDefault(item, path)
            if not item['value'] and item['required']:
                print(f"{getMsg(item, path, descs)}\n"
                      f"CAN'T SET REQUIRED VALUE - SET ENVIRONMENT VARIABLE\n\n"
                      f"   '{pOps.envName(path)}'\n\n"
                      f"TO THE APPROPRIATE VALUE.\n", file=sys.stderr)

        def setValueInteractive(item, path, descs, hideInput):
            default = getDefault(item, path)
            print(getMsg(item, path, descs))
            item['value'] = readInput('Enter value', default,
                                      not item['required'], hideInput, hideInput)
            print()

        def editRecursive(item, path, descs, hideInput):

            if 'description' in list(item.keys()):
                descs.append(item['description'].strip())

            if 'value' in list(item.keys()):

                # Found an entry

                if self._ctx.ar.non_interactive:
                    setValueNonInteractive(item, path, descs)

                else:
                    setValueInteractive(item, path, descs, hideInput)

            else:

                # Recurse until we find an entry

                for key, value in item.items():
                    if  isinstance(value, dict):
                        editRecursive(value, pOps.extend(path, key), descs, key == 'password')

            if 'description' in list(item.keys()):
                descs.pop()

        editRecursive(self._instance, '', [], False)

        self._write(self._instanceFile, self._instance)

    # Private functions

    def _readFile(self, fileName):
        contents = None

        if not pathlib.Path(fileName).is_file():
            logging.info(f"File '{fileName}' does not exist")
        else:
            with open(fileName, 'r') as ctFh:
                contents = ctFh.read()

        return contents

    def _read(self, fileName):
        contents = self._readFile(fileName)

        if contents:
            parsed = yaml.load(contents, Loader=yaml.Loader)
        else:
            parsed = None

        return parsed

    def _writeFile(self, fileName, contents):
        with open(fileName, 'w') as wFh:
            wFh.write(contents)

    def _write(self, fileName, contents):
        self._writeFile(fileName, yaml.dump(contents))
