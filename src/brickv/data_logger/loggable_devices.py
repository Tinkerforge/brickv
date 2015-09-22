# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Roland Dudko <roland.dudko@gmail.com>
Copyright (C) 2012, 2014 Marvin Lutz <marvin.lutz.mail@gmail.com>

loggable_devices.py: Util classes for the data logger

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

# https://docs.google.com/spreadsheets/d/14p6N8rAg8M9Ozr1fmOZePPflvNJmgt0pSAebliDrasI/edit?usp=sharing
# Documented for Testing and Blueprints
# Bricklets ############################################################################################################
from brickv.bindings.bricklet_accelerometer import BrickletAccelerometer # config: data_rate, full_scale,filter_bandwidth
from brickv.bindings.bricklet_ambient_light import BrickletAmbientLight
from brickv.bindings.bricklet_ambient_light_v2 import BrickletAmbientLightV2 # config: illuminance_range, integration_time
from brickv.bindings.bricklet_analog_in import BrickletAnalogIn # config: range, averaging
from brickv.bindings.bricklet_analog_in_v2 import BrickletAnalogInV2 # config: moving_average
from brickv.bindings.bricklet_analog_out_v2 import BrickletAnalogOutV2
from brickv.bindings.bricklet_barometer import BrickletBarometer # config: reference_air_pressure, averaging
from brickv.bindings.bricklet_color import BrickletColor # config: gain, integration_time
from brickv.bindings.bricklet_current12 import BrickletCurrent12
from brickv.bindings.bricklet_current25 import BrickletCurrent25
from brickv.bindings.bricklet_distance_ir import BrickletDistanceIR
from brickv.bindings.bricklet_distance_us import BrickletDistanceUS # config: moving_average
from brickv.bindings.bricklet_dual_button import BrickletDualButton
from brickv.bindings.bricklet_dust_detector import BrickletDustDetector # config: moving_average
from brickv.bindings.bricklet_gps import BrickletGPS
from brickv.bindings.bricklet_hall_effect import BrickletHallEffect # config: edge_type, debounce
from brickv.bindings.bricklet_humidity import BrickletHumidity
from brickv.bindings.bricklet_industrial_digital_in_4 import BrickletIndustrialDigitalIn4 # config: selection_mask, edge_type, debounce
from brickv.bindings.bricklet_industrial_dual_0_20ma import BrickletIndustrialDual020mA # config: sample_rate
from brickv.bindings.bricklet_industrial_dual_analog_in import BrickletIndustrialDualAnalogIn # config: sample_rate
from brickv.bindings.bricklet_io16 import BrickletIO16 # config: port_configuration
from brickv.bindings.bricklet_io4 import BrickletIO4 # config: port
from brickv.bindings.bricklet_joystick import BrickletJoystick
# from brickv.bindings.bricklet_laser_range_finder import BrickletLaserRangeFinder #NYI # config: mode, FIXME: special laser handling
from brickv.bindings.bricklet_led_strip import BrickletLEDStrip
from brickv.bindings.bricklet_line import BrickletLine
from brickv.bindings.bricklet_linear_poti import BrickletLinearPoti
from brickv.bindings.bricklet_load_cell import BrickletLoadCell # config: moving_average
from brickv.bindings.bricklet_moisture import BrickletMoisture # config: moving_average
from brickv.bindings.bricklet_motion_detector import BrickletMotionDetector
from brickv.bindings.bricklet_multi_touch import BrickletMultiTouch # config: electrode_config, electrode_sensitivity
from brickv.bindings.bricklet_ptc import BrickletPTC # config: wire_mode
from brickv.bindings.bricklet_rotary_encoder import BrickletRotaryEncoder
from brickv.bindings.bricklet_rotary_poti import BrickletRotaryPoti
# from brickv.bindings.bricklet_rs232 import BrickletRS232 #NYI FIXME: has to use read_callback to get all data
from brickv.bindings.bricklet_sound_intensity import BrickletSoundIntensity
from brickv.bindings.bricklet_temperature import BrickletTemperature # config: i2c_mode
from brickv.bindings.bricklet_temperature_ir import BrickletTemperatureIR # config: emissivity
from brickv.bindings.bricklet_tilt import BrickletTilt
from brickv.bindings.bricklet_voltage import BrickletVoltage
from brickv.bindings.bricklet_voltage_current import BrickletVoltageCurrent # config: averaging, voltage_conversion_time, current_conversion_time
# Bricks ###############################################################################################################
from brickv.bindings.brick_dc import BrickDC  # NYI
# from brickv.bindings.brick_stepper import BricklStepper #NYI

from brickv.data_logger.event_logger import EventLogger
import brickv.data_logger.utils as utils


# special_* functions are for special Bricks/Bricklets. Some device functions can
# return different values, depending on different situations, e.g. the GPS Bricklet.
# If the GPS Bricklet does not have a fix, then the function will return an Error
# instead of the specified return values.

# BrickletGPS
def special_get_gps_coordinates(device):
    if device.get_status()[0] == BrickletGPS.FIX_NO_FIX:
        raise Exception('No fix')
    else:
        return device.get_coordinates()

def special_get_gps_altitude(device):
    if device.get_status()[0] != BrickletGPS.FIX_3D_FIX:
        raise Exception('No 3D fix')
    else:
        return device.get_altitude()

def special_get_gps_motion(device):
    if device.get_status()[0] == BrickletGPS.FIX_NO_FIX:
        raise Exception('No fix')
    else:
        return device.get_motion()

# BrickletPTC
def special_get_ptc_resistance(device):
    if not device.is_sensor_connected():
        raise Exception('No sensor')
    else:
        return device.get_resistance()

def special_get_ptc_temperature(device):
    if not device.is_sensor_connected():
        raise Exception('No sensor')
    else:
        return device.get_temperature()


'''
/*---------------------------------------------------------------------------
                                Identifier
 ---------------------------------------------------------------------------*/
 '''


class Identifier(object):
    """
        This class is used to identify supported Bricks and Bricklets. The
        DEVICE_DEFINITIONS contains a Blueprint for each supported device.
        This Blueprint is used in the config file and the GUI.
    """
    # Devices
    DEVICES = "DEVICES"

    # config list access strings
    DD_NAME = "name"
    DD_CLASS = "class"
    DD_UID = "uid"
    DD_VALUES = "values"
    DD_VALUES_INTERVAL = "interval"
    # Device Definitions Keys
    DD_GETTER = "getter"
    DD_SUBVALUES = "subvalues"

    DD_UID_DEFAULT = "Enter UID"

    # Device Definitons(DD)
    DEVICE_DEFINITIONS = {
        ########################
        # Bricklets Start Here #
        ########################
        BrickletAccelerometer.DEVICE_DISPLAY_NAME: {
            'class': BrickletAccelerometer,
            'values': {
                'Acceleration': {
                    'getter': lambda device: device.get_acceleration(),
                    'subvalues': ['X', 'Y', 'Z']
                },
                'Temperature': {
                    'getter': lambda device: device.get_temperature(),
                    'subvalues': None
                }
            }
        },
        BrickletAmbientLight.DEVICE_DISPLAY_NAME: {
            'class': BrickletAmbientLight,
            'values': {
                'Analog Value': {
                    'getter': lambda device: device.get_analog_value(),
                    'subvalues': None
                },
                'Illuminance': {
                    'getter': lambda device: device.get_illuminance(),
                    'subvalues': None
                }
            }
        },
        BrickletAmbientLightV2.DEVICE_DISPLAY_NAME: {
            'class': BrickletAmbientLightV2,
            'values': {
                'Illuminance': {
                    'getter': lambda device: device.get_illuminance(),
                    'subvalues': None
                }
            }
        },
        BrickletAnalogIn.DEVICE_DISPLAY_NAME: {
            'class': BrickletAnalogIn,
            'values': {
                'Analog Value': {
                    'getter': lambda device: device.get_analog_value(),
                    'subvalues': None
                },
                'Voltage': {
                    'getter': lambda device: device.get_voltage(),
                    'subvalues': None
                }
            }
        },
        BrickletAnalogInV2.DEVICE_DISPLAY_NAME: {
            'class': BrickletAnalogInV2,
            'values': {
                'Analog Value': {
                    'getter': lambda device: device.get_analog_value(),
                    'subvalues': None
                },
                'Voltage': {
                    'getter': lambda device: device.get_voltage(),
                    'subvalues': None
                }
            }
        },
        BrickletAnalogOutV2.DEVICE_DISPLAY_NAME: {
            'class': BrickletAnalogOutV2,
            'values': {
                'Input Voltage': {
                    'getter': lambda device: device.get_input_voltage(),
                    'subvalues': None
                }
            }
        },
        BrickletBarometer.DEVICE_DISPLAY_NAME: {
            'class': BrickletBarometer,
            'values': {
                'Air Pressure': {
                    'getter': lambda device: device.get_air_pressure(),
                    'subvalues': None
                },
                'Altitude': {
                    'getter': lambda device: device.get_altitude(),
                    'subvalues': None
                },
                'Chip Temperature': {
                    'getter': lambda device: device.get_chip_temperature(),
                    'subvalues': None
                }
            }
        },
        BrickletColor.DEVICE_DISPLAY_NAME: {
            'class': BrickletColor,
            'values': {
                'Color': {
                    'getter': lambda device: device.get_color(),
                    'subvalues': ['Red', 'Green', 'Blue', 'Clear']
                },
                'Illuminance': {
                    'getter': lambda device: device.get_illuminance(),
                    'subvalues': None
                },
                'Color Temperature': {
                    'getter': lambda device: device.get_color_temperature(),
                    'subvalues': None
                }
            }
        },
        BrickletCurrent12.DEVICE_DISPLAY_NAME: {
            'class': BrickletCurrent12,
            'values': {
                'Analog Value': {
                    'getter': lambda device: device.get_analog_value(),
                    'subvalues': None
                },
                'Current': {
                    'getter': lambda device: device.get_current(),
                    'subvalues': None
                }
            }
        },
        BrickletCurrent25.DEVICE_DISPLAY_NAME: {
            'class': BrickletCurrent25,
            'values': {
                'Analog Value': {
                    'getter': lambda device: device.get_analog_value(),
                    'subvalues': None
                },
                'Current': {
                    'getter': lambda device: device.get_current(),
                    'subvalues': None
                }
            }
        },
        BrickletDistanceIR.DEVICE_DISPLAY_NAME: {
            'class': BrickletDistanceIR,
            'values': {
                'Analog Value': {
                    'getter': lambda device: device.get_analog_value(),
                    'subvalues': None
                },
                'Distance': {
                    'getter': lambda device: device.get_distance(),
                    'subvalues': None
                }
            }
        },
        BrickletDistanceUS.DEVICE_DISPLAY_NAME: {
            'class': BrickletDistanceUS,
            'values': {
                'Distance Value': {
                    'getter': lambda device: device.get_distance_value(),
                    'subvalues': None
                }
            }
        },
        BrickletDualButton.DEVICE_DISPLAY_NAME: {
            'class': BrickletDualButton,
            'values': {
                'Button State': {
                    'getter': lambda device: device.get_button_state(),
                    'subvalues': ['Left', 'Right']
                },
                'LED State': {
                    'getter': lambda device: device.get_led_state(),
                    'subvalues': ['Left', 'Right']
                }
            }
        },
        BrickletDustDetector.DEVICE_DISPLAY_NAME: {
            'class': BrickletDustDetector,
            'values': {
                'Dust Density': {
                    'getter': lambda device: device.get_dust_density(),
                    'subvalues': None
                }
            }
        },
        BrickletGPS.DEVICE_DISPLAY_NAME: {
            'class': BrickletGPS,
            'values': {
                'Altitude': {
                    'getter': special_get_gps_altitude,
                    'subvalues': ['Altitude', 'Geoidal Separation']
                },
                'Coordinates': {
                    'getter': special_get_gps_coordinates,
                    'subvalues': ['Latitude', 'NS', 'Longitude', 'EW', 'PDOP', 'HDOP', 'VDOP', 'EPE']
                },
                'Date Time': {
                    'getter': lambda device: device.get_date_time(),
                    'subvalues': ['Date', 'Time']
                },
                'Motion': {
                    'getter': special_get_gps_motion,
                    'subvalues': ['Course', 'Speed']
                },
                'Status': {
                    'getter': lambda device: device.get_status(),
                    'subvalues': ['Fix', 'Satellites View', 'Satellites Used']
                }
            }
        },
        BrickletHallEffect.DEVICE_DISPLAY_NAME: {
            'class': BrickletHallEffect,
            'values': {
                'Edge Count': {
                    'getter': lambda device: device.get_edge_count(False),
                    'subvalues': None
                },
                'Value': {
                    'getter': lambda device: device.get_value(),
                    'subvalues': None
                }
            }
        },
        BrickletHumidity.DEVICE_DISPLAY_NAME: {
            'class': BrickletHumidity,
            'values': {
                'Humidity': {
                    'getter': lambda device: device.get_humidity(),
                    'subvalues': None
                },
                'Analog Value': {
                    'getter': lambda device: device.get_analog_value(),
                    'subvalues': None
                }
            }
        },
        BrickletIndustrialDigitalIn4.DEVICE_DISPLAY_NAME: {
            'class': BrickletIndustrialDigitalIn4,
            'values': {
                'Edge Count (Pin 0)': {
                    'getter': lambda device: device.get_edge_count(0, False),
                    'subvalues': None
                },
                'Edge Count (Pin 1)': {
                    'getter': lambda device: device.get_edge_count(1, False),
                    'subvalues': None
                },
                'Edge Count (Pin 2)': {
                    'getter': lambda device: device.get_edge_count(2, False),
                    'subvalues': None
                },
                'Edge Count (Pin 3)': {
                    'getter': lambda device: device.get_edge_count(3, False),
                    'subvalues': None
                },
                'Value': {
                    'getter': lambda device: device.get_value(),
                    'subvalues': None
                }
            }
        },
        BrickletIndustrialDual020mA.DEVICE_DISPLAY_NAME: {
            'class': BrickletIndustrialDual020mA,
            'values': {
                'Current (Sensor 0)': {
                    'getter': lambda device: device.get_current(0),
                    'subvalues': None
                },
                'Current (Sensor 1)': {
                    'getter': lambda device: device.get_current(1),
                    'subvalues': None
                }
            }
        },
        BrickletIndustrialDualAnalogIn.DEVICE_DISPLAY_NAME: {
            'class': BrickletIndustrialDualAnalogIn,
            'values': {
                'Voltage (Channel 0)': {
                    'getter': lambda device: device.get_voltage(0),
                    'subvalues': None
                },
                'Voltage (Channel 1)': {
                    'getter': lambda device: device.get_voltage(1),
                    'subvalues': None
                },
                'ADC Values': {
                    'getter': lambda device: device.get_adc_values(),
                    'subvalues': ['Channel 0', 'Channel 1']
                }
            }
        },
        BrickletIO16.DEVICE_DISPLAY_NAME: {
            'class': BrickletIO16,
            'values': {
                'Edge Count (Pin A0)': {
                    'getter': lambda device: device.get_edge_count(0, False),
                    'subvalues': None
                },
                'Edge Count (Pin A1)': {
                    'getter': lambda device: device.get_edge_count(1, False),
                    'subvalues': None
                },
                'Port A': {
                    'getter': lambda device: device.get_port('a'),
                    'subvalues': None
                },
                'Port B': {
                    'getter': lambda device: device.get_port('b'),
                    'subvalues': None
                }
            }
        },
        BrickletIO4.DEVICE_DISPLAY_NAME: {
            'class': BrickletIO4,
            'values': {
                'Edge Count (Pin 0)': {
                    'getter': lambda device: device.get_edge_count(0, False),
                    'subvalues': None
                },
                'Edge Count (Pin 1)': {
                    'getter': lambda device: device.get_edge_count(1, False),
                    'subvalues': None
                },
                'Edge Count (Pin 2)': {
                    'getter': lambda device: device.get_edge_count(2, False),
                    'subvalues': None
                },
                'Edge Count (Pin 3)': {
                    'getter': lambda device: device.get_edge_count(3, False),
                    'subvalues': None
                },
                'Value': {
                    'getter': lambda device: device.get_value(),
                    'subvalues': None
                }
            }
        },
        BrickletJoystick.DEVICE_DISPLAY_NAME: {
            'class': BrickletJoystick,
            'values': {
                'Position': {
                    'getter': lambda device: device.get_position(),
                    'subvalues': ['X', 'Y']
                },
                'Pressed': {
                    'getter': lambda device: device.is_pressed(),
                    'subvalues': None
                },
                'Analog Value': {
                    'getter': lambda device: device.get_analog_value(),
                    'subvalues': ['X', 'Y']
                }
            }
        },
        BrickletLEDStrip.DEVICE_DISPLAY_NAME: {
            'class': BrickletLEDStrip,
            'values': {
                'Supply Voltage': {
                    'getter': lambda device: device.get_supply_voltage(),
                    'subvalues': None
                }
            }
        },
        BrickletLine.DEVICE_DISPLAY_NAME: {
            'class': BrickletLine,
            'values': {
                'Reflectivity': {
                    'getter': lambda device: device.get_reflectivity(),
                    'subvalues': None
                }
            }
        },
        BrickletLinearPoti.DEVICE_DISPLAY_NAME: {
            'class': BrickletLinearPoti,
            'values': {
                'Position': {
                    'getter': lambda device: device.get_position(),
                    'subvalues': None
                },
                'Analog Value': {
                    'getter': lambda device: device.get_analog_value(),
                    'subvalues': None
                }
            }
        },
        BrickletLoadCell.DEVICE_DISPLAY_NAME: {
            'class': BrickletLoadCell,
            'values': {
                'Weight': {
                    'getter': lambda device: device.get_weight(),
                    'subvalues': None
                }
            }
        },
        BrickletMoisture.DEVICE_DISPLAY_NAME: {
            'class': BrickletMoisture,
            'values': {
                'Value': {
                    'getter': lambda device: device.get_moisture_value(),
                    'subvalues': None
                }
            }
        },
        BrickletMotionDetector.DEVICE_DISPLAY_NAME: {
            'class': BrickletMotionDetector,
            'values': {
                'Motion Detected': {
                    'getter': lambda device: device.get_motion_detected(),
                    'subvalues': None
                }
            }
        },
        BrickletMultiTouch.DEVICE_DISPLAY_NAME: {
            'class': BrickletMultiTouch,
            'values': {
                'State': {
                    'getter': lambda device: device.get_touch_state(),
                    'subvalues': None
                }
            }
        },
        BrickletPTC.DEVICE_DISPLAY_NAME: {
            'class': BrickletPTC,
            'values': {
                'Resistance': {
                    'getter': special_get_ptc_resistance,
                    'subvalues': None
                },
                'Temperature': {
                    'getter': special_get_ptc_temperature,
                    'subvalues': None
                }
            }
        },
        BrickletRotaryEncoder.DEVICE_DISPLAY_NAME: {
            'class': BrickletRotaryEncoder,
            'values': {
                'Count': {
                    'getter': lambda device: device.get_count(False),
                    'subvalues': None
                },
                'Pressed': {
                    'getter': lambda device: device.is_pressed(),
                    'subvalues': None
                }
            }
        },
        BrickletRotaryPoti.DEVICE_DISPLAY_NAME: {
            'class': BrickletRotaryPoti,
            'values': {
                'Position': {
                    'getter': lambda device: device.get_position(),
                    'subvalues': None
                },
                'Analog Value': {
                    'getter': lambda device: device.get_analog_value(),
                    'subvalues': None
                }
            }
        },
        BrickletSoundIntensity.DEVICE_DISPLAY_NAME: {
            'class': BrickletSoundIntensity,
            'values': {
                'Intensity': {
                    'getter': lambda device: device.get_intensity(),
                    'subvalues': None
                }
            }
        },
        BrickletTemperature.DEVICE_DISPLAY_NAME: {
            'class': BrickletTemperature,
            'values': {
                'Temperature': {
                    'getter': lambda device: device.get_temperature(),
                    'subvalues': None
                }
            }
        },
        BrickletTemperatureIR.DEVICE_DISPLAY_NAME: {
            'class': BrickletTemperatureIR,
            'values': {
                'Ambient Temperature': {
                    'getter': lambda device: device.get_ambient_temperature(),
                    'subvalues': None
                },
                'Object Temperature': {
                    'getter': lambda device: device.get_object_temperature(),
                    'subvalues': None
                }
            }
        },
        BrickletTilt.DEVICE_DISPLAY_NAME: {
            'class': BrickletTilt,
            'values': {
                'State': {
                    'getter': lambda device: device.get_tilt_state(),
                    'subvalues': None
                }
            }
        },
        BrickletVoltage.DEVICE_DISPLAY_NAME: {
            'class': BrickletVoltage,
            'values': {
                'Voltage': {
                    'getter': lambda device: device.get_voltage(),
                    'subvalues': None
                },
                'Analog Value': {
                    'getter': lambda device: device.get_analog_value(),
                    'subvalues': None
                }
            }
        },
        BrickletVoltageCurrent.DEVICE_DISPLAY_NAME: {
            'class': BrickletVoltageCurrent,
            'values': {
                'Current': {
                    'getter': lambda device: device.get_current(),
                    'subvalues': None
                },
                'Voltage': {
                    'getter': lambda device: device.get_voltage(),
                    'subvalues': None
                },
                'Power': {
                    'getter': lambda device: device.get_power(),
                    'subvalues': None
                }
            }
        },
        #####################
        # Bricks Start Here #
        #####################
        BrickDC.DEVICE_DISPLAY_NAME: {
            'class': BrickDC,
            'values': {
                'Velocity': {
                    'getter': lambda device: device.get_velocity(),
                    'subvalues': None
                },
                'Current Velocity': {
                    'getter': lambda device: device.get_current_velocity(),
                    'subvalues': None
                },
                'Acceleration': {
                    'getter': lambda device: device.get_acceleration(),
                    'subvalues': None
                },
                'Stack Input Voltage': {
                    'getter': lambda device: device.get_stack_input_voltage(),
                    'subvalues': None
                },
                'External Input Voltage': {
                    'getter': lambda device: device.get_external_input_voltage(),
                    'subvalues': None
                },
                'Current Consumption': {
                    'getter': lambda device: device.get_current_consumption(),
                    'subvalues': None
                },
                'Chip Temperature': {
                    'getter': lambda device: device.get_chip_temperature(),
                    'subvalues': None
                }
            }
        }
    }

'''
/*---------------------------------------------------------------------------
                                AbstractDevice
 ---------------------------------------------------------------------------*/
 '''

class AbstractDevice(object):
    """DEBUG and Inheritance only class"""

    def __init__(self, data, datalogger):
        self.datalogger = datalogger
        self.data = data
        self.identifier = None

        self.__name__ = "AbstractDevice"

    def start_timer(self):
        """
        Starts all timer for all loggable variables of the devices.
        """
        EventLogger.debug(self.__str__())

    def _try_catch(self, func):
        """
        Creates a simple try-catch for a specific funtion.
        """
        value = "[NYI-FAIL-TIMER]"
        # err = 0
        try:
            value = func()
        except Exception as e:
            value = self._exception_msg(e.value, e.description)
            # err = 1
        return value

    def _exception_msg(self, value, msg):
        """
        For a uniform creation of Exception messages.
        """
        return "ERROR[" + str(value) + "]: " + str(msg)

    def __str__(self):
        """
        Representation String of the class. For simple overwiev.
        """
        return "[" + str(self.__name__) + "]"

'''
/*---------------------------------------------------------------------------
                                DeviceImpl
 ---------------------------------------------------------------------------*/
 '''

class DeviceImpl(AbstractDevice):
    """
    A SimpleDevice is every device, which only has funtion with one return value.
    """

    def __init__(self, data, datalogger):
        AbstractDevice.__init__(self, data, datalogger)

        self.device_name = self.data[Identifier.DD_NAME]
        self.device_uid = self.data[Identifier.DD_UID]
        self.device_definition = Identifier.DEVICE_DEFINITIONS[self.device_name]
        device_class = self.device_definition[Identifier.DD_CLASS]
        self.device = device_class(self.device_uid, self.datalogger.ipcon)
        self.identifier = self.device_name

        self.__name__ = Identifier.DEVICES + ":" + str(self.device_name)

    def start_timer(self):
        AbstractDevice.start_timer(self)

        for value in self.data[Identifier.DD_VALUES]:
            interval = self.data[Identifier.DD_VALUES][value][Identifier.DD_VALUES_INTERVAL]
            func_name = "_timer"
            var_name = value

            self.datalogger.timers.append(utils.LoggerTimer(interval, func_name, var_name, self))

    def _timer(self, var_name):
        """
        This function is used by the LoggerTimer to get the variable values from the brickd.
        In SimpleDevices the get-functions only return one value.
        """

        getter = self.device_definition[Identifier.DD_VALUES][var_name][Identifier.DD_GETTER]
        subvalue_names = self.device_definition[Identifier.DD_VALUES][var_name][
            Identifier.DD_SUBVALUES]
        timestamp = utils.CSVData._get_timestamp()

        try:
            value = getter(self.device)
        except Exception as e:
            value = self._exception_msg(str(self.identifier) + "-" + str(var_name), e)
            self.datalogger.add_to_queue(utils.CSVData(self.device_uid, self.identifier, var_name, value, timestamp))
            # log_exception(timestamp, value_name, e)
            return

        try:
            if subvalue_names is None:
                # log_value(value_name, value)
                self.datalogger.add_to_queue(
                    utils.CSVData(self.device_uid, self.identifier, var_name, value, timestamp))
            else:
                subvalue_bool = self.data[Identifier.DD_VALUES][var_name][Identifier.DD_SUBVALUES]
                for i in range(len(subvalue_names)):
                    if not isinstance(subvalue_names[i], list):
                        try:
                            if subvalue_bool[subvalue_names[i]]:
                                self.datalogger.add_to_queue(utils.CSVData(self.device_uid, self.identifier,
                                                                           str(var_name) + "-" + str(subvalue_names[i]),
                                                                           value[i], timestamp))
                        except Exception as e:
                            value = self._exception_msg(str(self.identifier) + "-" + str(var_name), e)
                            self.datalogger.add_to_queue(utils.CSVData(self.device_uid, self.identifier,
                                                                       str(var_name) + "-" + str(subvalue_names[i]),
                                                                       value[i], timestamp))
                            return
                    else:
                        for k in range(len(subvalue_names[i])):
                            try:
                                if subvalue_bool[subvalue_names[i][k]]:
                                    self.datalogger.add_to_queue(utils.CSVData(self.device_uid, self.identifier,
                                                                               str(var_name) + "-" + str(
                                                                                   subvalue_names[i][k]), value[i][k],
                                                                               timestamp))
                            except Exception as e:
                                value = self._exception_msg(str(self.identifier) + "-" + str(var_name), e)
                                self.datalogger.add_to_queue(utils.CSVData(self.device_uid, self.identifier,
                                                                           str(var_name) + "-" + str(
                                                                               subvalue_names[i][k]), value[i][k],
                                                                           timestamp))
                                return
        except Exception as e:
            value = self._exception_msg(str(self.identifier) + "-" + str(var_name), e)
            self.datalogger.add_to_queue(utils.CSVData(self.device_uid, self.identifier, var_name, value, timestamp))
