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

""" Credentials management """


# Global modules

import logging
import os
import pathlib
import re
import sys

import gnupg


# Local modules

from modules.fail       import fail
from modules.configbase import ConfigBase
from modules.command    import CmdShell

# Classes


class Creds(ConfigBase):
    """ Credentials management """

    def __init__(self, ctx, create=False):

        self._noFileMsg   = f"Credentials file '{ctx.ar.creds_file}' does not exist"

        # Determine encryption status of ctx.ar.creds_file
        # The file is considered not to be encrypted
        # - if a new credentials file is created and CLI argument
        #   '--unencypted' is set
        # - otherwise, if the file exists, encryption status of the file is
        #   derived from the file type returned by the Linux 'file' command,
        #   taking into consideration that the file maybe a symlink.

        credsfile = os.path.realpath(ctx.ar.creds_file)

        if create:
            # This case can only occur if the calling tool is 'tools/creds -n'
            self._unencrypted = ctx.ar.unencrypted

        elif pathlib.Path(credsfile).is_file():
            out = CmdShell().run(f'file -b {credsfile} --mime-type').out
            self._unencrypted = 'application/pgp' not in out

        else:
            # This case will lead to abort of the calling tool since
            # super().__init__() will finally try to read the non-existing file.
            # Nevertheless we need to set attribute self._unencrypted since it
            # is accessed before the calling tool is aborted.
            # Set it to True since this avoids some unnecessary actions.
            self._unencrypted = True

        self._gpg         = self._getGpg()
        self._recipient   = ctx.ar.recipient if hasattr(ctx.ar, 'recipient') else None
        self._passphrase  = os.getenv('SOOS_CREDS_PASSPHRASE')

        super().__init__(ctx, './creds.yaml.template', ctx.ar.creds_file, create)

        if create:
            return

        logging.debug(f"Assuming file '{ctx.ar.creds_file}'"
                      f" is{' not' if self._unencrypted else ''} encrypted")

    # Private functions

    def _getGpg(self):

        if self._unencrypted:
            gpg = None

        else:
            gpg = gnupg.GPG(use_agent=True)
            logging.getLogger("gnupg").setLevel(logging.ERROR)
            # Set gpg tty to make console pinentry reliably working
            try:
                # os.ttyname() fails when we are not running interactivly
                os.environ['GPG_TTY'] = os.ttyname(sys.stdin.fileno())
            except OSError:
                logging.info('Not setting GPG_TTY environment variable')

        return gpg

    def _setRecipient(self, credsDec):
        if not self._recipient:
            match = re.match(r'^[^<]*<([^<>]+)>[^>]*$', credsDec.stderr)
            if match:
                self._recipient = match.group(1)
            else:
                self._recipient = credsDec.key_id

        logging.debug(f'self._recipient >>>{self._recipient}<<<')

    def _readFile(self, fileName):
        """ Read credentials from possibly encrypted credentials file """

        credsFile = fileName
        creds     = None

        if self._unencrypted:
            creds = super()._readFile(credsFile)

        else:
            if not pathlib.Path(credsFile).is_file():
                logging.info(self._noFileMsg)

            else:
                credsRead = False

                while not credsRead:
                    # Repeat until read and decrypt were successful
                    # (i.e. until GPG agent responded or correct password was supplied)
                    try:
                        with open(credsFile, 'rb') as credsFh:
                            credsDec = self._gpg.decrypt_file(credsFh, passphrase=self._passphrase)
                        credsRead = credsDec.ok
                    except IOError:
                        fail(f"Error reading from {credsFile}")

                self._setRecipient(credsDec)

                creds = str(credsDec)

                # logging.debug(f'creds >>>{creds}<<<')

        return creds

    def _writeFile(self, fileName, contents):
        # See also https://pythonhosted.org/python-gnupg/#encryption

        credsFile = fileName
        creds     = contents

        if self._unencrypted:
            super()._writeFile(credsFile, contents)

        else:
            if self._recipient:
                # Recipient specified -> encrypt for recipient using asymmetric encryption
                print(f"Encrypting for recipient '{self._recipient}'", file=sys.stderr)

                credsEnc = self._gpg.encrypt(creds,
                                             recipients=[self._recipient],
                                             passphrase=self._passphrase)

            else:
                # No recipient specified -> use symmetric AES256 encryption
                print('No recipient specified - using symmetric AES256 encryption', file=sys.stderr)

                credsEnc = self._gpg.encrypt(creds,
                                             symmetric='AES256',
                                             recipients=None,
                                             passphrase=self._passphrase)

            if not credsEnc.ok:
                # pylint: disable=no-member
                fail(f"Encryption failed\n"
                     f" Status: '{credsEnc.status}'\n Stderr: '{credsEnc.stderr}'")

            try:
                # pylint: disable=unspecified-encoding
                with open(credsFile, 'w') as credsFh:
                    credsFh.write(str(credsEnc))
            except IOError:
                fail(f"Error writing to {credsFile}")
