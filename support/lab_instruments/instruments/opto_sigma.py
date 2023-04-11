from lab_instruments.classes.serial_communication import SerialInstrument
from enum import Enum
from toolbox_dict_pkg.toolbox_dict_methods import update_dict
import logging
import time


class ControllerException(Exception):
    pass


class StageType(Enum):
    ROTATION = 'rotation'
    LINEAR = 'linear'
    GONIO = 'gonio'
    NOT_CONNECTED = 'not_connected'

    @staticmethod
    def get_all() -> list:
        return [StageType.ROTATION, StageType.LINEAR, StageType.GONIO, StageType.NOT_CONNECTED]

    @staticmethod
    def get_all_values() -> list:
        return [StageType.ROTATION.value, StageType.LINEAR.value, StageType.GONIO.value, StageType.NOT_CONNECTED.value]

    @staticmethod
    def str_to_mode(mode_str: str):
        for mode in StageType.get_all():
            if mode.value == mode_str:
                return mode


class OptoSigmaStage():
    def __init__(self, axis_name: str, stage_type: StageType = StageType.NOT_CONNECTED):
        self.name = axis_name
        if not axis_name or axis_name is None:
            stage_type = StageType.NOT_CONNECTED
        self.type = stage_type
        if self.type == StageType.ROTATION:
            self.precision = 0.00005  # degrees or degrees/s
        elif self.type == StageType.LINEAR:
            self.precision = 0.00001  # mm or mm/s
        elif self.type == StageType.NOT_CONNECTED:
            self.precision = None
        else:
            raise ControllerException('Precision for this type is not yet defined')


class HIT(SerialInstrument):
    def __init__(self, com_port, log: logging._loggerClass = None):
        super().__init__(com_port=com_port, baudrate=38400, xonxoff=False, log=log, rtscts=True)
        self._axis_list = []
        self._name_list = []
        self.terminator = '\r\n'

    def add_axis(self, axis: OptoSigmaStage):
        for item in self._axis_list:
            if item.name == axis.name:
                raise ControllerException('Axis name has to be unique: ' + axis.name + '; Stages in place: ' + ', '.join(self._name_list))
        self._axis_list.append(axis)
        self._name_list.append(axis.name)

    def _on_open(self):
        pass

    def _treat_kwargs(self, **kwargs):
        value_list = []
        for axis in self._axis_list:
            new_val = None
            for key, val in kwargs.items():
                if axis.name == key:
                    new_val = val
                    break
                else:
                    continue
            value_list.append(new_val)
        value_list = [self._treat_value(val) for val in value_list]
        return value_list

    @staticmethod
    def _treat_value(value):
        if value is None:
            value = ''
        elif type(value) is float:
            value = str(int(value))
        elif type(value) is bool:
            value = str(int(value))
        else:
            value = str(value)
        return value.strip()

    @staticmethod
    def _check_controller_response(command: str, msg: str):
        if msg == 'OK':
            return msg
        elif msg == 'NG':
            raise ControllerException('Command denied: ' + command)
        else:
            raise ControllerException('Invalid return: <' + msg + '> for command: ' + command)

    def _multi_axis_log(self, info: str, value_list: list):
        self.logger.info(info)
        for idx, item in enumerate(value_list):
            if item:
                self.logger.info('Name: ' + self._name_list[idx] + ' : ' + str(item))

    def _create_multiaxis_message(self, cmd: str, axis_value_list: list):
        self._check_valid_cmd(cmd, valid_cmds='hHmMaAjJlLrRcCsS')
        msg = (cmd + ':' + ','.join(axis_value_list)).strip()
        self.logger.debug('Message created: ' + msg)
        return msg

    def _create_single_axis_message(self, cmd: str, axis_name: str, parameters: list):
        self._check_valid_cmd(cmd, valid_cmds='dDbB')
        axis_id = self._get_axis_id_by_name(axis_name)
        parameters = [self._treat_value(x) for x in parameters]
        msg = (cmd + ':' + axis_id + ',' + ','.join(parameters)).strip()
        self.logger.debug('Message created: ' + msg)
        return msg

    def _get_axis_id_by_name(self, axis_name: str):
        return str(int(self._name_list.index(axis_name)))

    def _get_axis_index_by_name(self, axis_name: str):
        return int(self._name_list.index(axis_name))

    def _check_valid_cmd(self, cmd, valid_cmds='hHmMaAeEkKjJlLrRdDbBcCqQoOiIpP!?'):
        if cmd not in valid_cmds:
            output = 'Wrong command parameter given.'
            self.logger.error(output)
            raise ControllerException(output)

    def _check_valid_axis_name(self, axis_name: str):
        if axis_name is None:
            self.logger.debug('NONE axis selected.')
            return
        if axis_name not in self._name_list:
            raise ControllerException('Invalid Axis name: ' + axis_name)

    def _apply_precision(self, **kwargs):
        local_dict = {}
        for axis in self._axis_list:
            for key, val in kwargs.items():
                if axis.name == key:
                    local_dict.update({key: val / axis.precision})
        return local_dict

    def _remove_precision(self, **kwargs):
        local_dict = {}
        for axis in self._axis_list:
            for key, val in kwargs.items():
                if axis.name == key:
                    local_dict.update({key: val * axis.precision})
        return local_dict

    def home(self, **kwargs):
        value_list = self._treat_kwargs(**kwargs)
        msg = self._create_multiaxis_message('H', value_list)
        reply = self.write_and_read_until(msg)
        self._check_controller_response(msg, reply)
        self._multi_axis_log('Stages homing:', value_list)

    def move_relative(self, **kwargs):
        move_dict = self._apply_precision(**kwargs)
        value_list = self._treat_kwargs(**move_dict)
        msg = self._create_multiaxis_message('M', value_list)
        reply = self.write_and_read_until(msg)
        self._check_controller_response(msg, reply)
        self._multi_axis_log('Relative Move:', value_list)

    def move_absolute(self, **kwargs):
        move_dict = self._apply_precision(**kwargs)
        value_list = self._treat_kwargs(**move_dict)
        msg = self._create_multiaxis_message('A', value_list)
        reply = self.write_and_read_until(msg)
        self._check_controller_response(msg, reply)
        self._multi_axis_log('Absolute Move:', value_list)

    def jog(self, **kwargs):
        value_list = self._treat_kwargs(**kwargs)
        if not all(x in '+-' for x in value_list):
            raise ControllerException('Invalid command for jog.')
        msg = self._create_multiaxis_message('J', value_list)
        reply = self.write_and_read_until(msg)
        self._check_controller_response(msg, reply)
        self._multi_axis_log('Jog:', value_list)

    def stop(self, emergency=False, **kwargs):
        if emergency:
            self.logger.warning('Emergency stop for all stages.')
            msg = 'L:E'
            reply = self.write_and_read_until(msg)
            self._check_controller_response(msg, reply)
        else:
            value_list = self._treat_kwargs(**kwargs)
            msg = self._create_multiaxis_message('L', value_list)
            reply = self.write_and_read_until(msg)
            self._check_controller_response(msg, reply)
            self._multi_axis_log('Stages stopping:', value_list)

    def set_logical_origin(self, **kwargs):
        value_list = self._treat_kwargs(**kwargs)
        msg = self._create_multiaxis_message('R', value_list)
        reply = self.write_and_read_until(msg)
        self._check_controller_response(msg, reply)
        self._multi_axis_log('Logical origin set for stages:', value_list)

    def set_axis_speed(self, axis_name: str, startup_speed: float, max_speed: float, acc_decc_time: int):
        self._check_valid_axis_name(axis_name)
        if startup_speed > max_speed:
            raise ControllerException('Startup Speed higher than Max Speed.')
        startup_speed = int(startup_speed / self._axis_list[self._get_axis_index_by_name(axis_name)].precision)
        max_speed = int(max_speed / self._axis_list[self._get_axis_index_by_name(axis_name)].precision)
        if not 1 <= startup_speed <= 999999999:
            raise ControllerException('Invalid Startup Speed: ' + str(startup_speed))
        if not 1 <= max_speed <= 999999999:
            raise ControllerException('Invalid Maximum Speed: ' + str(max_speed))
        if not 1 <= acc_decc_time <= 1000:
            raise ControllerException('Invalid Acceleration/Decceleration time: ' + str(acc_decc_time))
        msg = self._create_single_axis_message('D', axis_name, [startup_speed, max_speed, acc_decc_time])
        reply = self.write_and_read_until(msg)
        self._check_controller_response(msg, reply)
        self.logger.info('Speed setting updated for axis: ' + str(axis_name))

    def set_origin_speed(self, axis_name: str, startup_speed: float, max_speed: float, acc_decc_time: int, org_reset_speed: float):
        self._check_valid_axis_name(axis_name)
        if not startup_speed <= org_reset_speed <= max_speed:
            raise ControllerException('Speed value condition not fullfilled: ' + str(startup_speed) + ' <= ' + str(org_reset_speed) + ' <= ' + str(max_speed))
        startup_speed = int(startup_speed / self._axis_list[self._get_axis_index_by_name(axis_name)].precision)
        max_speed = int(max_speed / self._axis_list[self._get_axis_index_by_name(axis_name)].precision)
        org_reset_speed = int(org_reset_speed / self._axis_list[self._get_axis_index_by_name(axis_name)].precision)
        if not 1 <= startup_speed <= 999999999:
            raise ControllerException('Invalid Startup Speed.')
        if not 1 <= max_speed <= 999999999:
            raise ControllerException('Invalid Maximum Speed.')
        if not 1 <= acc_decc_time <= 1000:
            raise ControllerException('Invalid Acceleration/Decceleration time.')
        if not 1 <= org_reset_speed <= 999999999:
            raise ControllerException('Invalid ORG Reset Speed.')
        msg = self._create_single_axis_message('B', axis_name, [startup_speed, max_speed, acc_decc_time, org_reset_speed])
        reply = self.write_and_read_until(msg)
        self._check_controller_response(msg, reply)
        self.logger.info('Origin speed changed for axis: ' + str(axis_name))

    def motor_excitation(self, **kwargs):
        # relative movement
        # if axis == False, stage can be moved manually
        value_list = self._treat_kwargs(**kwargs)
        msg = self._create_multiaxis_message('C', value_list)
        reply = self.write_and_read_until(msg)
        self._check_controller_response(msg, reply)
        self._multi_axis_log('Motor excitation settings:', value_list)

    def get_position(self, axis_name: str = None):
        position_string = self.write_and_read_until('Q:')
        position_list = position_string.split(',')
        position_list = [int(position_list[idx]) * stage.precision for idx, stage in enumerate(self._axis_list)]
        if axis_name is None:
            return position_list
        else:
            self.logger.info('Stage position: ' + str(axis_name) + ':' + str(position_list[self._get_axis_index_by_name(axis_name)]))
            return position_list[self._get_axis_index_by_name(axis_name)]

    def get_status_dict(self):
        stage_status_dict = {'-LS': 0b00000001,
                             '+LS': 0b00000010,
                             'ORG': 0b00000100,
                             'Near': 0b00001000,
                             'z-Limit': 0b00010000,
                             'Reserve': 0b00100000,
                             'DRV alarm': 0b01000000,
                             'empty': 0b10000000,
                             }
        response = self.write_and_read_until('Q:S')
        response_list = response.split(',')
        # response_list = [x for x in response_list if x]
        ctrl_response = response_list.pop(0)  # 0 value is the controller response
        if ctrl_response == '01':
            raise ControllerException('Command rejected.')
        return_dict = dict()
        for idx, stage_response in enumerate(response_list):
            for key in stage_status_dict:
                if not stage_response:
                    continue
                update_dict(return_dict, ['axis'+str(idx+1), key], self._check_status_byte(int(stage_response, 16), stage_status_dict.get(key)))
        return return_dict

    @staticmethod
    def _check_status_byte(code, status_code):
        if code & status_code:
            return True
        else:
            return False

    def get_stage_busy(self, axis_name: str = None):
        self._check_valid_axis_name(axis_name)
        status_bits = self.write_and_read_until('!:')
        status_bit_list = status_bits.split(',')
        status_bit_list = [int(x) == 1 if x else None for x in status_bit_list]
        if axis_name is None:
            return status_bit_list
        else:
            return status_bit_list[self._get_axis_index_by_name(axis_name)]

    def get_device_name(self):
        response = self.write_and_read_until('?:N')
        return response

    def get_version(self):
        response = self.write_and_read_until('?:V')
        return response

    def get_travel_per_pulse(self, axis_name: str = None):
        self._check_valid_axis_name(axis_name)
        response_string = self.write_and_read_until('?:P')
        response_list = response_string.split(',')
        response_list = [float(x) for x in response_list]
        if axis_name is None:
            return response_list
        else:
            return response_list[self._get_axis_index_by_name(axis_name) - 1]

    def get_division(self, axis_name: str = None):
        self._check_valid_axis_name(axis_name)
        response_string = self.write_and_read_until('?:S')
        response_list = response_string.split(',')
        response_list = [float(x) for x in response_list]
        if axis_name is None:
            return response_list
        else:
            return response_list[self._get_axis_index_by_name(axis_name) - 1]

    def set_division(self, **kwargs):
        value_list = self._treat_kwargs(**kwargs)
        msg = self._create_multiaxis_message('S', value_list)
        reply = self.write_and_read_until(msg)
        self._check_controller_response(msg, reply)
        self._multi_axis_log('Stages homing:', value_list)

    def get_travel_speed(self, axis_name: str):
        self._check_valid_axis_name(axis_name)
        response_string = self.write_and_read_until('?:D' + self._get_axis_id_by_name(axis_name))
        response_list = response_string.split(',')
        # response_list = [int(response_list[idx]) * stage.precision for idx, stage in enumerate(self._axis_list)] TODO
        travel_speed_dict = {
            'startup_speed': response_list[0],
            'max_speed': response_list[1],
            'acc_decc_time': response_list[2],
        }
        return travel_speed_dict

    def get_origin_speed(self, axis_name: str):
        self._check_valid_axis_name(axis_name)
        response_string = self.write_and_read_until('?:B' + self._get_axis_id_by_name(axis_name))
        response_list = response_string.split(',')
        # response_list = [int(response_list[idx]) * stage.precision for idx, stage in enumerate(self._axis_list)] TODO
        org_speed_dict = {
            'startup_speed': response_list[0],
            'max_speed': response_list[1],
            'acc_decc_time': response_list[2],
            'org_reset_speed': response_list[3],
        }
        return org_speed_dict

    def is_moving(self, axis_name: str = None):
        self._check_valid_axis_name(axis_name)
        pos1 = self.get_position(axis_name)
        pos2 = self.get_position(axis_name)
        if axis_name is None:
            move_array = [not(pos == pos2[idx]) for idx, pos in enumerate(pos1)]
            return move_array
        else:
            return not(pos1 == pos2)

    def block_while_moving(self, axis_name: str = None):
        self._check_valid_axis_name(axis_name)
        if axis_name is None:
            while any(x is True for x in self.is_moving(axis_name)):
                self.wait_after_command()  # TODO verify that this is necessary
        else:
            while self.is_moving(axis_name):
                self.wait_after_command()  # TODO verify that this is necessary

    def block_until_not_busy(self, axis_name: str = None):
        self._check_valid_axis_name(axis_name)
        if axis_name is None:
            while any(x is True for x in self.get_stage_busy(axis_name)):
                # self.wait_after_command()  # TODO verify that this is necessary
                pass
        else:
            while self.get_stage_busy(axis_name):
                # self.wait_after_command()  # TODO verify that this is necessary
                pass

    def is_homing(self, axis: int = None):
        # TODO
        pass

    def status_is_homed(self, axis: int = None):
        # TODO
        pass


if __name__ == '__main__':
    ctrl = HIT('COM15')
    ctrl.add_axis(OptoSigmaStage('linear', StageType.LINEAR))
    ctrl.add_axis(OptoSigmaStage('lcos', StageType.ROTATION))
    ctrl.add_axis(OptoSigmaStage('retarder', StageType.ROTATION))
    ctrl.add_axis(OptoSigmaStage('circular_polariser', StageType.ROTATION))
    print(ctrl._axis_list)
    ctrl.open()
    ctrl.home(lcos=1, retarder=1, circular_polariser=1, linear=1)
    ctrl.block_until_not_busy()
    ctrl.set_axis_speed('linear', 0.1, 50, 200)
    ctrl.set_axis_speed('lcos', 5, 50, 200)
    ctrl.set_axis_speed('retarder', 5, 50, 200)
    ctrl.set_axis_speed('circular_polariser', 5, 50, 200)
    # ctrl.move_absolute(linear=100)
    while True:
        time.sleep(0.5)
        ax = input('ENTER the axis to move:')
        a = input('ENTER THE NEW POSITION:\r\n')
        if float(a) == float(-1):
            break
        elif float(a) == float(-2):
            continue
        if float(ax) == float(0):
            ctrl.move_absolute(linear=float(a))
        elif float(ax) == float(1):
            ctrl.move_absolute(lcos=float(a))
        elif float(ax) == float(2):
            ctrl.move_absolute(retarder=float(a))
        elif float(ax) == float(3):
            ctrl.move_absolute(circular_polariser=float(a))
        else:
            continue
    ctrl.block_until_not_busy()
    # ctrl.move_absolute(lcos=90)
    ctrl.block_until_not_busy()
    ctrl.move_absolute(linear=0)
    ctrl.block_until_not_busy()
    """
    ctrl.add_axis(OptoSigmaStage('lcos', StageType.ROTATION))
    ctrl.add_axis(OptoSigmaStage('retarder', StageType.ROTATION))
    ctrl.add_axis(OptoSigmaStage('circular_polariser', StageType.ROTATION))
    ctrl.add_axis(OptoSigmaStage('linear', StageType.ROTATION))
    print(ctrl.write_and_read_until('?:P'))
    ctrl.home(lcos=1, retarder=1, circular_polariser=1)
    ctrl.block_until_not_busy()
    print(ctrl.get_travel_per_pulse('lcos'))
    print(ctrl.get_division('lcos'))
    print(ctrl.get_travel_speed('lcos'))
    print(ctrl.get_travel_speed('retarder'))
    print(ctrl.get_travel_speed('circular_polariser'))
    print(ctrl.get_origin_speed('lcos'))
    # ctrl.set_division(lcos=10)
    print(ctrl.get_division('lcos'))
    # ctrl.set_axis_speed('lcos', 7000, 8000,200)
    ctrl.move_absolute(lcos=100, retarder=100, circular_polariser=100)
    print(ctrl.get_position())
    ctrl.block_until_not_busy()
    print(ctrl.get_position())
    
    ctrl.move_absolute(lcos=150)
    ctrl.move_absolute(lcos=200)
    # ctrl.write_and_read_until('A:1000000')
    # ctrl.home(lcos=1)
    # ctrl.wait_after_command(1)
    # ctrl.move_absolute(lcos=100)
    
    for n in range(0, 10):
        ctrl.wait_after_command(1)
        pos = ctrl.get_position('lcos')
        print('POS:', pos)
        reply = ctrl.get_stage_busy('lcos')
        if not reply:
            break

    
    ctrl.home(lcos=1, retarder=1, circular_polariser=1, linear=1)
    # ctrl.move_absolute(lcos=10, retarder=30, circular_polariser=50, linear=50)
    ctrl.get_position()
    # ctrl.block_while_moving()
    print(ctrl.get_origin_speed('lcos'))
    print(ctrl.get_origin_speed('retarder'))
    print(ctrl.get_origin_speed('circular_polariser'))
    print(ctrl.get_origin_speed('linear'))
    print(ctrl.get_travel_speed('lcos'))
    print(ctrl.get_travel_speed('retarder'))
    print(ctrl.get_travel_speed('circular_polariser'))
    print(ctrl.get_travel_speed('linear'))
    print(ctrl.get_position('lcos'))
    print(ctrl.get_position('retarder'))
    print(ctrl.get_position('circular_polariser'))
    print(ctrl.get_position('linear'))
    # """
    ctrl.close()