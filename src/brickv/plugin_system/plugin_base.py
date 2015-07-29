# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2009-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

plugin_base.py: Base class for all Brick Viewer Plugins

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

import sys
import traceback
from PyQt4.QtGui import QWidget
from brickv.bindings.ip_connection import IPConnection

class PluginBase(QWidget, object):
    PLUGIN_STATE_STOPPED = 0
    PLUGIN_STATE_RUNNING = 1
    PLUGIN_STATE_PAUSED = 2

    def __init__(self, device_class, ipcon, uid, hardware_version,
                 firmware_version, override_base_name=None):
        QWidget.__init__(self)

        self.plugin_state = PluginBase.PLUGIN_STATE_STOPPED
        self.label_timeouts = None
        self.ipcon = ipcon
        self.uid = uid
        self.hardware_version = hardware_version
        self.firmware_version = firmware_version
        self.error_count = 0
        self.actions = None

        if device_class is not None:
            self.base_name = device_class.DEVICE_DISPLAY_NAME
            self.device = device_class(uid, ipcon)
        else:
            self.base_name = 'Unnamed'
            self.device = None

        if override_base_name != None:
            self.base_name = override_base_name

        if self.is_hardware_version_relevant():
            self.name = '{0} {1}.{2}'.format(self.base_name,
                                             self.hardware_version[0],
                                             self.hardware_version[1])
        else:
            self.name = self.base_name

    def start_plugin(self):
        # only consider starting the plugin, if it's stopped
        if self.plugin_state == PluginBase.PLUGIN_STATE_STOPPED:
            if self.ipcon.get_connection_state() == IPConnection.CONNECTION_STATE_PENDING:
                # if connection is pending, the just mark it as paused. it'll
                # started later then
                self.plugin_state = PluginBase.PLUGIN_STATE_PAUSED
            else:
                # otherwise start now
                try:
                    self.start()
                except:
                    if not hasattr(sys, 'frozen'):
                        traceback.print_exc()

                self.plugin_state = PluginBase.PLUGIN_STATE_RUNNING

    def stop_plugin(self):
        # only stop the plugin, if it's running
        if self.plugin_state == PluginBase.PLUGIN_STATE_RUNNING:
            try:
                self.stop()
            except:
                if not hasattr(sys, 'frozen'):
                    traceback.print_exc()

        # set the state to stopped even it the plugin was not actually
        # running. this stops a paused plugin from being restarted after
        # it got stopped
        self.plugin_state = PluginBase.PLUGIN_STATE_STOPPED

    def pause_plugin(self):
        if self.plugin_state == PluginBase.PLUGIN_STATE_RUNNING:
            try:
                self.stop()
            except:
                if not hasattr(sys, 'frozen'):
                    traceback.print_exc()

            self.plugin_state = PluginBase.PLUGIN_STATE_PAUSED

    def resume_plugin(self):
        if self.plugin_state == PluginBase.PLUGIN_STATE_PAUSED:
            try:
                self.start()
            except:
                if not hasattr(sys, 'frozen'):
                    traceback.print_exc()

            self.plugin_state = PluginBase.PLUGIN_STATE_RUNNING

    def destroy_plugin(self):
        # destroy plugin first, then cleanup the UI stuff
        try:
            self.destroy()
        except:
            if not hasattr(sys, 'frozen'):
                traceback.print_exc()

        # before destroying the widgets ensure that all callbacks are
        # unregistered. callbacks a typically bound to Qt slots. the plugin
        # tab might already be gone but the actual device object might still
        # be alive as gets callbacks delivered to it. this callback will then
        # try to call non-existing Qt slots and trigger a segfault
        if self.device is not None:
            self.device.registered_callbacks = {}

        # disconnect all signals to ensure that callbacks that already emitted
        # a signal don't get delivered anymore after this point
        try:
            self.disconnect()
        except TypeError:
            # fallback for PyQt versions that miss parameterless disconnect()
            for member in dir(self):
                # FIXME: filtering by name prefix is not so robust
                if member.startswith('qtcb_'):
                    obj = getattr(self, member)

                    # FIXME: checking type by display name of type is not so robust
                    if str(type(obj)) == "<type 'PyQt4.QtCore.pyqtBoundSignal'>":
                        try:
                            obj.disconnect()
                        except:
                            pass

        # ensure that the widgets gets correctly destroyed. otherwise QWidgets
        # tend to leak as Python is not able to collect their PyQt object
        """for member in dir(self):
            print "Current member = " + member
            obj = getattr(self, member)

            if isinstance(obj, QWidget):
                obj.hide()
                obj.setParent(None)

                setattr(self, member, None)"""

    def increase_error_count(self):
        self.error_count += 1
        if self.label_timeouts:
            try:
                # as this method might be called after the plugin tab
                # is already done this can raise a
                #
                # RuntimeError: underlying C/C++ object has been deleted
                self.label_timeouts.setText('{0}'.format(self.error_count))
            except:
                pass

    def set_actions(self, actions):
        self.actions = actions

    def get_actions(self):
        return self.actions

    # To be overridden by inheriting class
    def stop(self):
        pass

    def start(self):
        pass

    def destroy(self):
        pass

    def has_custom_version(self, label_version_name, label_version):
        return False

    def is_hardware_version_relevant(self):
        return False

    def get_url_part(self):
        return 'UNKNOWN'

    @staticmethod
    def has_device_identifier(device_identifier):
        return False
