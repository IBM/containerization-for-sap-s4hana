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

""" Perform selective remote copy with correct symlink preservation """

# Global modules

import logging
import os
import tempfile

# Local modules

from modules.command import (
    CmdShell,
    CmdSsh
)

# Classes


class RemoteCopy():
    """ Perform selective remote copy with correct symlink preservation """

    def __init__(self, host, user, filterFilePath='/dev/null'):
        """Perform selective remote copy with correct symlink preservation

        Parameters:

        host:           host of source directory; also ssh and rsync host
        user:           ssh and rsync user
        filterFilePath: optional; path to rsync filter file

        """

        self._host = host
        self._user = user
        self._filterFilePath = filterFilePath

        # Initialize ssh connection

        self._cmdSsh = CmdSsh(host, user)

    def _runRsync(self, source, filterFilePath, verbose, dryRun):
        logging.debug(f'source: >>>{source}<<<')
        cmdShell = CmdShell()
        cmd = 'rsync -a --relative'
        if verbose > 0:
            cmd += ' -'+'v'*verbose
        cmd += f' -f "merge {filterFilePath}"'
        if dryRun:
            cmd += ' -n'
        if not isinstance(source, list):
            cmd += f' {self._user}@{self._host}:{source} ./'
            cmdShell.run(cmd)
        else:
            with tempfile.NamedTemporaryFile(mode='w') as tfh:
                tfh.write("\n".join(str(fn) for fn in source))
                tfh.flush()
                logging.debug(f"Contents of file '{tfh.name}':")
                logging.debug('>>>')
                with open(tfh.name) as rfh:
                    logging.debug(rfh.read())
                logging.debug('<<<')
                cmd += f' -r --files-from={tfh.name}'
                cmd += f' {self._user}@{self._host}:/ ./'
                cmdShell.run(cmd)

    def _getRealPathAndSymlinks(self, path, targets):
        logging.debug(f"path '{path}', targets '{targets}'")
        curPath = ''
        for component in list(filter(lambda x: x != '', path.split('/'))):
            curDir = curPath
            curPath = curDir + '/' + component
            logging.debug(f"Current path '{curPath}'")
            if curPath not in targets.keys():
                logging.debug(f"Visiting new path '{curPath}'")
                target = self._cmdSsh.run(f'readlink {curPath}').out
                if not target:
                    targets[curPath] = None
                else:
                    logging.debug(f"found symlink '{curPath}', target '{target}'")
                    if not target.startswith('/'):
                        relTarget = target
                        target = os.path.normpath(curDir + '/' + target)
                        logging.debug(f"Converted relative target '{relTarget}'"
                                      f" to absolute target '{target}'")
                    (targets[curPath], targets) = self._getRealPathAndSymlinks(target, targets)
            if targets[curPath]:
                curPath = targets[curPath]
        logging.debug(f"returning path '{curPath}', targets >>>{targets}<<<")
        return (curPath, targets)

    def _symlinkConvertRelToAbs(self, symlink, linkTarget):
        if not linkTarget.startswith('/'):
            relTarget = linkTarget
            linkTarget = os.path.join(os.path.dirname(symlink), linkTarget)[1:]  # skip leading '.'
            logging.debug(f"Converted relative target '{relTarget}' "
                          f"to absolute target '{linkTarget}'")
        return linkTarget

    def copy(self, source, filterFilePath=None, verbose=1, dryRun=False):
        """ Perform remote copy

        Parameters:

        source        : root of source directorytree; must be an absolute path
        filterFilePath: optional: path to file containing rsync filters;
                        if not supplied filter file path supplied to constructor will be used
        verbose       : optional: set rsync verbose level;
                        choices: [0, 1, 2, 3], corresponding to rsync verbose levels
                        [<none>, '-v', '-vv', '-vvv']
        dryRun        : optional: if set to True, perform a trial rsync run with no changes made'

        """

        if not filterFilePath:
            filterFilePath = self._filterFilePath

        logging.info(f"Remote copy of '{source}' started.")

        logging.debug(f'source         >>>{source        }<<<')
        logging.debug(f'filterFilePath >>>{filterFilePath}<<<')
        logging.debug(f'verbose        >>>{verbose       }<<<')
        logging.debug(f'dryRun         >>>{dryRun        }<<<')

        cmdShell = CmdShell()

        symlinksVisited = []
        existingSymlinks = cmdShell.run('find ./ -type l').out
        if existingSymlinks:
            # Do not follow local existing symlinks
            symlinksVisited = existingSymlinks.strip().split('\n')
        logging.debug(f'symlinksVisited >>>{symlinksVisited}<<<')
        # rsync root of source directory supplied on command line
        (realPath, targets) = self._getRealPathAndSymlinks(source, {})
        self._runRsync(realPath, filterFilePath, verbose, dryRun)
        # If root of source directory tree is a symlink itself append it to list of visited links
        logging.debug(f"source  : '{source}'")
        logging.debug(f"realPath: '{realPath}'")
        if realPath != source:
            # cmdShell.run(f'ln -s {realPath} .{source}')
            symlinksVisited.append(f'.{source}')
        # Recursively detect all symlinks and rsync their targets
        finished = False
        while not finished:
            finished = True
            symlinksFound = cmdShell.run('find ./ -type l').out
            logging.debug(f'symlinksFound >>>{symlinksFound}<<<')
            logging.debug(f'symlinksVisited >>>{symlinksVisited}<<<')
            if symlinksFound:
                symlinksFound = symlinksFound.strip().split('\n')
                realPaths = []
                for symlink in symlinksFound:
                    if (symlink not in symlinksVisited
                            and symlink[1:] not in targets.keys()):  # skip leading '.'
                        logging.debug(f'symlink >>>{symlink}<<<')
                        linkTarget = os.readlink(symlink)
                        logging.debug(f'linkTarget >>>{linkTarget}<<<')
                        linkTarget = self._symlinkConvertRelToAbs(symlink, linkTarget)
                        (realPath, targets) = self._getRealPathAndSymlinks(linkTarget, targets)
                        if realPath not in realPaths:
                            realPaths.append(realPath)
                            logging.debug(f'realPaths: >>>{realPaths}<<<')
                        symlinksVisited.append(symlink)
                        finished = False
                if realPaths:
                    self._runRsync(realPaths, filterFilePath, verbose, dryRun)
        # Copy all symlinks that were not yet copied
        logging.debug('Final rsync call')
        self._runRsync([s for (s, t) in targets.items() if t],
                       filterFilePath, verbose, dryRun)
        logging.info(f"Remote copy of '{source}' finished.")
