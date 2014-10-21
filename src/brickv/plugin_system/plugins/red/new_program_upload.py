# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

new_program_upload.py: New Program Wizard Upload Page

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

from PyQt4.QtGui import QWizardPage
from brickv.plugin_system.plugins.red.new_program_utils import Constants
from brickv.plugin_system.plugins.red.ui_new_program_upload import Ui_NewProgramUpload

class NewProgramUpload(QWizardPage, Ui_NewProgramUpload):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.upload_done = False

        self.setTitle('Step 8 of {0}: Upload'.format(Constants.STEP_COUNT))

        self.button_start_upload.clicked.connect(self.start_upload)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle(u'Upload the new {0} program [{1}].'
                         .format(Constants.language_names[self.field('language').toInt()[0]],
                                 unicode(self.field('name').toString())))
        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        return -1

    # overrides QWizardPage.isComplete
    def isComplete(self):
        return self.upload_done and QWizardPage.isComplete(self)

    def update_ui_state(self):
        pass

    def start_upload(self):
        self.upload_done = True
        self.completeChanged.emit()
