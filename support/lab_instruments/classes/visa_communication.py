import abc
import time
import visa
import logging
from lab_instruments.classes.lab_instrument import LabInstrument
from lab_instruments.classes.Exceptions import CommunicationException, InstrumentException
from pyvisa.resources import SerialInstrument


class VISAInstrument(LabInstrument):
    def __init__(self, instr_description: str, log: logging._loggerClass = None, log_level = logging.INFO):
        super().__init__(log=log, log_level=log_level)
        self.rm = visa.ResourceManager()
        self.resource_name: str = instr_description
        self.find_instrument()
        self.resource: SerialInstrument = None
        self.seconds_to_wait = None

    def find_instrument(self):
        list_inst = self.rm.list_resources()
        self.logger.debug('VISA instruments found: ' + str(list_inst))
        for inst in list_inst:
            if self.resource_name in inst:
                self.resource_name = inst
                self.logger.info('Instrument found: ' + self.resource_name)
                return

        self.logger.error('VISA instruments found: ' + str(list_inst))
        raise InstrumentException("No matching instrument was found: " + self.resource_name)

    def open(self):
        self.resource = self.rm.open_resource(self.resource_name)
        try:
            self.resource.open()
            self.logger.info(self.resource_name + ' has been opened.')
        except Exception:
            self.logger.error('Cannot open ' + self.resource_name)

    def write(self, msg: str, *args):
        self._pre_write(msg, *args)
        self.resource.write(msg)
        self.wait_after_command()
        self._post_write(msg, *args)
        self.cmd_time = time.time()
        self.logger.debug('WRITE: ' + msg.rstrip())

    def query(self, msg: str, *args):
        self._pre_query(msg, *args)
        reply = self.resource.query(msg, delay=self.seconds_to_wait)
        reply = self._post_query(reply)
        self.cmd_time = time.time()
        self.logger.debug('QUERY: ' + msg)
        self.logger.debug('REPLY: ' + str(reply))
        return reply

    def close(self):
        self.resource.close()
        self.logger.info('Ressource: ' + str(self.resource_name) + ' closed.')

    @abc.abstractmethod
    def _pre_write(self, msg, *args):
        pass

    @abc.abstractmethod
    def _post_write(self, msg, *args):
        pass

    @abc.abstractmethod
    def _pre_query(self, msg, *args):
        pass

    @abc.abstractmethod
    def _post_query(self, msg_read: str) -> str:
        return msg_read
