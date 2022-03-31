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

""" Helper tools for message formatting """


# Global modules

import textwrap


# Functions

def formatMessageParagraphs(paragraphs, width, prefix, indentLevel):
    """ Format a list of paragraphs """
    return _formatMessage(paragraphs, width, prefix*indentLevel, prefix*indentLevel)


def formatMessageList(listItems, width, prefix, indentLevel):
    """ Format a list of list items """
    return _formatMessage(listItems, width, prefix*indentLevel+'- ', prefix*indentLevel+'  ')


def getMessage(*parmList):
    """ returns the message text for given message number """
    msgNo = parmList[0]
    # First entry in parmList is the msgNo, ignore it!
    nmbrOfParmsPassed = len(parmList) - 1
    messageText = ""
    msgObj = msgList[msgNo]

    if msgObj["noOfParms"] != nmbrOfParmsPassed:
        # Throw exception?
        return messageText
    # Replacing placeholders
    for element in msgObj["msg"]:
        messageText += _formatMessageElement(element, parmList)
    return messageText


def _formatMessage(paragraphs, width, initialPrefix, subsequentPrefix):
    msg = ''
    first = True
    for paragraph in paragraphs:
        if first:
            first = False
        else:
            msg += '\n'
        msg += '\n'.join(textwrap.wrap(paragraph,
                                       width=width,
                                       initial_indent=initialPrefix,
                                       subsequent_indent=subsequentPrefix
                                       )
                         )
    return msg


def _formatMessageElement(element, parmList):
    if "index" in element.keys():
        return element["msg"].format(parmList[element["index"]])
    return element["msg"]


def _setNumberOfParms(msgObj):
    highestNo = 0
    for element in msgObj:
        if "index" in element.keys():
            if element["index"] > highestNo:
                highestNo = element["index"]
    return highestNo


# Message definitions

# Messages printed by logging

# parmList:
# 1: type of the resource (limits/requests)
# 2: containerType
# 3: memory size
msgL001 = [{"msg":   "Caution: You did not specify a value for the {} ",
            "index":  1},
           {"msg":   "memory size for the "},
           {"msg":   "{} container.\n",
            "index":  2},
           {"msg":   "The memory size is set to its default value {}.\n",
            "index":  3},
           {"msg":   "If the 'limits' memory size is smaller than the value "},
           {"msg":   "of the 'requested' memory size, \n"},
           {"msg":   "the generation of the deployment will fail "},
           {"msg":   "and the process is stopped. \n"},
           {"msg":   "Use the 'verify-config' tool to make sure "},
           {"msg":   "that your memory settings are valid.\n"}]

# Messages printed by Exceptions

# parmList:
# 1: path to rpm file
# 2: packageName
# 3: additional error text
msgE001 = [{"msg":   "The default package file path '{}' ",
            "index":  1},
           {"msg":   "{} \n",
            "index":  3},
           {"msg":   "Provide the rpm package file for package '{}' ",
            "index":  2},
           {"msg":   "at the local directory {}. \n",
            "index":  1},
           {"msg":   "For more information about additionally required RPM packages "},
           {"msg":   "see the documentation."}]

# parmList:
# 1: limits memory size
# 2: containerType
# 3: requests memory size
msgE002 = [{"msg":   "The specified 'limits' memory value {} ",
            "index":  1},
           {"msg":   "for the {} container \n",
            "index":  2},
           {"msg":   "is less than the specified 'requests' memory value {}.\n",
            "index":  3},
           {"msg":   "The Container cannot be started."}]

msgList = {"msgE001": {"msg": msgE001, "noOfParms": _setNumberOfParms(msgE001)},
           "msgE002": {"msg": msgE002, "noOfParms": _setNumberOfParms(msgE002)},
           "msgL001": {"msg": msgL001, "noOfParms": _setNumberOfParms(msgL001)}
          }
