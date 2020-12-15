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

""" Execute a command """

# Global modules

import logging
import os
import subprocess
import sys
import types

import paramiko

# Classes


class Command():
    """ Execute a command """

    def __init__(self):
        pass

    def _buildResult(self, cmd, out, err, rc, rcOk):
        # pylint: disable=invalid-name,too-many-arguments
        if rc not in rcOk:
            logFunc = logging.error
        else:
            logFunc = logging.debug

        logFunc(f'cmd >>>{cmd}<<<')
        logFunc(f'out >>>{out}<<<')
        logFunc(f'err >>>{err}<<<')
        logFunc(f'rc  >>>{rc}<<<')

        return types.SimpleNamespace(**{
            'out': out,
            'err': err,
            'rc':  rc
        })

    def run(self, cmd, rcOk=(0,), dryRun=False):
        """ Execute a command """
        result = None
        if dryRun:
            logging.info('dry run - not executing')
            result = self._buildResult(cmd, '', '', 0, rcOk)
        return result


class CmdSsh(Command):
    """ Execute a command on a remote host using SSH """

    def __init__(self, hostname, username, password=''):
        super().__init__()
        self._sshClient = paramiko.SSHClient()
        self._sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._sshClient.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        try:
            if len(password) > 0:
                self._sshClient.connect(hostname, username=username, password=password)
            else:
                self._sshClient.connect(hostname, username=username)
        except paramiko.ssh_exception.SSHException:
            msg = 'Please run this command in an ssh-agent session' \
                  ' or provide an SSH key pair with a passphraseless private key'
            print('-'*len(msg)+f'\n{msg}\n'+'-'*len(msg), file=sys.stderr)
            sys.exit(1)
        logging.getLogger("paramiko").setLevel(logging.WARNING)

    def run(self, cmd, rcOk=(0,), dryRun=False):
        """ Execute a command on a remote host using SSH """
        result = super().run(cmd, dryRun)
        if not result:
            # pylint: disable=bad-whitespace,invalid-name
            _stdin, _stdout, _stderr = self._sshClient.exec_command(cmd)
            out = _stdout.read().decode().strip()
            err = _stderr.read().decode().strip()
            rc  = _stdout.channel.recv_exit_status()
            result = self._buildResult(cmd, out, err, rc, rcOk)
        return result


class CmdShell(Command):
    """ Execute a local shell command """

    def __init__(self):
        # pylint: disable=useless-super-delegation
        super().__init__()

    def run(self, cmd, rcOk=(0,), dryRun=False):
        """ Execute a local shell command """
        result = super().run(cmd, dryRun)
        if not result:
            # pylint: disable=bad-whitespace,invalid-name
            cProc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=True, check=False)
            out = cProc.stdout.decode().strip()
            err = cProc.stderr.decode().strip()
            rc  = cProc.returncode
            result = self._buildResult(cmd, out, err, rc, rcOk)
        return result
