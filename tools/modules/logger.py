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

""" Logging setup """

# Global modules

import logging
import os
import sys
import time

# Functions


def _getScriptName():
    scriptName = os.path.basename(sys.argv[0])
    if scriptName.endswith('.py'):
        scriptName = scriptName[:-3]
    return scriptName


def _getLogFilePath(logfileDir, infix=''):
    prefix = _getScriptName()
    if len(infix) > 0:
        prefix += '-'+infix
    return f'{logfileDir}/{prefix}-{str(time.time()).replace(".","")}.log'


def setupLogging(args, infix=''):
    """ Set up logging """

    # Delete existing root handlers except in case we write log messages to terminal

    if not args.log_to_terminal:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    # Custom formatting

    class _LogRecordFactory(logging.LogRecord):
        # pylint: disable=too-few-public-methods
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.origin = f"{self.filename}:{self.funcName}()"
    logging.setLogRecordFactory(_LogRecordFactory)

    logFormat = '[{origin:25}] {message}'

    # Configure logging

    loglevel = getattr(logging, args.loglevel.upper())

    if args.log_to_terminal:
        logging.basicConfig(format=logFormat, style='{', level=loglevel)
    else:
        if not os.path.exists(args.logfile_dir):
            os.makedirs(args.logfile_dir)
        logFilePath = _getLogFilePath(args.logfile_dir, infix=infix)
        logging.basicConfig(format=logFormat, style='{', level=loglevel,
                            filename=logFilePath, filemode='w')
        print(f"Logging to '{logFilePath}'", file=sys.stderr)
