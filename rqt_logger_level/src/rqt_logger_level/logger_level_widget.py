# Software License Agreement (BSD License)
#
# Copyright (c) 2012, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os

from qt_gui.qt_binding_helper import loadUi
from QtCore import qWarning
from QtGui import QWidget


class LoggerLevelWidget(QWidget):
    """
    Widget for use with LoggerLevelServiceCaller class to alter the loggerlevels
    """
    def __init__(self, caller):
        super(QWidget, self).__init__()
        ui_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logger_level.ui')
        loadUi(ui_file, self)
        self.setObjectName('LoggerLevelWidget')

        self._caller = caller

        self.node_list.currentRowChanged[int].connect(self.node_changed)
        self.logger_list.currentRowChanged[int].connect(self.logger_changed)
        self.level_list.currentRowChanged[int].connect(self.level_changed)
        self.refresh_button.clicked[bool].connect(self.refresh_nodes)

        self.refresh_nodes()
        if self.node_list.count() > 0:
            self.node_list.setCurrentRow(0)

    def refresh_nodes(self):
        self.level_list.clear()
        self.logger_list.clear()
        self.node_list.clear()
        for name in self._caller.get_node_names():
            self.node_list.addItem(name)

    def node_changed(self, row):
        if row == -1:
            return
        if row < 0 or row >= self.node_list.count():
            qWarning('Node row %s out of bounds. Current count: %s' % (row, self.node_list.count()))
            return
        self.logger_list.clear()
        self.level_list.clear()
        loggers = self._caller.get_loggers(self.node_list.item(row).text())
        if len(loggers) == 0:
            return
        for logger in sorted(loggers):
            self.logger_list.addItem(logger)
        if self.logger_list.count() != 0:
            self.logger_list.setCurrentRow(0)

    def logger_changed(self, row):
        if row == -1:
            return
        if row < 0 or row >= self.logger_list.count():
            qWarning('Logger row %s out of bounds. Current count: %s' % (row, self.logger_list.count()))
            return
        if self.level_list.count() == 0:
            for level in self._caller.get_levels():
                self.level_list.addItem(level)
        for index in range(self.level_list.count()):
            if self.level_list.item(index).text().lower() == self._caller._current_levels[self.logger_list.currentItem().text()].lower():
                self.level_list.setCurrentRow(index)

    def level_changed(self, row):
        if row == -1:
            return
        if row < 0 or row >= self.level_list.count():
            qWarning('Level row %s out of bounds. Current count: %s' % (row, self.level_list.count()))
            return
        self._caller.send_logger_change_message(self.node_list.currentItem().text(), self.logger_list.currentItem().text(), self.level_list.item(row).text())
