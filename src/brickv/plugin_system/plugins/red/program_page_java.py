# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QDialog, QMessageBox
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_java import Ui_ProgramPageJava
from brickv.plugin_system.plugins.red.java_utils import get_jar_file_main_classes, get_class_file_main_classes
from brickv.async_call import async_call
from brickv.utils import get_main_window
import posixpath
import json
import zlib

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


def get_main_classes_from_class_or_jar(uploads, abort_ref):
    main_classes = []

    for upload in uploads:
        if abort_ref[0]:
            break

        if upload.source.endswith('.jar'):
            try:
                main_classes.extend(get_jar_file_main_classes(upload.source, abort_ref))
            except:
                pass
        elif upload.source.endswith('.class'):
            try:
                main_classes.extend(get_class_file_main_classes(upload.source))
            except:
                pass

    return main_classes


class ProgramPageJava(ProgramPage, Ui_ProgramPageJava):
    def __init__(self, title_prefix=''):
        ProgramPage.__init__(self)

        self.setupUi(self)

        self.language              = Constants.LANGUAGE_JAVA
        self.bin_directory         = '/tmp'
        self.class_path_candidates = []

        self.setTitle('{0}{1} Configuration'.format(title_prefix, Constants.language_display_names[self.language]))

        self.registerField('java.version', self.combo_version)
        self.registerField('java.start_mode', self.combo_start_mode)
        self.registerField('java.main_class', self.combo_main_class, 'currentText')
        self.registerField('java.jar_file', self.combo_jar_file, 'currentText')
        self.registerField('java.working_directory', self.combo_working_directory, 'currentText')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(self.completeChanged.emit)
        self.check_show_class_path.stateChanged.connect(self.update_ui_state)
        self.button_add_class_path_entry.clicked.connect(self.add_class_path_entry)
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)
        self.label_main_class_error.setVisible(False)
        self.label_spacer.setText('')

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
        self.class_path_list_editor           = ListWidgetEditor(self.label_class_path,
                                                                 self.list_class_path,
                                                                 self.label_class_path_help,
                                                                 None,
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
        self.check_show_class_path.setChecked(False)
        self.check_show_advanced_options.setChecked(False)
        self.combo_working_directory_selector.reset()
        self.option_list_editor.reset()

        # if a program exists then this page is used in an edit wizard
        program = self.wizard().program

        if program != None:
            self.bin_directory = posixpath.join(program.root_directory, 'bin')
        else:
            identifier         = self.get_field('identifier')
            self.bin_directory = posixpath.join('/', 'home', 'tf', 'programs', identifier, 'bin')

        # collect class path entries
        self.class_path_candidates = ['.']

        for filename in sorted(self.wizard().available_files):
            directroy = posixpath.split(filename)[0]

            if len(directroy) > 0 and directroy not in self.class_path_candidates:
                self.class_path_candidates.append(directroy)

            if filename.endswith('.class') or filename.endswith('.properties'):
                if program == None:
                    self.class_path_list_editor.add_item(directroy)
            elif filename.endswith('.jar'):
                self.class_path_candidates.append(filename)

                if program == None:
                    self.class_path_list_editor.add_item(filename)

        self.class_path_list_editor.add_item('/usr/tinkerforge/bindings/java/Tinkerforge.jar')
        self.class_path_candidates.append('/usr/tinkerforge/bindings/java/Tinkerforge.jar')

        self.combo_main_class.clear()
        self.combo_main_class.clearEditText()

        # collect main classes
        if program != None:
            self.combo_main_class.setEnabled(False)

            def get_main_classes():
                script_instance_ref = [None]

                def progress_canceled():
                    script_instance = script_instance_ref[0]

                    if script_instance == None:
                        return

                    self.wizard().script_manager.abort_script(script_instance)

                progress = ExpandingProgressDialog(self.wizard())
                progress.set_progress_text_visible(False)
                progress.setWindowTitle('Edit Program')
                progress.setLabelText('Collecting Java main classes')
                progress.setModal(True)
                progress.setRange(0, 0)
                progress.canceled.connect(progress_canceled)
                progress.show()

                def cb_java_main_classes(result):
                    script_instance = script_instance_ref[0]

                    if script_instance != None:
                        aborted = script_instance.abort
                    else:
                        aborted = False

                    script_instance_ref[0] = None

                    def done():
                        progress.cancel()
                        self.combo_main_class.setEnabled(True)
                        self.completeChanged.emit()

                    if aborted:
                        done()
                        return

                    if result == None or result.exit_code != 0:
                        if result == None or len(result.stderr) == 0:
                            self.label_main_class_error.setText('<b>Error:</b> Internal script error occurred')
                        else:
                            self.label_main_class_error.setText('<b>Error:</b> ' + Qt.escape(result.stderr.decode('utf-8').strip()))

                        self.label_main_class_error.setVisible(True)
                        done()
                        return

                    def expand_async(data):
                        try:
                            main_classes = json.loads(zlib.decompress(buffer(data)).decode('utf-8'))

                            if not isinstance(main_classes, dict):
                                main_classes = {}
                        except:
                            main_classes = {}

                        return main_classes

                    def cb_expand_success(main_classes):
                        self.combo_main_class.clear()

                        for cls in sorted(main_classes.keys()):
                            self.combo_main_class.addItem(cls, main_classes[cls])

                        self.combo_main_class_checker.set_current_text(program.cast_custom_option_value('java.main_class', unicode, ''))
                        done()

                    def cb_expand_error():
                        self.label_main_class_error.setText('<b>Error:</b> Internal async error occurred')
                        self.label_main_class_error.setVisible(True)
                        done()

                    async_call(expand_async, result.stdout, cb_expand_success, cb_expand_error)

                script_instance_ref[0] = self.wizard().script_manager.execute_script('java_main_classes', cb_java_main_classes,
                                                                                     [self.bin_directory], max_length=1024*1024,
                                                                                     decode_output_as_utf8=False)

            # need to decouple this with a timer, otherwise it's executed at
            # a time where the progress bar cannot properly enter model state
            # to block the parent widget
            QTimer.singleShot(0, get_main_classes)
        elif self.wizard().hasVisitedPage(Constants.PAGE_FILES):
            uploads = self.wizard().page(Constants.PAGE_FILES).get_uploads()

            if len(uploads) > 0:
                abort_ref = [False]

                def progress_canceled():
                    abort_ref[0] = True

                progress = ExpandingProgressDialog(self)
                progress.set_progress_text_visible(False)
                progress.setWindowTitle('New Program')
                progress.setLabelText('Collecting Java main classes')
                progress.setModal(True)
                progress.setRange(0, 0)
                progress.canceled.connect(progress_canceled)
                progress.show()

                def cb_main_classes(main_classes):
                    for main_class in main_classes:
                        self.combo_main_class.addItem(main_class)

                    if self.combo_main_class.count() > 1:
                        self.combo_main_class.clearEditText()

                    progress.cancel()

                    self.combo_main_class.setEnabled(True)
                    self.completeChanged.emit()

                def cb_main_classes_error():
                    self.label_main_class_error.setText('<b>Error:</b> Internal async error occurred')
                    self.label_main_class_error.setVisible(True)

                    progress.cancel()

                    self.combo_main_class.clearEditText()
                    self.combo_main_class.setEnabled(True)
                    self.completeChanged.emit()

                def get_main_classes_async(uploads):
                    return sorted(get_main_classes_from_class_or_jar(uploads, abort_ref))

                self.combo_main_class.setEnabled(False)

                async_call(get_main_classes_async, uploads, cb_main_classes, cb_main_classes_error)

        # if a program exists then this page is used in an edit wizard
        if program != None:
            # start mode
            start_mode_api_name = program.cast_custom_option_value('java.start_mode', unicode, '<unknown>')
            start_mode          = Constants.get_java_start_mode(start_mode_api_name)

            self.combo_start_mode.setCurrentIndex(start_mode)

            # main class
            self.combo_main_class_checker.set_current_text(program.cast_custom_option_value('java.main_class', unicode, ''))

            # jar file
            self.combo_jar_file_selector.set_current_text(program.cast_custom_option_value('java.jar_file', unicode, ''))

            # class path
            self.class_path_list_editor.clear()

            for class_path_entry in program.cast_custom_option_value_list('java.class_path', unicode, []):
                self.class_path_list_editor.add_item(class_path_entry)

            # working directory
            self.combo_working_directory_selector.set_current_text(program.working_directory)

            # options
            self.option_list_editor.clear()

            for option in program.cast_custom_option_value_list('java.options', unicode, []):
                self.option_list_editor.add_item(option)

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        executable = self.get_executable()
        start_mode = self.get_field('java.start_mode')

        if len(executable) == 0:
            return False

        if start_mode == Constants.JAVA_START_MODE_MAIN_CLASS and \
           not self.combo_main_class_checker.complete:
            return False

        if start_mode == Constants.JAVA_START_MODE_JAR_FILE and \
           not self.combo_jar_file_selector.complete:
            return False

        return self.combo_working_directory_selector.complete and ProgramPage.isComplete(self)

    # overrides ProgramPage.update_ui_state
    def update_ui_state(self):
        start_mode            = self.get_field('java.start_mode')
        start_mode_main_class = start_mode == Constants.JAVA_START_MODE_MAIN_CLASS
        start_mode_jar_file   = start_mode == Constants.JAVA_START_MODE_JAR_FILE
        show_class_path       = self.check_show_class_path.isChecked()
        show_advanced_options = self.check_show_advanced_options.isChecked()

        self.label_main_class.setVisible(start_mode_main_class)
        self.combo_main_class.setVisible(start_mode_main_class)
        self.label_main_class_help.setVisible(start_mode_main_class)
        self.combo_jar_file_selector.set_visible(start_mode_jar_file)
        self.class_path_list_editor.set_visible(show_class_path)
        self.button_add_class_path_entry.setVisible(show_class_path)
        self.combo_working_directory_selector.set_visible(show_advanced_options)
        self.option_list_editor.set_visible(show_advanced_options)
        self.label_spacer.setVisible(not show_class_path and not show_advanced_options)

        self.class_path_list_editor.update_ui_state()
        self.option_list_editor.update_ui_state()

    def add_class_path_entry(self):
        dialog = ExpandingInputDialog(self)
        dialog.setModal(True)
        dialog.setWindowTitle('Add Class Path Entry')
        dialog.setLabelText('Enter/Choose new class path entry:')
        dialog.setOkButtonText('Add')
        dialog.setComboBoxItems(self.class_path_candidates)
        dialog.setComboBoxEditable(True)
        dialog.setTextValue('')

        if dialog.exec_() != QDialog.Accepted:
            return

        entry = dialog.textValue()

        if len(entry) == 0:
            QMessageBox.critical(get_main_window(), 'Add Class Path Entry Error',
                                 'A valid class path entry cannot be empty.',
                                 QMessageBox.Ok)
            return

        self.class_path_list_editor.add_item(entry, select_item=True)

    def get_executable(self):
        return self.combo_version.itemData(self.get_field('java.version'))

    def get_html_summary(self):
        version           = self.get_field('java.version')
        start_mode        = self.get_field('java.start_mode')
        main_class        = self.get_field('java.main_class')
        jar_file          = self.get_field('java.jar_file')
        working_directory = self.get_field('java.working_directory')
        class_path        = ':'.join(self.class_path_list_editor.get_items())
        options           = ' '.join(self.option_list_editor.get_items())

        html  = u'Java Version: {0}<br/>'.format(Qt.escape(self.combo_version.itemText(version)))
        html += u'Start Mode: {0}<br/>'.format(Qt.escape(Constants.java_start_mode_display_names[start_mode]))

        if start_mode == Constants.JAVA_START_MODE_MAIN_CLASS:
            html += u'Main Class: {0}<br/>'.format(Qt.escape(main_class))
        elif start_mode == Constants.JAVA_START_MODE_JAR_FILE:
            html += u'JAR File: {0}<br/>'.format(Qt.escape(jar_file))

        html += u'Class Path: {0}<br/>'.format(Qt.escape(class_path))
        html += u'Working Directory: {0}<br/>'.format(Qt.escape(working_directory))
        html += u'JVM Options: {0}<br/>'.format(Qt.escape(options))

        return html

    def get_custom_options(self):
        return {
            'java.start_mode': Constants.java_start_mode_api_names[self.get_field('java.start_mode')],
            'java.main_class': self.get_field('java.main_class'),
            'java.jar_file':   self.get_field('java.jar_file'),
            'java.class_path': self.class_path_list_editor.get_items(),
            'java.options':    self.option_list_editor.get_items()
        }

    def get_command(self):
        executable         = self.get_executable()
        arguments          = self.option_list_editor.get_items()
        environment        = []
        start_mode         = self.get_field('java.start_mode')
        class_path_entries = self.class_path_list_editor.get_items()

        if len(class_path_entries) > 0:
            absolute_entries = []

            for filename in class_path_entries:
                if not filename.startswith('/'):
                    absolute_entries.append(posixpath.join(self.bin_directory, filename))
                else:
                    absolute_entries.append(filename)

            arguments += ['-cp', ':'.join(absolute_entries)]

        if start_mode == Constants.JAVA_START_MODE_MAIN_CLASS:
            arguments.append(self.get_field('java.main_class'))
        elif start_mode == Constants.JAVA_START_MODE_JAR_FILE:
            arguments.append('-jar')
            arguments.append(self.get_field('java.jar_file'))

        working_directory = self.get_field('java.working_directory')

        return executable, arguments, environment, working_directory

    def apply_program_changes(self):
        self.apply_program_custom_options_and_command_changes()
