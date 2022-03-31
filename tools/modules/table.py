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

""" Render a table using Unicode box drawings characters

    Features:

    - The width of a column automatically adapts to the
      maximum item width of all items displayed in the column

    - Display optional title in the table header

    - Display optional column headings

    - Optionally separate table rows by separator rows

    - Multiple line styles ('none', 'light', 'lightarc', 'heavy', 'double')

    - Choosable title, column headings and data cells alignments

    - Choosable horizontal cell margin width

 """


# Global modules

import logging
import types


# Classes

class Table():
    """ Render a table using Unicode box drawings characters """

    # pylint: disable=too-many-instance-attributes

    # Table styles

    STYLE_NONE     = 0
    STYLE_LIGHT    = 1
    STYLE_LIGHTARC = 2
    STYLE_HEAVY    = 3
    STYLE_DOUBLE   = 4

    _styles = [
        # STYLE_NONE
        {
            'dh':  '─',  # down-horizontal
            'dl':  ' ',  # down-left
            'dr':  ' ',  # down-right
            'h':   '─',  # horizontal
            'uh':  '─',  # up-horizontal
            'ul':  ' ',  # up-left
            'ur':  ' ',  # up-right
            'v':   ' ',  # vertical
            'vh':  '─',  # vertical-horizontal
            'vl':  ' ',  # vertical-left
            'vr':  ' ',  # vertical-right

            'rsf': '╶',  # row separator fill
            'rsi': '╶',  # row separator inner
            'rsl': ' ',  # row separator left
            'rsr': ' ',  # row separator right
        },

        # STYLE_LIGHT
        {
            'dh':  '┬',  # down-horizontal
            'dl':  '┐',  # down-left
            'dr':  '┌',  # down-right
            'h':   '─',  # horizontal
            'uh':  '┴',  # up-horizontal
            'ul':  '┘',  # up-left
            'ur':  '└',  # up-right
            'v':   '│',  # vertical
            'vh':  '┼',  # vertical-horizontal
            'vl':  '┤',  # vertical-left
            'vr':  '├',  # vertical-right

            'rsf': '╶',  # row separator fill
            'rsi': '│',  # row separator inner
            'rsl': '│',  # row separator left
            'rsr': '│',  # row separator right
        },

        # STYLE_LIGHTARC
        {
            'dh':  '┬',  # down-horizontal
            'dl':  '╮',  # down-left
            'dr':  '╭',  # down-right
            'h':   '─',  # horizontal
            'uh':  '┴',  # up-horizontal
            'ul':  '╯',  # up-left
            'ur':  '╰',  # up-right
            'v':   '│',  # vertical
            'vh':  '┼',  # vertical-horizontal
            'vl':  '┤',  # vertical-left
            'vr':  '├',  # vertical-right

            'rsf': '╶',  # row separator fill
            'rsi': '│',  # row separator inner
            'rsl': '│',  # row separator left
            'rsr': '│',  # row separator right
        },

        # STYLE_HEAVY
        {
            'dh':  '┳',  # down-horizontal
            'dl':  '┓',  # down-left
            'dr':  '┏',  # down-right
            'h':   '━',  # horizontal
            'uh':  '┻',  # up-horizontal
            'ul':  '┛',  # up-left
            'ur':  '┗',  # up-right
            'v':   '┃',  # vertical
            'vh':  '╋',  # vertical-horizontal
            'vl':  '┫',  # vertical-left
            'vr':  '┣',   # vertical-right

            'rsf': '─',  # row separator fill
            'rsi': '╂',  # row separator inner
            'rsl': '┠',  # row separator left
            'rsr': '┨',  # row separator right
        },

        # STYLE_DOUBLE
        {
            'dh':  '╦',  # down-horizontal
            'dl':  '╗',  # down-left
            'dr':  '╔',  # down-right
            'h':   '═',  # horizontal
            'uh':  '╩',  # up-horizontal
            'ul':  '╝',  # up-left
            'ur':  '╚',  # up-right
            'v':   '║',  # vertical
            'vh':  '╬',  # vertical-horizontal
            'vl':  '╣',  # vertical-left
            'vr':  '╠',   # vertical-right

            'rsf': '─',  # row separator fill
            'rsi': '╫',  # row separator inner
            'rsl': '╟',  # row separator left
            'rsr': '╢',  # row separator right
        }
    ]

    def __init__(self,
                 title="",           # table title
                 headings=None,      # list of column headings
                 tAlign='',          # table tile alignment ('<' (left), '^' (center), '>' (right))
                 hAlign='',          # string of '<', '^', '>', one for each heading
                 cAlign='',          # string of '<', '^', '>', one for each column
                 style=STYLE_LIGHT,  # table line style
                 rowSep=False,       # add separater row between two data rows
                 hMargin=1           # #spaces between cell content and left / right separators
    ):
        # pylint: disable=too-many-arguments
        self._title     = title
        headings        = headings if headings   else []
        self._tAlign    = self._checkCorrectAlign(tAlign, '^')
        self._hAlign    = self._checkCorrectAlign(hAlign, '^')
        self._cAlign    = self._checkCorrectAlign(cAlign, '<')
        self._style     = types.SimpleNamespace(**Table._styles[style])
        self._rowSep    = rowSep
        self._hMargin   = hMargin

        self._rows      = []
        self._numCols   = len(headings)
        self._colWidths = []

        self.appendRow(headings)  # headings are stored as first rows

    # Public methods

    def appendRow(self, row):
        """ Append a row of items to the table

            If there are table headings:

            - If the row contains x items less than the number of column headings
              x new items with content '?' are appended to the row.

            - If the row contains x more items than the number of column headings
              x new headings with label '?' are appended to the column headings.
        """
        return self._appendRow(row)

    def render(self):
        """ Return a string containing the rendered table """
        return self._render()

    # Private methods

    def _checkCorrectAlign(self, align, default):
        """ Replace all invalid characters in 'align' by 'default' """
        if not align:
            cAlign = default
        else:
            cAlign = ''
            for alg in align:
                if alg in '<^>':
                    cAlign += alg
                else:
                    cAlign += default
        return cAlign

    def _appendRow(self, row):
        """ Append a row of data to the table """

        if not isinstance(row, list):
            logging.debug(f"'{row} ({type(row)})' is not a list - ignoring")
            return

        row = [str(item) for item in row]             # Convert all data in the row to strings
        self._numCols = max(self._numCols, len(row))  # Adjust number of columns
        self._recalcColWidths(row)                    # Adjust list of column widths
        self._rows.append(row)                        # Add the row

    def _recalcColWidths(self, row):
        """ Set each colum width to the current maximum string width in the column """

        cwLen  = len(self._colWidths)
        rowLen = len(row)

        newWidths = []

        for i in range(self._numCols):
            colWidth  = self._colWidths[i] if i < cwLen  else 0
            itemWidth = len(row[i])        if i < rowLen else 0
            newWidths.append(max(colWidth, itemWidth))

        self._colWidths = newWidths

    def _render(self):
        """ Return a string containing the rendered table """

        rTable = ''

        # Title and / or header

        if self._title:
            # Header including title
            rTable += self._renderRule(self._style.dr, self._style.h,
                                       self._style.dl, self._style.h) + '\n'
            rTable += self._renderTitle() + '\n'
            rTable += self._renderRule(self._style.vr, self._style.dh,
                                       self._style.vl, self._style.h) + '\n'
        else:
            # Header without title
            rTable += self._renderRule(self._style.dr, self._style.dh,
                                       self._style.dl, self._style.h) + '\n'

        # Column headings
        #
        # Headings are stored as first row and are empty if no headings were specified

        headings = self._rows[0]

        if headings:
            rTable += self._renderRow(headings, self._hAlign, '^') + '\n'
            rTable += self._renderRule(self._style.vr, self._style.vh,
                                       self._style.vl, self._style.h) + '\n'

        # Rows
        #
        # Data rows start with the second row

        for row in self._rows[1:-1]:
            # All rows but last row
            rTable += self._renderRow(row, self._cAlign, '<') + '\n'
            if self._rowSep:
                rTable += self._renderRule(self._style.rsl, self._style.rsi,
                                           self._style.rsr, self._style.rsf) + '\n'
        rTable += self._renderRow(self._rows[-1], self._cAlign, '<') + '\n'  # last row

        # Footer

        rTable += self._renderRule(self._style.ur, self._style.uh,
                                   self._style.ul, self._style.h)

        return rTable

    def _renderTitle(self):
        titleWidth = sum(self._colWidths)                      # column widths without margins
        titleWidth += (self._numCols - 1) * 2 * self._hMargin  # add sum of inner margin widths
        titleWidth += self._numCols - 1                        # add number of inner separators

        title = self._renderCell(self._title, titleWidth, self._tAlign, ' ')

        return f'{self._style.v}{title}{self._style.v}'

    def _renderRule(self, left, inner, right, hfill):
        rule = left
        for width in self._colWidths[:-1]:
            # All columns but last column
            rule += self._renderCell(hfill * width, width, '<', hfill)
            rule += inner
        width = self._colWidths[-1]
        rule += self._renderCell(hfill * width, width, '<', hfill)  # last column
        rule += right
        return rule

    def _renderRow(self, row, rowAlign, alignDefault):
        rowLen  = len(row)
        rowALen = len(rowAlign)

        rRow = self._style.v

        for i in range(self._numCols):
            item  = row[i]      if i < rowLen else  '?'
            align = rowAlign[i] if i < rowALen else alignDefault
            rRow += self._renderCell(item, self._colWidths[i], align, ' ')
            rRow += self._style.v

        return rRow

    def _renderCell(self, item, width, align, marginFill):
        item  = ('{i:'+align+'{w}}').format(i=item, w=width)
        fill  = marginFill * self._hMargin
        return fill + item + fill
