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

""" Generate documentation from CLI command definitions """


# Global modules

import argparse
import html
import sys


# Classes

# The follwowing classes partly rely on internal
# implementation details of the Python argparse module
#
# See https://github.com/python/cpython/blob/main/Lib/argparse.py

# The following classes were inspired by the GitHub Gist
#
# https://gist.githubusercontent.com/parajain/772e138f7604c0ecb7e57898e45a903a/raw/e7e8e4d5544e337cbfa1ec527d093e287da23045/generate_doc.py
#
# This Gist contains the following note:
#
# > MARKDOWN boilerplate
# >
# > Copyright 2016 The Chromium Authors. All rights reserved.
# > Use of this source code is governed by a BSD-style license that can be
# > found in the LICENSE file.
#
# XXX TO BE SOLVED BEFORE PUBLICATION ON github.com:
# - DO WE HAVE TO MENTION THE GIST SINCE THE CODE WAS CONSIDERABLY CHANGED?
# - IF YES, WHAT DO WE HAVE TO DO IN DETAIL TO FULFILL THE ABOVE COPYRIGHT STATEMENT


class ArgsDocsGfmAction(argparse.Action):
    """ Python argparse action for generating a
        GitHub Flavored Markdown (GFM) document snippet """

    def __call__(self, parser, namespace, values, option_string=None):

        parser.formatter_class = _ArgsDocsGfmFormatter

        # Format the GFM snippet from the argparse definitions

        gfm = parser.format_help()

        # Remove trailing ':' at end of table definition line
        # emitted by argparse._Section().format_help()
        # There seems to be no other was of getting rid of the ':'

        gfm = gfm.replace(':--------|:\n', ':--------|\n')

        print(gfm)

        sys.exit(0)


class _ArgsDocsGfmFormatter(argparse.HelpFormatter):
    """ Python argparse help formatter for generating a
        GitHub Flavored Markdown (GFM) document snippet """

    def format_help(self):
        # Generate GFM snippet by means of parent class formatter
        # Prepend GFM heading

        return f'## Tool `{self._prog}`\n\n{super().format_help()}'

    def _format_usage(self, usage, actions, groups, prefix):
        # Generate GFM for usage section by means of parent class formatter

        usage = super()._format_usage(usage, actions, groups, prefix='')

        # Trim the received string by removing all unwanted whitespaces

        usage = ' '.join(s.strip() for s in usage.split())

        # Prepend the heading for the 'Usage' section
        # Also append the heading for the 'Purpose' section since there
        # seems to be no other way to get it into the final GFM snippet

        usage = f'### Usage\n\n`{usage}`\n\n### Purpose\n\n'

        return usage

    def start_section(self, heading):
        # Formatter for head of each section
        # 'heading': 'positional arguments', 'optional arguments', ...

        # Capitalize the first character of each word in heading
        # and HTML escape the heading

        heading = ' '.join(s.capitalize() for s in heading.split())
        heading = html.escape(heading)

        # Start the section by means of the parent class formatter
        # Pass the table head in addition to the heading

        super().start_section(
            f'### {heading}\n'
            f'\n'
            f'| Argument | Description | Default |\n'
            f'|:---------|:------------|:--------|'
        )

    def _format_action(self, action):
        # Formatter for a single CLI argument

        argument    = f'`{super()._format_action_invocation(action)}`'
        description = html.escape(self._expand_help(action))
        default     = f'`{action.default}`' if action.default != argparse.SUPPRESS else ''

        return f'| {argument} | {description} | {default} |\n'
