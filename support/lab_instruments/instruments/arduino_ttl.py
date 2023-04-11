"""
Created by nuffer at 4/6/20

"""
import time
import serial
from lab_instruments.classes.serial_communication import SerialInstrument


class ArduinoTTL(SerialInstrument):

    def __int__(self, com_port: str):
        super().__init__(com_port=com_port, baudrate=250000)

    def _on_open(self):
        raise NotImplemented

    def _on_close(self):
        raise NotImplemented

    def _pre_write(self, msg, *args):
        raise NotImplemented

    def _post_write(self, msg, *args):
        raise NotImplemented

    def _pre_read(self):
        raise NotImplemented

    def _post_read(self, msg_read: str) -> str:
        raise NotImplemented

    def open(self):
        """
        Overwrite parent method
        :return:
        """
        self.ser = serial.Serial(self.port, 250000)
        time.sleep(3)  # let the time to open the port
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def close(self):
        self.ser.close()

    def send_sequence(self, sequences: str):
        """
         Sequence syntax:");
            use the syntax PIN:ON to turn on the pin (e.g. D1:ON)
            use the syntax PIN:OFF to turn on the pin (e.g. D1:OFF)
            use the syntax WAIT:<ms> to wait during ms (e.g. WAIT:1000)
            Compose your <sequence> like: S/D1:ON/WAIT:1000/D1:OFF/
        :param sequences:
        :return:
        """
        command = sequences + '\n'
        self.logger.debug("send command: " + command.strip())
        self.ser.write(command.encode())
        while True:
            feedback = self.ser.readline()
            self.logger.debug("arduino response: " + feedback.decode())
            if feedback == b'Done sequence\r\n':
                self.logger.debug("Done sequence")
                break

    def get_humidity_and_temperature(self):
        """
        If the sensor is connected, otherwise return impossible values
        """
        command = 'H\n'
        self.logger.debug("send command: " + command.strip())
        self.ser.write(command.encode())
        humidity = float(self.ser.readline())

        command = 'T\n'
        self.logger.debug("send command: " + command.strip())
        self.ser.write(command.encode())
        temperature = float(self.ser.readline())

        self.logger.info("read Humidity and Temperature sensor: " + str(humidity) + "% " + str(temperature) + "C")
        return humidity, temperature


if __name__ == '__main__':

    arduino = ArduinoTTL('/dev/cu.wchusbserial14110')
    arduino.open()
    arduino.send_sequence('S/D1:ON/WAIT:1000/D1:OFF/')
    h,t = arduino.get_humidity_and_temperature()
    print(h)
    print(t)
    arduino.close()


