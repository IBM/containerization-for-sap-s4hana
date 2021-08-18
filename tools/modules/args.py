# ------------------------------------------------------------------------
# Copyright 2020, 2021 IBM Corp. All Rights Reserved.
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
        ctx.ar.commonArgsStr += ' --dump-context'


# Common Args, used in all tools

def addArgConfigFile(argsParser):
    """ Argument: Configuration file """
    argsParser.add_argument(
        '-c',
        '--config-file',
        metavar  = '<config-file>',
        required = False,
        default  = './config.yaml',
        help     = 'Configuration file'
    )


def addArgCredsFile(argsParser):
    """ Argument: Credentials file """
    argsParser.add_argument(
        '-q',
        '--creds-file',
        metavar  = '<creds-file>',
        required = False,
        default  = './creds.yaml.gpg',
        help     = 'Credentials file (encrypted)'
    )


def addArgLogFileDir(argsParser):
    """ Argument: Directory to which logging files are written """
    argsParser.add_argument(
        '-g',
        '--logfile-dir',
        metavar  = '<logfile-dir>',
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
        '--loglevel',
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
        '--log-to-terminal',
        required = False,
        action   ='store_true',
        help     = "Log to terminal instead of logging to file"
    )


def addArgDumpContext(argsParser):
    """ Argument: Dump context (CLI arguments, configuration, credentials) """
    argsParser.add_argument(
        '--dump-context',
        required = False,
        action   ='store_true',
        help     = "Dump context (CLI arguments, configuration, credentials)"
    )


# Non-common args, used in multiple tools

def addArgContainerFlavor(argsParser, choices=('di', 'ascs', 'hdb'), required=False):
    """ Argument: Container flavor """
    argsParser.add_argument(
        '-i',
        '--container-flavor',
        metavar  = '<container-flavor>',
        required = required,
        choices  = choices,
        default  = choices[0],
        help     = "Container flavor ('"+"', '".join(choices)+"')"
    )


def addArgImageFlavor(argsParser, choices=('init', 'nws4', 'hdb'), required=False):
    """ Argument: Image flavor """
    argsParser.add_argument(
        '-f',
        '--image-flavor',
        metavar  = '<image-flavor>',
        required = required,
        choices  = choices,
        default  = choices[0],
        help     = "Image flavor ('"+"', '".join(choices)+"')"
    )


def addArgOutputFile(argsParser, default):
    """ Argument: Output file """
    argsParser.add_argument(
        '-o',
        '--output-file',
        metavar  = '<output-file>',
        required = False,
        default  = default,
        help     = "Path to output file"
    )


def addArgOverlayUuid(argsParser, required=True):
    """ Argument: Overlay share unique ID """
    argsParser.add_argument(
        '-u',
        '--overlay-uuid',
        metavar  = '<overlay-uuid>',
        required = required,
        help     = "UUID of the overlay NFS share on which the HANA DB data resides"
    )
