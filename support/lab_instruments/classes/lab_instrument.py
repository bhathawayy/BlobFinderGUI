import logging
import time


class LabInstrument:
    def __init__(self, log: logging._loggerClass = None, log_level = logging.INFO):
        self.logger = log
        self.log_level = log_level
        if self.logger is None:
            self._basic_logger()
        self.seconds_to_wait = 0.1
        self.cmd_time = 0

    def _basic_logger(self):
        log_format: str = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        logging.basicConfig(level=self.log_level, format=log_format)
        self.logger = logging.getLogger(__name__)

    def wait_after_command(self, t=None):
        if t is None:
            t = self.seconds_to_wait
        if t is not None:
            time.sleep(t)
