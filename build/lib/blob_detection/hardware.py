import ctypes, time, cv2, threading, json
import numpy as np
from blob_detection.errors import *
from inspect import currentframe
from pylablib.devices.IMAQdx import IMAQdx


def check_path(save_path):
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


class AmScopeCam:

    def __init__(self, device_id=1):
        # Variables
        self.device = None
        self.current_frame = np.array([])
        self.is_streaming = False
        self.scale_window = 1
        self.stream_thread = threading.Thread(target=self.threaded_stream, daemon=True)

        # Settings
        self.device_id = device_id
        self.exposure_us = 1000000
        self.gain = 0
        self.gamma = 1

        self.open()

    def open(self):
        """
        Initiate a connection to the available camera, set default settings, and start streaming image data.
        """
        device = cv2.VideoCapture(self.device_id, cv2.CAP_DSHOW)
        if not (device.isOpened()):
            error_check(801, currentframe())
        else:
            self.device = device
            self.device.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
            self.set_exposure(self.exposure_us)
            # self.set_gamma(self.gamma)

            self.start_stream()

    def set_exposure(self, new_value=None):
        """
        Set exposure time in microseconds.
        :param new_value: (float) Exposure time [us]
        """
        if self.device is not None:
            if new_value is not None:
                self.exposure_us = float(new_value)
            new_exposure_s = float(self.exposure_us / 1e6)
            value_to_send = np.log(new_exposure_s) / np.log(2)
            self.device.set(cv2.CAP_PROP_EXPOSURE, value_to_send)
            print(float(self.device.get(cv2.CAP_PROP_EXPOSURE)))

    def set_gamma(self, new_value=None):
        """
        Set gamma, or auto-gamma mode.
        :param new_value: (float) Gamma value
        """
        if self.device is not None:
            if new_value is not None:
                self.gamma = float(new_value)
            self.device.set(cv2.CAP_PROP_GAMMA, self.gamma)

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

    def close(self):
        """
        Stop stream and close device.
        """
        if self.device is not None:
            if self.is_streaming:
                self.stop_stream()
            self.device.release()

    def start_stream(self):
        """
        Start streaming image data from camera with threading.
        """
        if self.device is not None:
            self.is_streaming = True
            self.stream_thread.start()
            time.sleep(1)

    def threaded_stream(self):
        """
        Background thread for grabbing raw image data and assigning it to self.current_frame.
        """
        while self.is_streaming:
            ok, frame = self.device.read()
            if ok:
                self.current_frame = frame
            else:
                error_check(802, currentframe())
        self.stream_thread = threading.Thread(target=self.threaded_stream, daemon=True)

    def stop_stream(self):
        """
        Stop streaming image data from camera.
        """
        if self.device is not None:
            self.is_streaming = False

    def live_video(self):
        """
        Display streamed image data onto an OpenCV window.
        """
        if self.device is not None:
            window_name = "AmScope Vision"
            h, w, _ = self.current_frame.shape
            w = int(w / self.scale_window)
            h = int(h / self.scale_window)
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, w, h)
            while 1:
                # shown_img = cv2.cvtColor(self.current_frame.copy(), cv2.COLOR_BGR2RGB)
                shown_img = self.current_frame.copy()
                cv2.imshow(window_name, shown_img)
                cv2.waitKey(1)
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            cv2.destroyAllWindows()


class AmScopeCamNI:

    def __init__(self, device_id=5):
        # Variables
        self.device = None
        self.current_frame = np.array([])
        self.is_streaming = False
        self.scale_window = 3
        self.nodes = {}
        self.stream_thread = threading.Thread(target=self.threaded_stream, daemon=True)

        # Settings
        self.device_id = device_id
        self.exposure_us = 200000
        self.gain = 0
        self.gamma = 1

        self.open()

    def open(self):
        """
        Initiate a connection to the available camera, set default settings, and start streaming image data.
        """
        try:
            device = IMAQdx.IMAQdxCamera('cam%i' % self.device_id)
            self.device = device
            self.nodes = self.device.get_all_attributes().as_dict()
        except:
            error_check(801, currentframe())
            return

        # Send settings
        self.device.enable_raw_readout("frame")
        self.device.set_attribute_value("CameraAttributes/Exposure/Mode", "Manual")
        self.device.set_attribute_value("AcquisitionAttributes/VideoMode", "1920x1520 MJPG 30.00fps")
        self.device.set_roi((0, self.device.get_detector_size()[0], 0, self.device.get_detector_size()[1]))
        # self.set_exposure(self.exposure_us)
        # self.set_gamma(self.gamma)
        # self.set_gain(self.gain)

        self.start_stream()

    def set_exposure(self, new_value=None):
        """
        Set exposure time in microseconds.
        :param new_value: (float) Exposure time [us]
        """
        if self.device is not None:
            attr_min = self.nodes["CameraAttributes"]["Exposure"]["Value"].min
            attr_max = self.nodes["CameraAttributes"]["Exposure"]["Value"].max
            if attr_min <= (float(new_value) / 1e6) <= attr_max:
                if new_value is not None:
                    self.exposure_us = float(new_value)
                self.exposure_us = float(self.exposure_us / 1e6)
                self.device.set_attribute_value("CameraAttributes/Exposure/Value", self.exposure_us)
            else:
                print(f"ERROR: Input out of range: [{attr_min}, {attr_max}]")

    def set_gamma(self, new_value=None):
        """
        Set gamma, or auto-gamma mode.
        :param new_value: (float) Gamma value
        """
        if self.device is not None:
            attr_min = self.nodes["CameraAttributes"]["Gamma"]["Value"].min
            attr_max = self.nodes["CameraAttributes"]["Gamma"]["Value"].max
            if attr_min <= float(new_value) <= attr_max:
                if new_value is not None:
                    self.gamma = float(new_value)
                self.device.set_attribute_value("CameraAttributes/Gamma/Value", self.gamma)
            else:
                print(f"ERROR: Input out of range: [{attr_min}, {attr_max}]")

    def set_gain(self, new_value=None):
        # TODO: THIS ISN'T THE CORRECT GAIN
        if self.device is not None:
            attr_min = self.nodes["AcquisitionAttributes"]["Bayer"]["GainG"].min
            attr_max = self.nodes["AcquisitionAttributes"]["Bayer"]["GainG"].max
            if attr_min <= float(new_value) <= attr_max:
                if new_value is not None:
                    self.gain = float(new_value)
                self.device.set_attribute_value("AcquisitionAttributes/Bayer/GainR", self.gain)
                self.device.set_attribute_value("AcquisitionAttributes/Bayer/GainG", self.gain)
                self.device.set_attribute_value("AcquisitionAttributes/Bayer/GainB", self.gain)
            else:
                print(f"ERROR: Input out of range: [{attr_min}, {attr_max}]")

    def image_capture(self, save_path=""):
        """
        Save latest image frame to input path.
        :param save_path: (str) Path to where image should be saved. Default: current directory.
        """
        if self.device is not None and self.is_streaming:
            if save_path == "":
                save_path = os.path.join(os.getcwd(), "captured_image.png")
            save_path = check_path(save_path)
            img_16 = (self.current_frame.copy() * 256).astype('uint16')
            cv2.imwrite(save_path, img_16)
            print("Saved image to:", save_path)

    def close(self):
        """
        Stop stream and close device.
        """
        if self.device is not None:
            if self.is_streaming:
                self.stop_stream()
            while self.stream_thread.is_alive():
                time.sleep(0.01)
            self.device.close()

    def start_stream(self):
        """
        Start streaming image data from camera with threading.
        """
        if self.device is not None:
            self.is_streaming = True
            self.stream_thread.start()

    def threaded_stream(self):
        """
        Background thread for grabbing raw image data and assigning it to self.current_frame.
        """
        self.device.start_acquisition()
        while self.is_streaming:
            self.device.wait_for_frame()
            frame = self.device.read_oldest_image()
            if frame is not None and frame.any():
                self.current_frame = self.reformat_frame(frame)
            else:
                error_check(802, currentframe())
                break
        self.device.stop_acquisition()
        self.stream_thread = threading.Thread(target=self.threaded_stream, daemon=True)

    def stop_stream(self):
        """
        Stop streaming image data from camera.
        """
        self.is_streaming = False

    def live_video(self):
        """
        Display streamed image data onto an OpenCV window.
        """
        if self.device is not None:
            window_name = "Vision"
            while len(self.current_frame.shape) < 2:
                time.sleep(0.1)
            s = self.current_frame.shape
            w = int(s[0] / self.scale_window)
            h = int(s[1] / self.scale_window)
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, h, w)
            while 1:
                shown_img = self.current_frame.copy()
                # shown_img = np.clip(shown_img * float(10.0), 0, 255).astype(np.uint8)
                cv2.imshow(window_name, shown_img)
                cv2.waitKey(1)
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            cv2.destroyAllWindows()

    def reformat_frame(self, frame):
        if self.device is not None:
            width = self.device.get_attribute_value("AcquisitionAttributes/Width")
            height = self.device.get_attribute_value("AcquisitionAttributes/Height")

            red = frame[0::4].reshape(height, width)
            green = frame[1::4].reshape(height, width)
            blue = frame[2::4].reshape(height, width)
            alpha = frame[3::4].reshape(height, width)
            rgba = np.dstack((red, green, blue, alpha))
            rgb = cv2.cvtColor(rgba, cv2.COLOR_RGBA2RGB)

            return rgb


if __name__ == "__main__":
    dev = AmScopeCamNI(device_id=0)
    dev.live_video()
    dev.close()

    # import libusb_package
    # import usb.core
    # import usb.backend.libusb1
    #
    # libusb1_backend = usb.backend.libusb1.get_backend(find_library=libusb_package.find_library)
    #
    # dev = usb.core.find(idVendor=0xaa47, idProduct=0x12aa, backend=libusb1_backend)
    # print(dev)
