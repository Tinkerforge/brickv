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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtBoundSignal

from brickv.bindings.ip_connection import IPConnection
from brickv.bindings.bricklet_gps_v2 import GPSV2

class PluginBase(QWidget, object):
    PLUGIN_STATE_STOPPED = 0
    PLUGIN_STATE_RUNNING = 1
    PLUGIN_STATE_PAUSED = 2

    def __init__(self, device_class, ipcon, device_info, override_base_name=None):
        QWidget.__init__(self)

        self.has_comcu = False # Will be overwritten if plugin has comcu
        self.plugin_state = PluginBase.PLUGIN_STATE_STOPPED
        self.label_timeouts = None
        self.device_class = device_class
        self.ipcon = ipcon
        self.device_info = device_info
        self.uid = device_info.uid
        self.hardware_version = device_info.hardware_version
        self.firmware_version = device_info.firmware_version_installed
        self.error_count = 0
        self.configs = []
        self.actions = []

        if device_class is not None:
            self.base_name = self.device_class.DEVICE_DISPLAY_NAME
            self.device = self.device_class(self.uid, self.ipcon)
        else:
            self.base_name = 'Unnamed'
            self.device = None

        if override_base_name != None:
            self.base_name = override_base_name
            # This is a little bit of a hack, but as far as i can see has no problems.
            # If a new Bricklet (with comcu) is enumerated and currently unknown,
            # we still want to be able to flash a firmware on it.
            # To be able to do this we instanciate the GPSV2 class. It has all of the
            # functions necessary to flash (the FIDs are at the same position for all
            # new Bricklets) and no other function is used during flashing.
            if override_base_name == 'Unknown':
                self.device = GPSV2(self.uid, self.ipcon)

        if self.is_hardware_version_relevant():
            self.name = '{0} {1}.{2}'.format(self.base_name,
                                             self.hardware_version[0],
                                             self.hardware_version[1])
        else:
            self.name = self.base_name

        self.device_info.plugin = self
        self.device_info.name = self.name
        self.device_info.url_part = self.get_url_part()

    def start_plugin(self):
        # only consider starting the plugin, if it's stopped
        if self.plugin_state == PluginBase.PLUGIN_STATE_STOPPED:
            if self.ipcon.get_connection_state() == IPConnection.CONNECTION_STATE_PENDING:
                # if connection is pending, the just mark it as paused. it'll
                # started later then
                self.plugin_state = PluginBase.PLUGIN_STATE_PAUSED
            else:
                # otherwise start now
                # Let any exceptions fall through, they will be cached and reported by the exception hook.
                if hasattr(self, 'start_comcu'):
                    self.start_comcu()
                else:
                    self.start()

                self.plugin_state = PluginBase.PLUGIN_STATE_RUNNING

    def stop_plugin(self):
        # only stop the plugin, if it's running
        if self.plugin_state == PluginBase.PLUGIN_STATE_RUNNING:
            # Let any exceptions fall through, they will be cached and reported by the exception hook.
            if hasattr(self, 'stop_comcu'):
                self.stop_comcu()
            else:
                self.stop()

        # set the state to stopped even it the plugin was not actually
        # running. this stops a paused plugin from being restarted after
        # it got stopped
        self.plugin_state = PluginBase.PLUGIN_STATE_STOPPED

    def pause_plugin(self):
        if self.plugin_state == PluginBase.PLUGIN_STATE_RUNNING:
            self.stop() # Let any exceptions fall through, they will be cached and reported by the exception hook.

            self.plugin_state = PluginBase.PLUGIN_STATE_PAUSED

    def resume_plugin(self):
        if self.plugin_state == PluginBase.PLUGIN_STATE_PAUSED:
            self.start() # Let any exceptions fall through, they will be cached and reported by the exception hook.

            self.plugin_state = PluginBase.PLUGIN_STATE_RUNNING

    def destroy_plugin(self):
        # destroy plugin first, then cleanup the UI stuff
        
        # Let any exceptions fall through, they will be cached and reported by the exception hook.
        self.destroy()

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

                    if isinstance(obj, pyqtBoundSignal):
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

    def set_configs(self, configs):
        self.configs = configs

    def get_configs(self):
        return self.configs

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
        if self.device_class != None:
            return self.device_class.DEVICE_URL_PART
        else:
            return 'unknown'

    @staticmethod
    def has_device_identifier(device_identifier):
        return False
