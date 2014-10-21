# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

new_program_constants.py: New Program Wizard Constants

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

class Constants:
    PAGE_GENERAL = 0
    PAGE_FILES = 1
    PAGE_JAVA = 2
    PAGE_PYTHON = 3
    PAGE_STDIO = 4
    PAGE_SCHEDULE = 5

    LANGUAGE_INVALID = 0
    LANGUAGE_JAVA = 1
    LANGUAGE_PYTHON = 2

    language_names = {
        LANGUAGE_INVALID: '<invalid>',
        LANGUAGE_JAVA:    'Java',
        LANGUAGE_PYTHON:  'Python'
    }

    JAVA_START_MODE_MAIN_CLASS = 0
    JAVA_START_MODE_JAR_FILE   = 1

    PYTHON_START_MODE_SCRIPT_FILE = 0
    PYTHON_START_MODE_MODULE_NAME = 1
    PYTHON_START_MODE_COMMAND     = 2

    STDIO_REDIRECTION_DEV_NULL = 0
    STDIO_REDIRECTION_PIPE     = 1
    STDIO_REDIRECTION_FILE     = 2
    STDIO_REDIRECTION_LOG      = 3
    STDIO_REDIRECTION_STDOUT   = 4

    SCHEDULE_START_CONDITION_NEVER  = 0
    SCHEDULE_START_CONDITION_NOW    = 1
    SCHEDULE_START_CONDITION_REBOOT = 2
    SCHEDULE_START_CONDITION_TIME   = 3

    SCHEDULE_REPEAT_MODE_NEVER     = 0
    SCHEDULE_REPEAT_MODE_INTERVAL  = 1
    SCHEDULE_REPEAT_MODE_SELECTION = 2

    DEFAULT_JAVA_START_MODE          = JAVA_START_MODE_MAIN_CLASS
    DEFAULT_PYTHON_START_MODE        = PYTHON_START_MODE_SCRIPT_FILE
    DEFAULT_STDIN_REDIRECTION        = STDIO_REDIRECTION_PIPE
    DEFAULT_STDOUT_REDIRECTION       = STDIO_REDIRECTION_LOG
    DEFAULT_STDERR_REDIRECTION       = STDIO_REDIRECTION_STDOUT
    DEFAULT_SCHEDULE_START_CONDITION = SCHEDULE_START_CONDITION_NOW
    DEFAULT_SCHEDULE_REPEAT_MODE     = SCHEDULE_REPEAT_MODE_NEVER
