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

""" Record time stamps during program execution and print them at program termination """


# Global Modules

import datetime
import inspect
import logging
import types


# Local Modules

from modules.table import Table


# Functions

def saveStartTime():
    """ Save program start time """
    saveCurrentTime('Program Start')


def saveEndTime():
    """ Save program termination time """
    saveCurrentTime('Program End')


def saveCurrentTime(label, traceback=None):
    """ Save current time together with a descriptive label """

    time = types.SimpleNamespace()
    time.label = label
    time.time = datetime.datetime.now()

    _getTimes(traceback).append(time)


def printTimes(traceback=None):
    """ Print all saved times """

    times = _getTimes(traceback)

    if len(times) > 0:
        table = Table(title    = 'Elapsed Times',
                      headings = ['Step', 'Date', 'Time', 'Δt Prev. Step'],
        )

        startTime = times[0].time
        prevTime  = startTime

        for time in times:

            curTime = time.time
            delta   = curTime-prevTime if curTime != prevTime else ''

            table.appendRow([time.label, curTime.date(), curTime.time(), delta])

            prevTime = curTime

        logging.critical(f'\n{table.render()}\n')  # Always log times


def _getTimes(traceback):

    # We store the times in the local variables section of the main module
    # For accessing them we first need to get the frame for the main module

    frame = _getModuleFrame(traceback)

    # Now we can retrieve the times from the local variable section of the main module

    if not frame:
        logging.debug("Could not find frame for '<module>'")
        times = []

    else:
        timesKey = '_soos_times'

        if timesKey not in frame.f_locals.keys():

            # This is the first time _getTimes() is called.
            # Add an empty times array to the local
            # variable section of the main module.

            frame.f_locals[timesKey] = []

        times = frame.f_locals[timesKey]

    return times


def _getModuleFrame(traceback):

    # Get the start frame for searching the main module frame
    # See https://docs.python.org/3/library/inspect.html

    if not traceback:
        # Retrieve the start frame via inspect()
        frame = inspect.currentframe()

    else:
        # Retrieve the start frame from the traceback
        # See https://www.oreilly.com/library/view/python-cookbook/0596001673/ch14s05.html

        while traceback.tb_next:
            traceback = traceback.tb_next
        frame = traceback.tb_frame

    # Search the main module frame starting from the start frame

    while frame and frame.f_code.co_name != '<module>':
        frame = frame.f_back

    return frame
