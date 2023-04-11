import serial
import time
from argparse import ArgumentParser
import re
from lab_instruments.classes.serial_communication import SerialInstrument
import logging

'''
Manual: https://www.newport.com/mam/celum/celum_assets/resources/CONEX-CC_-_Controller_Documentation.pdf?1
'''


def create_parser():
    p = ArgumentParser()
    p.add_argument('--port',
                   type=str,
                   help='Specify the COM port.',
                   default='COM7',
                   required=False)
    p.add_argument('--value',
                   type=str,
                   help='Any value...',
                   default='0',
                   required=False)
    return p


class ConexCC(SerialInstrument):
    def __init__(self, com_port, controller_number, baudrate=921600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, xonxoff=True, log: logging._loggerClass = None, log_level=logging.INFO):
        super().__init__(com_port,
                         baudrate=baudrate,
                         bytesize=bytesize,
                         parity=parity,
                         stopbits=stopbits,
                         xonxoff=xonxoff,
                         log=log,
                         log_level=log_level)
        self._controller_address_nn = str(controller_number)
        self._command_regex = re.compile("([0-9]{0,1})([a-zA-Z?]{2,})([0-9+-.a-zA-Z]*)")

    def _send_command(self, AA: str, xx=''):
        msg = self._controller_address_nn + AA + xx
        self.write(msg)

    def _send_command_get_response(self, AA: str, xx=''):
        self._send_command(AA, xx)
        reply = self.read_until()
        _, _, val = self._parse_reply(reply)
        return val

    def _parse_reply(self, reply):
        addr, cmd, val = self._command_regex.match(reply).groups()
        return addr, cmd, val

    def home_device(self):
        self.logger.info('Homing device.')
        self._send_command('OR')

    def move_absolute(self, position: float, blocking=False):
        self.logger.info('Absolute move to: ' + str(position))
        self._send_command('PA', str(position))
        if blocking:
            self.block_until_end_move()

    def move_relative(self, position: float, blocking=False):
        self.logger.info('Relative move to: ' + str(position))
        # time_to_wait = 0
        # if blocking:
        #     time_to_wait = float(self.get_rel_move_motion_time(position))
        # self._send_command('PR', str(position))
        # if blocking:
        #     time.sleep(time_to_wait)
        self._send_command('PR', str(position))
        if blocking:
            self.block_until_end_move()

    def get_absolute_target_position(self):
        return float(self._send_command_get_response('PA', '?'))

    def get_relative_target_position(self):
        return float(self._send_command_get_response('PR', '?'))

    def get_current_position(self):
        timing = self.seconds_to_wait
        self.seconds_to_wait = 0
        pos = float(self._send_command_get_response('TP'))
        self.seconds_to_wait = timing
        return pos

    def get_set_point_position(self):
        return float(self._send_command_get_response('TH'))

    def get_velocity(self):
        return float(self._send_command_get_response('VA', '?'))

    def set_velocity(self, velocity: float):
        self.logger.info('Velocity set to: ' + str(velocity))
        self._send_command('VA', str(velocity))

    def stop_motion(self):
        self.logger.info('Stop motion')
        self._send_command('ST')
        while self.is_moving():
            self.wait_after_command()

    def get_id(self):
        return self._send_command_get_response('ID', '?')

    def get_rel_move_motion_time(self, position: float):
        return self._send_command_get_response('PT', str(position))

    def toggle_enable_state(self, state: bool = True):
        self.logger.info('Toggled enable state to: ' + str(state))
        self._send_command('MM', str(int(state)))

    def get_enable_state(self):
        mm_state = self._send_command_get_response('MM', '?')
        return self.get_controller_state(mm_state)

    def get_state(self):
        return self._send_command_get_response('TS')

    def set_tracking_mode(self, tracking_mode: bool):
        self.logger.info('Set tracking mode to: ' + str(tracking_mode))
        self._send_command('TK', str(int(tracking_mode)))

    def enter_leave_configuration_state(self, state: bool):
        self._send_command('PW', str(int(state)))
        self.logger.info('Toggled configuration state to: ' + str(state))

    def get_controller_state(self, state=None):
        if state is None:
            state = self.get_state()
            status_byte = state[4:]
        else:
            status_byte = state
        # state_dict = {
        #     'NOT REFERENCED from RESET': 0x0A,
        #     'NOT REFERENCED from HOMING': '0B',
        #     'NOT REFERENCED from CONFIGURATION': 0x0C,
        #     'NOT REFERENCED from DISABLE': 0x0D,
        #     'NOT REFERENCED from READY': 0x0E,
        #     'NOT REFERENCED from MOVING': 0x0F,
        #     'NOT REFERENCED - NO PARAMETERS IN MEMORY': 0x10,
        #     'CONFIGURATION': 0x14,
        #     'HOMING': 0x1E,
        #     'MOVING': 0x28,
        #     'READY from HOMING': 0x32,
        #     'READY from MOVING': 0x33,
        #     'READY from DISABLE':0x34,
        #     'READY T from READY': 0x36,
        #     'READY T from TRACKING': 0x37,
        #     'READY T from DISABLE T': 0x38,
        #     'DISABLE from READY': 0x3C,
        #     'DISABLE from MOVING': 0x3D,
        #     'DISABLE from TRACKING': 0x3E,
        #     'DISABLE from READY T': 0x3F,
        #     'TRACKING from READY T': 0x46,
        #     'TRACKING from TRACKING': 0x47,
        # }
        inverse_state_dict = {
            '0A': 'NOT REFERENCED from RESET',
            '0B': 'NOT REFERENCED from HOMING',
            '0C': 'NOT REFERENCED from CONFIGURATION',
            '0D': 'NOT REFERENCED from DISABLE',
            '0E': 'NOT REFERENCED from READY',
            '0F': 'NOT REFERENCED from MOVING',
            '10': 'NOT REFERENCED - NO PARAMETERS IN MEMORY',
            '14': 'CONFIGURATION',
            '1E': 'HOMING',
            '28': 'MOVING',
            '32': 'READY from HOMING',
            '33': 'READY from MOVING',
            '34': 'READY from DISABLE',
            '36': 'READY T from READY',
            '37': 'READY T from TRACKING',
            '38': 'READY T from DISABLE T',
            '3C': 'DISABLE from READY',
            '3D': 'DISABLE from MOVING',
            '3E': 'DISABLE from TRACKING',
            '3F': 'DISABLE from READY T',
            '46': 'TRACKING from READY T',
            '47': 'TRACKING from TRACKING',
        }
        error_msg = 'ERROR: STATUS:' + str(status_byte)
        status = inverse_state_dict.get(status_byte, error_msg)
        self.logger.debug('CURRENT CONTROLLER STATE: ' + str(status))
        return status

    @staticmethod
    def check_status_byte(code, status_code):
        if code & status_code:
            return True
        else:
            return False

    def block_until_end_move(self):
        while self.is_moving():
            self.wait_after_command()
            # print(self.is_moving(), self.get_controller_state())
        while 'READY' not in self.get_controller_state():
            self.logger.debug('Stage not yet ready from Moving.')
            self.wait_after_command()
        while not self.get_current_position() == self.get_absolute_target_position():
            self.wait_after_command()
        self.logger.info('MOVE has been finished.')

    def is_moving(self):
        state = self.get_controller_state()
        self.logger.debug('Current moving/homing state:' + str(state))
        return state  == 'MOVING' or state == 'HOMING'

    def is_homed(self):
        state = self.get_controller_state()
        self.logger.debug('Current homed state:' + str(state))
        return state == 'READY from HOMING'


def conex(port, controller_number, value, todo='timing'):
    cc = ConexCC(port, controller_number)
    print(cc.get_controller_state())
    # cc.open()
    cc.toggle_enable_state()
    print(cc.get_controller_state())
    cc.home_device()
    print(cc.get_controller_state())
    cc.block_until_end_move()
    print(cc.get_controller_state())
    cc.move_absolute(0, blocking=True)
    print(cc.get_state())
    if todo == 'id':
        cc.get_id()
        print(cc.get_controller_state())
    elif todo == 'home':
        cc.home_device()
    elif todo == 'pos':
        print('POSITION:', cc.get_current_position())
    elif todo == 'move':
        cc.move_absolute(-20)
        cc.block_until_end_move()
        cc.move_absolute(20)
        cc.block_until_end_move()
    elif todo == 'move_rel':
        for n in range(0, 10):
            cc.move_relative(n, blocking=False)
    elif todo == 'status':
        cc.home_device()
        print(cc.get_controller_state())
        cc.block_until_end_move()
        print(cc.get_controller_state())
    elif todo == 'timing':
        cc.move_absolute(180)
        for n in range(100):
            t1 = time.time()
            pos = cc.get_current_position()
            print(n, time.time()-t1, pos)
        cc.stop_motion()
        cc.move_absolute(0, blocking=True)
        print(cc.get_current_position(), cc.get_absolute_target_position())
        # print(cc.get_current_position(), cc.get_absolute_target_position())
        # print(cc.get_current_position(), cc.get_absolute_target_position())
        # print(cc.get_current_position(), cc.get_absolute_target_position())
    cc.close()


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    conex(args.port,'1', args.value)
