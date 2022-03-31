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

""" Exceptions """


# Global modules

import sys


# Local modules

from modules.messages import getMessage
from modules.times    import (
    saveCurrentTime,
    printTimes
)


# Classes

class RpmFileNotFoundException(Exception):
    """ Raises if RPM File for specific package could not be found  """

    def __init__(self, path, packageName, err):
        super().__init__()
        self.errorText = getMessage("msgE001", path, packageName, err)


# Functions

def setExceptHook():
    """ Set the global exception hook """

    sys.excepthook = _exceptHook


def _exceptHook(extype, exinstance, traceback):
    """ Handle an exception depending on the type of the exception """

    # Print times recorded during program execution

    saveCurrentTime('Exception', traceback)
    printTimes(traceback)

    # Handle exception

    if extype == KeyboardInterrupt:
        _exceptHookKeyboardInterrupt(extype, exinstance, traceback)

    elif extype == ModuleNotFoundError:
        _exceptHookModuleNotFoundError(extype, exinstance, traceback)

    else:
        sys.__excepthook__(extype, exinstance, traceback)


def _exceptHookKeyboardInterrupt(extype, exinstance, traceback):
    # pylint: disable=unused-argument
    print()


def _exceptHookModuleNotFoundError(extype, exinstance, traceback):
    # pylint: disable=unused-argument
    hrule = '\n' + '='*50 + '\n'
    print(f'{hrule}\n',
          f' GOT THE FOLLOWING EXCEPTION:\n\n'
          f'    {exinstance}\n',
          sep = '',
          file=sys.stderr
    )

    if sys.prefix != sys.base_prefix:
        # Running in a virtual environment
        print(' YOUR VIRTUAL PYTHON ENVIRONMENT SEEMS NOT TO BE\n'
              ' SET UP AS EXPECTED.\n\n'
              ' LEAVE YOUR VIRTUAL ENVIRONMENT BY EXECUTING\n\n'
              '    deactivate\n\n'
              ' AND REMOVE IT BY EXECUTING\n\n'
              '     rm -rf ./venv/\n\n'
              ' RECREATE THE VIRTUAL ENVIRONMENT BY RUNNING\n\n'
              '     tools/venv-setup\n\n'
              ' AND ACTIVATE IT BY EXECUTING\n\n'
              '     source ./venv/bin/activate',
              file=sys.stderr
        )

    else:
        # Not running in a virtual environment
        print(' NOT RUNNING IN A VIRTUAL PYTHON ENVIRONMENT.\n\n'
              ' CREATE A VIRTUAL PYTHON ENVIRONMENT BY RUNNING\n\n'
              '     tools/venv-setup\n\n'
              ' AND ACTIVATE IT BY EXECUTING\n\n'
              '     source ./venv/bin/activate\n\n'
              ' OR MAKE SURE THAT YOUR CURRENT PYTHON RUNTIME\n'
              ' ENVIRONMENT PROVIDES ALL REQUIRED PYTHON MODULES\n'
              " (SEE ERROR MESSAGE ABOVE).",
              file=sys.stderr
        )

    print(hrule, file=sys.stderr)
