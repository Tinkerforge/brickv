# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_page_java.py: Program Wizard Java Page

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

from PyQt4.QtCore import QVariant
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_java import Ui_ProgramPageJava
from brickv.plugin_system.plugins.red.javatools.jarinfo import JarInfo
from brickv.plugin_system.plugins.red.javatools import unpack_class
import os

def get_java_versions(script_manager, callback):
    def cb_versions(result):
        if result != None:
            try:
                version = result.stderr.split('\n')[1].split(' ')[5].replace(')', '')
                callback([ExecutableVersion('/usr/bin/java', version)])
                return
            except:
                pass

        # Could not get versions, we assume that some version of java 8 is installed
        callback([ExecutableVersion('/usr/bin/java', '1.8')])

    script_manager.execute_script('java_versions', cb_versions)


def get_classes_from_class_or_jar(uploads):
    MAIN_ENDING = '.main(java.lang.String[]):void'

    def parse_jar(f):
        try:
            with JarInfo(filename=f) as ji:
                return ji.get_provides()
        except:
            pass

        return []

    def parse_class(f):
        try:
            with open(f) as cf:
                return unpack_class(cf).get_provides()
        except:
            pass

        return []

    classes = []
    main_classes = []
    for upload in uploads:
        if upload.source.endswith('.jar'):
            classes.extend(parse_jar(upload.source))
        elif upload.source.endswith('.class'):
            classes.extend(parse_class(upload.source))

    for cls in classes:
        if cls.endswith(MAIN_ENDING):
            main_classes.append(cls.replace(MAIN_ENDING, ''))

    return main_classes


class ProgramPageJava(ProgramPage, Ui_ProgramPageJava):
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.language = Constants.LANGUAGE_JAVA

        self.setTitle('{0}{1} Configuration'.format(title_prefix, Constants.language_display_names[self.language]))

        self.registerField('java.version', self.combo_version)
        self.registerField('java.start_mode', self.combo_start_mode)
        self.registerField('java.main_class', self.combo_main_class, 'currentText')
        self.registerField('java.jar_file', self.combo_jar_file, 'currentText')
        self.registerField('java.working_directory', self.combo_working_directory, 'currentText')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(self.completeChanged.emit)
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)

        self.combo_main_class_checker         = MandatoryEditableComboBoxChecker(self,
                                                                                 self.label_main_class,
                                                                                 self.combo_main_class)
        self.combo_jar_file_selector          = MandatoryTypedFileSelector(self,
                                                                           self.label_jar_file,
                                                                           self.combo_jar_file,
                                                                           self.label_jar_file_type,
                                                                           self.combo_jar_file_type,
                                                                           self.label_jar_file_help)
        self.combo_working_directory_selector = MandatoryDirectorySelector(self,
                                                                           self.label_working_directory,
                                                                           self.combo_working_directory)
        # FIXME: allow adding class path entries using a combo box prefilled with avialable .jar files
        self.class_path_list_editor           = ListWidgetEditor(self.label_class_path,
                                                                 self.list_class_path,
                                                                 self.label_class_path_help,
                                                                 self.button_add_class_path_entry,
                                                                 self.button_remove_class_path_entry,
                                                                 self.button_up_class_path_entry,
                                                                 self.button_down_class_path_entry,
                                                                 '<new class path entry {0}>')
        self.option_list_editor               = ListWidgetEditor(self.label_options,
                                                                 self.list_options,
                                                                 self.label_options_help,
                                                                 self.button_add_option,
                                                                 self.button_remove_option,
                                                                 self.button_up_option,
                                                                 self.button_down_option,
                                                                 '<new JVM option {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Specify how the {language} program [{name}] should be executed.')

        self.update_combo_version('java', self.combo_version)

        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_JAVA_START_MODE)
        self.combo_jar_file_selector.reset()
        self.class_path_list_editor.reset()
        self.check_show_advanced_options.setCheckState(Qt.Unchecked)
        self.combo_working_directory_selector.reset()
        self.option_list_editor.reset()

        identifier = str(self.get_field('identifier').toString())
        root_dir = os.path.join('/', 'home', 'tf', 'programs', identifier, 'bin')
        for f in sorted(self.wizard().available_files):
            if f.endswith('.jar'):
                self.class_path_list_editor.add_item(os.path.join(root_dir, f))

        self.combo_main_class.clear()
        self.combo_main_class.clearEditText()

        # FIXME: make this work in edit mode
        # FIXME: make get_classes_from_class_or_jar async
        if self.wizard().hasVisitedPage(Constants.PAGE_FILES):
            for cls in sorted(get_classes_from_class_or_jar(self.wizard().page(Constants.PAGE_FILES).get_uploads())):
                self.combo_main_class.addItem(cls)

        if self.combo_main_class.count() > 1:
            self.combo_main_class.clearEditText()

        # if a program exists then this page is used in an edit wizard
        if self.wizard().program != None:
            program = self.wizard().program

            self.combo_working_directory_selector.set_current_text(unicode(program.working_directory))

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        executable = self.get_executable()
        start_mode = self.get_field('java.start_mode').toInt()[0]

        if len(executable) == 0:
            return False

        if start_mode == Constants.JAVA_START_MODE_MAIN_CLASS and \
           not self.combo_main_class_checker.complete:
            return False

        if start_mode == Constants.JAVA_START_MODE_JAR_FILE and \
           not self.combo_jar_file_selector.complete:
            return False

        return self.combo_working_directory_selector.complete and ProgramPage.isComplete(self)

    def update_ui_state(self):
        start_mode            = self.get_field('java.start_mode').toInt()[0]
        start_mode_main_class = start_mode == Constants.JAVA_START_MODE_MAIN_CLASS
        start_mode_jar_file   = start_mode == Constants.JAVA_START_MODE_JAR_FILE
        show_advanced_options = self.check_show_advanced_options.checkState() == Qt.Checked

        self.label_main_class.setVisible(start_mode_main_class)
        self.combo_main_class.setVisible(start_mode_main_class)
        self.label_main_class_help.setVisible(start_mode_main_class)
        self.combo_jar_file_selector.set_visible(start_mode_jar_file)
        self.combo_working_directory_selector.set_visible(show_advanced_options)
        self.option_list_editor.set_visible(show_advanced_options)

        self.class_path_list_editor.update_ui_state()
        self.option_list_editor.update_ui_state()

    def get_executable(self):
        return unicode(self.combo_version.itemData(self.get_field('java.version').toInt()[0]).toString())

    def get_html_summary(self):
        return 'FIXME<br/>'

    def get_custom_options(self):
        return {}

    def get_command(self):
        executable         = self.get_executable()
        arguments          = self.option_list_editor.get_items()
        environment        = []
        start_mode         = self.get_field('java.start_mode').toInt()[0]
        class_path_entries = self.class_path_list_editor.get_items()

        if len(class_path_entries) > 0:
            arguments += ['-cp', ':'.join(class_path_entries)]

        if start_mode == Constants.JAVA_START_MODE_MAIN_CLASS:
            arguments.append(unicode(self.get_field('java.main_class').toString()))
        elif start_mode == Constants.JAVA_START_MODE_JAR_FILE:
            arguments.append('-jar')
            arguments.append(unicode(self.get_field('java.jar_file').toString()))

        working_directory = unicode(self.get_field('java.working_directory').toString())

        return executable, arguments, environment, working_directory
