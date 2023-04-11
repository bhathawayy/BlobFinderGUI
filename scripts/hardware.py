import time, ctypes, cv2, threading, serial, logging
import numpy as np
from arena_api.system import system
from errors import *
from inspect import currentframe
from pipython import GCSDevice, pitools
from lab_instruments.classes.serial_communication import SerialInstrument
from lab_instruments.classes.Exceptions import InstrumentException


class PIStageC884:

    def __init__(self, serial_num, interface="USB"):
        self.controller = "C-884"
        self.device = None
        self.interface = interface  # options: "USB", "TCP"
        self.device_id = serial_num
        self.axes_data = {}
        self.velocity = 5

        self.open()

    def close(self):
        """
        Close PI device connection.
        """
        if self.device is not None:
            self.device.gcsdevice.CloseConnection()
            self.device = None
            print("Controller connection closed.")

    def get_axes_data(self):
        axes = None
        if self.device is not None:
            axes = self.device.qCST()
            refs = self.device.qFRF()
            poss = self.device.qPOS()
            mins = self.device.qTMN()
            maxs = self.device.qTMX()
            homes = self.device.qDFH()
            for axis in axes:
                self.axes_data[axis] = {"name": axes[axis]}
                if axis in refs.keys():
                    self.axes_data[axis]["ref"] = refs[axis]
                    self.axes_data[axis]["pos"] = poss[axis]
                    self.axes_data[axis]["min"] = mins[axis]
                    self.axes_data[axis]["max"] = maxs[axis]
                    self.axes_data[axis]["home"] = homes[axis]
                else:
                    self.axes_data[axis]["ref"] = None
                    self.axes_data[axis]["pos"] = None
                    self.axes_data[axis]["min"] = None
                    self.axes_data[axis]["max"] = None
                    self.axes_data[axis]["home"] = None

        return axes, self.axes_data

    def move_to(self, axis, position):
        position = float(position)
        if self.is_axis_valid(axis):
            if self.axes_data[axis]["min"] <= position <= self.axes_data[axis]["max"]:
                pitools.waitontarget(self.device)
                self.device.MOV(axis, float(position))
            else:
                error_check(303, currentframe())

    def move_by(self, axis, step):
        step = float(step)
        if self.is_axis_valid(axis):
            position = self.axes_data[axis]["pos"]
            if self.axes_data[axis]["min"] <= (step + position) <= self.axes_data[axis]["max"]:
                pitools.waitontarget(self.device)
                self.device.MVR(axis, float(step))
            else:
                error_check(303, currentframe())

    def move_to_home(self, axis=None):
        if axis is None:
            if self.device is not None:
                for each_axis in self.axes_data:
                    pitools.waitontarget(self.device)
                    self.device.GOH(each_axis)
        else:
            if self.is_axis_valid(axis):
                pitools.waitontarget(self.device)
                self.device.GOH(axis)

    def reference_axis(self, axis=None):
        if axis is None:
            for each_axis in self.axes_data:
                if self.axes_data[each_axis]["ref"] == False and self.device is not None:
                    pitools.waitontarget(self.device)
                    self.device.REF(each_axis)
        else:
            if self.is_axis_valid(axis):
                pitools.waitontarget(self.device)
                self.device.REF(axis)

    def is_axis_valid(self, axis):
        ok = False
        if self.device is not None:
            if axis in self.axes_data.keys():
                if "NOSTAGE" not in self.axes_data[axis]["name"]:
                    ok = True
                else:
                    error_check(304, currentframe())
            else:
                error_check(305, currentframe())

        return ok

    def open(self):
        """
        Initialize the stage connection.
        :return: PI device handle; format: (obj) GCSDevice object
        """
        # Establish a connection to PI device
        try:
            pi_device = GCSDevice(self.controller)
            if "USB" in self.interface:
                pi_device.ConnectUSB(serialnum=self.device_id)
            elif "TCP" in self.interface:
                pi_device.ConnectTCPIP(ipaddress=self.device_id)
            else:
                error_check(302, currentframe())
                self.close()
                return
        except Exception:
            error_check(301, currentframe())
            self.close()
            return

        self.device = pi_device
        print("\nPI Device found: {}".format(pi_device.qIDN().strip()))

        # Initialize axes control
        axes, _ = self.get_axes_data()
        pitools.startup(self.device, stages=list(axes.values()))

    def set_home(self, axis=None, position=None):
        """
        Set either current positions or entered position as home.
        :param position: (dict) {"R": #.##, "S": #.##, "T": #.##}
        """
        if self.device is not None:
            if axis is not None and "NOSTAGE" not in self.axes_data[axis]["name"]:
                if position:
                    self.move_by(axis, position)
                self.device.DFH(axes=axis)
            elif axis is None:
                for each_axis in self.axes_data:
                    if position:
                        self.move_by(each_axis, position)
                    self.device.DFH(axes=each_axis)


class AtlasCam:

    def __init__(self, device_id=0):
        # Variables
        self.current_frame = np.array([])
        self.device = None
        self.device_id = device_id
        self.is_streaming = False
        self.wait_time = 0.1
        self.node_map = []
        self.scale_window = 3
        self.stream_thread = threading.Thread(target=self.thread_stream, daemon=True)

        # Settings
        self.auto_exposure = False
        self.auto_gain = False
        self.gamma_enable = False
        self.exposure_us = 16667
        self.fps = 1.687439
        self.gain = 0
        self.gamma = 1
        self.pixel_mode = "Mono16"  # "Mono16"

        self.open()

    def open(self):
        """
        Initiate a connection to the available camera, set default settings, and start streaming image data.
        """
        start = time.time()
        devices = system.create_device()
        if devices:
            print("\nCreated %i Atlas device(s)." % len(devices))
            device = devices[int(self.device_id)]
        else:
            error_check(201, currentframe())
            return

        # Enable stream auto negotiate packet size & packet resend
        stream_node_map = device.tl_stream_nodemap
        stream_node_map["StreamBufferHandlingMode"].value = "NewestOnly"  # for video
        stream_node_map['StreamAutoNegotiatePacketSize'].value = True
        stream_node_map['StreamPacketResendEnable'].value = True

        # Set AOI to maximum
        nodes = device.nodemap.get_node(['Width', 'Height'])
        try:
            nodes['Width'].value = nodes['Width'].max
            nodes['Height'].value = nodes['Height'].max
        except Exception:  # TODO: what exception?
            error_check(203, currentframe())
            return

        # Output
        self.device = device
        self.node_map = self.device.nodemap

        # Set settings
        defaults = {
            "PixelFormat": self.pixel_mode,
            "AcquisitionFrameRateEnable": True
        }
        self.set_settings(defaults)
        self.set_gain()
        self.set_gamma()
        self.set_exposure()
        self.set_fps()

        # Stat streaming data frames
        self.start_stream()

    def set_settings(self, settings, attempts=10):
        """
        Send settings to change for Atlas camera. May need adaption for untested input settings.
        :param settings: (dict) Dictionary of tool name to change and the new value.
        """
        ok = False
        attempt = 0
        if self.device is not None:
            while not ok:
                try:
                    if settings != {}:
                        for tool_name in settings:
                            node = self.node_map.get_node(tool_name)  # TODO: check if tool_name is not valid name
                            new_tool_value = settings[tool_name]
                            interface = node.interface_type.value
                            if interface == 9:  # enumerator
                                options = node.enumentry_names
                                if new_tool_value in options:
                                    node.value = new_tool_value
                                else:
                                    error_check(205, currentframe())
                                    print(f'{tool_name} options: {options}')
                            elif interface == 3:  # boolean
                                node.value = new_tool_value
                            elif interface == 5:  # float
                                new_tool_value = float(new_tool_value)
                                min_value = node.min
                                max_value = node.max
                                if min_value <= new_tool_value <= max_value:
                                    node.value = new_tool_value
                                else:
                                    if abs(new_tool_value - min_value) < abs(new_tool_value - max_value):
                                        node.value = min_value
                                    else:
                                        node.value = max_value
                                    print(f'{tool_name} input out of range, setting to {node.value}.')
                        time.sleep(self.wait_time)
                        ok = True
                except TimeoutError as er:
                    if attempt == attempts:
                        break
                    else:
                        print(attempt, er)
                        attempt += 1

    def set_exposure(self, new_value=None, auto=False):
        """
        Set exposure time in microseconds, or auto-exposure mode.
        :param auto: (bool) Turn off or on auto-exposure
        :param new_value: (float) Exposure time [us]
        """
        if self.device is not None:
            auto_name = "ExposureAuto"
            tool_name = "ExposureTime"
            auto_str = "Off"

            self.auto_exposure = auto
            if self.auto_exposure:
                auto_str = "Continuous"
                tool_dict = {auto_name: auto_str}
            else:
                if new_value is not None:
                    self.exposure_us = float(new_value)
                tool_dict = {auto_name: auto_str, tool_name: self.exposure_us}
            self.set_settings(tool_dict)

        return self.exposure_us

    def set_gain(self, new_value=None, auto=False):
        """
        Set gain, or auto-gain mode.
        :param auto: (bool) Turn off or on auto-gain
        :param new_value: (float) Gain value
        """
        if self.device is not None:
            auto_name = "GainAuto"
            tool_name = "Gain"
            auto_str = "Off"

            self.auto_gain = auto
            if self.auto_gain:
                auto_str = "On"
                tool_dict = {auto_name: auto_str}
            else:
                if new_value is not None:
                    self.gain = float(new_value)
                tool_dict = {auto_name: auto_str, tool_name: self.gain}
            self.set_settings(tool_dict)

        return self.gain

    def set_gamma(self, new_value=None, enable=True):
        """
        Set gamma, or auto-gamma mode.
        :param enable: (bool) Turn off or on auto-gamma
        :param new_value: (float) Gamma value
        """
        if self.device is not None:
            auto_name = "GammaEnable"
            tool_name = "Gamma"

            self.gamma_enable = enable
            if self.gamma_enable:
                if new_value is not None:
                    self.gamma = float(new_value)
                tool_dict = {auto_name: self.gamma_enable, tool_name: self.gamma}
            else:
                tool_dict = {auto_name: self.gamma_enable}
            self.set_settings(tool_dict)

        return self.gamma

    def set_fps(self, new_value=None):
        if self.device is not None:
            tool_name = "AcquisitionFrameRate"

            if new_value is not None:
                self.fps = float(new_value)

            tool_dict = {tool_name: self.fps}
            self.set_settings(tool_dict)

        return self.fps

    def close(self):
        """
        Stop stream and close device.
        """
        if self.device is not None:
            if self.is_streaming:
                self.stop_stream()
            system.destroy_device()

    def start_stream(self):
        """
        Start streaming image data from camera with threading.
        """
        if self.device is not None:
            self.is_streaming = True
            self.device.start_stream()
            self.stream_thread.start()
            time.sleep(self.wait_time)

    def thread_stream(self):
        """
        Background thread for grabbing raw image data and assigning it to self.current_frame.
        """
        while self.is_streaming:
            try:
                image_buffer = self.device.get_buffer()
                image_data = ctypes.cast(image_buffer.pdata, ctypes.POINTER(ctypes.c_ushort))
                current_frame = np.ctypeslib.as_array(image_data, (image_buffer.height, image_buffer.width))
                while not current_frame.any():
                    time.sleep(0.01)
                self.current_frame = current_frame
                self.device.requeue_buffer(image_buffer)
            except Exception as er:
                pass
        self.stream_thread = threading.Thread(target=self.thread_stream, daemon=True)

    def stop_stream(self):
        """
        Stop streaming image data from camera.
        """
        if self.device is not None:
            self.is_streaming = False
            time.sleep(self.wait_time)
            self.device.stop_stream()

    def image_capture(self, save_path=""):
        """
        Save latest image frame to input path.
        :param save_path: (str) Path to where image should be saved. Default: current directory.
        """
        if self.device is not None:
            if save_path == "":
                save_path = os.path.join(os.getcwd(), "captured_image.png")
            save_path = check_path(save_path)
            cv2.imwrite(save_path, self.current_frame)
            print("Saved image to:", save_path)

    def live_video(self):
        """
        Display streamed image data onto an OpenCV window.
        """
        if self.device is not None:
            window_name = "Atlas Vision"
            if len(self.current_frame.shape) == 2:
                h, w = self.current_frame.shape
            elif len(self.current_frame.shape) == 3:
                h, w, _ = self.current_frame.shape
            else:
                h, w = 4000, 4000
            w = int(w / self.scale_window)
            h = int(h / self.scale_window)
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, w, h)
            while 1:
                try:
                    cv2.imshow(window_name, self.current_frame)
                    cv2.waitKey(1)
                except cv2.error:
                    pass
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            cv2.destroyAllWindows()


class DC4100(SerialInstrument):
    def __init__(self, com_port: str, log: logging._loggerClass = None):
        super().__init__(com_port=com_port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE, xonxoff=False, log=log)
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


def check_path(save_path):
    """
    Check if file already exists and change name if so.
    :param save_path: (str) Original path to file.
    :return: (str) Corrected path to file.
    """
    if os.path.exists(save_path):
        count = 1
        directory = os.path.split(save_path)[0]
        file_name, file_ext = os.path.split(save_path)[-1].split(".")
        # file_ext = os.path.splitext(file_name)[-1]
        new_file_name = "%s (%i).%s" % (file_name, count, file_ext)
        while os.path.exists(os.path.join(directory, new_file_name)):
            count += 1
            new_file_name = "%s (%i).%s" % (file_name, count, file_ext)
        save_path = os.path.join(directory, new_file_name)

    return save_path

