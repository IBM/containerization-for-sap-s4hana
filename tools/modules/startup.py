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

""" Common startup sequence for all tools """


# Global Modules

import sys


# Local Modules

from modules.exceptions import setExceptHook
from modules.times      import (
    printTimes,
    saveEndTime,
    saveStartTime
)


# Functions

def startup(mainFunc):
    """ Execute common startup sequence and start main function """

    # Handle specifc uncaught exceptions in a particular way
    # and print all saved times in case of an uncaught exception

    setExceptHook()

    # Save the program start time

    saveStartTime()

    # Run the program

    retCode = mainFunc()

    # Save the program termination time

    saveEndTime()

    # Print all saved times

    printTimes()

    exitCode = 0 if not retCode else retCode

    sys.exit(exitCode)
