# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

new_program_summary.py: New Program Wizard Summary Page

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
from brickv.plugin_system.plugins.red.new_program_utils import Constants
from brickv.plugin_system.plugins.red.ui_new_program_summary import Ui_NewProgramSummary

class NewProgramSummary(QWizardPage, Ui_NewProgramSummary):
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

        html  = u'<b>General Information</b><br/>'
        html += u'Name: {0}<br/>'.format(Qt.escape(name))
        html += u'Identifier: {0}<br/>'.format(Qt.escape(self.field('identifier').toString()))
        html += u'Language: {0}<br/>'.format(Qt.escape(language_display_name))
        html += u'<br/>'

        html += u'<b>Files</b><br/>'
        for item in self.wizard().page(Constants.PAGE_FILES).get_items():
            html += u'{0}<br/>'.format(Qt.escape(item))
        html += u'<br/>'

        html += u'<b>{0} Configuration</b><br/>'.format(Qt.escape(language_display_name))
        html += u'FIXME<br/>'
        html += u'<br/>'

        html += u'<b>Arguments</b><br/>'
        for argument in self.wizard().page(Constants.PAGE_ARGUMENTS).get_arguments():
            html += u'{0}<br/>'.format(Qt.escape(argument))
        html += u'<br/>'

        html += u'<b>Stdio Redirection</b><br/>'
        html += u'FIXME<br/>'
        html += u'<br/>'

        html += u'<b>Schedule</b><br/>'
        html += u'FIXME<br/>'

        self.text_summary.setHtml(html)
        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        return Constants.PAGE_UPLOAD

    def update_ui_state(self):
        pass
