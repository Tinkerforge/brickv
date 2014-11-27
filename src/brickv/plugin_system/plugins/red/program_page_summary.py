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
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_summary import Ui_ProgramPageSummary

class ProgramPageSummary(ProgramPage, Ui_ProgramPageSummary):
    def __init__(self, title_prefix=''):
        ProgramPage.__init__(self)

        self.setupUi(self)

        self.setTitle(title_prefix + 'Summary')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'The complete configuration of the {language} program [{name}].')

        language              = self.get_field('language').toInt()[0]
        language_display_name = Constants.language_display_names[language]
        language_api_name     = Constants.language_api_names[language]

        # general information
        html  = u'<b>General Information</b><br/>'
        html += u'Name: {0}<br/>'.format(Qt.escape(unicode(self.get_field('name').toString())))
        html += u'Identifier: {0}<br/>'.format(Qt.escape(self.get_field('identifier').toString()))
        html += u'Language: {0}<br/>'.format(Qt.escape(language_display_name))
        html += u'Description: {0}<br/>'.format(Qt.escape(self.get_field('description').toString()))
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
        html += self.wizard().page(Constants.get_language_page(language_api_name)).get_html_summary()
        html += u'<br/>'

        if self.wizard().hasVisitedPage(Constants.PAGE_ARGUMENTS):
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
                html += u'{0}<br/>'.format(Qt.escape(variable))

            html += u'<br/>'

        # stdio redirection
        if self.wizard().hasVisitedPage(Constants.PAGE_STDIO):
            html += u'<b>Stdio Redirection</b><br/>'

            stdin_redirection  = self.get_field('stdin_redirection').toInt()[0]
            stdout_redirection = self.get_field('stdout_redirection').toInt()[0]
            stderr_redirection = self.get_field('stderr_redirection').toInt()[0]

            if stdin_redirection == Constants.STDIN_REDIRECTION_FILE:
                html += u'Standard Input: {0}<br/>'.format(self.get_field('stdin_file').toString())
            else:
                html += u'Standard Input: {0}<br/>'.format(Constants.get_stdin_redirection_display_name(stdin_redirection))

            if stdout_redirection == Constants.STDOUT_REDIRECTION_FILE:
                html += u'Standard Output: {0}<br/>'.format(self.get_field('stdout_file').toString())
            else:
                html += u'Standard Output: {0}<br/>'.format(Constants.get_stdout_redirection_display_name(stdout_redirection))

            if stderr_redirection == Constants.STDERR_REDIRECTION_FILE:
                html += u'Standard Error: {0}<br/>'.format(self.get_field('stderr_file').toString())
            else:
                html += u'Standard Error: {0}<br/>'.format(Constants.get_stderr_redirection_display_name(stderr_redirection))

            html += u'<br/>'

        # schedule
        if self.wizard().hasVisitedPage(Constants.PAGE_SCHEDULE):
            html += u'<b>Schedule</b><br/>'

            start_mode = self.get_field('start_mode').toInt()[0]

            if start_mode == Constants.START_MODE_ONCE:
                html += u'Mode: Once After Upload<br/>'
            else:
                html += u'Mode: {0}<br/>'.format(Constants.get_start_mode_display_name(start_mode))

            if start_mode != Constants.START_MODE_NEVER and start_mode != Constants.START_MODE_ONCE:
                if self.get_field('continue_after_error').toBool():
                    html += u'Continue After Error: Enabled<br/>'
                else:
                    html += u'Continue After Error: Disabled<br/>'

            if start_mode == Constants.START_MODE_INTERVAL:
                html += u'Interval: {0} seconds<br/>'.format(self.get_field('start_interval').toUInt()[0])
            elif start_mode == Constants.START_MODE_CRON:
                html += u'Fields: {0}<br/>'.format(self.get_field('start_fields').toString())

        self.text_summary.setHtml(html)
        self.update_ui_state()

    # overrides ProgramPage.update_ui_state
    def update_ui_state(self):
        pass
