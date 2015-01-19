# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

program_wizard_new.py: New Program Wizard

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

from brickv.plugin_system.plugins.red.program_wizard import ProgramWizard
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.program_page_general import ProgramPageGeneral
from brickv.plugin_system.plugins.red.program_page_files import ProgramPageFiles
from brickv.plugin_system.plugins.red.program_page_c import ProgramPageC
from brickv.plugin_system.plugins.red.program_page_csharp import ProgramPageCSharp
from brickv.plugin_system.plugins.red.program_page_delphi import ProgramPageDelphi
from brickv.plugin_system.plugins.red.program_page_java import ProgramPageJava
from brickv.plugin_system.plugins.red.program_page_javascript import ProgramPageJavaScript
from brickv.plugin_system.plugins.red.program_page_octave import ProgramPageOctave
from brickv.plugin_system.plugins.red.program_page_perl import ProgramPagePerl
from brickv.plugin_system.plugins.red.program_page_php import ProgramPagePHP
from brickv.plugin_system.plugins.red.program_page_python import ProgramPagePython
from brickv.plugin_system.plugins.red.program_page_ruby import ProgramPageRuby
from brickv.plugin_system.plugins.red.program_page_shell import ProgramPageShell
from brickv.plugin_system.plugins.red.program_page_vbnet import ProgramPageVBNET
from brickv.plugin_system.plugins.red.program_page_arguments import ProgramPageArguments
from brickv.plugin_system.plugins.red.program_page_stdio import ProgramPageStdio
from brickv.plugin_system.plugins.red.program_page_schedule import ProgramPageSchedule
from brickv.plugin_system.plugins.red.program_page_summary import ProgramPageSummary
from brickv.plugin_system.plugins.red.program_page_upload import ProgramPageUpload

class ProgramWizardNew(ProgramWizard):
    def __init__(self, parent, context):
        ProgramWizard.__init__(self, parent, context)

        self.setWindowTitle('New Program')

        self.setPage(Constants.PAGE_GENERAL,    ProgramPageGeneral(title_prefix='Step 1 of 8: '))
        self.setPage(Constants.PAGE_FILES,      ProgramPageFiles(title_prefix='Step 2 of 8: '))
        self.setPage(Constants.PAGE_C,          ProgramPageC(title_prefix='Step 3 of 8: '))
        self.setPage(Constants.PAGE_CSHARP,     ProgramPageCSharp(title_prefix='Step 3 of 8: '))
        self.setPage(Constants.PAGE_DELPHI,     ProgramPageDelphi(title_prefix='Step 3 of 8: '))
        self.setPage(Constants.PAGE_JAVA,       ProgramPageJava(title_prefix='Step 3 of 8: '))
        self.setPage(Constants.PAGE_JAVASCRIPT, ProgramPageJavaScript(title_prefix='Step 3 of 8: '))
        self.setPage(Constants.PAGE_OCTAVE,     ProgramPageOctave(title_prefix='Step 3 of 8: '))
        self.setPage(Constants.PAGE_PERL,       ProgramPagePerl(title_prefix='Step 3 of 8: '))
        self.setPage(Constants.PAGE_PHP,        ProgramPagePHP(title_prefix='Step 3 of 8: '))
        self.setPage(Constants.PAGE_PYTHON,     ProgramPagePython(title_prefix='Step 3 of 8: '))
        self.setPage(Constants.PAGE_RUBY,       ProgramPageRuby(title_prefix='Step 3 of 8: '))
        self.setPage(Constants.PAGE_SHELL,      ProgramPageShell(title_prefix='Step 3 of 8: '))
        self.setPage(Constants.PAGE_VBNET,      ProgramPageVBNET(title_prefix='Step 3 of 8: '))
        self.setPage(Constants.PAGE_ARGUMENTS,  ProgramPageArguments(title_prefix='Step 4 of 8: '))
        self.setPage(Constants.PAGE_STDIO,      ProgramPageStdio(title_prefix='Step 5 of 8: '))
        self.setPage(Constants.PAGE_SCHEDULE,   ProgramPageSchedule(title_prefix='Step 6 of 8: '))
        self.setPage(Constants.PAGE_SUMMARY,    ProgramPageSummary(title_prefix='Step 7 of 8: '))
        self.setPage(Constants.PAGE_UPLOAD,     ProgramPageUpload(title_prefix='Step 8 of 8: '))

    # overrides QWizard.nextId
    def nextId(self):
        currentId = self.currentId()

        if currentId == Constants.PAGE_GENERAL:
            return Constants.PAGE_FILES
        elif currentId == Constants.PAGE_FILES:
            language = self.get_field('language')

            try:
                return Constants.language_pages[language]
            except KeyError:
                return Constants.PAGE_GENERAL
        elif currentId == Constants.PAGE_JAVASCRIPT:
            if self.get_field('javascript.flavor') == Constants.JAVASCRIPT_FLAVOR_BROWSER:
                return Constants.PAGE_SUMMARY
            else:
                return Constants.PAGE_ARGUMENTS
        elif currentId == Constants.PAGE_PYTHON:
            if self.get_field('python.start_mode') == Constants.PYTHON_START_MODE_WEB_INTERFACE:
                return Constants.PAGE_SUMMARY
            else:
                return Constants.PAGE_ARGUMENTS
        elif currentId == Constants.PAGE_PHP:
            if self.get_field('php.start_mode') == Constants.PHP_START_MODE_WEB_INTERFACE:
                return Constants.PAGE_SUMMARY
            else:
                return Constants.PAGE_ARGUMENTS
        elif currentId in Constants.language_pages.values():
            return Constants.PAGE_ARGUMENTS
        elif currentId == Constants.PAGE_ARGUMENTS:
            return Constants.PAGE_STDIO
        elif currentId == Constants.PAGE_STDIO:
            return Constants.PAGE_SCHEDULE
        elif currentId == Constants.PAGE_SCHEDULE:
            return Constants.PAGE_SUMMARY
        elif currentId == Constants.PAGE_SUMMARY:
            return Constants.PAGE_UPLOAD
        elif currentId == Constants.PAGE_UPLOAD:
            return -1
        else:
            return Constants.PAGE_GENERAL

    @property
    def available_files(self):
        available_files = []

        if self.hasVisitedPage(Constants.PAGE_FILES):
            for upload in self.page(Constants.PAGE_FILES).get_uploads():
                available_files.append(upload.target)

        return available_files

    @property
    def available_directories(self):
        if self.hasVisitedPage(Constants.PAGE_FILES):
            return self.page(Constants.PAGE_FILES).get_directories()
        else:
            return []

    @property
    def program(self):
        return self.page(Constants.PAGE_UPLOAD).program

    @property
    def upload_successful(self):
        return self.page(Constants.PAGE_UPLOAD).upload_successful
