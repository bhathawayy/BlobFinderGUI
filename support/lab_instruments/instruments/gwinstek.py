import serial
import time
from argparse import ArgumentParser
import numpy as np
from lab_instruments.classes.serial_communication import SerialInstrument

"""
https://www.gwinstek.com/en-global
Class to use GWInstek hardware:
- AFG-2225 Function generator
"""


def create_parser():
    p = ArgumentParser()
    p.add_argument('--port',
                   type=str,
                   help='Specify the COM port.',
                   default='COM12',
                   required=False)
    return p


class AFG2225(SerialInstrument):
    def __init__(self, com_port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, xonxoff=True, log=None):
        super().__init__(com_port,
                         baudrate=baudrate,
                         bytesize=bytesize,
                         parity=parity,
                         stopbits=stopbits,
                         xonxoff=xonxoff,
                         log=log)
        self._amplitude = None
        self._channel = None
        self._freq = None
        self._amp_type = None
        self.set_amp_type()
        self._signal_offset = None
        self.set_signal_offset()
        self._display_state = True
        self._check_display_state = True
        self.terminator = '\r'

    def _pre_write(self, msg, *args):
        pass

    def _post_write(self, msg, *args):
        self.wait_on_display_on()

    def _pre_read(self):
        pass

    def _post_read(self, msg_read: str):
        return msg_read

    def _on_open(self):
        pass

    def _on_close(self):
        self.display_state(True)
        self.toggle_output(False)
        self.toggle_local()

    # Device specific commands

    def wait_on_display_on(self):
        if self._display_state and self._check_display_state:
            self.logger.debug('Wait extra time for Hardware to complete the action.')
            self.wait_after_command(1)

    def set_channel(self, channel:int):
        self._channel = str(channel)
        self.logger.info('Channel set to: ' + str(channel))

    def get_channel(self):
        return int(self._channel)
        
    def set_frequency(self, freq:str):
        freq = freq.upper()
        self._freq = freq
        self.logger.info('Frequency set to: ' + str(freq))

    def set_amplitude(self, amplitude:float):
        self._amplitude = str(amplitude)
        self.logger.info('Amplitude set to: ' + str(amplitude))

    def set_amp_type(self, amp_type='VPP'):
        if amp_type not in ['VPP', 'VRMS', 'DBM']:
            self.logger.warning('Unit description wrong')
            return
        self._amp_type = amp_type
        self.logger.info('Amplitude type set to: ' + str(amp_type))

    def set_signal_offset(self, offset='DEF'):
        if offset not in ['DEF']:
            self.logger.warning('Unit description wrong')
            return
        self._signal_offset = offset
        self.logger.info('Signal offset set to: ' + str(offset))

    def get_identification(self):
        return self.write_and_read('*idn?')

    def toggle_remote(self):
        self.write('SYST:REM')
        self.logger.info('Remote toggled.')

    def toggle_local(self):
        self.write('SYST:LOC')
        self.logger.info('Local toggled.')

    def display_state(self, display_state: bool):
        self.write('DISPlay ' + self._bool_to_display(display_state))
        self._display_state = display_state
        self.wait_after_command(1)
        self.logger.info('Display state set to: ' + str(display_state))

    def square_wave(self):
        self.write('SOUR' + self._channel + ':APPL:SQU ' + self._freq + ',' + self._amplitude + self._amp_type + ',' + self._signal_offset)
        self.wait_on_display_on()
        self.logger.info(('Square wave set.'))

    def apply_source_amplitude(self):
        self.write('SOUR' + self._channel + ':AMP ' + self._amplitude + self._amp_type)
        self.logger.info('Source amplitude applied: ' + str(self._amplitude) + str(self._amp_type) + ' on Channel ' + str(self._channel))

    def get_source_amplitude(self):
        self.write('SOUR' + str(self._channel) + ':AMP?')
        self.wait_after_command()
        amp = float(self.read_until())
        return amp

    def get_min_max_source_amplitude(self):
        amp_min = float(self.write_and_read('SOUR' + str(self._channel) + ':AMP? MIN'))
        amp_max = float(self.write_and_read('SOUR' + str(self._channel) + ':AMP? MAX'))
        return amp_min, amp_max

    def toggle_output(self, state:bool):
        self.write('OUTP' + self._channel + ' ' + self._bool_to_display(state))
        self.logger.info('Output on channel ' + str(self._channel) + ' set to: ' + str(state))

    def get_output_state(self):
        self.write('OUTP' + str(self._channel) + '?')
        self.wait_after_command()
        output = bool(int(self.read_until()))
        # output = bool(int(self.write_and_read('OUTP' + str(self._channel) + '?')))
        return output

    def set_voltage_unit(self, unit:str):
        if unit not in ['VPP', 'VRMS', 'DBM']:
            self.logger.warning('Unit description wrong')
            return
        self.write('SOUR' + self._channel + ':VOLT:UNIT ' + unit)
        self.logger.info('Voltage unit on channel ' + str(self._channel) + ' set to: ' + str(unit))

    def query_voltage_unit(self):
        return self.write_and_read('SOUR' + str(self._channel) + ':VOLT:UNIT?')

    def get_current_settings(self):
        self.logger.debug('CH: ' + self._channel + 'DATA: ' + self._freq + ',' + self._amplitude + self._amp_type + ',' + self._signal_offset)

    def _bool_to_display(self, input:bool):
        if input:
            return 'ON'
        else:
            return 'OFF'


def test_fg(port, todo='full_test'):
    fg = AFG2225(port)
    fg.open()
    fg.set_channel(2)
    if todo == 'id':
        fg.get_identification()
    elif todo == 'rect':
        fg.set_frequency('4KHZ')
        fg.set_amplitude(2.5)
        fg.get_current_settings()
        fg.square_wave()
        fg.display_state(True)
        for n in range(1, 10):
            fg.set_amplitude(n)
            fg.apply_source_amplitude()
            fg.get_source_amplitude()
        fg.get_source_amplitude()
        fg.display_state(True)
    elif todo == 'get_amp':
        fg.query_voltage_unit(2)
        fg.get_source_amplitude(2)
    elif todo == 'rem':
        fg.toggle_remote()
    elif todo == 'loc':
        fg.toggle_local()
    elif todo == 'out':
        fg.toggle_output(True)
        time.sleep(2)
        fg.toggle_output(False)
    elif todo == 'disp':
        fg.display_state(False)
        time.sleep(2)
        fg.display_state(True)
    elif todo == 'full_test':
        full_test_fg(fg)
    elif todo == 'output':
        print(fg.get_output_state())
        fg.toggle_output(True)
        print(fg.get_output_state())
        fg.toggle_output(False)
        print(fg.get_output_state())
    fg.close()


def full_test_fg(fg:AFG2225):
    time_overview = []
    for display_state in [False]:
        time_list = [time.time()]
        fg.display_state(display_state)
        time_list.append(time.time())
        fg.set_channel(2)
        time_list.append(time.time())
        fg.set_frequency('5KHZ')
        time_list.append(time.time())
        fg.set_amplitude(2.5)
        time_list.append(time.time())
        fg.get_current_settings()
        time_list.append(time.time())
        fg.square_wave()
        time_list.append(time.time())
        voltage_list = []
        for n in range(1, 10):
            fg.set_amplitude(n)
            time_list.append(time.time())
            fg.apply_source_amplitude()
            time_list.append(time.time())
            if n == 9:
                print(fg.get_source_amplitude())
            time_list.append(time.time())
        time_overview.append(np.diff(time_list))
        # print(voltage_list)
    # print(time_overview)
    print('TOTAL TIME ON:', np.sum(time_overview[0]))
    # print('TOTAL TIME OFF:', np.sum(time_overview[1]))


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    test_fg(args.port)
