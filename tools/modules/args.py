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

""" Command line argument handling """


# Global modules

import argparse


# Local modules

from modules.argsdoc   import ArgsDocsGfmAction
from modules.constants import getConstants


# Functions


# Args parser

def getCommonArgsParser(description=''):
    """ Get parser for common CLI arguments """
    parser = argparse.ArgumentParser(
        description     = description,
        formatter_class = argparse.ArgumentDefaultsHelpFormatter
    )

    addArgConfigFile(parser)     # -c
    addArgCredsFile(parser)      # -q
    addArgLogFileDir(parser)     # -g
    addArgLogLevel(parser)       # -v
    addArgLogToTerminal(parser)  # -w
    addArgDumpContext(parser)    # <no short switch>
    addArgGenDocGfm(parser)      # <no short switch>

    return parser


def getCommonArgs(description=''):
    """ Get common CLI arguments """
    return getCommonArgsParser(description).parse_args()


def addCommonArgsString(ctx):
    """ Add string of all common CLI arguments including current values to context """

    ctx.ar.commonArgsStr = ''
    ctx.ar.commonArgsStr += f' -c {ctx.ar.config_file}'
    ctx.ar.commonArgsStr += f' -q {ctx.ar.creds_file}'
    ctx.ar.commonArgsStr += f' -g {ctx.ar.logfile_dir}'
    ctx.ar.commonArgsStr += f' -v {ctx.ar.loglevel}'

    if ctx.ar.log_to_terminal:
        ctx.ar.commonArgsStr += ' -w'

    if ctx.ar.dump_context:
        ctx.ar.commonArgsStr += f' --{ctx.cs.argDumpContext}'

    if ctx.ar.gen_doc_gfm:
        ctx.ar.commonArgsStr += f' --{ctx.cs.argGenDocGfm}'


# Common Args, used in all tools

def addArgConfigFile(argsParser):
    """ Argument: Configuration file """
    argsParser.add_argument(
        '-c',
        f'--{getConstants().argConfigFile}',
        metavar  = f'<{getConstants().argConfigFile}>',
        required = False,
        default  = './config.yaml',
        help     = 'Configuration file'
    )


def addArgCredsFile(argsParser):
    """ Argument: Credentials file """
    argsParser.add_argument(
        '-q',
        f'--{getConstants().argCredsFile}',
        metavar  = f'<{getConstants().argCredsFile}>',
        required = False,
        default  = './creds.yaml.gpg',
        help     = 'Credentials file (encrypted)'
    )


def addArgLogFileDir(argsParser):
    """ Argument: Directory to which logging files are written """
    argsParser.add_argument(
        '-g',
        f'--{getConstants().argLogFileDir}',
        metavar  = f'<{getConstants().argLogFileDir}>',
        required = False,
        default  = './log',
        help     = 'logfile directory'
    )


def addArgLogLevel(argsParser):
    """ Argument: Logging level """

    loglevelChoices = [
        'critical',  # logging.CRITICAL
        'error',     # logging.ERROR
        'warning',   # logging.WARNING
        'info',      # logging.INFO
        'debug',     # logging.DEBUG
        'notset'     # logging.NOTSET
    ]

    loglevelDefault = 'warning'

    argsParser.add_argument(
        '-v',
        f'--{getConstants().argLogLevel}',
        type     = str,
        default  = loglevelDefault,
        required = False,
        choices  = loglevelChoices,
        help     = 'logging level'
    )


def addArgLogToTerminal(argsParser):
    """ Argument: Flag to enable logging to terminal instead of logging to file  """
    argsParser.add_argument(
        '-w',
        f'--{getConstants().argLogToTerminal}',
        required = False,
        action   ='store_true',
        help     = "Log to terminal instead of logging to file"
    )


def addArgDumpContext(argsParser):
    """ Argument: Dump context (CLI arguments, configuration, credentials) """
    argsParser.add_argument(
        f'--{getConstants().argDumpContext}',
        required = False,
        action   ='store_true',
        help     = "Dump context (CLI arguments, configuration, credentials)"
    )


def addArgGenDocGfm(argsParser):
    """ Argument: Generate documentation snippet for inclusion in GFM files """
    argsParser.add_argument(
        f'--{getConstants().argGenDocGfm}',
        required = False,
        action   = ArgsDocsGfmAction,
        nargs    = 0,
        help     = argparse.SUPPRESS
    )


# Non-common args, used in multiple tools

def addArgContainerFlavor(argsParser, choices=('di', 'ascs', 'hdb'), required=False):
    """ Argument: Container flavor """
    argsParser.add_argument(
        '-i',
        f'--{getConstants().argContainerFlavor}',
        metavar  = f'<{getConstants().argContainerFlavor}>',
        required = required,
        choices  = choices,
        default  = choices[0],
        help     = "Container flavor ('"+"', '".join(choices)+"')"
    )


def addArgImageFlavor(argsParser, choices=('init', 'nws4', 'hdb'), required=False):
    """ Argument: Image flavor """
    argsParser.add_argument(
        '-f',
        f'--{getConstants().argImageFlavor}',
        metavar  = f'<{getConstants().argImageFlavor}>',
        required = required,
        choices  = choices,
        default  = choices[0],
        help     = "Image flavor ('"+"', '".join(choices)+"')"
    )


def addArgOutputFile(argsParser, default):
    """ Argument: Output file """
    argsParser.add_argument(
        '-o',
        f'--{getConstants().argOutputFile}',
        metavar  = f'<{getConstants().argOutputFile}>',
        required = False,
        default  = default,
        help     = "Path to output file"
    )


def addArgOverlayUuid(argsParser, required=True, helpText=None):
    """ Argument: Overlay share unique ID """
    if not helpText:
        helpText = "UUID of the overlay NFS share on which the HANA DB data resides"

    argsParser.add_argument(
        '-u',
        f'--{getConstants().argOverlayUuid}',
        metavar  = f'<{getConstants().argOverlayUuid}>',
        required = required,
        help     = helpText
    )


def addArgAdditionalDeployments(argsParser):
    """ Argument: deployment suffix number, must be between 1 and 99 """
    argsParser.add_argument(
        '-n',
        f'--{getConstants().argNumber}',
        metavar  = '<number-of-deployments>',
        required = False,
        type     = int,
        default  = 1,
        help     = "Number of deployments to be added"
    )


def addArgDeploymentFile(argsParser, required=False, helpText=None):
    """ Argument: deployment filename """
    if not helpText:
        helpText = "Deployment filename"
    argsParser.add_argument(
        '-f',
        f'--{getConstants().argDeploymentFile}',
        metavar  = f'<{getConstants().argDeploymentFile}>',
        required = required,
        help     = helpText
    )


def addArgLoop(argsParser):
    """ Argument: loop """
    argsParser.add_argument(
        '-l',
        f'--{getConstants().argLoop}',
        required = False,
        action   = 'store_true',
        help     = "Print information in endless loop"
    )


def addArgSleepTime(argsParser):
    """ Argument: sleeptime """
    argsParser.add_argument(
        '-t',
        f'--{getConstants().argSleepTime}',
        metavar  = f'<{getConstants().argSleepTime}>',
        required = False,
        type     = int,
        default  = 5,
        help     = "Sleep time in seconds between two loop executions"
    )


def addArgAppName(argsParser, default=None):
    """ Argument: app-name """
    helpText  = "Application Name. Specify either "
    helpText += "the uuid, "
    helpText += "a unique part or "
    helpText += "the whole application name."

    argsParser.add_argument(
        f'--{getConstants().argAppName}',
        metavar  = f'<{getConstants().argAppName}>',
        required = False,
        default  = default,
        help     = helpText
    )
