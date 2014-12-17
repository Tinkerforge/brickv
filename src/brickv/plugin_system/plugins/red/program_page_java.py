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

from PyQt4.QtCore import QVariant, QTimer
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_java import Ui_ProgramPageJava
from brickv.plugin_system.plugins.red.java_utils import get_jar_file_main_classes, get_class_file_main_classes
from brickv.async_call import async_call
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

        self.language = Constants.LANGUAGE_JAVA

        self.setTitle('{0}{1} Configuration'.format(title_prefix, Constants.language_display_names[self.language]))

        self.registerField('java.version', self.combo_version)
        self.registerField('java.start_mode', self.combo_start_mode)
        self.registerField('java.main_class', self.combo_main_class, 'currentText')
        self.registerField('java.jar_file', self.combo_jar_file, 'currentText')
        self.registerField('java.working_directory', self.combo_working_directory, 'currentText')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(self.completeChanged.emit)
        self.check_show_class_path.stateChanged.connect(self.update_ui_state)
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
        self.check_show_class_path.setCheckState(Qt.Unchecked)
        self.check_show_advanced_options.setCheckState(Qt.Unchecked)
        self.combo_working_directory_selector.reset()
        self.option_list_editor.reset()

        program = self.wizard().program

        # if a program exists then this page is used in an edit wizard
        if program != None:
            bin_directory = posixpath.join(unicode(program.root_directory), 'bin')
        else:
            identifier    = unicode(self.get_field('identifier').toString())
            bin_directory = posixpath.join('/', 'home', 'tf', 'programs', identifier, 'bin')

        jar_filenames = []

        for filename in sorted(self.wizard().available_files):
            if filename.endswith('.jar'):
                jar_filenames.append(posixpath.join(bin_directory, filename))

        if program == None:
            for jar_filename in jar_filenames:
                self.class_path_list_editor.add_item(jar_filename)

        self.class_path_list_editor.set_add_menu_items(['/usr/tinkerforge/bindings/java/Tinkerforge.jar'] + jar_filenames,
                                                       '<new class path entry>')

        self.combo_main_class.clear()
        self.combo_main_class.clearEditText()

        if program != None:
            self.combo_main_class.setEnabled(False)

            def get_main_classes():
                def progress_canceled(sd_ref):
                    sd = sd_ref[0]

                    if sd == None:
                        return

                    self.wizard().script_manager.abort_script(sd)

                sd_ref   = [None]
                progress = ExpandingProgressDialog(self.wizard())
                progress.hide_progress_text()
                progress.setWindowTitle('Edit Program')
                progress.setLabelText('Collecting Java main classes')
                progress.setModal(True)
                progress.setRange(0, 0)
                progress.canceled.connect(lambda: progress_canceled(sd_ref))
                progress.show()

                def cb_java_main_classes(sd_ref, result):
                    sd = sd_ref[0]

                    if sd != None:
                        aborted = sd.abort
                    else:
                        aborted = False

                    sd_ref[0] = None

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
                            self.combo_main_class.addItem(cls, QVariant(main_classes[cls]))

                        self.combo_main_class_checker.set_current_text(program.cast_custom_option_value('java.main_class', unicode, ''))
                        done()

                    def cb_expand_error():
                        self.label_main_class_error.setText('<b>Error:</b> Internal async error occurred')
                        self.label_main_class_error.setVisible(True)
                        done()

                    async_call(expand_async, result.stdout, cb_expand_success, cb_expand_error)

                sd_ref[0] = self.wizard().script_manager.execute_script('java_main_classes',
                                                                        lambda result: cb_java_main_classes(sd_ref, result),
                                                                        [bin_directory], max_length=1024*1024,
                                                                        decode_output_as_utf8=False)

            # need to decouple this with a timer, otherwise it's executed at
            # a time where the progress bar cannot properly enter model state
            # to block the parent widget
            QTimer.singleShot(0, get_main_classes)
        elif self.wizard().hasVisitedPage(Constants.PAGE_FILES):
            uploads = self.wizard().page(Constants.PAGE_FILES).get_uploads()

            if len(uploads) > 0:
                def progress_canceled(abort_ref):
                    abort_ref[0] = True

                abort_ref = [False]
                progress = ExpandingProgressDialog(self)
                progress.hide_progress_text()
                progress.setWindowTitle('New Program')
                progress.setLabelText('Collecting Java main classes')
                progress.setModal(True)
                progress.setRange(0, 0)
                progress.canceled.connect(lambda: progress_canceled(abort_ref))
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
            self.combo_working_directory_selector.set_current_text(unicode(program.working_directory))

            # options
            self.option_list_editor.clear()

            for option in program.cast_custom_option_value_list('java.options', unicode, []):
                self.option_list_editor.add_item(option)

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

    # overrides ProgramPage.update_ui_state
    def update_ui_state(self):
        start_mode            = self.get_field('java.start_mode').toInt()[0]
        start_mode_main_class = start_mode == Constants.JAVA_START_MODE_MAIN_CLASS
        start_mode_jar_file   = start_mode == Constants.JAVA_START_MODE_JAR_FILE
        show_class_path       = self.check_show_class_path.checkState() == Qt.Checked
        show_advanced_options = self.check_show_advanced_options.checkState() == Qt.Checked

        self.label_main_class.setVisible(start_mode_main_class)
        self.combo_main_class.setVisible(start_mode_main_class)
        self.label_main_class_help.setVisible(start_mode_main_class)
        self.combo_jar_file_selector.set_visible(start_mode_jar_file)
        self.class_path_list_editor.set_visible(show_class_path)
        self.combo_working_directory_selector.set_visible(show_advanced_options)
        self.option_list_editor.set_visible(show_advanced_options)
        self.label_spacer.setVisible(not show_class_path and not show_advanced_options)

        self.class_path_list_editor.update_ui_state()
        self.option_list_editor.update_ui_state()

    def get_executable(self):
        return unicode(self.combo_version.itemData(self.get_field('java.version').toInt()[0]).toString())

    def get_html_summary(self):
        return 'FIXME<br/>'

    def get_custom_options(self):
        return {
            'java.start_mode': Constants.java_start_mode_api_names[self.get_field('java.start_mode').toInt()[0]],
            'java.main_class': unicode(self.get_field('java.main_class').toString()),
            'java.jar_file':   unicode(self.get_field('java.jar_file').toString()),
            'java.class_path': self.class_path_list_editor.get_items(),
            'java.options':    self.option_list_editor.get_items()
        }

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

    def apply_program_changes(self):
        self.apply_program_custom_options_and_command_changes()
