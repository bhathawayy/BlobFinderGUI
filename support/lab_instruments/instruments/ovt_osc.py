from lab_instruments.classes.serial_communication import SerialInstrument
import serial
import logging


class RingoReferenceBoard(SerialInstrument):
    def __init__(self, com_port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, xonxoff=False, log=None, log_level=logging.DEBUG):
        super().__init__(com_port,
                         baudrate=baudrate,
                         bytesize=bytesize,
                         parity=parity,
                         stopbits=stopbits,
                         xonxoff=xonxoff,
                         log=log,
                         log_level=log_level)
        self.terminator = ''
        self.seconds_to_wait = 0.2

    def _check_input_read(self, slave_id, address):
        xx = str(slave_id)
        yyyy = str(address)
        if len(xx) > 2:
            e = 'Wrong Slave_ID length.'
            self.logger.error(e)
            raise serial.SerialException(e)
        if len(yyyy) > 2:
            e = 'Wrong address length.'
            self.logger.error(e)
            raise serial.SerialException(e)
        return xx, yyyy

    def _check_input_write(self, slave_id, address, byte):
        xx = str(slave_id)
        yyyy = str(address)
        dd = str(byte)
        if len(xx) > 2:
            e = 'Wrong Slave_ID length.'
            self.logger.error(e)
            raise serial.SerialException(e)
        if len(yyyy) > 2:
            e = 'Wrong address length.'
            self.logger.error(e)
            raise serial.SerialException(e)
        if len(dd) > 2:
            e = 'Wrong byte length.'
            self.logger.error(e)
            raise serial.SerialException(e)
        return xx, yyyy, dd

    def _clean_reply(self, reply):
        reply = reply.split('\r\n')
        reply = [x.strip() for x in reply if x]
        val = ''
        if 'PID decoded:' in reply:
            for elem in reply:
                if 'Lot ID:' not in elem:
                    continue
                val = elem
            new = reply.pop(reply.index(val))
            new = new.split(',')
            new = [x.strip() for x in new]
            reply.extend(new)
        return reply

    def read_one_byte(self, slave_id, address):
        xx, yyyy = self._check_input_read(slave_id, address)
        msg = '\\rd ' + xx + ' ' + yyyy
        return self.write_and_read_until(msg)

    def read_four_bytes(self, slave_id, address):
        xx, yyyy = self._check_input_read(slave_id, address)
        msg = '\\rd4 ' + xx + ' ' + yyyy
        return self.write_and_read_until(msg)

    def write_one_byte(self, slave_id, address, byte):
        xx, yyyy, dd = self._check_input_write(slave_id, address, byte)
        msg = '\\wr ' + xx + ' ' + yyyy + ' ' + dd
        self.write(msg)

    def write_four_bytes(self, slave_id, address, bytes):
        xx, yyyy, dd = self._check_input_write(slave_id, address, bytes)
        msg = '\\wr4 ' + xx + ' ' + yyyy + ' ' + dd
        self.write(msg)

    def get_temperature(self):
        reply = self.write_and_continous_read('t')
        reply = self._clean_reply(reply)
        # Sample reply: ['Temperature:', 'Register value read from 0x083, 0x082 = 0x92, 0x8C (146, 140)', 'Approx temp = 27.8C', 'None OTP']
        local_dict = {}
        for idx, key in enumerate(['approx_temp_C']):
            try:
                local_dict.update({key: reply[idx + 2].split('=')[1].strip().rstrip('C')})
            except IndexError:
                local_dict.update({key: None})
        self.logger.info('Temperature read: ' + str(local_dict.get('approx_temp_C')))
        return local_dict

    def get_panel_id(self):
        reply = self.write_and_continous_read('p')
        reply = self._clean_reply(reply)
        # Sample reply: ['\x1b[2J\x1b[0;0HProduction OTP Data read', 'Product ID = 000000', 'Lot ID = 00 00 00 00 00 00 00 00', 'Wafer number = 00 [0]', 'X coordinate = 00', 'Y coordinate = 00', 'Reserved bytes = 00 00', 'PID can not be decoded']

        # Sample reply with PID:
        # ['\x1b[2J\x1b[0;0HProduction OTP Data read', 'Product ID = 003000', 'Lot ID = 0b 1b 19 01 02 07 00 00', 'Wafer number = 03 [3]', 'X coordinate = 14', 'Y coordinate = 15', 'Reserved bytes = 00 00', 'PID decoded:', 'Panel ID: AV21', 'Lot ID: BRP12700', 'Wafer ID: 3']
        local_dict = {'product_id': 'Product ID =',
                      'lot_id': 'Lot ID =',
                      'wafer_number': 'Wafer number =',
                      'x_coordinate': 'X coordinate =',
                      'y_coordinate': 'Y coordinate =',
                      'reserved_bytes': 'Reserved bytes =',
                      'pid': 'PID decoded:',
                      'lot_id_decoded': 'Lot ID: ',
                      'wafer_id_decoded': 'Wafer ID: ',
                      'panel_id_decoded': 'Panel ID: ',
                      }
        for key in local_dict.keys():
            val = local_dict.get(key)
            found = False
            for elem in reply:
                if val in elem:
                    local_dict.update({key: elem.split(val)[1]})
                    found = True
            if not found:
                local_dict.update({key: None})

        self.logger.info('Panel info:')
        for key in local_dict.keys():
            self.logger.info('Panel info: ' + key + ': ' + str(local_dict.get(key)))
        return local_dict

    def power_up_board(self):
        reply = ''
        for command in ['E', 'U', 'Q']:
            self.write(command)
            reply += self.continous_read_all_available(0.5)
        reply = self._clean_reply(reply)
        self.logger.info('Board is powered up.')
        return reply

    def power_down_board(self):
        reply = ''
        for command in ['E', 'Z', 'Q']:
            self.write(command)
            reply += self.continous_read_all_available(0.5)
        reply = self._clean_reply(reply)
        self.logger.info('Board is powered down.')
        return reply

    def is_board_status_on(self):
        self.write('I')
        self.wait_after_command(0.5)
        reply = self.continous_read_all_available()
        reply = self._clean_reply(reply)
        status = False
        for elem in reply:
            if elem.startswith('System is powered up'):
                status = True
        self.logger.info('Board status is: ' + str(status))
        return status

    def get_firmware(self):
        self.write('I')
        self.wait_after_command(0.5)
        reply = self.continous_read_all_available()
        reply = self._clean_reply(reply)
        local_dict = {}
        for elem in reply:
            if elem.startswith('Firmware version '):
                local_dict.update({'firmware_version': elem.split('Firmware version ')[1]})
            if elem.startswith('Firmware date '):
                local_dict.update({'firmware_date': elem.split('Firmware date ')[1]})
        self.logger.info('Firmware version: ' + str(local_dict.get('firmware_version')))
        self.logger.info('Firmware date: ' + str(local_dict.get('firmware_date')))
        return local_dict

    def get_menu(self):
        self.write('?')
        reply = self.continous_read_all_available()
        reply = self._clean_reply(reply)
        return reply


def example():
    board = RingoReferenceBoard('COM5', log_level=logging.INFO)
    board.open()
    board.is_board_status_on()
    board.power_up_board()
    board.is_board_status_on()
    board.get_temperature()
    board.get_panel_id()
    board.get_firmware()
    board.power_down_board()
    board.is_board_status_on()
    board.close()


if __name__ == '__main__':
    example()
