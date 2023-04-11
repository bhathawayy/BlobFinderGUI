import serial
import time
import re
from argparse import ArgumentParser
import statistics
from lab_instruments.classes.serial_communication import SerialInstrument
from lab_instruments.classes.visa_communication import VISAInstrument
from lab_instruments.classes.Exceptions import CommunicationException, InstrumentException
import logging


class TC200(SerialInstrument):
    def __init__(self, com_port: str, log: logging._loggerClass = None):
        super().__init__(com_port=com_port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, xonxoff=False, log=log)
        self._dataset = []
        self.terminator = '\r'
        self.terminator_write = '\r'
        self.terminator_read = b'> '

    def _on_open(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def _on_close(self):
        pass

    def _pre_write(self, msg, *args):
        self.terminator = self.terminator_write

    def _post_write(self, msg, *args):
        pass

    def _pre_read(self):
        self.terminator = self.terminator_read

    def _post_read(self, msg_read: str):
        bytemsg = msg_read.encode()
        msg = self._cleanup_byte_string(bytemsg)
        return msg

    def write_and_read_until(self, cmd):
        self.write(cmd)
        msg = self.read_until()
        cmd, response = self._get_cmd_and_response(cmd, msg)
        self.logger.info('CMD: ' + cmd)
        self.logger.info('RESPONSE: ' + response)
        return cmd, response

    def _cleanup_byte_string(self, bytemsg):
        self.logger.debug('BYTEMESSAGE: ' + bytemsg)
        msg = bytemsg.replace(b'\r', b'\r\n').decode('utf-8')
        msg = msg.rstrip('> ')
        return msg

    def _toggle_enable(self):
        self.write_and_read_until('ens')

    def get_enabled_state(self):
        enabled_state = bool(self.get_stat().get('Disabled=0_Enabled=1'))
        return enabled_state

    def set_enable_state(self, new_state):
        if new_state == self.get_enabled_state():
            pass
        else:
            self._toggle_enable()

    def set_temperature(self, temperature):
        self.write_and_read_until('tset=' + str(temperature))

    def get_set_temperature(self):
        cmd, response = self.write_and_read_until('tset?')
        match = re.search("[0-9]+.[0-9]+", response)
        if match:
            value = float(match.group(0))
        else:
            value = -1
        return value

    def get_actual_temperature(self):
        cmd, response = self.write_and_read_until('tact?')
        match = re.search("[0-9]+.[0-9]+", response)
        if match:
            value = float(match.group(0))
        else:
            value = -1
        return value

    def get_stat(self):
        cmd, response = self.write_and_read_until('stat?')
        match = re.search("[0-9]+", response)
        if match:
            value = int(match.group(0))
        else:
            value = -1

        status_dict = {'Disabled=0_Enabled=1': 0b00000001,
                       'NormalMode=0_CycleMode=1': 0b00000010,
                       'TH10K=0_PTC100=1': 0b00000100,
                       'TH10K=0_PTC1000=1': 0b00001000,
                       'DegreesK=0_DegreesC=1': 0b00010000,
                       'DegreesK=0_DegreesF=1': 0b00100000,
                       'NoSensorAlarm=0_SensorAlarm=1': 0b01000000,
                       'CycleNotPaused=0_CyclePaused=1': 0b10000000,
                       }

        return_dict = dict()
        for key in status_dict.keys():
            return_dict.update({key: self.check_status_byte(value, status_dict.get(key))})
        return return_dict

    def check_status_byte(self, code, status_code):
        if code & status_code:
            return 1
        else:
            return 0

    def get_available_commands(self):
        return self.write_and_read_until('commands?')

    def get_id(self):
        return self.write_and_read_until('id?')

    def get_identification(self):
        return self.write_and_read_until('*idn?')

    def get_config(self):
        msg_read = self.write_and_read_until('config?')
        msg_list = [data for elem in msg_read for data in elem.split('\r\n')]
        return msg_list

    def _get_cmd_and_response(self, cmd_sent, msg):
        if cmd_sent in msg.splitlines()[0]:
            command = msg.splitlines()[0]
            response = '\r\n'.join(msg.splitlines()[1:])
        else:
            command = 'Command not returned.'
            response = '\r\n'.join(msg.splitlines()[0:])
        return command, response

    def check_set_temp_reached(self, limit=1, use_dataset=False):
        temp_set = self.get_set_temperature()
        if use_dataset:
            status = abs(statistics.mean(self._dataset) - temp_set) <= limit
        else:
            temp_act = self.get_actual_temperature()
            status = abs(temp_act - temp_set) <= limit
        return status

    def check_max_temp_limit_reached(self, upper_limit, use_dataset=False):
        if use_dataset:
            status = any(i >= upper_limit for i in self._dataset)
        else:
            temp_act = self.get_actual_temperature()
            status = temp_act > upper_limit
        return status

    def signal_is_stable(self, stdev_limit, mean_limit):
        stable = False
        data_1 = self._dataset[:int(len(self._dataset) / 2)]
        data_2 = self._dataset[int(len(self._dataset) / 2):]
        stdev_1 = statistics.stdev(data_1)
        stdev_2 = statistics.stdev(data_1)
        mean_data_1 = statistics.mean(data_1)
        mean_data_2 = statistics.mean(data_2)
        if stdev_1 <= stdev_limit and stdev_2 <= stdev_limit and abs(mean_data_1 - mean_data_2) <= mean_limit:
            stable = True
        return stable

    def update_dataset(self, number_of_samples=10, wait=0.5):
        self._dataset = []
        for n in range(0, number_of_samples):
            val = self.get_actual_temperature()
            self._dataset.append(val)
            time.sleep(wait)

    def get_dataset(self):
        return self._dataset


class DC4104(SerialInstrument):
    def __init__(self, com_port: str, log: logging._loggerClass = None):
        super().__init__(com_port=com_port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, xonxoff=False, log=log)
        # self.seconds_to_wait = 1
        pass

    def _on_close(self):
        for i in range(4):
            try:
                self.set_led(i, 0)
            except Exception:
                self.logger.info('DC4104 Channel does not exist: ' + str(i))
        pass

    def get_operation_mode(self):
        msg = ' '.join(['M?'])
        reply = self.write_and_read_until(msg)
        return reply

    def set_operation_mode(self, mode):
        if mode not in [0, 1, 2]:
            raise InstrumentException('Wrong mode value')
        msg = ' '.join(['M', str(mode)])
        self.write(msg)
        self.wait_after_command(1)
        self.logger.info('Operation mode set to: ' + str(mode))

    def set_constant_current(self, channel: int, current_mA: float):
        self._check_channel(channel, all_channel_option=True)
        self._check_current_limit(current_mA)
        msg = ' '.join(['CC', str(channel), str(current_mA)])
        self.write(msg)
        self.logger.info('Constant current on channel ' + str(channel) + ' set to: ' + str(current_mA))

    def get_constant_current(self, channel: int):
        self._check_channel(channel)
        msg = ' '.join(['CC', str(channel)])
        reply = self.write_and_read_until(msg)
        self.logger.info('Constant current on channel ' + str(channel) + ' is: ' + str(reply))
        return reply

    def set_current_limit(self, channel: int, current_mA: float):
        self._check_channel(channel, all_channel_option=True)
        self._check_current_limit(current_mA)
        msg = ' '.join(['L', str(channel), str(current_mA)])
        self.write(msg)
        self.logger.info('Constant current limit on channel ' + str(channel) + ' set to: ' + str(current_mA))
        pass

    def get_current_limit(self, channel: int):
        self._check_channel(channel)
        msg = ' '.join(['L?', str(channel)])
        reply = self.write_and_read_until(msg)
        self.logger.info('Constant current limit on channel ' + str(channel) + ' is: ' + str(reply))
        return reply

    def set_brightness(self, channel: int, brightness: float):
        self._check_channel(channel, all_channel_option=True)
        self._check_brightness(brightness)
        msg = ' '.join(['BP', str(channel), str(brightness)])
        self.write(msg)
        self.logger.info('Brightness on channel ' + str(channel) + ' set to: ' + str(brightness))
        pass

    def get_brightness(self, channel: int):
        self._check_channel(channel)
        msg = ' '.join(['BP?', str(channel)])
        reply = self.write_and_read_until(msg)
        self.logger.info('Brightness on channel ' + str(channel) + ' is: ' + str(reply))
        return reply

    def set_led(self, channel: int, led_on_off: int):
        self._check_channel(channel, all_channel_option=True)
        if led_on_off not in [0, 1]:
            raise InstrumentException('Wrong led status.')
        msg = ' '.join(['O', str(channel), str(led_on_off)])
        self.write(msg)
        self.logger.info('LED status on channel ' + str(channel) + ' set to: ' + str(led_on_off))
        pass

    def get_led(self, channel: int):
        self._check_channel(channel)
        msg = ' '.join(['O?', str(channel)])
        reply = int(self.write_and_read_until(msg))
        self.logger.info('LED status on channel ' + str(channel) + ' is: ' + str(reply))
        return reply

    def set_led_lock(self, channel: int, lock_unlock: int):
        self._check_channel(channel, all_channel_option=True)
        if lock_unlock not in [0, 1]:
            raise InstrumentException('Wrong lock status.')
        msg = ' '.join(['A', str(channel), str(lock_unlock)])
        self.write(msg)
        self.logger.info('LED lock on channel ' + str(channel) + ' set to: ' + str(lock_unlock))
        pass

    def get_led_lock(self, channel: int):
        self._check_channel(channel)
        msg = ' '.join(['A?', str(channel)])
        reply = self.write_and_read_until(msg)
        return reply

    def set_display_brightness(self, brightness: float):
        self._check_brightness(brightness)
        msg = ' '.join(['B', str(brightness)])
        self.write(msg)
        self.logger.info('Display brightness set to: ' + str(brightness))
        pass

    def get_display_brightness(self):
        msg = ' '.join(['B?'])
        reply = self.write_and_read_until(msg)
        self.logger.debug('Display brightness is: ' + str(reply))
        return reply

    def get_status_register(self):
        msg = ' '.join(['R?'])
        reply = self.write_and_read_until(msg)
        self.logger.debug('Stgatus register: ' + str(reply))
        return reply

    def get_device_name(self):
        msg = ' '.join(['N?'])
        reply = self.write_and_read_until(msg)
        self.logger.debug('Device name: ' + str(reply))
        return reply

    def get_device_serial_number(self):
        msg = ' '.join(['S?'])
        reply = self.write_and_read_until(msg)
        self.logger.debug('Device serial number: ' + str(reply))
        return reply

    def set_maximum_current_limit(self, channel: int, current_mA: float):
        self._check_channel(channel, all_channel_option=True)
        self._check_current_limit(current_mA)
        msg = ' '.join(['ML', str(channel), str(current_mA)])
        self.write(msg)
        self.logger.info('Maximum current limit on channel ' + str(channel) + ' set to: ' + str(current_mA))
        pass

    def get_maximum_current_limit(self, channel: int):
        self._check_channel(channel)
        msg = ' '.join(['ML?', str(channel)])
        reply = self.write_and_read_until(msg)
        self.logger.debug('Maximum current limit on channel ' + str(channel) + ' is: ' + str(reply))
        return reply

    def get_firmware_version(self):
        msg = ' '.join(['V?'])
        reply = self.write_and_read_until(msg)
        self.logger.debug('Firmware version: ' + str(reply))
        return reply

    def get_manufacturer_name(self):
        msg = ' '.join(['H?'])
        reply = self.write_and_read_until(msg)
        self.logger.debug('Manufacturer: ' + str(reply))
        return reply

    def get_error_code(self):
        msg = ' '.join(['E?'])
        reply = self.write_and_read_until(msg)
        self.logger.debug('Errorcode: ' + str(reply))
        return reply

    def get_led_serial_number(self, channel: int):
        self._check_channel(channel)
        msg = ' '.join(['HS?', str(channel)])
        reply = self.write_and_read_until(msg)
        self.logger.debug('LED serial number on channel ' + str(channel) + ' is: ' + str(reply))
        return reply

    def get_led_name(self, channel: int):
        self._check_channel(channel)
        msg = ' '.join(['HN?', str(channel)])
        reply = self.write_and_read_until(msg)
        self.logger.debug('LED name on channel ' + str(channel) + ' is: ' + str(reply))
        return reply

    def get_calibration_date(self):
        msg = ' '.join(['CD?'])
        reply = self.write_and_read_until(msg)
        self.logger.debug('Calibration date is: ' + str(reply))
        return reply

    def get_led_wavelength(self, channel: int):
        self._check_channel(channel)
        msg = ' '.join(['WL?', str(channel)])
        reply = float(self.write_and_read_until(msg))
        self.logger.debug('LED wavelength on channel ' + str(channel) + ' is: ' + str(reply))
        return reply

    def get_led_forward_voltage(self, channel: int):
        self._check_channel(channel)
        msg = ' '.join(['FB?', str(channel)])
        reply = self.write_and_read_until(msg)
        self.logger.debug('LED forward voltage on channel ' + str(channel) + ' is: ' + str(reply))
        return reply

    def set_safety_mode(self, safety_mode: int):
        if safety_mode not in [0, 1]:
            raise InstrumentException('Wrong safety mode.')
        msg = ' '.join(['SM', str(safety_mode)])
        self.write(msg)
        self.logger.info('Safety mode set to: ' + str(safety_mode))
        pass

    def get_safety_mode(self):
        msg = ' '.join(['SM?'])
        reply = self.write_and_read_until(msg)
        self.logger.debug('Safety mode is: ' + str(reply))
        return reply

    @staticmethod
    def _check_channel(channel, all_channel_option=False):
        channel_list = [0, 1, 2, 3]
        if all_channel_option:
            channel_list.insert(0, -1)
        if channel not in channel_list:
            raise InstrumentException('Wrong channel value.')

    @staticmethod
    def _check_current_limit(current_mA):
        if not 0 <= current_mA <= 1000:
            raise InstrumentException('Current outside spec.')

    @staticmethod
    def _check_brightness(brightness: float):
        if not 0 <= brightness <= 100:
            raise InstrumentException('Brightness outside spec.')


class TL_ITC4005(VISAInstrument):
    def __init__(self, serial_number: str, log: logging._loggerClass = None):
        super().__init__(instr_description=serial_number, log=log)

    def get_configuration(self):
        self.logger.info("Config ")
        self.logger.info(str(self.resource.query("CONF?")))

    def read(self):
        self.logger.info(str("Read for %s" % (self.resource.query("CONF?"),)))
        self.logger.info(str(self.resource.query("READ?")))

    def abort_measurement(self):
        self.logger.info("Abort ")
        self.logger.info(str(self.resource.write("ABORT")))

    def ld_off(self):
        self.logger.info(str(self.resource.write("OUTPut:STATe OFF")))

    def ld_on(self):
        self.resource.write("OUTPut:STATe ON")

    def get_optical_power(self):
        return self.resource.query("MEASure:POWer2?")

    def get_voltage(self):
        return self.resource.query("MEASure:VOLTage?")

    def get_current(self):
        return self.resource.query("MEASure?")

    def get_laser_drive_mode(self):
        return self.resource.query("SOURce:FUNCtion:MODE?")

    def set_laser_drive_mode_current(self):
        return self.resource.write("SOURce:FUNCtion:MODE CURRENT")

    def set_laser_drive_mode_power(self):
        return self.resource.write("SOURce:FUNCtion:MODE POWER")

    def get_laser_drive_current(self):
        return self.resource.query("SOURce:CURRent?")

    def set_laser_drive_current(self, current_val):
        return self.resource.write("SOURce:CURRent %f" % (current_val,))

    def get_laser_drive_power(self):
        return self.resource.query("SOURce:POWER?")

    def set_laser_drive_power(self, power_val):
        return self.resource.write("SOURce:POWER %f" % (power_val,))

    def get_laser_temperature(self):
        return self.resource.query("MEASure:TEMPerature?")

    def all_measurement(self):
        self.logger.info(str("Temp %s" % (self.resource.query("MEASure:TEMPerature?"),)))
        self.logger.info(str("Current %s" % (self.resource.query("MEASure?"),)))
        self.logger.info(str("Voltage %s" % (self.resource.query("MEASure:VOLTage?"),)))
        self.logger.info(str("Optical PD Power %s" % (self.resource.query("MEASure:POWer2?"),)))

    def bip(self):
        for i in range(0, 5):
            self.resource.write("SYSTem:BEEPer")
            time.sleep(0.2)

    def close(self):
        self.logger.info(str("Session ID %s" % (self.resource.session)))
        self.resource.close()
        self.rm.close()


class PowerMeter(VISAInstrument):
    def __init__(self, serial_number: str, wavelength_nm: int, count: int = 1, log: logging._loggerClass = None):
        super().__init__(instr_description=serial_number, log=log)
        self.initialized = False
        self.serial_number = serial_number
        self.wavelength_nm = wavelength_nm
        self.power_unit = 'w'
        self.count = count
        self.zero_relative_power = 0
        self._max_range = 0
        self._min_range = 0

    def open(self):
        super().open()
        self._get_min_max_range()

    def set_wavelength_nm(self, wavelength_nm: int):
        if not self.initialized:
            raise InstrumentException("Should be initialized before using this method")
        self.write('sense:correction:wavelength ' + str(self.wavelength_nm))
        self.wavelength_nm = wavelength_nm
        pass

    def get_wavelength_nm(self) -> int:
        return self.wavelength_nm

    def get_power_unit(self) -> str:
        return self.power_unit

    def get_serial_number(self) -> str:
        return self.serial_number

    def set_relative_zero(self):
        """
        Make the current power as a relative zero
        :return:
        """
        self.write('sense:correction:collect:zero:initiate')
        time.sleep(2)  # allow to the command to be active
        # update the value
        self.get_relative_zero()
        pass

    def get_relative_zero(self):
        self.zero_relative_power = float(self.query('sense:correction:collect:zero:magnitude?'))
        return self.zero_relative_power

    def set_average_count(self, count: int):
        """
        The number of samples for one data output (1 sample takes approx. 3ms)
        :param count: int
        :return:
        """
        if not self.initialized:
            raise InstrumentException("Should be initialized before using this method")
        self.write('sense:average:count ' + str(self.count))
        self.count = count

    def get_average_count(self) -> int:
        reply = self.query('sense:average:count ?')
        return reply

    def get_approx_average_time_ms(self) -> int:
        return self.count * 3  # milliseconds

    def initialize(self):
        # initiate a default config
        commands = [
            'configure:power',
            'sense:correction:wavelength ' + str(self.wavelength_nm),
            'sense:power:unit ' + str(self.power_unit),
            'sense:average:count ' + str(self.count),
            'initiate'
        ]
        for cmd in commands:
            self.write(cmd)
        # read the zero relative
        self.get_relative_zero()
        self.initialized = True
        self.logger.info('Ressource: ' + str(self.resource_name) + ' initialized.')
        pass

    def get_relative_power(self) -> float:
        if not self.initialized:
            raise InstrumentException("Should be initialized before using this method")
        relative_power = float(self.query('read?'))
        self.logger.info('Relative Power: ' + str(relative_power))
        return relative_power

    def get_absolute_power(self) -> float:
        absolute_power = self.zero_relative_power + self.get_relative_power()
        self.logger.info('Absolute Power: ' + str(absolute_power))
        return absolute_power

    def switch_auto_range(self, auto=True):
        self.write('sense:pow:rang:auto ' + str(int(auto)))
        self.logger.info('Range set to: ' + str(self.get_range()))

    def is_range_auto(self):
        auto = bool(int(self.query('sense:pow:rang:auto?').rstrip()))
        self.logger.debug('Range auto is: ' + str(auto))
        return auto

    def get_range(self):
        range = self.query('sense:pow:rang?').rstrip()
        return range

    def _get_min_max_range(self):
        self._min_range =  float(self.query('sense:pow:rang:upp? min').rstrip())
        self._max_range = float(self.query('sense:pow:rang:upp? max').rstrip())

    def set_range(self, power_to_measure: float):
        if power_to_measure < self._min_range or power_to_measure > self._max_range:
            raise ValueError('Power outside range bounds: ' + str(power_to_measure))
        self.write('sense:pow:rang:upp ' + str(power_to_measure))


def test_thorlabs_PM():
    # serial_number = input('Please enter the serial number: ')
    serial_number = '16111417'
    serial_number = '1907037'
    pm = PowerMeter(serial_number, 690)
    pm.open()
    pm.initialize()
    # print(pm.cmd_time)
    # power = pm.get_absolute_power()
    # print(pm.cmd_time)
    # pm.set_relative_zero()
    # print(pm.cmd_time)
    # pm.get_relative_zero()
    # print(pm.cmd_time)
    # zero = pm.get_relative_zero()
    # print(pm.cmd_time)
    # power = pm.get_relative_power()
    # print(pm.cmd_time)
    # power = pm.get_absolute_power()
    # print(pm.cmd_time)
    # pm.write('sense:pow:rang:auto 1')
    pm.switch_auto_range(True)
    print('#######')
    print('AUTO', pm.is_range_auto())
    print('RANGE', pm.get_range())
    print('MIN', pm._min_range)
    print('MAX', pm._max_range)
    print('#######')
    # print(pm.query('syst:sense:idn?').rstrip())
    pm.switch_auto_range(False)
    # pm.write('sense:pow:rang:upp min')
    power_val = 0.1
    pm.set_range(power_val)
    print('#######')
    print('AUTO', pm.is_range_auto())
    print('RANGE', pm.get_range())
    print('MIN', pm._min_range)
    print('MAX', pm._max_range)
    print('#######')
    pm.close()


# if __name__ == '__main__':
#     test_thorlabs_PM()
