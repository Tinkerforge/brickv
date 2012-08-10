DESTDIR =

PREFIX  = /usr
BINDIR  = ${PREFIX}/bin
DATADIR = ${PREFIX}/share

quiet-command = $(if ${V},${1},$(if ${2},@echo ${2} && ${1}, @${1}))
quiet-install = $(call quiet-command,install -m ${1} ${2} ${3},"INSTALL	${3}")
quiet-installdir = $(call quiet-command,install -m ${1} -d ${2},"MKDIR	${2}")

sed-rules = -e "s,@BRICKV_DIR@,${BRICKV_DIR},"

BRICKV_DIR              = ${DATADIR}/brickv
BRICKV_BINDINGS_DIR     = ${BRICKV_DIR}/bindings
BRICKV_PLUGINSYSTEM_DIR = ${BRICKV_DIR}/plugin_system
BRICKV_PLUGINS_DIR      = ${BRICKV_PLUGINSYSTEM_DIR}/plugins
BRICKV_PLUGIN_AMBIENTLIGHT_DIR = ${BRICKV_PLUGINS_DIR}/ambient_light
BRICKV_PLUGIN_ANALOGIN_DIR = ${BRICKV_PLUGINS_DIR}/analog_in
BRICKV_PLUGIN_ANALOGOUT_DIR = ${BRICKV_PLUGINS_DIR}/analog_out
BRICKV_PLUGIN_CURRENT12_DIR = ${BRICKV_PLUGINS_DIR}/current12
BRICKV_PLUGIN_CURRENT25_DIR = ${BRICKV_PLUGINS_DIR}/current25
BRICKV_PLUGIN_DC_DIR = ${BRICKV_PLUGINS_DIR}/dc
BRICKV_PLUGIN_DISTANCEIR_DIR = ${BRICKV_PLUGINS_DIR}/distance_ir
BRICKV_PLUGIN_DUALRELAY_DIR = ${BRICKV_PLUGINS_DIR}/dual_relay
BRICKV_PLUGIN_HUMIDITY_DIR = ${BRICKV_PLUGINS_DIR}/humidity
BRICKV_PLUGIN_IMU_DIR = ${BRICKV_PLUGINS_DIR}/imu
BRICKV_PLUGIN_IO16_DIR = ${BRICKV_PLUGINS_DIR}/io16
BRICKV_PLUGIN_IO4_DIR = ${BRICKV_PLUGINS_DIR}/io4
BRICKV_PLUGIN_JOYSTICK_DIR = ${BRICKV_PLUGINS_DIR}/joystick
BRICKV_PLUGIN_LCD16x2_DIR = ${BRICKV_PLUGINS_DIR}/lcd_16x2
BRICKV_PLUGIN_LCD20x4_DIR = ${BRICKV_PLUGINS_DIR}/lcd_20x4
BRICKV_PLUGIN_LINEARPOTI_DIR = ${BRICKV_PLUGINS_DIR}/linear_poti
BRICKV_PLUGIN_MASTER_DIR = ${BRICKV_PLUGINS_DIR}/master
BRICKV_PLUGIN_PIEZOBUZZER_DIR = ${BRICKV_PLUGINS_DIR}/piezo_buzzer
BRICKV_PLUGIN_ROTARYPOTI_DIR = ${BRICKV_PLUGINS_DIR}/rotary_poti
BRICKV_PLUGIN_SERVO_DIR = ${BRICKV_PLUGINS_DIR}/servo
BRICKV_PLUGIN_STEPPER_DIR = ${BRICKV_PLUGINS_DIR}/stepper
BRICKV_PLUGIN_TEMPERATURE_DIR = ${BRICKV_PLUGINS_DIR}/temperature
BRICKV_PLUGIN_TEMPERATUREIR_DIR = ${BRICKV_PLUGINS_DIR}/temperature_ir
BRICKV_PLUGIN_VOLTAGE_DIR = ${BRICKV_PLUGINS_DIR}/voltage

BRICKV_CORE_SRCDIR         = src/brickv
BRICKV_BINDINGS_SRCDIR     = ${BRICKV_CORE_SRCDIR}/bindings
BRICKV_PLUGINSYSTEM_SRCDIR = ${BRICKV_CORE_SRCDIR}/plugin_system
BRICKV_PLUGINS_SRCDIR      = ${BRICKV_PLUGINSYSTEM_SRCDIR}/plugins
BRICKV_PLUGIN_AMBIENTLIGHT_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/ambient_light
BRICKV_PLUGIN_ANALOGIN_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/analog_in
BRICKV_PLUGIN_ANALOGOUT_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/analog_out
BRICKV_PLUGIN_CURRENT12_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/current12
BRICKV_PLUGIN_CURRENT25_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/current25
BRICKV_PLUGIN_DC_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/dc
BRICKV_PLUGIN_DISTANCEIR_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/distance_ir
BRICKV_PLUGIN_DUALRELAY_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/dual_relay
BRICKV_PLUGIN_HUMIDITY_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/humidity
BRICKV_PLUGIN_IMU_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/imu
BRICKV_PLUGIN_IO16_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/io16
BRICKV_PLUGIN_IO4_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/io4
BRICKV_PLUGIN_JOYSTICK_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/joystick
BRICKV_PLUGIN_LCD16x2_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/lcd_16x2
BRICKV_PLUGIN_LCD20x4_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/lcd_20x4
BRICKV_PLUGIN_LINEARPOTI_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/linear_poti
BRICKV_PLUGIN_MASTER_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/master
BRICKV_PLUGIN_PIEZOBUZZER_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/piezo_buzzer
BRICKV_PLUGIN_ROTARYPOTI_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/rotary_poti
BRICKV_PLUGIN_SERVO_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/servo
BRICKV_PLUGIN_STEPPER_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/stepper
BRICKV_PLUGIN_TEMPERATURE_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/temperature
BRICKV_PLUGIN_TEMPERATUREIR_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/temperature_ir
BRICKV_PLUGIN_VOLTAGE_SRCDIR = ${BRICKV_PLUGINS_SRCDIR}/voltage

BRICKV_SHELL = brickv

BRICKV_ICON = brickv-icon.png

BRICKV_CORE += __init__.py
BRICKV_CORE += advanced.py
BRICKV_CORE += config.py
BRICKV_CORE += config_linux.py
BRICKV_CORE += flashing.py
BRICKV_CORE += main.py
BRICKV_CORE += mainwindow.py
BRICKV_CORE += plot_widget.py
BRICKV_CORE += program_path.py
BRICKV_CORE += samba.py
BRICKV_CORE += ui_advanced.py
BRICKV_CORE += ui_flashing.py
BRICKV_CORE += ui_mainwindow.py

BRICKV_PLUGINSYSTEM += __init__.py
BRICKV_PLUGINSYSTEM += plugin_base.py
BRICKV_PLUGINSYSTEM += plugin_manager.py

BRICKV_BINDINGS += __init__.py
BRICKV_BINDINGS += bricklet_analog_out.py
BRICKV_BINDINGS += bricklet_lcd_16x2.py
BRICKV_BINDINGS += bricklet_lcd_20x4.py
BRICKV_BINDINGS += bricklet_piezo_buzzer.py
BRICKV_BINDINGS += bricklet_temperature.py
BRICKV_BINDINGS += ks0066u.py
BRICKV_BINDINGS += brick_dc.py
BRICKV_BINDINGS += brick_imu.py
BRICKV_BINDINGS += brick_master.py
BRICKV_BINDINGS += brick_servo.py
BRICKV_BINDINGS += brick_stepper.py
BRICKV_BINDINGS += bricklet_ambient_light.py
BRICKV_BINDINGS += bricklet_analog_in.py
BRICKV_BINDINGS += bricklet_current12.py
BRICKV_BINDINGS += bricklet_current25.py
BRICKV_BINDINGS += bricklet_distance_ir.py
BRICKV_BINDINGS += bricklet_dual_relay.py
BRICKV_BINDINGS += bricklet_humidity.py
BRICKV_BINDINGS += bricklet_io16.py
BRICKV_BINDINGS += bricklet_io4.py
BRICKV_BINDINGS += bricklet_joystick.py
BRICKV_BINDINGS += bricklet_linear_poti.py
BRICKV_BINDINGS += bricklet_rotary_poti.py
BRICKV_BINDINGS += bricklet_temperature_ir.py
BRICKV_BINDINGS += bricklet_voltage.py
BRICKV_BINDINGS += ip_connection.py

BRICKV_PLUGINS_CORE += __init__.py

BRICKV_PLUGIN_AMBIENTLIGHT += __init__.py
BRICKV_PLUGIN_AMBIENTLIGHT += ambient_light.py

BRICKV_PLUGIN_ANALOGIN += __init__.py
BRICKV_PLUGIN_ANALOGIN += analog_in.py

BRICKV_PLUGIN_ANALOGOUT += __init__.py
BRICKV_PLUGIN_ANALOGOUT += analog_out.py

BRICKV_PLUGIN_CURRENT12 += __init__.py
BRICKV_PLUGIN_CURRENT12 += current12.py

BRICKV_PLUGIN_CURRENT25 += __init__.py
BRICKV_PLUGIN_CURRENT25 += current25.py

BRICKV_PLUGIN_DC += __init__.py
BRICKV_PLUGIN_DC += dc.py
BRICKV_PLUGIN_DC += speedometer.py
BRICKV_PLUGIN_DC += ui_dc.py

BRICKV_PLUGIN_DISTANCEIR += __init__.py
BRICKV_PLUGIN_DISTANCEIR += distance_ir.py

BRICKV_PLUGIN_DUALRELAY += __init__.py
BRICKV_PLUGIN_DUALRELAY += dual_relay.py
BRICKV_PLUGIN_DUALRELAY += ui_dual_relay.py

BRICKV_PLUGIN_HUMIDITY += __init__.py
BRICKV_PLUGIN_HUMIDITY += humidity.py

BRICKV_PLUGIN_IMU += __init__.py
BRICKV_PLUGIN_IMU += calibrate_accelerometer.py
BRICKV_PLUGIN_IMU += calibrate_gyroscope_bias.py
BRICKV_PLUGIN_IMU += calibrate_gyroscope_gain.py
BRICKV_PLUGIN_IMU += calibrate_import_export.py
BRICKV_PLUGIN_IMU += calibrate_magnetometer.py
BRICKV_PLUGIN_IMU += calibrate_temperature.py
BRICKV_PLUGIN_IMU += calibrate_window.py
BRICKV_PLUGIN_IMU += imu.py
BRICKV_PLUGIN_IMU += imu_gl_widget.py
BRICKV_PLUGIN_IMU += ui_calibrate.py
BRICKV_PLUGIN_IMU += ui_calibrate_accelerometer.py
BRICKV_PLUGIN_IMU += ui_calibrate_gyroscope_bias.py
BRICKV_PLUGIN_IMU += ui_calibrate_gyroscope_gain.py
BRICKV_PLUGIN_IMU += ui_calibrate_import_export.py
BRICKV_PLUGIN_IMU += ui_calibrate_magnetometer.py
BRICKV_PLUGIN_IMU += ui_calibrate_temperature.py
BRICKV_PLUGIN_IMU += ui_imu.py

BRICKV_PLUGIN_IO16 += __init__.py
BRICKV_PLUGIN_IO16 += io16.py
BRICKV_PLUGIN_IO16 += ui_io16.py

BRICKV_PLUGIN_IO4 += __init__.py
BRICKV_PLUGIN_IO4 += io4.py
BRICKV_PLUGIN_IO4 += ui_io4.py

BRICKV_PLUGIN_JOYSTICK += __init__.py
BRICKV_PLUGIN_JOYSTICK += joystick.py

BRICKV_PLUGIN_LCD16x2 += __init__.py
BRICKV_PLUGIN_LCD16x2 += lcd_16x2.py

BRICKV_PLUGIN_LCD20x4 += __init__.py
BRICKV_PLUGIN_LCD20x4 += lcd_20x4.py

BRICKV_PLUGIN_LINEARPOTI += __init__.py
BRICKV_PLUGIN_LINEARPOTI += linear_poti.py

BRICKV_PLUGIN_MASTER += __init__.py
BRICKV_PLUGIN_MASTER += master.py
BRICKV_PLUGIN_MASTER += ui_chibi.py
BRICKV_PLUGIN_MASTER += ui_extension_type.py
BRICKV_PLUGIN_MASTER += ui_master.py
BRICKV_PLUGIN_MASTER += ui_rs485.py

BRICKV_PLUGIN_PIEZOBUZZER += __init__.py
BRICKV_PLUGIN_PIEZOBUZZER += piezo_buzzer.py

BRICKV_PLUGIN_ROTARYPOTI += __init__.py
BRICKV_PLUGIN_ROTARYPOTI += rotary_poti.py

BRICKV_PLUGIN_SERVO += __init__.py
BRICKV_PLUGIN_SERVO += servo.py
BRICKV_PLUGIN_SERVO += ui_servo.py

BRICKV_PLUGIN_STEPPER += __init__.py
BRICKV_PLUGIN_STEPPER += speedometer.py
BRICKV_PLUGIN_STEPPER += stepper.py
BRICKV_PLUGIN_STEPPER += ui_stepper.py

BRICKV_PLUGIN_TEMPERATURE += __init__.py
BRICKV_PLUGIN_TEMPERATURE += temperature.py

BRICKV_PLUGIN_TEMPERATUREIR += __init__.py
BRICKV_PLUGIN_TEMPERATUREIR += temperature_ir.py

BRICKV_PLUGIN_VOLTAGE += __init__.py
BRICKV_PLUGIN_VOLTAGE += voltage.py

BRICKV_UI += $(addprefix ${BRICKV_CORE_SRCDIR}/, $(filter ui_%, ${BRICKV_CORE}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_AMBIENTLIGHT_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_AMBIENTLIGHT}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_ANALOGIN_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_ANALOGIN}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_ANALOGOUT_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_ANALOGOUT}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_CURRENT12_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_CURRENT12}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_CURRENT25_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_CURRENT25}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_DC_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_DC}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_DISTANCEIR_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_DISTANCEIR}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_DUALRELAY_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_DUALRELAY}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_HUMIDITY_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_HUMIDITY}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_IMU_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_IMU}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_IO16_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_IO16}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_IO4_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_IO4}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_JOYSTICK_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_JOYSTICK}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_LCD16x2_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_LCD16x2}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_LCD20x4_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_LCD20x4}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_LINEARPOTI_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_LINEARPOTI}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_MASTER_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_MASTER}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_PIEZOBUZZER_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_PIEZOBUZZER}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_ROTARYPOTI_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_ROTARYPOTI}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_SERVO_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_SERVO}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_STEPPER_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_STEPPER}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_TEMPERATURE_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_TEMPERATURE}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_TEMPERATUREIR_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_TEMPERATUREIR}))
BRICKV_UI += $(addprefix ${BRICKV_PLUGIN_VOLTAGE_SRCDIR}/, $(filter ui_%, ${BRICKV_PLUGIN_VOLTAGE}))

all: build

### BUILD ###

build: build-shell build-ui

build-shell: $(addsuffix .sh, ${BRICKV_SHELL})

build-ui: ${BRICKV_UI}

%.py:
	$(call quiet-command, pyuic4 -o $@ $(@D)/ui/$(patsubst ui_%,%,$(patsubst %py,%ui,$(@F))), "PYUIC	$@")

%.sh: src/%.sh.in
	$(call quiet-command, sed ${sed-rules} $< > $@, "SED	$@")

### INSTALL ###

install: build install-shell install-icon install-python

install-shell: $(addprefix ${DESTDIR}${BINDIR}/, ${BRICKV_SHELL}) install-dir-bindir

install-icon: $(addprefix ${DESTDIR}${BRICKV_DIR}/, ${BRICKV_ICON})

install-python: install-core install-pluginsystem install-plugins install-bindings

install-plugins: install-plugins-core install-plugin-ambientlight install-plugin-analogin install-plugin-analogout \
                 install-plugin-current12 install-plugin-current25 install-plugin-dc install-plugin-distanceir \
                 install-plugin-dualrelay install-plugin-humidity install-plugin-imu install-plugin-io16 \
                 install-plugin-io4 install-plugin-joystick install-plugin-lcd16x2 install-plugin-lcd20x4 \
                 install-plugin-linearpoti install-plugin-master install-plugin-piezobuzzer install-plugin-rotarypoti \
                 install-plugin-servo install-plugin-stepper install-plugin-temperature install-plugin-temperatureir \
                 install-plugin-voltage

install-core: $(addprefix ${DESTDIR}${BRICKV_DIR}/, ${BRICKV_CORE})

install-pluginsystem: $(addprefix ${DESTDIR}${BRICKV_PLUGINSYSTEM_DIR}/, ${BRICKV_PLUGINSYSTEM})

install-bindings: $(addprefix ${DESTDIR}${BRICKV_BINDINGS_DIR}/, ${BRICKV_BINDINGS})

install-plugins-core: ${addprefix ${DESTDIR}${BRICKV_PLUGINS_DIR}/, ${BRICKV_PLUGINS_CORE}}

install-plugin-ambientlight: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_AMBIENTLIGHT_DIR}/, ${BRICKV_PLUGIN_AMBIENTLIGHT})

install-plugin-analogin: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_ANALOGIN_DIR}/, ${BRICKV_PLUGIN_ANALOGIN})

install-plugin-analogout: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_ANALOGOUT_DIR}/, ${BRICKV_PLUGIN_ANALOGOUT})

install-plugin-current12: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_CURRENT12_DIR}/, ${BRICKV_PLUGIN_CURRENT12})

install-plugin-current25: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_CURRENT25_DIR}/, ${BRICKV_PLUGIN_CURRENT25})

install-plugin-dc: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_DC_DIR}/, ${BRICKV_PLUGIN_DC})

install-plugin-distanceir: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_DISTANCEIR_DIR}/, ${BRICKV_PLUGIN_DISTANCEIR})

install-plugin-dualrelay: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_DUALRELAY_DIR}/, ${BRICKV_PLUGIN_DUALRELAY})

install-plugin-humidity: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_HUMIDITY_DIR}/, ${BRICKV_PLUGIN_HUMIDITY})

install-plugin-imu: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_IMU_DIR}/, ${BRICKV_PLUGIN_IMU})

install-plugin-io16: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_IO16_DIR}/, ${BRICKV_PLUGIN_IO16})

install-plugin-io4: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_IO4_DIR}/, ${BRICKV_PLUGIN_IO4})

install-plugin-joystick: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_JOYSTICK_DIR}/, ${BRICKV_PLUGIN_JOYSTICK})

install-plugin-lcd16x2: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_LCD16x2_DIR}/, ${BRICKV_PLUGIN_LCD16x2})

install-plugin-lcd20x4: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_LCD20x4_DIR}/, ${BRICKV_PLUGIN_LCD20x4})

install-plugin-linearpoti: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_LINEARPOTI_DIR}/, ${BRICKV_PLUGIN_LINEARPOTI})

install-plugin-master: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_MASTER_DIR}/, ${BRICKV_PLUGIN_MASTER})

install-plugin-piezobuzzer: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_PIEZOBUZZER_DIR}/, ${BRICKV_PLUGIN_PIEZOBUZZER})

install-plugin-rotarypoti: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_ROTARYPOTI_DIR}/, ${BRICKV_PLUGIN_ROTARYPOTI})

install-plugin-servo: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_SERVO_DIR}/, ${BRICKV_PLUGIN_SERVO})

install-plugin-stepper: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_STEPPER_DIR}/, ${BRICKV_PLUGIN_STEPPER})

install-plugin-temperature: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_TEMPERATURE_DIR}/, ${BRICKV_PLUGIN_TEMPERATURE})

install-plugin-temperatureir: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_TEMPERATUREIR_DIR}/, ${BRICKV_PLUGIN_TEMPERATUREIR})

install-plugin-voltage: $(addprefix ${DESTDIR}${BRICKV_PLUGIN_VOLTAGE_DIR}/, ${BRICKV_PLUGIN_VOLTAGE})

${DESTDIR}${BINDIR}/%: %.sh install-dir-bindir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_DIR}/%: ${BRICKV_CORE_SRCDIR}/% install-dir-brickvdir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGINSYSTEM_DIR}/%: ${BRICKV_PLUGINSYSTEM_SRCDIR}/% install-dir-brickvpluginsystemdir install-dir-brickvpluginsdir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_BINDINGS_DIR}/%: ${BRICKV_BINDINGS_SRCDIR}/% install-dir-brickvbindingsdir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGINS_DIR}/%: ${BRICKV_PLUGINS_SRCDIR}/% install-dir-brickvpluginsdir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_AMBIENTLIGHT_DIR}/%: ${BRICKV_PLUGIN_AMBIENTLIGHT_SRCDIR}/% install-dir-brickvpluginambientlightdir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_ANALOGIN_DIR}/%: ${BRICKV_PLUGIN_ANALOGIN_SRCDIR}/% install-dir-brickvpluginanalogindir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_ANALOGOUT_DIR}/%: ${BRICKV_PLUGIN_ANALOGOUT_SRCDIR}/% install-dir-brickvpluginanalogoutdir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_CURRENT12_DIR}/%: ${BRICKV_PLUGIN_CURRENT12_SRCDIR}/% install-dir-brickvplugincurrent12dir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_CURRENT25_DIR}/%: ${BRICKV_PLUGIN_CURRENT25_SRCDIR}/% install-dir-brickvplugincurrent25dir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_DC_DIR}/%: ${BRICKV_PLUGIN_DC_SRCDIR}/% install-dir-brickvplugindcdir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_DISTANCEIR_DIR}/%: ${BRICKV_PLUGIN_DISTANCEIR_SRCDIR}/% install-dir-brickvplugindistanceirdir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_DUALRELAY_DIR}/%: ${BRICKV_PLUGIN_DUALRELAY_SRCDIR}/% install-dir-brickvplugindualrelaydir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_HUMIDITY_DIR}/%: ${BRICKV_PLUGIN_HUMIDITY_SRCDIR}/% install-dir-brickvpluginhumiditydir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_IMU_DIR}/%: ${BRICKV_PLUGIN_IMU_SRCDIR}/% install-dir-brickvpluginimudir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_IO16_DIR}/%: ${BRICKV_PLUGIN_IO16_SRCDIR}/% install-dir-brickvpluginio16dir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_IO4_DIR}/%: ${BRICKV_PLUGIN_IO4_SRCDIR}/% install-dir-brickvpluginio4dir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_JOYSTICK_DIR}/%: ${BRICKV_PLUGIN_JOYSTICK_SRCDIR}/% install-dir-brickvpluginjoystickdir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_LCD16x2_DIR}/%: ${BRICKV_PLUGIN_LCD16x2_SRCDIR}/% install-dir-brickvpluginlcd16x2dir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_LCD20x4_DIR}/%: ${BRICKV_PLUGIN_LCD20x4_SRCDIR}/% install-dir-brickvpluginlcd20x4dir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_LINEARPOTI_DIR}/%: ${BRICKV_PLUGIN_LINEARPOTI_SRCDIR}/% install-dir-brickvpluginlinearpotidir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_MASTER_DIR}/%: ${BRICKV_PLUGIN_MASTER_SRCDIR}/% install-dir-brickvpluginmasterdir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_PIEZOBUZZER_DIR}/%: ${BRICKV_PLUGIN_PIEZOBUZZER_SRCDIR}/% install-dir-brickvpluginpiezobuzzerdir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_ROTARYPOTI_DIR}/%: ${BRICKV_PLUGIN_ROTARYPOTI_SRCDIR}/% install-dir-brickvpluginrotarypotidir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_SERVO_DIR}/%: ${BRICKV_PLUGIN_SERVO_SRCDIR}/% install-dir-brickvpluginservodir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_STEPPER_DIR}/%: ${BRICKV_PLUGIN_STEPPER_SRCDIR}/% install-dir-brickvpluginstepperdir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_TEMPERATURE_DIR}/%: ${BRICKV_PLUGIN_TEMPERATURE_SRCDIR}/% install-dir-brickvplugintemperaturedir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_TEMPERATUREIR_DIR}/%: ${BRICKV_PLUGIN_TEMPERATUREIR_SRCDIR}/% install-dir-brickvplugintemperatureirdir
	$(call quiet-install, 755, $<, $@)

${DESTDIR}${BRICKV_PLUGIN_VOLTAGE_DIR}/%: ${BRICKV_PLUGIN_VOLTAGE_SRCDIR}/% install-dir-brickvpluginvoltagedir
	$(call quiet-install, 755, $<, $@)

install-dir-bindir:
	$(call quiet-installdir, 755, ${DESTDIR}${BINDIR})

install-dir-brickvdir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_DIR})

install-dir-brickvpluginsystemdir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGINSYSTEM_DIR})

install-dir-brickvpluginsdir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGINS_DIR})

install-dir-brickvbindingsdir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_BINDINGS_DIR})

install-dir-brickvpluginambientlightdir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_AMBIENTLIGHT_DIR})

install-dir-brickvpluginanalogindir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_ANALOGIN_DIR})

install-dir-brickvpluginanalogoutdir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_ANALOGOUT_DIR})

install-dir-brickvplugincurrent12dir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_CURRENT12_DIR})

install-dir-brickvplugincurrent25dir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_CURRENT25_DIR})

install-dir-brickvplugindcdir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_DC_DIR})

install-dir-brickvplugindistanceirdir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_DISTANCEIR_DIR})

install-dir-brickvplugindualrelaydir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_DUALRELAY_DIR})

install-dir-brickvpluginhumiditydir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_HUMIDITY_DIR})

install-dir-brickvpluginimudir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_IMU_DIR})

install-dir-brickvpluginio16dir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_IO16_DIR})

install-dir-brickvpluginio4dir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_IO4_DIR})

install-dir-brickvpluginjoystickdir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_JOYSTICK_DIR})

install-dir-brickvpluginlcd16x2dir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_LCD16x2_DIR})

install-dir-brickvpluginlcd20x4dir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_LCD20x4_DIR})

install-dir-brickvpluginlinearpotidir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_LINEARPOTI_DIR})

install-dir-brickvpluginmasterdir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_MASTER_DIR})

install-dir-brickvpluginpiezobuzzerdir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_PIEZOBUZZER_DIR})

install-dir-brickvpluginrotarypotidir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_ROTARYPOTI_DIR})

install-dir-brickvpluginservodir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_SERVO_DIR})

install-dir-brickvpluginstepperdir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_STEPPER_DIR})

install-dir-brickvplugintemperaturedir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_TEMPERATURE_DIR})

install-dir-brickvplugintemperatureirdir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_TEMPERATUREIR_DIR})

install-dir-brickvpluginvoltagedir:
	$(call quiet-installdir, 755, ${DESTDIR}${BRICKV_PLUGIN_VOLTAGE_DIR})

clean:
	$(call quiet-command, rm -f $(addsuffix .sh, ${BRICKV_SHELL}), "RM	$(addsuffix .sh, ${BRICKV_SHELL})")
	$(call quiet-command, rm -f ${BRICKV_UI}, "RM	${BRICKV_UI}")
