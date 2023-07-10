# -*- coding: utf-8 -*-

import sys, PySide6, matplotlib, json, time, cv2, os, argparse, ctypes, csv
import numpy as np
import blob_detection.hardware as hw
import blob_detection.img_processing as ip
from datetime import datetime
from PySide6 import QtCore
from PySide6.QtGui import (QImage, QPixmap, QCloseEvent, QPalette, QColor)
from PySide6.QtWidgets import (QApplication, QWidget, QFileDialog, QGraphicsScene, QGraphicsPixmapItem)
from blob_detection.ui_form import Ui_Widget


# Adjust debugger and define input arguments for command line call
matplotlib.use('tkagg')
argParser = argparse.ArgumentParser()
argParser.add_argument("-n", "--cam_num", type=int, help="Camera number")


class Widget(QWidget):

    def __init__(self, camera_num, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.threadpool = QtCore.QThreadPool()
        self.main_thread = QtCore.QThread.currentThread()

        # Local Variables ------------------------------------------------------------------------------------------- #
        try:
            self.settings_path = os.path.join(os.getcwd(), "blob_detection\\support\\gui_settings.json")
            with open(self.settings_path) as f:
                self.json_settings = json.load(f)
        except FileNotFoundError:
            self.settings_path = os.path.join(os.getcwd(), "..\\blob_detection\\support\\gui_settings.json")
            with open(self.settings_path) as f:
                self.json_settings = json.load(f)

        self.camera_num = camera_num
        self.camera = None
        self.pixmap = None
        self.is_dialog_open = False
        self.is_closed = False
        self.is_test = False  # set this to True if you do not want to load hardware
        self.is_circle_fit = False
        self.is_zeroed = False
        self.is_frozen = False
        self.folder_path = ""
        self.json_width = 48
        self.output_on_close = 0
        self.zoom = 0
        self.armin_per_pxl = 0
        self.pxl_size_mm = 0
        self.raw_frame = np.array([])
        self.drawn_frame = np.array([])
        self.blob_kpis = {}
        self.set_defaults()

        # Buttons --------------------------------------------------------------------------------------------------- #
        self.ui.camera_capture_button.clicked.connect(self.click_capture)
        self.ui.camera_connect_button.clicked.connect(self.thread_connect_camera)
        self.ui.measure_zero_button.clicked.connect(self.click_zero)
        self.ui.measure_freeze_button.clicked.connect(self.click_freeze)
        self.ui.measure_save_button.clicked.connect(self.click_save)
        self.ui.browse_button.clicked.connect(self.click_browse)
        self.ui.settings_save_config_button.clicked.connect(self.click_save_config)

        # Check Boxes ----------------------------------------------------------------------------------------------- #
        self.ui.settings_circle_fit_check.clicked.connect(self.click_circle_fit)

        # Sliders --------------------------------------------------------------------------------------------------- #
        self.ui.camera_exposure_slider.sliderReleased.connect(self.change_exposure)
        self.ui.camera_gamma_slider.sliderReleased.connect(self.change_gamma)
        self.ui.camera_exposure_slider.valueChanged.connect(lambda: self.change_exposure(just_label=True))
        self.ui.camera_gamma_slider.valueChanged.connect(lambda: self.change_exposure(just_label=True))

        # Spin Boxes ------------------------------------------------------------------------------------------------ #
        self.ui.camera_exposure_spin.editingFinished.connect(lambda: self.change_exposure(spin_change=True))
        self.ui.camera_gamma_spin.editingFinished.connect(lambda: self.change_gamma(spin_change=True))
        self.ui.camera_com_spin.editingFinished.connect(self.do_pass)

        # Threads --------------------------------------------------------------------------------------------------- #
        if not self.is_test:
            self.thread_connect_camera()

    def closeEvent(self, event: QCloseEvent):
        """
        Custom call for when close event is called on main window.
        :param event: (QCloseEvent) Qt flag of closing event.
        """
        self.hide()
        self.is_closed = True
        time.sleep(1)

        if self.camera is not None:
            self.camera.close()

        print("CLOSED")

    def wheelEvent(self, event):
        """
        Custom call for scrolling wheel on mouse. Applies to only region with live stream.
        :param event: (QEvent) Qt flag for any event.
        """
        if self.pixmap is not None:
            if (20 < event.position().x() < 475) and (40 < event.position().y() < 375):
                if event.angleDelta().y() > 0:
                    factor = 1.25
                    self.zoom += 1
                else:
                    factor = 0.8
                    self.zoom -= 1

                if self.zoom > 0:
                    self.ui.stream_window.scale(factor, factor)
                elif self.zoom == 0:
                    self.full_screen()
                else:
                    self.zoom = 0

        super(Widget, self).wheelEvent(event)

    def change_exposure(self, spin_change=False, just_label=False):
        """
        Change exposure settings on camera.
        :param spin_change: (bool) Was this change initiated by the spin box?
        :param just_label: (bool) Was this change initiated by the slider?
        """
        if spin_change:
            new_value = int(self.ui.camera_exposure_spin.value())
            self.ui.camera_exposure_slider.setValue(new_value)
        else:
            new_value = int(self.ui.camera_exposure_slider.value())
            self.ui.camera_exposure_spin.setValue(new_value)

        if not just_label and self.camera is not None:
            self.camera.set_exposure(new_value=new_value)

    def change_gamma(self, spin_change=False, just_label=False):
        """
        Change gamma settings on camera.
        :param spin_change: (bool) Was this change initiated by the spin box?
        :param just_label: (bool) Was this change initiated by the slider?
        """
        if spin_change:
            new_value = float(self.ui.camera_gamma_spin.value())
            self.ui.camera_gamma_slider.setValue(new_value * 10)
        else:
            new_value = float(self.ui.camera_gamma_slider.value()) / 10
            self.ui.camera_gamma_spin.setValue(new_value)

        if not just_label and self.camera is not None:
            self.camera.set_gamma(new_value=new_value)

    def click_browse(self):
        """
        Action for clicking the folder browse button.
        """
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path != "":
            self.ui.save_path_entry.setText(folder_path)
            self.folder_path = folder_path

    def click_capture(self):
        """
        Action for clicking the 'Capture' button.
        """
        if self.camera is not None:
            # Check folder path
            folder = self.ui.save_path_entry.toPlainText()
            if not os.path.exists(folder):
                os.mkdir(folder)

            # Get file name or generate one
            image_name = self.ui.camera_file_name_entry.toPlainText()
            if image_name == "":
                now = datetime.now()
                exposure_us = int(self.ui.camera_exposure_spin.text())
                gamma_10 = int(float(self.ui.camera_gamma_spin.text()))
                image_name = "image_%s_%sus_%s.png" % (now.strftime("%Y%m%d-%H%M%S"), exposure_us, gamma_10)
            elif not image_name.endswith(".png"):
                image_name = "%s.png" % image_name

            # Check path and save
            image_path = hw.check_path(os.path.join(folder, image_name))
            self.thread_save_image(image_path, self.raw_frame)

    def click_circle_fit(self):
        """
        Action for clicking the 'Circle fit' toggle.
        """
        if self.ui.settings_circle_fit_check.isChecked():
            self.is_circle_fit = True
            self.ui.settings_circularity_min_spin.setEnabled(True)
            self.ui.settings_circularity_max_spin.setEnabled(True)
        else:
            self.is_circle_fit = False
            self.ui.settings_circularity_min_spin.setEnabled(False)
            self.ui.settings_circularity_max_spin.setEnabled(False)

    def click_freeze(self):
        """
        Action for clicking the 'Freeze' button.
        """
        if self.is_frozen:
            is_frozen = False
            self.ui.measure_freeze_button.setText("Freeze")
            self.ui.measure_save_button.setEnabled(True)
        else:
            is_frozen = True
            self.ui.measure_freeze_button.setText("Unfreeze")
        self.is_frozen = is_frozen

    def click_save(self):
        """
        Action for clicking the 'Save' button.
        """
        # Disable button to avoid repeat conflict
        self.ui.measure_save_button.setEnabled(False)

        # Make or get file path
        file_name = self.ui.measure_file_name_entry.toPlainText()
        if file_name == "":
            now = datetime.now().strftime("%Y%m%d-%H%M%S")
            file_name = "bob_data_%s" % now
        file_path = os.path.join(self.folder_path, "%s.csv" % file_name)

        # Get relevant parameters and save to CSV
        input_params = self.make_params_dict()
        if not os.path.exists(file_path):
            with open(file_path, "w", newline="") as f:
                writer_object = csv.writer(f)
                writer_object.writerow(list(input_params.keys()))
                f.close()
        else:  # get measurement number
            with open(file_path, "r", newline="") as f:
                reader_object = csv.reader(f)
                data = list(reader_object)
            input_params["Measurement"] = int(data[-1][0]) + 1
        with open(file_path, "a", newline="") as f:
            writer_object = csv.writer(f)
            writer_object.writerow(list(input_params.values()))
            f.close()

        # Save image with data
        image_path = os.path.join(self.folder_path, "M%i.png" % input_params["Measurement"])
        self.thread_save_image(image_path, self.raw_frame)

        # Enable save button
        self.ui.measure_save_button.setEnabled(True)

    def click_save_config(self):
        """
        Action for clicking the 'Save to Config' button.
        """
        contour_limits = [self.ui.settings_contour_limits_min_spin.value(),
                          self.ui.settings_contour_limits_max_spin.value()]
        threshold = self.ui.settings_threshold_spin.value()
        circularity = [self.ui.settings_circularity_min_spin.value(), self.ui.settings_circularity_max_spin.value()]
        circle_fit = int(self.ui.settings_circle_fit_check.isChecked())
        exposure = self.ui.camera_exposure_spin.value()
        gamma = self.ui.camera_gamma_spin.value()

        answer = self.dialog_prompt("Save current settings as default and overwrite the config file?", button=0x04)
        if answer == 6:
            self.json_settings["Detection"]["Threshold"] = threshold
            self.json_settings["Detection"]["Contours"] = contour_limits
            self.json_settings["Detection"]["Circularity"] = circularity
            self.json_settings["Detection"]["Circle Fit"] = circle_fit
            self.json_settings["Camera"]["Exposure us"] = exposure
            self.json_settings["Camera"]["Gamma"] = gamma
            with open(self.settings_path, "w") as f:
                json.dump(self.json_settings, f, indent=4)

    def click_zero(self):
        """
        Action for clicking the 'Set Zero' button.
        """
        self.is_zeroed = True
        self.ui.measure_zero_button.setEnabled(False)

    def dialog_prompt(self, message, button=0x0, level=0):
        """
        Display dialog box to prompt or inform the user.
        :param button: (hex) Options: 0x0 = OK, 0x01 = OK/CANCEL, 0x03 = YES/NO/CANCEL, 0x04 = YES/NO
        :param message: (str) Message to display in box.
        :param level: (int) 0 = prompt, 1 = warning, 2 = error
        :return: (int) Response from user.
        """
        mb_sys_modal = 0x00001000
        message = bytes(message, 'utf-8')
        title = b"Action Required"
        icon = 0x40
        if level == 1:
            title = b"Warning"
            icon = 0x30
        elif level == 2:
            title = b"ERROR"
            icon = 0x10

        self.is_dialog_open = True
        dialog_answer = ctypes.windll.user32.MessageBoxA(0, message, title, button | icon | mb_sys_modal)
        self.is_dialog_open = False

        return dialog_answer

    def do_pass(self):
        """
        Do nothing (for debugging).
        """
        pass

    def full_screen(self):
        """
        Full screen the image on the streaming window.
        """
        rect = QtCore.QRectF(self.pixmap.rect())
        if not rect.isNull():
            self.ui.stream_window.setSceneRect(rect)
            unity = self.ui.stream_window.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.ui.stream_window.scale(1 / unity.width(), 1 / unity.height())
            view_rect = self.ui.stream_window.viewport().rect()
            scene_rect = self.ui.stream_window.transform().mapRect(rect)
            factor = min(view_rect.width() / scene_rect.width(), view_rect.height() / scene_rect.height())
            self.ui.stream_window.scale(factor, factor)
            self.zoom = 0

    def make_params_dict(self):
        """
        Make a parameter dictionary for CSV saving.
        """
        now = datetime.now()
        input_params = {
            "Measurement": 0,
            "Date": now.strftime("%m-%d-%Y"),
            "Time": now.strftime("%H:%M:%S"),
            "X0 (pxl)": self.blob_kpis["zero"][0], "Y0 (pxl)": self.blob_kpis["zero"][1],
            "dX (arcmin)": self.blob_kpis["delta"][0], "dY (arcmin)": self.blob_kpis["delta"][1],
            "Saturation (%)": self.blob_kpis["saturation"],
            "Light Level": self.blob_kpis["level"],
            "Side": self.ui.parameters_side_combo.currentText(),
            "SN": self.ui.parameters_sn_entry.toPlainText(),
            "Operator": self.ui.parameters_operator_entry.toPlainText(),
            "Exposure": self.ui.camera_exposure_spin.value(),
            "Gamma": self.ui.camera_gamma_spin.value(),
            "Blob Min": self.ui.settings_contour_limits_min_spin.value(),
            "Blob Max": self.ui.settings_contour_limits_max_spin.value(),
            "Threshold": self.ui.settings_threshold_spin.value(),
            "Circle Fit": bool(self.ui.settings_circle_fit_check.isChecked()),
            "Circle Min": self.ui.settings_circularity_min_spin.value(),
            "Circle Max": self.ui.settings_circularity_max_spin.value(),
            "Comments": self.ui.parameters_sn_entry.toPlainText(),
            "": "",
            "Code Version": self.json_settings["Version"],
            "Camera": "%s+%s" % (self.json_settings["Camera"]["Sensor"], self.json_settings["Camera"]["Lens"]),
            "Pixel Size (mm)": self.json_settings["Camera"]["Pixel Size mm"],
            "AMPF": self.json_settings["Camera"]["Arcmin/pxl"],
            "Poly Fit": self.json_settings["Detection"]["Poly Fit"],
            "Gaussian": self.json_settings["Detection"]["Gaussian"],
            "Feature Size": self.json_settings["Detection"]["Feature Size"]
        }

        return input_params

    def set_defaults(self):
        """
        Set defaults on GUI based on settings json.
        """
        # Other
        self.armin_per_pxl = self.json_settings["Camera"]["Arcmin/pxl"]
        self.pxl_size_mm = self.json_settings["Camera"]["Pixel Size mm"]
        device_id = self.json_settings["Camera"]["ID"]
        self.folder_path = self.json_settings["Save Path"]
        self.blob_kpis = {"zero": (0, 0), "detected": (0, 0), "delta": (0, 0), "saturation": 0, "level": ""}

        # GUI values
        self.ui.camera_exposure_spin.setValue(self.json_settings["Camera"]["Exposure us"])
        self.ui.camera_gamma_spin.setValue(self.json_settings["Camera"]["Gamma"])
        self.ui.save_path_entry.setText(self.json_settings["Save Path"])
        self.ui.camera_com_spin.setValue(device_id)

        self.ui.settings_threshold_spin.setValue(self.json_settings["Detection"]["Threshold"])
        self.ui.settings_contour_limits_min_spin.setValue(self.json_settings["Detection"]["Contours"][0])
        self.ui.settings_contour_limits_max_spin.setValue(self.json_settings["Detection"]["Contours"][1])
        self.ui.settings_circularity_min_spin.setValue(self.json_settings["Detection"]["Circularity"][0])
        self.ui.settings_circularity_max_spin.setValue(self.json_settings["Detection"]["Circularity"][1])
        self.ui.settings_circle_fit_check.setChecked(bool(self.json_settings["Detection"]["Circle Fit"]))
        if self.ui.settings_circle_fit_check.isChecked():
            self.ui.settings_circularity_min_spin.setEnabled(True)
            self.ui.settings_circularity_max_spin.setEnabled(True)
        self.ui.stream_label.setText("Camera Stream %i" % device_id)

    def thread_connect_camera(self):
        """
        Thread call for connecting and initializing the present camera.
        """
        worker = ThreadLoadHW(1, parent=self)
        self.threadpool.start(worker)

    def thread_save_image(self, save_path, frame_to_save):
        """
        Thread call for saving an image.
        :param save_path: (str) Path to where image should be saved including file name.
        :param frame_to_save: (np.array) Image frame to save.
        """
        worker = ThreadSave(save_path, frame_to_save, parent=self)
        self.threadpool.start(worker)

    def thread_stream(self):
        """
        Thread call for starting the camera stream to UI main window..
        """
        worker = ThreadStream(parent=self)
        self.threadpool.start(worker)


class ThreadLoadHW(QtCore.QRunnable):
    def __init__(self, device, parent=None):
        """
        Load hardware connections.
        :param parent: (QWidget) Qt main window handle.
        :param device: 0=stages, 1=camera, 2=dc4100 (1), 3=dc4100 (2)
        """
        super().__init__()
        self.root = parent
        self.device = device

    @QtCore.Slot()
    def start(self):
        """
        Connect slot to run() function.
        """
        if not self.root.is_test:
            self.run()

    def run(self):
        """
        Run thread: Connect to hardware after GUI has opened.
        """
        # Connect to camera
        if self.device == 1:
            self.root.ui.camera_connect_button.setEnabled(False)
            if self.root.camera is None:
                if self.root.json_settings["Camera"]["Sensor"] == "AmScope":
                    self.root.camera = hw.AmScopeCamNI(self.root.json_settings["Camera"]["ID LR"][self.root.camera_num])
                if self.root.camera.device is not None:
                    print("CAMERA SUCCESS")
                    self.change_color(self.root.ui.camera_connect_indicator, "green")
                    self.root.change_exposure(spin_change=True)
                    self.root.change_gamma(spin_change=True)
                    self.root.thread_stream()
                else:
                    print("CAMERA FAILURE")
                    self.change_color(self.root.ui.camera_connect_indicator, "red")
                    self.root.camera = None
            else:
                self.change_color(self.root.ui.camera_connect_indicator, "gray")
                self.root.camera.close()
                self.root.camera = None
            self.root.ui.camera_connect_button.setEnabled(True)

    def change_color(self, indicator, color):
        """
        Change the color of the status indicator on main GUI.
        :param indicator: (QRadioButton) Handle to correct indicator/radio button.
        :param color: (str) Color to change to.
        """
        indicator.setStyleSheet("QRadioButton::indicator{background-color : %s}" % color)


class ThreadStream(QtCore.QRunnable):

    def __init__(self, parent=None):
        """
        Stream image frames from connected camera.
        :param parent: (QWidget) Qt main window handle.
        """
        super().__init__()
        self.root = parent
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.feature_size = 8
        self.colors = ["R", "G", "B"]
        self.is_first = True

    @QtCore.Slot()
    def start(self):
        """
        Connect slot to run() function.
        """
        if not self.root.is_test:
            self.run()

    def run(self):
        """
        Run thread: Stream image with blob detection and saturation measurements.
        """
        while self.root.camera is None:
            time.sleep(0.01)

        while not self.root.is_closed:
            try:
                # Get frame and format it into RGB 8-bit
                while self.root.is_dialog_open is None:
                    time.sleep(0.01)
                self.root.raw_frame = self.root.camera.current_frame.copy()
                self.get_saturation()
                self.detect_blob()
                if self.root.drawn_frame.any():
                    img_array = self.root.drawn_frame.copy()
                else:
                    img_array = self.root.raw_frame.copy()
                img_array = ip.convert_color_bit(img_array, "rgb", 8)

                if img_array.any():
                    s = img_array.shape
                    pic = QGraphicsPixmapItem()
                    self.root.pixmap = QPixmap.fromImage(QImage(img_array, s[1], s[0], 3 * s[1], QImage.Format_RGB888))
                    pic.setPixmap(self.root.pixmap)
                    self.root.ui.scene = QGraphicsScene()
                    self.root.ui.scene.addItem(pic)
                    self.root.ui.stream_window.setScene(self.root.ui.scene)

                    if self.is_first:
                        self.root.full_screen()
                        self.is_first = False
            except (AttributeError, IndexError) as er:
                pass
            except Exception as er:
                print(er)
                pass

    def detect_blob(self):
        """
        Detect blobs in current image frame.
        """
        if self.root.raw_frame.any():
            # Detect blob with settings
            threshold = self.root.ui.settings_threshold_spin.value()
            contours = [self.root.ui.settings_contour_limits_min_spin.value(),
                        self.root.ui.settings_contour_limits_max_spin.value()]
            circle_limits = [self.root.ui.settings_circularity_min_spin.value(),
                             self.root.ui.settings_circularity_max_spin.value()]
            self.root.drawn_frame, detected = ip.detect_blob(self.root.raw_frame, threshold=threshold,
                                                             contour_limits=contours, circle_limits=circle_limits,
                                                             zero_point=self.root.blob_kpis["zero"],
                                                             m_point=self.root.blob_kpis["detected"],
                                                             fit_circle=self.root.is_circle_fit)

            # Add cross-hairs if requested
            if self.root.ui.settings_crosshairs_check.isChecked() and self.root.drawn_frame.any():
                s = self.root.drawn_frame.shape
                feature_sz = self.root.json_settings["Detection"]["Feature Size"]
                ch_center = (int(s[1] / 2), int(s[0] / 2))
                cv2.line(self.root.drawn_frame, (ch_center[0], (ch_center[1] - feature_sz * 10)),
                         (ch_center[0], (ch_center[1] + feature_sz * 10)), (0, 0, 0), thickness=feature_sz)
                cv2.line(self.root.drawn_frame, ((ch_center[0] - feature_sz * 10), ch_center[1]),
                         ((ch_center[0] + feature_sz * 10), ch_center[1]), (0, 0, 0), thickness=feature_sz)

            # Update stored KPIs
            self.root.ui.measure_detected_position.setText("(%i, %i)" % (detected[0], detected[1]))
            if self.root.is_zeroed:
                answer = 6
                if self.root.blob_kpis["zero"] != (0, 0):
                    answer = self.root.dialog_prompt("Zero already set. Would you like to overwrite?", button=0x04)
                if answer == 6:
                    self.root.blob_kpis["zero"] = detected
                    self.root.ui.measure_zero_position.setText("(%i, %i)" % (self.root.blob_kpis["zero"][0],
                                                                             self.root.blob_kpis["zero"][1]))
                    self.root.is_zeroed = False
                    self.root.ui.measure_zero_button.setEnabled(True)
            if not self.root.is_frozen:
                self.root.blob_kpis["detected"] = detected
                delta = ((self.root.blob_kpis["detected"][0] - self.root.blob_kpis["zero"][0]) * self.root.armin_per_pxl,
                         (self.root.blob_kpis["zero"][1] - self.root.blob_kpis["detected"][1]) * self.root.armin_per_pxl)
                self.root.blob_kpis["delta"] = delta
                self.root.ui.measure_delta_position.setText("(%.3f, %.3f)" % (self.root.blob_kpis["delta"][0],
                                                                              self.root.blob_kpis["delta"][1]))

    def get_saturation(self):
        """
        Calculate saturation levels in current image frame.
        :return:
        """
        if self.root.raw_frame.any():
            measure_frame = ip.convert_color_bit(self.root.raw_frame.copy(), "mono", 16)

            # Calculate brightness (not currently used)
            total_pixels = measure_frame.shape[0] * measure_frame.shape[1]
            brightness = np.sum(measure_frame, dtype='uint64') / total_pixels

            # Define the saturation of the image
            frame_flat = np.array(measure_frame.copy().flatten())
            sat_limits = [int((2 ** 16 - 256) * 0.50), int((2 ** 16 - 256) * 0.95)]  # low: 50%, high: 95%
            sat_threshold = round(0.001 * total_pixels)  # typically 0.00001 not 0.001
            sat_array = frame_flat[frame_flat >= sat_limits[0]]
            is_low_sat = bool(len(sat_array) <= sat_threshold)
            if not is_low_sat:
                sat_array = frame_flat[frame_flat >= sat_limits[1]]
                is_high_sat = bool(len(sat_array) >= sat_threshold)
            else:
                is_high_sat = False
            sat_percent = (sat_array >= sat_limits[1]).sum() / total_pixels * 100

            # Update GUI widgets
            self.root.ui.saturation_value_label.setText("%.4f %%" % sat_percent)
            palette = self.root.ui.saturation_status_label.palette()
            if is_high_sat:
                label_style = ["HIGH", "red"]
            elif is_low_sat:
                label_style = ["LOW", "red"]
            else:
                label_style = ["GOOD", "green"]
            palette.setColor(QPalette.WindowText, QColor(label_style[1]))
            self.root.ui.saturation_status_label.setPalette(palette)
            self.root.ui.saturation_status_label.setText(label_style[0])

            # Add data to KPIs
            self.root.blob_kpis["saturation"] = sat_percent
            self.root.blob_kpis["level"] = label_style[0]


class ThreadSave(QtCore.QRunnable):
    def __init__(self, save_path, frame_to_save, parent=None):
        """
        Stream image frames from connected camera.
        :param save_path: (str) Path to where image should be saved including file name.
        :param frame_to_save: (np.array) Image frame to save.
        :param parent: (QWidget) Qt main window handle.
        """
        super().__init__()
        self.frame_to_save = frame_to_save
        self.save_path = hw.check_path(save_path)
        self.root = parent

    @QtCore.Slot()
    def start(self):
        """
        Connect slot to run() function.
        """
        if not self.root.is_test:
            self.run()

    def run(self):
        """
        Run thread: Save input image
        """
        if not self.root.is_closed:
            cv2.imwrite(self.save_path, cv2.cvtColor(self.frame_to_save, cv2.COLOR_BGR2RGB))


def launch_gui(camera_num):
    """
    Launch the main GUI.
    :param camera_num: (int) Camera ID.
    """
    args = dict(argParser.parse_args()._get_kwargs())
    if args["cam_num"] is not None:
        camera_num = args["cam_num"]
    app = QApplication(sys.argv)
    widget = Widget(camera_num)
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_gui(0)
