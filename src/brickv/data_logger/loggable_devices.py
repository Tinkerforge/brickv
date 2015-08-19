# https://docs.google.com/spreadsheets/d/14p6N8rAg8M9Ozr1fmOZePPflvNJmgt0pSAebliDrasI/edit?usp=sharing
# Documented for Testing and Blueprints
# Bricklets ############################################################################################################
# from brickv.bindings.bricklet_accelerometer import Accelerometer #NYI
from brickv.bindings.bricklet_ambient_light import AmbientLight
# from brickv.bindings.bricklet_ambient_light_v2 import AmbientLightV2 #NYI
from brickv.bindings.bricklet_analog_in import AnalogIn
# from brickv.bindings.bricklet_analog_in_v2 import AnalogInV2 #NYI
from brickv.bindings.bricklet_analog_out import AnalogOut
# from brickv.bindings.bricklet_analog_out_v2 import AnalogOutV2 #NYI
from brickv.bindings.bricklet_barometer import Barometer
# from brickv.bindings.bricklet_breakout??? import Breakout??? #NYI
from brickv.bindings.bricklet_color import Color
from brickv.bindings.bricklet_current12 import Current12
from brickv.bindings.bricklet_current25 import Current25
from brickv.bindings.bricklet_distance_ir import DistanceIR
from brickv.bindings.bricklet_distance_us import DistanceUS
from brickv.bindings.bricklet_dual_button import DualButton
from brickv.bindings.bricklet_dual_relay import DualRelay
# from brickv.bindings.bricklet_dust_detector import DustDetector #NYI
from brickv.bindings.bricklet_gps import GPS
from brickv.bindings.bricklet_hall_effect import HallEffect
from brickv.bindings.bricklet_humidity import Humidity
# from brickv.bindings.bricklet_industrial_analog_out import IndustrialAnalogOut #NYI
# from brickv.bindings.bricklet_industrial_digital_in_4 import IndustrialDigitalIn4 #NYI
# from brickv.bindings.bricklet_industrial_digital_out_4 import IndustrialDigitalOut4 #NYI
from brickv.bindings.bricklet_industrial_dual_0_20ma import IndustrialDual020mA
# from brickv.bindings.bricklet_industrial_dual_analog_in import IndustrialDualAnalogIn #NYI
# from brickv.bindings.bricklet_industrial_quad_relay import IndustrialQuadRelay #NYI
from brickv.bindings.bricklet_io16 import IO16
from brickv.bindings.bricklet_io4 import IO4
from brickv.bindings.bricklet_joystick import Joystick
# from brickv.bindings.bricklet_laser_range_finder import LaserRangeFinder #NYI
# from brickv.bindings.bricklet_lcd_16x2 import LCD16x2 #NYI
# from brickv.bindings.bricklet_lcd_20x4 import LCD20x4 #NYI
from brickv.bindings.bricklet_led_strip import LEDStrip
from brickv.bindings.bricklet_line import Line
from brickv.bindings.bricklet_linear_poti import LinearPoti
# from brickv.bindings.bricklet_load_cell import LoadCell #NYI
from brickv.bindings.bricklet_moisture import Moisture
from brickv.bindings.bricklet_motion_detector import MotionDetector
from brickv.bindings.bricklet_multi_touch import MultiTouch
# from brickv.bindings.bricklet_nfc_rfid import NFCRFID #NYI
# from brickv.bindings.bricklet_piezo_buzzer import PiezoBuzzer #NYI
# from brickv.bindings.bricklet_piezo_speaker import PiezoSpeaker #NYI
from brickv.bindings.bricklet_ptc import PTC
# from brickv.bindings.bricklet_remote_switch import RemoteSwitch #NYI
from brickv.bindings.bricklet_rotary_encoder import RotaryEncoder
from brickv.bindings.bricklet_rotary_poti import RotaryPoti
# from brickv.bindings.bricklet_rs232 import RS232 #NYI
from brickv.bindings.bricklet_segment_display_4x7 import SegmentDisplay4x7
from brickv.bindings.bricklet_solid_state_relay import SolidStateRelay
from brickv.bindings.bricklet_sound_intensity import SoundIntensity
from brickv.bindings.bricklet_temperature import Temperature
from brickv.bindings.bricklet_temperature_ir import TemperatureIR
from brickv.bindings.bricklet_tilt import Tilt
from brickv.bindings.bricklet_voltage import Voltage
from brickv.bindings.bricklet_voltage_current import VoltageCurrent
# Bricks ###############################################################################################################
from brickv.bindings.brick_dc import DC  # NYI
# from brickv.bindings.brick_stepper import Stepper #NYI


from brickv.data_logger.event_logger import EventLogger
import brickv.data_logger.utils as utils

'''
/*---------------------------------------------------------------------------
                                SpecialDevices
 ---------------------------------------------------------------------------*/
 '''


class SpecialDevices(object):
    """
    SpecialDevices are functions for special Bricks/Bricklets. Some Device functions can return different values,
    depending on different situations, e.g. the GPS Bricklet. If the GPS Bricklet does not have a so called FIX Value,
    then the function will return an Error instead of the specified return values.
    """

    # GPS
    def get_gps_coordinates(device):
        if device.get_status()[0] == GPS.FIX_NO_FIX:
            raise Exception('No fix')
        else:
            return device.get_coordinates()

    get_gps_coordinates = staticmethod(get_gps_coordinates)

    def get_gps_altitude(device):
        if device.get_status()[0] != GPS.FIX_3D_FIX:
            raise Exception('No 3D fix')
        else:
            return device.get_altitude()

    get_gps_altitude = staticmethod(get_gps_altitude)

    def get_gps_motion(device):
        if device.get_status()[0] == GPS.FIX_NO_FIX:
            raise Exception('No fix')
        else:
            return device.get_motion()

    get_gps_motion = staticmethod(get_gps_motion)

    # PTC
    def get_ptc_temperature(device):
        if not device.is_sensor_connected():
            raise Exception('No sensor')
        else:
            return device.get_temperature()

    get_ptc_temperature = staticmethod(get_ptc_temperature)


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
        ################################################################################################################
        # Bricklets Start Here #
        ########################
        AmbientLight.DEVICE_DISPLAY_NAME: {
            'class': AmbientLight,
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
        AnalogIn.DEVICE_DISPLAY_NAME: {
            'class': AnalogIn,
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
        AnalogOut.DEVICE_DISPLAY_NAME: {
            'class': AnalogOut,
            'values': {
                'Voltage': {
                    'getter': lambda device: device.get_voltage(),
                    'subvalues': None
                }
            }
        },
        Barometer.DEVICE_DISPLAY_NAME: {
            'class': Barometer,
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
        Color.DEVICE_DISPLAY_NAME: {
            'class': Color,
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
        Current12.DEVICE_DISPLAY_NAME: {
            'class': Current12,
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
        Current25.DEVICE_DISPLAY_NAME: {
            'class': Current25,
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
        DistanceIR.DEVICE_DISPLAY_NAME: {
            'class': DistanceIR,
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
        DistanceUS.DEVICE_DISPLAY_NAME: {
            'class': DistanceUS,
            'values': {
                'Distance': {
                    'getter': lambda device: device.get_distance_value(),
                    'subvalues': None
                }
            }
        },
        DualButton.DEVICE_DISPLAY_NAME: {
            'class': DualButton,
            'values': {
                'Button State': {
                    'getter': lambda device: device.get_button_state(),
                    'subvalues': ['Left', 'Right']
                },
                'Led State': {
                    'getter': lambda device: device.get_led_state(),
                    'subvalues': ['Left', 'Right']
                }
            }
        },
        DualRelay.DEVICE_DISPLAY_NAME: {
            'class': DualRelay,
            'values': {
                'State': {
                    'getter': lambda device: device.get_state(),
                    'subvalues': ['Relay1', 'Relay2']
                },
                'Monoflop1': {
                    'getter': lambda device: device.get_monoflop(1),
                    'subvalues': ['State', 'Time', 'Time Remaining']
                },
                'Monoflop2': {
                    'getter': lambda device: device.get_monoflop(2),
                    'subvalues': ['State', 'Time', 'Time Remaining']
                }
            }
        },
        GPS.DEVICE_DISPLAY_NAME: {
            'class': GPS,
            'values': {
                'Altitude': {
                    'getter': SpecialDevices.get_gps_altitude,
                    'subvalues': ['Altitude', 'Geoidal Separation']
                },
                'Coordinates': {
                    'getter': SpecialDevices.get_gps_coordinates,
                    'subvalues': ['Latitude', 'NS', 'Longitude', 'EW', 'PDOP', 'HDOP', 'VDOP', 'EPE']
                },
                'Date Time': {
                    'getter': lambda device: device.get_date_time(),
                    'subvalues': ['Date', 'Time']
                },
                'Motion': {
                    'getter': SpecialDevices.get_gps_motion,
                    'subvalues': ['Course', 'Speed']
                },
                'Status': {
                    'getter': lambda device: device.get_status(),
                    'subvalues': ['Fix', 'Satellites View', 'Satellites Used']
                }
            }
        },
        HallEffect.DEVICE_DISPLAY_NAME: {
            'class': HallEffect,
            'values': {
                'Value': {
                    'getter': lambda device: device.get_value(),
                    'subvalues': None
                }
            }
        },
        Humidity.DEVICE_DISPLAY_NAME: {
            'class': Humidity,
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
        IndustrialDual020mA.DEVICE_DISPLAY_NAME: {
            'class': IndustrialDual020mA,
            'values': {
                'Current Sensor0': {
                    'getter': lambda device: device.get_current(0),
                    'subvalues': None
                },
                'Current Sensor1': {
                    'getter': lambda device: device.get_current(1),
                    'subvalues': None
                }
            }
        },
        IO16.DEVICE_DISPLAY_NAME: {
            'class': IO16,
            'values': {
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
        IO4.DEVICE_DISPLAY_NAME: {
            'class': IO4,
            'values': {
                'Value': {
                    'getter': lambda device: device.get_value(),
                    'subvalues': None
                }
            }
        },
        Joystick.DEVICE_DISPLAY_NAME: {
            'class': Joystick,
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
        # TODO Bricklet with some big return Arrays (3x16!) -> To many subvalues?
        LEDStrip.DEVICE_DISPLAY_NAME: {
            'class': LEDStrip,
            'values': {
                'Supply Voltage': {
                    'getter': lambda device: device.get_supply_voltage(),
                    'subvalues': None
                }
            }
        },
        Line.DEVICE_DISPLAY_NAME: {
            'class': Line,
            'values': {
                'Reflectivity': {
                    'getter': lambda device: device.get_reflectivity(),
                    'subvalues': None
                }
            }
        },
        LinearPoti.DEVICE_DISPLAY_NAME: {
            'class': LinearPoti,
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
        Moisture.DEVICE_DISPLAY_NAME: {
            'class': Moisture,
            'values': {
                'Value': {
                    'getter': lambda device: device.get_moisture_value(),
                    'subvalues': None
                }
            }
        },
        MotionDetector.DEVICE_DISPLAY_NAME: {
            'class': MotionDetector,
            'values': {
                'Motion Detected': {
                    'getter': lambda device: device.get_motion_detected(),
                    'subvalues': None
                }
            }
        },
        MultiTouch.DEVICE_DISPLAY_NAME: {
            'class': MultiTouch,
            'values': {
                'State': {
                    'getter': lambda device: device.get_touch_state(),
                    'subvalues': None
                }
            }
        },
        PTC.DEVICE_DISPLAY_NAME: {
            'class': PTC,
            'values': {
                'Resistance': {
                    'getter': lambda device: device.get_resistance(),
                    'subvalues': None
                },
                'Temperature': {
                    'getter': lambda device: device.get_temperature(),
                    'subvalues': None
                }
            }
        },
        RotaryEncoder.DEVICE_DISPLAY_NAME: {
            'class': RotaryEncoder,
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
        RotaryPoti.DEVICE_DISPLAY_NAME: {
            'class': RotaryPoti,
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
        SegmentDisplay4x7.DEVICE_DISPLAY_NAME: {
            'class': SegmentDisplay4x7,
            'values': {
                'Counter Value': {
                    'getter': lambda device: device.get_counter_value(),
                    'subvalues': None
                },
                'Segments': {
                    'getter': lambda device: device.get_segments(),
                    'subvalues': [['Segm1', 'Segm2', 'Segm3', 'Segm4'], 'Brightness', 'Colon']
                }
            }
        },
        SolidStateRelay.DEVICE_DISPLAY_NAME: {
            'class': SolidStateRelay,
            'values': {
                'State': {
                    'getter': lambda device: device.get_state(),
                    'subvalues': None
                },
                'Monoflop': {
                    'getter': lambda device: device.get_monoflop(),
                    'subvalues': ['State', 'Time', 'Time Remaining']
                }
            }
        },
        SoundIntensity.DEVICE_DISPLAY_NAME: {
            'class': SoundIntensity,
            'values': {
                'Intensity': {
                    'getter': lambda device: device.get_intensity(),
                    'subvalues': None
                }
            }
        },
        Temperature.DEVICE_DISPLAY_NAME: {
            'class': Temperature,
            'values': {
                'Temperature': {
                    'getter': lambda device: device.get_temperature(),
                    'subvalues': None
                }
            }
        },
        TemperatureIR.DEVICE_DISPLAY_NAME: {
            'class': TemperatureIR,
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
        Tilt.DEVICE_DISPLAY_NAME: {
            'class': Tilt,
            'values': {
                'State': {
                    'getter': lambda device: device.get_tilt_state(),
                    'subvalues': None
                }
            }
        },
        Voltage.DEVICE_DISPLAY_NAME: {
            'class': Voltage,
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
        VoltageCurrent.DEVICE_DISPLAY_NAME: {
            'class': VoltageCurrent,
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
        ################################################################################################################
        # Bricks Start Here #
        #####################
        DC.DEVICE_DISPLAY_NAME: {
            'class': DC,
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