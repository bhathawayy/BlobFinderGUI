import abc
import time
import serial
import logging
from lab_instruments.classes.Exceptions import CommunicationException
from lab_instruments.classes.lab_instrument import LabInstrument


class SerialInstrument(LabInstrument):
    def __init__(self,
                 com_port,
                 log: logging._loggerClass = None,
                 baudrate = 115200,
                 bytesize = serial.EIGHTBITS,
                 parity = serial.PARITY_NONE,
                 stopbits = serial.STOPBITS_ONE,
                 xonxoff = True,
                 log_level = logging.INFO,
                 **kwargs):
        super().__init__(log=log, log_level=log_level)
        self.port = com_port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.xonxoff = xonxoff

        self.ser = serial.Serial(port=self.port,
                                 baudrate=self.baudrate,
                                 bytesize=self.bytesize,
                                 parity=self.parity,
                                 stopbits=self.stopbits,
                                 xonxoff=self.xonxoff,
                                 **kwargs)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.expected = '\r\n'
        self.encoding_format = 'utf-8'
        self.msg_join_character = ' '

    def open(self):
        if self.ser.isOpen():
            self.ser.close()
        self.ser.open()
        if self.ser.isOpen():
            self.logger.info(self.port + ' has been opened.')
            self._on_open()
        else:
            raise serial.SerialException
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    @abc.abstractmethod
    def _on_open(self):
        pass

    def close(self):
        self._on_close()
        self.ser.close()
        if not self.ser.isOpen():
            self.logger.info(self.port + ' has been closed.')

    @abc.abstractmethod
    def _on_close(self):
        """
        steps that are executed before the device is actually closed.
        :return:
        """

    def write(self, msg: str, *args):
        self._pre_write(msg, *args)
        msg = self.msg_creation(msg, *args)
        if not msg.endswith(self.expected):
            msg = msg + self.expected
        self.ser.write(msg.encode(self.encoding_format))
        self.wait_after_command()
        self._post_write(msg, *args)
        self.cmd_time = time.time()
        self.logger.debug('WRITE: ' + msg.rstrip(self.expected))

    def read_until(self):
        self._pre_read()
        msg_read = self.ser.read_until(expected=self.expected.encode(self.encoding_format)).decode(self.encoding_format)
        msg_read = msg_read.rstrip(self.expected)
        msg_read = self._post_read(msg_read)
        self.cmd_time = time.time()
        self.logger.debug('READ: ' + msg_read)
        return msg_read

    def read_all(self):
        self._pre_read()
        msg_read = self.ser.read_all().decode(self.encoding_format)
        msg_read = msg_read.rstrip(self.expected)
        msg_read = self._post_read(msg_read)
        self.cmd_time = time.time()
        self.logger.debug('READ: ' + msg_read)
        return msg_read

    def read(self, bytes_to_read=None):
        self._pre_read()
        if bytes_to_read is None:
            bytes_to_read = self.ser.in_waiting
        msg_read = self.ser.read(bytes_to_read).decode(self.encoding_format)
        msg_read = msg_read.rstrip(self.expected)
        msg_read = self._post_read(msg_read)
        self.cmd_time = time.time()
        self.logger.debug('READ: ' + msg_read)
        return msg_read

    def continous_read_all_available(self, t_to_read=None):
        """
        This function will poll the serial port until no more bytes are available.
        :param t_to_read: This is the time between each poll to wait. If None, waits the time of the serial port.
        :return:
        """
        self._pre_read()
        line = bytearray()
        while self.ser.inWaiting() > 0:
            c = self.ser.read(self.ser.in_waiting)
            if c:
                line += c
            self.wait_after_command(t=t_to_read)
        msg_read = bytes(line).decode(self.encoding_format)
        msg_read = msg_read.rstrip(self.expected)
        msg_read = self._post_read(msg_read)
        self.cmd_time = time.time()
        self.logger.debug('READ: ' + msg_read)
        return msg_read

    def read_until_string(self, break_on_occurence: str, timeout=30):
        """
        This function reads until either the timeout time is hit or the correct line is found
        :param break_on_occurence: string to search for in line
        :param timeout: time in s after which the reading stops
        :return:
        """
        self._pre_read()
        msg_read = ''
        t_start = time.time()
        while time.time() < (t_start + timeout):
            line = self.ser.read_all()
            if line.decode(self.encoding_format):
                msg_read += line.decode(self.encoding_format)
                if break_on_occurence in line.decode(self.encoding_format):
                    break
            else:
                time.sleep(0.001)
        msg_read = self._post_read(msg_read)
        self.cmd_time = time.time()
        self.logger.debug('READ: ' + msg_read)
        return msg_read

    def write_and_read(self, msg: str, *args):
        self.write(msg, *args)
        return self.read()

    def write_and_read_all(self, msg: str, *args):
        self.write(msg, *args)
        return self.read_all()

    def write_and_read_until(self, msg: str, *args):
        self.write(msg, *args)
        return self.read_until()

    def write_and_continous_read(self, msg: str, *args):
        self.write(msg, *args)
        return self.continous_read_all_available()

    def msg_creation(self, *args) -> str:
        msg = self.msg_join_character.join([str(x) for x in args])
        return msg

    @abc.abstractmethod
    def _pre_write(self, msg, *args):
        pass

    @abc.abstractmethod
    def _post_write(self, msg, *args):
        pass

    @abc.abstractmethod
    def _pre_read(self):
        pass

    @abc.abstractmethod
    def _post_read(self, msg_read: str) -> str:
        return msg_read

    def disable_logging(self):
        self.logger.disabled = True

    def enable_logging(self):
        self.logger.disabled = False
