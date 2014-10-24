# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_page_summary.py: Program Wizard Summary Page

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWizardPage
from brickv.plugin_system.plugins.red.program_wizard_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_summary import Ui_ProgramPageSummary

class ProgramPageSummary(QWizardPage, Ui_ProgramPageSummary):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('Step 7 of {0}: Summary'.format(Constants.STEP_COUNT))

    # overrides QWizardPage.initializePage
    def initializePage(self):
        name = unicode(self.field('name').toString())
        language_display_name = Constants.language_display_names[self.field('language').toInt()[0]]

        self.setSubTitle(u'The complete configuration of the new {0} program [{1}].'
                         .format(language_display_name, name))

        # general information
        html  = u'<b>General Information</b><br/>'
        html += u'Name: {0}<br/>'.format(Qt.escape(name))
        html += u'Identifier: {0}<br/>'.format(Qt.escape(self.field('identifier').toString()))
        html += u'Language: {0}<br/>'.format(Qt.escape(language_display_name))
        html += u'<br/>'

        # files
        html += u'<b>Files</b>'

        items = self.wizard().page(Constants.PAGE_FILES).get_items()

        if len(items) == 0:
            html += u' (none)'

        html += u'<br/>'

        for item in items:
            html += u'{0}<br/>'.format(Qt.escape(item))

        html += u'<br/>'

        # language specific configuration
        html += u'<b>{0} Configuration</b><br/>'.format(Qt.escape(language_display_name))
        html += u'FIXME<br/>'
        html += u'<br/>'

        # arguments
        html += u'<b>Arguments</b>'

        arguments = self.wizard().page(Constants.PAGE_ARGUMENTS).get_arguments()

        if len(arguments) == 0:
            html += u' (none)'

        html += u'<br/>'

        for argument in arguments:
            html += u'{0}<br/>'.format(Qt.escape(argument))

        html += u'<br/>'

        # environment
        html += u'<b>Environment</b>'

        environment = self.wizard().page(Constants.PAGE_ARGUMENTS).get_environment()

        if len(environment) == 0:
            html += u' (empty)'

        html += u'<br/>'

        for variable in environment:
            html += u'{0} = {1}<br/>'.format(Qt.escape(variable[0]), Qt.escape(variable[1]))

        html += u'<br/>'

        # stdio redirection
        html += u'<b>Stdio Redirection</b><br/>'
        html += u'FIXME<br/>'
        html += u'<br/>'

        # schedule
        html += u'<b>Schedule</b><br/>'
        html += u'FIXME<br/>'

        self.text_summary.setHtml(html)
        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        return Constants.PAGE_UPLOAD

    def update_ui_state(self):
        pass
