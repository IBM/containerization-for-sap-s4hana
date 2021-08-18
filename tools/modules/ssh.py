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

""" Helper functions for SSH handling """


# Global modules

import logging
from   pathlib  import Path
import tempfile


# Local modules

from modules.command  import (
    CmdShell,
    CmdSsh
)
from modules.fail     import fail
from modules.tools    import (
    getBuildHost,
    getHomeDir
)


# Classes

class _PublicKeyInformation():
    """ Information about the origin of a public key """

    def __init__(self, hname, user, path):
        self._hname = hname
        self._user  = user
        self._path  = path

    def __str__(self):
        return f'{self._user.name}@{self._hname}:{self._path}'


class _PublicKey():
    """ Representation of an OpenSSH public key """

    def __init__(self, line, info):
        self.line    = line  # Line in key file
        self.info    = info  # Info on origin of key
        self.algo    = ''
        self.key     = ''
        self.comment = ''
        self.isKey   = False

        self._parse()

    def __eq__(self, other):
        return self.key == other.key

    def __ne__(self, other):
        return self.key != other.key

    def __repr__(self):
        return self.line

    def _parse(self):
        """ Parse a line of a public key file or an authorized_keys file """

        # Assume OpenSSH public key line format '<algorithm> <key> <comment>'

        line = self.line.strip()

        if (line == '' or line.startswith('#')):
            # Line is empty or a comment line
            # We don't change anything in this case
            # self.isKey is already set to False in __init__()
            pass

        else:
            # Line is not empty and no comment line

            items = line.split()

            if len(items) < 2 or len(items) > 3:
                # Invalid line - self.isKey will remain False
                logging.warning(f'Encountered invalid public key line >>>\n{self.line}\n<<<')

            else:
                self.algo = items[0]
                self.key  = items[1]
                if len(items) == 3:
                    self.comment = items[2]
                self.isKey = True


class _PublicKeys():
    """ Representation of a public keys file as list of keys """

    def __init__(self, content, info, keepAll=False):
        # 'keepAll': Keep non-key lines as "keys" with attribute 'isKey' set to 'False'
        #            Required if we want to preserve everything in the content of the
        #            key file 'as is' (except the key lines we are dealing with)
        self._keys = []
        self._parse(content, info, keepAll)

    def __str__(self):
        return '\n'.join([str(k) for k in self._keys])

    def _parse(self, content, info, keepAll):
        """ Parse the content of a public keys file """

        if not content:
            return

        # Only consider non empty content

        for line in content.split('\n'):
            key = _PublicKey(line, info)
            if key.isKey or keepAll:
                self._keys.append(key)

    def getKey(self, index):
        """ Get the key at given index in the internal key list """
        return self._keys[index]

    def addKeys(self, keys):
        """ Add keys in a given key list to the internal key list
            Only add keys which are not yet in the internal key list
            to avoid duplicate entries
            Return the list of keys which were actually added  """

        addedKeys = [k for k in keys if k not in self._keys]

        self._keys += addedKeys

        return addedKeys

    def removeKeys(self, keys):
        """ Remove keys in a given key list from the internal key list
            Return the list of keys which were actually removed """

        remainingKeys = [k for k in self._keys if k not in keys]
        removedKeys = [k for k in self._keys if k not in remainingKeys]

        self._keys = remainingKeys

        return removedKeys

    def numKeys(self):
        """ Return the number of keys in the internal key list """
        return len(self._keys)


class AuthorizedKeys():
    """ Representation of an authorized_keys file of a specific user at a specific host """

    def __init__(self, ctx, hname, user):

        self._userFull = f'{user.name}@{hname}'
        self._authKeys = None

        # Prepare command execution

        self._cmdShell = CmdShell()
        self._cmdSsh   = CmdSsh(ctx, hname, user)
        self._rsyncSsh, self._rsyncSshSecrets = self._cmdSsh.getSshCmdAndSecrets(withLogin=False)

        # Get the path to the remote authorized_keys file

        homeDir = getHomeDir(ctx, hname, user)

        if not homeDir:
            fail(f"Could not determine the home directory of '{self._userFull}'")

        self._akPath = f'{homeDir}/.ssh/authorized_keys'

        # Read the authorized_keys file

        info = _PublicKeyInformation(hname, user, self._akPath)

        self._read(info)  # Sets self._authKeys

        logging.debug(f'self._authKeys >>>\n{self._authKeys}\n<<< self._authKeys')

    def __str__(self):
        return str(self._authKeys)

    def _read(self, info):
        """ Read the contents of the authorized_keys file """

        res = self._cmdSsh.run(f'cat {self._akPath}')

        if res.rc != 0:
            fail(f"Could not get the authorized keys '{self._akPath}' file of '{self._userFull}'")

        self._authKeys = _PublicKeys(res.out, info, keepAll=True)

    def write(self):
        """ Write the contents of the authorized_keys file """

        # Write the contents to a temporary local file and transfer the file to
        # the remote user's .ssh directory using rsync
        # Keep a backup of the original authorized_keys file on the remote side

        with tempfile.NamedTemporaryFile(mode='w') as akFh:
            print(self._authKeys, file=akFh, flush=True)

            source = akFh.name
            target = self._akPath

            backupSuffix = '.bak'

            rsyncCmd  = f'rsync -av -e "{self._rsyncSsh}"'
            rsyncCmd += f' --backup --suffix "{backupSuffix}"'
            rsyncCmd += f' "{source}" "{self._userFull}:{target}"'

            res = self._cmdShell.run(rsyncCmd, self._rsyncSshSecrets)

            if res.rc != 0:
                fail(f"Could not write the authorized keys file '{target}'"
                     f" of '{self._userFull}\n({res.err})")

    def add(self, keys):
        """ Add keys in a key list to the internal authorized_keys list """
        return self._authKeys.addKeys(keys)

    def remove(self, keys):
        """ Remove keys in a key list from internal authorized_keys list """
        return self._authKeys.removeKeys(keys)

    def numKeys(self):
        """ Return the number of keys in the internal authorized_keys key list """
        return self._authKeys.numKeys()


# Functions

def getPublicKey(ctx, hname, user):
    """ Get the public key from a public key file of a specifc user at a specific host """

    userFull = f'{user.name}@{hname}'

    # Prepare command execution and determine path of public key file

    if hname == getBuildHost().name:
        cmd = CmdShell()
        defaultPubKeyPath = f'{Path.home()}/.ssh/id_rsa.pub'
    else:
        cmd = CmdSsh(ctx, hname, user)
        defaultPubKeyPath = f'{getHomeDir(ctx, hname, user)}/.ssh/id_rsa.pub'

    if f'{user.sshid}':
        pubKeyPath = f'{user.sshid}.pub'
    else:
        pubKeyPath = defaultPubKeyPath

    # Read public key file

    res = cmd.run(f'cat {pubKeyPath}')

    if res.rc != 0:
        fail(f"Could not get public key record of user '{userFull}' from file '{pubKeyPath}'")

    # Get the public key from the public key file content

    info = _PublicKeyInformation(hname, user, pubKeyPath)

    pubKeys = _PublicKeys(res.out, info, keepAll=False)

    logging.debug(f'pubKeys >>>\n{pubKeys}\n<<< pubKeys')

    if pubKeys.numKeys() == 0:
        fail(f'Public key file of {userFull} does not contain any key record')

    if pubKeys.numKeys() > 1:
        records = '\n\n'.join(pubKeys)
        fail(f"Public key file '{pubKeyPath}' of {userFull}"
             f" contains multiple records:\n\n{records}")

    pubKey = pubKeys.getKey(0)

    logging.debug(f'Public key for {userFull}: >>>\n{pubKey}\n<<<')

    return pubKey
