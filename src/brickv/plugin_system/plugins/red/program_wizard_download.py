# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_wizard_download.py: Download Logs/Files Wizard

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
from brickv.plugin_system.plugins.red.program_page_download import ProgramPageDownload

class ProgramWizardDownload(ProgramWizard):
    def __init__(self, parent, context, program, download_kind, download_directory, downloads):
        ProgramWizard.__init__(self, parent, context)

        self.program = program

        self.setWindowTitle('Download ' + download_kind[0].upper() + download_kind[1:])

        self.setPage(Constants.PAGE_DOWNLOAD, ProgramPageDownload(download_kind, download_directory, downloads))

    # overrides QWizard.nextId
    def nextId(self):
        return -1

    # overrides ProgramWizard.get_field
    def get_field(self, name):
        if name == 'identifier':
            return QVariant(unicode(self.program.identifier))
        elif name == 'name':
            return QVariant(self.program.cast_custom_option_value('name', unicode, '<unknown>'))
        elif name == 'language':
            language_api_name = self.program.cast_custom_option_value('language', unicode, '<unknown>')

            try:
                language = Constants.get_language(language_api_name)
            except:
                language = Constants.LANGUAGE_INVALID

            return QVariant(language)
        else:
            return ProgramWizard.get_field(self, name)
