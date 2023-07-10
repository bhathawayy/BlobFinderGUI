import sys, PySide6, matplotlib, json, time, cv2, os, math, argparse
import blob_detection.hardware as hw
import blob_detection.img_processing as ip
import pandas as pd
import numpy as np
from PySide6 import QtCore
from datetime import datetime
# from PySide6.QtCore import Qt
from PySide6.QtGui import (QImage, QPixmap, QCloseEvent)
from PySide6.QtWidgets import (QApplication, QWidget, QFileDialog, QGraphicsScene, QGraphicsPixmapItem)
from datetime import datetime
from blob_detection.ui_form_sep import Ui_Widget

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

        # Variables ------------------------------------------------------------------------------------------------- #
        self.settings_path = os.path.join(os.getcwd(), "blob_detection\\support\\gui_settings.json")
        with open(self.settings_path) as f:
            self.json_settings = json.load(f)
        self.camera_num = camera_num
        self.camera = None
        self.pixmap = None
        self.is_closed = False
        self.is_test = False
        self.is_zeroed = False
        self.folder_path = ""
        self.is_frozen = False
        self.csv_data = {"zero x": np.array([]), "zero y": np.array([]),
                         "detected x": np.array([]), "detected y": np.array([]),
                         "delta x": np.array([]), "delta y": np.array([])}
        self.json_width = 48
        self.output_on_close = 0
        self.zoom = 0
        self.pxl_size_mm = 0
        self.raw_frame = np.array([])
        self.drawn_frame = np.array([])
        self.set_defaults()

        # Buttons --------------------------------------------------------------------------------------------------- #
        self.ui.camera_capture_button.clicked.connect(self.click_capture)
        self.ui.camera_connect_button.clicked.connect(self.thread_connect_camera)
        self.ui.measure_zero_button.clicked.connect(self.click_zero)
        self.ui.measure_freeze_button.clicked.connect(self.click_freeze)
        self.ui.measure_save_button.clicked.connect(self.click_save)
        self.ui.browse_button.clicked.connect(self.click_browse)

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
        if spin_change:
            new_value = int(self.ui.camera_exposure_spin.value())
            self.ui.camera_exposure_slider.setValue(new_value)
        else:
            new_value = int(self.ui.camera_exposure_slider.value())
            self.ui.camera_exposure_spin.setValue(new_value)

        if not just_label and self.camera is not None:
            self.camera.set_exposure(new_value=new_value)

    def change_gamma(self, spin_change=False, just_label=False):
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

    def click_freeze(self):
        if self.is_frozen:
            is_frozen = False
            self.ui.measure_freeze_button.setText("Freeze")
            self.ui.measure_save_button.setEnabled(True)
        else:
            is_frozen = True
            self.ui.measure_freeze_button.setText("Unfreeze")
        self.is_frozen = is_frozen

    def click_zero(self):
        self.is_zeroed = True
        self.ui.measure_zero_button.setEnabled(False)

    def click_capture(self):
        """
        Action for clicking the CAPTURE button.
        """
        if self.camera is not None:
            # Check folder path
            folder = self.ui.save_path_entry.toPlainText()
            if not os.path.exists(folder):
                os.mkdir(folder)

            # Get  variables for path
            now = datetime.now()
            exposure_us = int(self.ui.camera_exposure_spin.text())
            gamma_10 = int(float(self.ui.camera_gamma_spin.text()))
            image_name = "image_%s_%sus_%s.png" % (now.strftime("%Y%m%d-%H%M%S"), exposure_us, gamma_10)

            # Check path and save
            image_path = hw.check_path(os.path.join(folder, image_name))
            self.thread_save_image(image_path, self.raw_frame)

    def click_save(self):
        # Create data array for CSV
        for i, key in enumerate(self.csv_data):
            if i == 0:
                csv_array = self.csv_data[key].reshape(-1, 1)
            else:
                csv_array = np.hstack((csv_array, self.csv_data[key].reshape(-1, 1)))

        # Create file name
        file_name = self.ui.measure_file_name_entry.toPlainText()
        if file_name == "":
            now = datetime.now().strftime("%Y%m%d-%H%M%S")
            file_name = "bob_data_%s" % now
        file_path = os.path.join(self.folder_path, "%s.csv" % file_name)

        # Check path to append or write
        if os.path.exists(file_path):
            pd.DataFrame(csv_array).to_csv(file_path, header=False, mode='a', index=False)
        else:
            pd.DataFrame(csv_array).to_csv(file_path, header=list(self.csv_data.keys()), index=False)

        # Clear saved data
        self.csv_data = {"zero x": np.array([]), "zero y": np.array([]),
                         "detected x": np.array([]), "detected y": np.array([]),
                         "delta x": np.array([]), "delta y": np.array([])}
        self.ui.measure_save_button.setEnabled(False)

    def do_pass(self):
        pass

    def full_screen(self):
        """
        Full screen image or image frame on streaming window.
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

    def set_defaults(self):
        # Other
        self.pxl_size_mm = self.json_settings["Camera"]["Pixel Size mm"]
        device_id = self.json_settings["Camera"]["ID"][self.camera_num]
        self.folder_path = self.json_settings["Save Path"]

        # GUI values
        self.ui.camera_exposure_spin.setValue(self.json_settings["Camera"]["Exposure us"])
        self.ui.camera_gamma_spin.setValue(self.json_settings["Camera"]["Gamma"])
        self.ui.save_path_entry.setText(self.json_settings["Save Path"])
        self.ui.camera_com_spin.setValue(device_id)
        self.ui.stream_label.setText("Camera %i Stream" % device_id)

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

    # @QtCore.Slot()
    def start(self):
        """
        Connect slot to run() function.
        """
        if not self.root.is_test:
            self.run()

    def run(self):
        """
        Run thread.
        """
        # Connect to camera
        if self.device == 1:
            self.root.ui.camera_connect_button.setEnabled(False)
            if self.root.camera is None:
                if self.root.json_settings["Camera"]["Sensor"] == "AmScope":
                    self.root.camera = hw.AmScopeCamNI(self.root.json_settings["Camera"]["ID"][self.root.camera_num])
                # elif self.json_settings["Camera"]["Sensor"] == "EXAMPLE":
                #     self.root.camera = hw.EXAMPLE_CALL(self.json_settings["Camera"]["ID"])

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
        self.is_recorded = False
        self.blob_kpis = {"zero": (0, 0), "detected": (0, 0), "delta": (0, 0)}

    @QtCore.Slot()
    def start(self):
        """
        Connect slot to run() function.
        """
        if not self.root.is_test:
            self.run()

    def run(self):
        """
        Run thread.
        """
        while self.root.camera is None:
            time.sleep(0.01)

        while not self.root.is_closed:
            try:
                # Get frame and format it into RGB 8-bit
                self.root.raw_frame = self.root.camera.current_frame.copy()
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
            except (AttributeError, IndexError):
                pass
            except Exception as er:
                print(er)
                pass

    def detect_blob(self):
        if self.root.raw_frame.any():
            threshold = self.root.ui.settings_threshold_spin.value()
            contours = [self.root.ui.settings_contour_limits_min_spin.value(),
                        self.root.ui.settings_contour_limits_max_spin.value()]
            circle_limits = [self.root.ui.settings_circularity_min_spin.value(),
                             self.root.ui.settings_circularity_max_spin.value()]

            self.root.drawn_frame, detected = ip.detect_blob(self.root.raw_frame, threshold=threshold,
                                                             contour_limits=contours, circle_limits=circle_limits,
                                                             zero_point=self.blob_kpis["zero"])
            self.blob_kpis["detected"] = detected
            self.root.ui.measure_detected_position.setText("(%i, %i)" % (self.blob_kpis["detected"][0],
                                                                         self.blob_kpis["detected"][1]))

            if self.root.is_zeroed:
                self.blob_kpis["zero"] = detected
                self.root.ui.measure_zero_position.setText("(%i, %i)" % (self.blob_kpis["zero"][0],
                                                                         self.blob_kpis["zero"][1]))
                self.root.is_zeroed = False
                self.root.ui.measure_zero_button.setEnabled(True)

            if not self.root.is_frozen:
                delta = (self.blob_kpis["detected"][0] - self.blob_kpis["zero"][0],
                         self.blob_kpis["detected"][1] - self.blob_kpis["zero"][1])
                self.blob_kpis["delta"] = delta
                self.root.ui.measure_delta_position.setText("(%i, %i)" % (self.blob_kpis["delta"][0],
                                                                          self.blob_kpis["delta"][1]))
                self.is_recorded = False
            else:
                if not self.is_recorded:
                    self.root.csv_data["zero x"] = np.append(self.root.csv_data["zero x"], self.blob_kpis["zero"][0])
                    self.root.csv_data["zero y"] = np.append(self.root.csv_data["zero y"], self.blob_kpis["zero"][1])
                    self.root.csv_data["detected x"] = np.append(self.root.csv_data["detected x"],
                                                                 self.blob_kpis["detected"][0])
                    self.root.csv_data["detected y"] = np.append(self.root.csv_data["detected y"],
                                                                 self.blob_kpis["detected"][1])
                    self.root.csv_data["delta x"] = np.append(self.root.csv_data["delta x"], self.blob_kpis["delta"][0])
                    self.root.csv_data["delta y"] = np.append(self.root.csv_data["delta y"], self.blob_kpis["delta"][1])
                    self.is_recorded = True



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
        Run thread
        """
        if not self.root.is_closed:
            cv2.imwrite(self.save_path, cv2.cvtColor(self.frame_to_save, cv2.COLOR_BGR2RGB))


def launch_gui(camera_num):
    print("AYYYYYYYYYYY")
    args = dict(argParser.parse_args()._get_kwargs())
    if args["cam_num"] is not None:
        camera_num = args["cam_num"]
    app = QApplication(sys.argv)
    widget = Widget(camera_num)
    widget.show()
    sys.exit(app.exec())

#
# if __name__ == "__main__":
#     launch_gui(0)
