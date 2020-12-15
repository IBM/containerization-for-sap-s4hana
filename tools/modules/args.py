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

""" Command line argument handling """

# Global modules

import argparse

# Functions

# pylint: disable=bad-whitespace


def getCommonArgsParser(description=""):
    """ Get parser for common CLI  arguments """
    parser = argparse.ArgumentParser(
        description     = description,
        formatter_class = argparse.ArgumentDefaultsHelpFormatter
    )

    addArgLogLevel(parser)       # -v
    addArgLogToTerminal(parser)  # -w
    addArgLogFileDir(parser)     # -g
    addArgConfigFile(parser)     # -c

    return parser


def getCommonArgs(description=""):
    """ Get common CLI arguments """
    return getCommonArgsParser(description).parse_args()


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


def addArgFlavor(argsParser, choices=('init', 'nws4', 'hdb'), required=False):
    """ Argument: Flavor of image file """
    argsParser.add_argument(
        '-f',
        '--flavor',
        metavar  = '<flavor>',
        required = required,
        choices  = choices,
        default  = choices[0],
        help     = "Flavor of image file ('"+"', '".join(choices)+"')"
    )


def addArgNws4InstanceType(argsParser, choices=('di', 'ascs'), required=False):
    """ Argument: Instance type for flavor 'nws4' """
    argsParser.add_argument(
        '-i',
        '--nws4-instance-type',
        metavar  = '<nws4_instance_type>',
        required = required,
        choices  = choices,
        default  = choices[0],
        help     = "Instance type for flavor 'nws4' ('"+"', '".join(choices)+"')"
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


def addArgLogToTerminal(argsParser):
    """ Argument: Flag to enable logging to terminal instead of logging to file  """
    argsParser.add_argument(
        '-w',
        '--log-to-terminal',
        required = False,
        action   ='store_true',
        help     = "Log to terminal instead of logging to file"
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


def addArgHelperUser(argsParser, required=False):
    """ Argument: Overlay share unique ID """
    argsParser.add_argument(
        '--helper-user',
        metavar  = '<helper-user>',
        required = required,
        default  = 'root',
        help     = 'Name of user used for login on helper node'
    )
