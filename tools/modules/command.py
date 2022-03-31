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

""" Execute a command """


# Global modules

import getpass
import logging
from   pathlib import Path
import socket
import subprocess
import types


# Local modules

from modules.fail     import fail
from modules.messages import (
    formatMessageList,
    formatMessageParagraphs
)


# Classes

class Command():
    """ Execute a command """

    @staticmethod
    def buildResult(out, err, rc, rcOk=(0,)):
        """ Build command execution result """
        # pylint: disable=invalid-name,too-many-arguments

        logging.debug(f'rcOk >>>{rcOk}<<<')

        if rc not in rcOk:
            logFunc = logging.error
        else:
            logFunc = logging.debug

        logFunc('Result of command execution:')
        logFunc('# stdout: ' + (f'>>>\n{out}\n<<<' if out.strip() else '<empty>'))
        logFunc('# stderr: ' + (f'>>>\n{err}\n<<<' if err.strip() else '<empty>'))
        logFunc(f'# rc: {rc}')

        return types.SimpleNamespace(**{
            'out': out,
            'err': err,
            'rc':  rc
        })

    @staticmethod
    def _shiftSecrets(cmd, secrets, shift):
        """ Increment each secret ID by amount <shift> """
        if secrets:
            for i in range(len(secrets), 0, -1):
                cmd = cmd.replace(f':{i+shift-2}:', f':{i+shift-1}:')
        return cmd

    @staticmethod
    def _instantiateSecrets(cmd, secrets, hide):
        """ Instantiate secrets in command from list of secrets """
        if secrets:
            for (i, secret) in enumerate(secrets):
                if hide:
                    secret = '<hidden>'
                cmd = cmd.replace(f':{i}:', secret)
        return cmd

    def __init__(self):
        pass

    def run(self, cmd, secrets=None, rcOk=(0,), dryRun=False):
        """ Execute a command """

        logCmd = Command._instantiateSecrets(cmd, secrets, hide=True)
        logging.debug(f"Executing command >>>\n{logCmd}\n<<<")

        result = None

        if dryRun:
            logging.info('dry run - not executing')
            result = Command.buildResult('', '', 0, rcOk)

        return result


class CmdShell(Command):
    """ Execute a local shell command """

    def __init__(self):
        # pylint: disable=useless-super-delegation
        super().__init__()

    def run(self, cmd, secrets=None, rcOk=(0,), dryRun=False):
        """ Execute a local shell command """

        result = super().run(cmd, secrets=secrets, rcOk=rcOk, dryRun=dryRun)

        if not result:

            runCmd = Command._instantiateSecrets(cmd, secrets, hide=False)

            cProc = subprocess.run(runCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=True, check=False)
            out   = cProc.stdout.decode().strip()
            err   = cProc.stderr.decode().strip()
            rcode = cProc.returncode

            result = Command.buildResult(out, err, rcode, rcOk)

        return result


class CmdSsh(Command):
    """ Execute a command on a remote host using SSH """

    @staticmethod
    def _getSshDir():
        """ Path to user's SSH directory """
        return f'{Path.home()}/.ssh'

    @staticmethod
    def _getSocketPath():
        """ Path to connection sharing control socket """
        return f'{CmdSsh._getSshDir()}/soos-%r@%h-%p'

    @staticmethod
    def _getSshCmdAndSecrets(hostname, user, sshId, reuseCon):
        """ Get a command to establish an SSH connections to <user.name@hostname>.

            The connection is established by means of the OpenSSH 'ssh' command.

            If reuseCon is true the command uses the OpenSSH connection sharing mechanism
            (via a control socket).

            Authentcation takes place as follows:

            - If sshId is not empty it will be used for authentication
            - otherwise if user.password is not empty it will be used for authentication.
            - If both sshId and user.password are empty generic OpenSSH ssh authentication
              is used (see section "AUTHENTICATION" in the OpenSSH 'ssh' command man page)
        """

        sshCmdSecrets = []

        if sshId:
            sshCmd = f'ssh -i {sshId}'

        elif user.password:
            sshCmd = 'sshpass -v -p :0: ssh'
            sshCmdSecrets += [user.password]

        else:
            sshCmd = 'ssh'

        sshCmd +=  ' -o StrictHostKeyChecking=no'

        if reuseCon:
            sshCmd +=  ' -o ControlMaster=auto'
            sshCmd += f' -o ControlPath={CmdSsh._getSocketPath()}'
            sshCmd +=  ' -o ControlPersist=600'

        # Need to separate login part for use with 'rsync -e'

        sshLogin  = f'{user.name}@{hostname}'

        return sshCmd, sshLogin, sshCmdSecrets

    def __init__(self, ctx, hostname, user, sshId=None, check=True, reuseCon=True):  # pylint: disable=too-many-arguments

        super().__init__()

        self._cmdShell = CmdShell()
        self._sshId         = None

        if not sshId:
            sshId = ctx.cr.build.user.sshid
            self._sshId = sshId

        if sshId:
            logging.debug(f"Using SSH ID '{sshId}'")
        else:
            logging.debug('SSH ID is not set')

        sshCmd, sshLogin, sshCmdSecrets = CmdSsh._getSshCmdAndSecrets(hostname, user,
                                                                      sshId, reuseCon)

        self._sshCmd        = sshCmd
        self._sshLogin      = sshLogin
        self._sshCmdSecrets = sshCmdSecrets

        # Check the connection and create the socket for connection
        # reuse in case the socket does not exist yet

        if check:

            logging.debug(f"Connecting to host '{hostname}'")

            res = self.run('true')
            if res.rc != 0:
                msg = self.formatSshError(res, hostname, user)
                fail(msg)

    def formatSshError(self, res, hostname, user):
        """ return formatted ssh error """
        logging.debug(f"Got SSH error: '{res.err}'")

        thisUser = getpass.getuser()
        thisHost = socket.gethostname()
        width = 67
        msg = formatMessageParagraphs([
            "Got SSH error when trying to establish connection",
            '',
            f"'{thisUser}@{thisHost}' → '{user.name}@{hostname}'.",
            '',
            '>>> Error message >>>',
            '',
            f"{res.err}",
            '',
            '<<< Error message <<<',
            '',
            f"Please make sure that the SSH public key"
            f" of user '{thisUser}' on host '{thisHost}'"
            f" is part of the 'authorized_keys' file"
            f" of user '{user.name}' on host '{hostname}'"
            f" by executing",
            '',
            "   ./tools/ssh-keys --add-keys",
            '',
            f"as user '{thisUser}' on host '{thisHost}' and"
        ], width-2, ' ', 1)
        msg += '\n\n'
        msg += formatMessageList([
            'rerun this command in an ssh-agent session',
            '',
            f"or remove the passphrase from the private key"
            f" of user '{thisUser}' on host '{thisHost}'"
            f" and rerun this command."
        ], width-2, ' ', 1)
        msg = '-'*width+f'\n{msg}\n'+'-'*width+'\n'
        return msg

    def run(self, cmd, secrets=None, rcOk=(0,), dryRun=False):
        """ Execute a command on a remote host using SSH """
        if secrets:
            cmd = Command._shiftSecrets(cmd, secrets, len(self._sshCmdSecrets))
        else:
            secrets = []

        cmd     = f"{self._sshCmd} {self._sshLogin} '{cmd}'"
        secrets = self._sshCmdSecrets + secrets

        return  self._cmdShell.run(cmd, secrets, rcOk, dryRun)

    def getSshCmdAndSecrets(self, withLogin=True):
        """ Get SSH command which is executed by this instance """

        sshCmd = self._sshCmd
        if withLogin:
            sshCmd += f' {self._sshLogin}'

        return sshCmd, self._sshCmdSecrets

    def passwordNeeded(self):
        """ True if password must be entered for ssh connection """
        cmd = "ssh "
        if self._sshId:
            cmd += f"-i {self._sshId} "
        cmd += f"-o PasswordAuthentication=no -o BatchMode=yes {self._sshLogin} 'exit'"
        return self._cmdShell.run(cmd).rc > 0
