import serial
from lab_instruments.classes.serial_communication import SerialInstrument, CommunicationException
from enum import Enum


"""
https://www.cooltronic.ch/
Class to use Cooltronic hardware:
- TC0806 temperature controller
"""


class CoolTronicException(Exception):
    pass


class CoolTronicMode(Enum):
    ON = 0
    OFF = 64
    SINE = 128
    DUAL = 192

    @staticmethod
    def get_all() -> list:
        return [CoolTronicMode.ON, CoolTronicMode.OFF, CoolTronicMode.SINE, CoolTronicMode.DUAL]

    @staticmethod
    def get_all_values() -> list:
        return [CoolTronicMode.ON.value, CoolTronicMode.OFF.value, CoolTronicMode.SINE.value, CoolTronicMode.DUALMode.value]

    @staticmethod
    def str_to_mode(mode_str: str):
        for mode in CoolTronicMode.get_all():
            if mode.value == mode_str:
                return mode


class TC0806(SerialInstrument):
    def __init__(self, com_port, log=None):
        super().__init__(com_port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO, log=log)
        self.terminator = '\x15'
        # self.logger.setLevel(logging.DEBUG)

    def _on_open(self):
        pass

    def _on_close(self):
        pass

    def _pre_write(self):
        pass

    def _post_write(self):
        self.wait_after_command()
        self._check_message_confirmation()

    def _pre_read(self):
        pass

    def _post_read(self, msg_read: str):
        if len(msg_read) <= 1:
            response, response_char = msg_read, msg_read
        else:
            response, response_char = msg_read[:-1], msg_read[-1]
        if response_char != self.terminator:
            raise CommunicationException('POST READ: WRONG response character' + response_char)
        return response

    def write(self, msg: str):
        if not msg.endswith(self.terminator):
            msg = msg + self.terminator
        if not msg.startswith('*'):
            msg = '*' + msg
        self._pre_write()
        self.logger.debug('WRITE: ' + msg)
        for char in msg:
            self.ser.write(char.encode())
            if char == '*':
                continue
            read_char = self.ser.read(1).decode()
            if read_char != char:
                raise CommunicationException
        self._post_write()

    def _construct_message(self, command: str, parameter: int, value: int):
        if command not in 'druw' or len(command) > 1:
            raise CommunicationException('WARNING: wrong command. ' + command)
        if parameter > 65535:
            raise CommunicationException('WARNING: parameter exceeding 65535.')
        if value > 65535:
            raise CommunicationException('WARNING: value exceeding 65535.')
        msg = '_'.join(['A', command, str(parameter), str(value)])
        return msg

    def _check_message_confirmation(self):
        response_char = self.ser.read(1).decode()
        if response_char == '.':
            self.logger.debug('Acknowledge: OK')
        elif response_char == '?':
            raise CommunicationException('WARNING: unknown / incomplete command sequence')
        elif response_char == '#':
            raise CommunicationException('WARNING: Internal fault')
        else:
            raise CommunicationException('ERROR: unkown return character')
        
    def get_device_type(self):
        response = self.write_and_read_all(self._construct_message('r', 200, 0))
        if response == '1':
            device = 'TC0806'
        elif response == '0':
            device = 'unknown device'
        else:
            raise CoolTronicException
        return device

    def get_error_state(self):
        response = self.write_and_read_all(self._construct_message('r', 202, 0))
        return response

    def get_firmware(self):
        response = self.write_and_read_all(self._construct_message('r', 106, 0))
        return response

    def get_pid(self):
        p = self.write_and_read_all(self._construct_message('r', 103, 0))
        i = self.write_and_read_all(self._construct_message('r', 104, 0))
        d = self.write_and_read_all(self._construct_message('r', 105, 0))
        return p, i, d

    def get_sensor_value(self, sensor: int):
        if sensor not in [1, 2, 3]:
            raise CoolTronicException('Invalid sensor.')
        param = 120 + sensor - 1
        response = self.write_and_read_all(self._construct_message('r', param, 0))
        return response

    def get_temperature_ramp(self):
        response = self.write_and_read_all(self._construct_message('r', 12, 0))
        return response

    def set_temperature_ramp(self, value: float):
        if not 0 <= value <= 9.9:
            raise CoolTronicException('Value outside range.')
        value = int(value * 10)
        self.write(self._construct_message('w', 12, value))

    def get_temperature(self, value_number: int):
        if value_number not in [1, 2]:
            raise CoolTronicException('Invalid temperature number.')
        value_number -= value_number
        response = self.write_and_read_all(self._construct_message('r', value_number, 0))
        return float(response) / 10

    def set_temperature(self, value_number: int, value: float):
        if value_number not in [1, 2]:
            raise CoolTronicException('Invalid temperature number.')
        value_number -= value_number
        value = int(value * 10)
        self.write(self._construct_message('w', value_number, value))

    def get_cfg(self):
        response = self.write_and_read_all(self._construct_message('r', 5, 0))
        return response

    def set_cfg(self, mode: CoolTronicMode, alarm_output=False):
        value = mode.value
        if alarm_output:
            value += 16
        self.write(self._construct_message('w', 5, value))

    def get_temperature_offset(self):
        response = self.write_and_read_all(self._construct_message('r', 11, 0))
        return float(response) / 10

    def set_temperature_offset(self, value):
        value = int(value * 10)
        self.write(self._construct_message('w', 11, value))


if __name__ == '__main__':
    cool = TC0806('COM10')
    cool.open()
    todo = 'get_error'

    if todo == 'get_device':
        device = cool.get_device_type()
        print('DEVICE:', device)
    elif todo == 'get_error':
        error_state = cool.get_error_state()
        print('ERRORSTATE:', error_state)
    elif todo == 'information':
        print(cool.get_firmware())
        print(cool.get_pid())
        print(cool.get_sensor_value(1))
        print(cool.get_sensor_value(2))
        print(cool.get_sensor_value(3))
        print(cool.get_temperature_ramp())
    elif todo == 'temp':
        print(cool.get_temperature(1))
        cool.set_temperature_ramp(5.7)
        cool.wait_after_command()
        cool.set_temperature(1, 35)
        print(cool.get_temperature(1))
    elif todo == 'on':
        cool.set_cfg(CoolTronicMode.OFF)
    elif todo == 'sensor':
        while True:
            print(cool.get_sensor_value(1))

    cool.close()


"""
Synchronization *
Command (Master only) <address> _ <command> _ <parameter> _ <value>§
Acknowledge (Slave only) . / ? / #
Response (Slave only) <value> §
The several components are defined as follows:
address A..Z (at present only A)
command a..z (used: d, r, u, w)
parameter 0..65535
(no leading zeros, negative figures will be transferred as
positive figures, and then accordingly interpreted
“typecasted”)
value 0..65535
(no leading zeros, negative figures will be transferred as
positive figures, and then interpreted accordingly
“typecast”)

* Reset communication (from Master to re-synchronize)
A..Z Address
a..z commands
_ (underline) is separation character between values
§ End of the message (hex 0x15 or decimal 21 !)
. acknowledge “OK”
? acknowledge “unknown / incomplete command sequence”
# Internal fault
"""