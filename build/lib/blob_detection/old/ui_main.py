import sys, PySide6, matplotlib, json, time, cv2, os, math
import hardware as hw
import numpy as np
from PySide6 import QtCore
# from PySide6.QtCore import Qt
from PySide6.QtGui import (QImage, QPixmap, QCloseEvent)
from PySide6.QtWidgets import (QApplication, QWidget, QFileDialog, QGraphicsScene, QGraphicsPixmapItem)
from datetime import datetime
from ui_form import Ui_Widget


matplotlib.use('tkagg')


class Widget(QWidget):

    def __init__(self, parent=None, config_path=r"C:\Users\bhathaway\PycharmProjects\blob_detection\blob_detection"):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.threadpool = QtCore.QThreadPool()
        self.main_thread = QtCore.QThread.currentThread()

        # Variables ------------------------------------------------------------------------------------------------- #
        self.settings_path = os.path.join(config_path, "../support/gui_settings.json")
        with open(self.settings_path) as f:
            self.json_settings = json.load(f)
        self.camera1 = None
        self.camera2 = None
        self.pixmap1 = None
        self.pixmap2 = None
        self.is_closed = False
        self.is_test = False
        self.json_width = 48
        self.output_on_close = 0
        self.zoom = 0
        self.pxl_size_mm = 0
        self.raw_frame = np.array([])
        self.drawn_frame = np.array([])
        self.set_defaults()

        # Buttons --------------------------------------------------------------------------------------------------- #
        self.ui.cam1_camera_capture_button.clicked.connect(lambda: self.click_capture(1))
        self.ui.cam1_camera_connect_button.clicked.connect(lambda: self.thread_connect_camera(1))
        self.ui.cam1_measure_zero_button.clicked.connect(self.do_pass)
        self.ui.cam1_freeze_delta_button.clicked.connect(self.do_pass)
        self.ui.cam1_save_button.clicked.connect(self.do_pass)
        self.ui.cam1_browse_button.clicked.connect(lambda: self.click_browse(1))

        self.ui.cam2_camera_capture_button.clicked.connect(lambda: self.click_capture(2))
        self.ui.cam2_camera_connect_button.clicked.connect(lambda: self.thread_connect_camera(2))
        self.ui.cam2_measure_zero_button.clicked.connect(self.do_pass)
        self.ui.cam2_freeze_delta_button.clicked.connect(self.do_pass)
        self.ui.cam2_save_button.clicked.connect(self.do_pass)
        self.ui.cam2_browse_button.clicked.connect(lambda: self.click_browse(2))

        # Sliders --------------------------------------------------------------------------------------------------- #
        self.ui.cam1_camera_exposure_slider.sliderReleased.connect(lambda: self.change_exposure(1))
        self.ui.cam1_camera_gamma_slider.sliderReleased.connect(lambda: self.change_gamma(1))
        self.ui.cam1_camera_exposure_slider.valueChanged.connect(lambda: self.change_exposure(1, just_label=True))
        self.ui.cam1_camera_gamma_slider.valueChanged.connect(lambda: self.change_exposure(1, just_label=True))

        self.ui.cam2_camera_exposure_slider.sliderReleased.connect(lambda: self.change_exposure(2))
        self.ui.cam2_camera_gamma_slider.sliderReleased.connect(lambda: self.change_gamma(2))
        self.ui.cam2_camera_exposure_slider.valueChanged.connect(lambda: self.change_exposure(2, just_label=True))
        self.ui.cam2_camera_gamma_slider.valueChanged.connect(lambda: self.change_exposure(2, just_label=True))

        # Combo Boxes ----------------------------------------------------------------------------------------------- #
        # self.ui.cam1_camera_com_combo.currentIndexChanged.connect(self.do_pass)
        # self.ui.cam2_camera_com_combo.currentIndexChanged.connect(self.do_pass)

        # Spin Boxes ------------------------------------------------------------------------------------------------ #
        self.ui.cam1_camera_exposure_spin.editingFinished.connect(lambda: self.change_exposure(1, spin_change=True))
        self.ui.cam1_camera_gamma_spin.editingFinished.connect(lambda: self.change_gamma(1, spin_change=True))

        self.ui.cam2_camera_exposure_spin.editingFinished.connect(lambda: self.change_exposure(2, spin_change=True))
        self.ui.cam2_camera_gamma_spin.editingFinished.connect(lambda: self.change_gamma(2, spin_change=True))

        # Threads --------------------------------------------------------------------------------------------------- #
        if not self.is_test:
            self.thread_connect_camera(1)
            self.thread_connect_camera(2)

    def closeEvent(self, event: QCloseEvent):
        """
        Custom call for when close event is called on main window.
        :param event: (QCloseEvent) Qt flag of closing event.
        """
        self.hide()
        self.is_closed = True
        time.sleep(1)

        if self.stage_c887 is not None:
            self.stage_c887.close()

        if self.stage_c884 is not None:
            self.stage_c884.close()

        if self.camera is not None:
            self.camera.close()

        if self.lcos is not None:
            self.lcos.close()

        if self.labjack is not None:
            self.labjack.close()

        print("CLOSED")

    def wheelEvent(self, event):
        """
        Custom call for scrolling wheel on mouse. Applies to only region with live stream.
        :param event: (QEvent) Qt flag for any event.
        """
        if self.pixmap1 is not None:
            if (580 < event.position().x() < 1040) and (40 < event.position().y() < 375):
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

    def change_exposure(self, camera_num, spin_change=False, just_label=False):
        if spin_change:
            new_value = int(self.ui.camera_exposure_spin.value())
            self.ui.camera_exposure_slider.setValue(new_value)
        else:
            new_value = int(self.ui.camera_exposure_slider.value())
            self.ui.camera_exposure_spin.setValue(new_value)

        if not just_label and eval("self.camera%i" % camera_num) is not None:
            exec("self.camera%i.set_exposure(new_value=new_value)" % camera_num)

    def change_gamma(self, camera_num, spin_change=False, just_label=False):
        if spin_change:
            new_value = float(self.ui.camera_gamma_spin.value())
            self.ui.camera_gamma_slider.setValue(new_value * 10)
        else:
            new_value = float(self.ui.camera_gamma_slider.value()) / 10
            self.ui.camera_gamma_spin.setValue(new_value)

        if not just_label and eval("self.camera%i" % camera_num) is not None:
            exec("self.camera%i.set_exposure(new_value=new_value)" % camera_num)

    def click_browse(self, camera_num):
        """
        Action for clicking the folder browse button.
        """
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path != "":
            exec("self.ui.cam%i_save_path_entry.setText(folder_path)" % camera_num)

    def click_capture(self, camera_num):
        """
        Action for clicking the CAPTURE button.
        """
        if self.camera is not None:
            # Check folder path
            folder = eval("self.ui.cam%i_save_path_entry.toPlainText()" % camera_num)
            if not os.path.exists(folder):
                os.mkdir(folder)

            # Get  variables for path
            now = datetime.now()
            exposure_us = int(eval("self.ui.cam%i_camera_exposure_spin.text())" % camera_num))
            gamma_10 = int(float(eval("self.ui.cam%i_camera_gamma_spin.text())" % camera_num)))
            image_name = "image_%s_%sus_%sdB_%s.png" % (now.strftime("%Y%m%d-%H%M%S"), exposure_us, gamma_10)

            # Check path and save
            image_path = hw.check_path(os.path.join(folder, image_name))
            self.thread_save_image(image_path, self.camera.current_frame.copy())

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
        # GUI values (camera 1)
        self.ui.cam1_camera_exposure_spin.setValue(self.json_settings["Camera"]["Exposure us"])
        self.ui.cam1_camera_gamma_spin.setValue(self.json_settings["Camera"]["Gamma"])
        self.ui.cam1_save_path_entry.setText(self.json_settings["Save Path"])
        self.ui.cam1_camera_com_spin.setValue(self.json_settings["Camera"]["ID"][0])

        # GUI values (camera 2)
        self.ui.cam2_camera_exposure_spin.setValue(self.json_settings["Camera"]["Exposure us"])
        self.ui.cam2_camera_gamma_spin.setValue(self.json_settings["Camera"]["Gamma"])
        self.ui.cam2_save_path_entry.setText(self.json_settings["Save Path"])
        self.ui.cam2_camera_com_spin.setValue(self.json_settings["Camera"]["ID"][1])

        # Other
        self.pxl_size_mm = self.json_settings["Camera"]["Pixel Size mm"]

    def thread_connect_camera(self, camera_num):
        """
        Thread call for connecting and initializing the present camera.
        """
        worker = ThreadLoadHW(camera_num, parent=self)
        self.threadpool.start(worker)

    def thread_stream(self, camera_num):
        """
        Thread call for starting the camera stream to UI main window..
        """
        worker = ThreadStream(camera_num, parent=self)
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
        # Connect to camera 1
        if self.device == 1:
            if self.root.camera1 is None:
                if self.root.json_settings["Camera"]["Sensor"] == "AmScope":
                    self.root.camera1 = hw.AmScopeCam(self.root.json_settings["Camera"]["ID"][0])
                # elif self.json_settings["Camera"]["Sensor"] == "EXAMPLE":
                #     self.root.camera = hw.EXAMPLE_CALL(self.json_settings["Camera"]["ID"])

                if self.root.camera1.device is not None:
                    print("CAMERA SUCCESS")
                    self.change_color(self.root.ui.cam1_camera_connect_indicator, "green")
                    self.root.change_exposure(self.root.camera1, spin_change=True)
                    self.root.change_gamma(self.root.camera1, spin_change=True)
                    self.root.thread_stream(1)
                else:
                    print("CAMERA FAILURE")
                    self.change_color(self.root.ui.cam1_camera_connect_indicator, "red")
                    self.root.camera1 = None
            else:
                self.change_color(self.root.ui.cam1_camera_connect_indicator, "gray")
                self.root.camera1.close()
                self.root.camera1 = None
        # Connect to camera 2
        elif self.device == 2:
            if self.root.camera2 is None:
                if self.root.json_settings["Camera"]["Sensor"] == "AmScope":
                    self.root.camera2 = hw.AmScopeCam(self.root.json_settings["Camera"]["ID"][1])
                # elif self.json_settings["Camera"]["Sensor"] == "EXAMPLE":
                #     self.root.camera = hw.EXAMPLE_CALL(self.json_settings["Camera"]["ID"])

                if self.root.camera2.device is not None:
                    print("CAMERA SUCCESS")
                    self.change_color(self.root.ui.hardware_connect_camera_indicator, "green")
                    self.root.change_exposure(self.root.camera2, spin_change=True)
                    self.root.change_gamma(self.root.camera2, spin_change=True)
                    self.root.thread_stream(2)
                else:
                    print("CAMERA FAILURE")
                    self.change_color(self.root.ui.hardware_connect_camera_indicator, "red")
                    self.root.camera2 = None
            else:
                self.change_color(self.root.ui.hardware_connect_camera_indicator, "gray")
                self.root.camera2.close()
                self.root.camera2 = None

    def change_color(self, indicator, color):
        """
        Change the color of the status indicator on main GUI.
        :param indicator: (QRadioButton) Handle to correct indicator/radio button.
        :param color: (str) Color to change to.
        """
        indicator.setStyleSheet("QRadioButton::indicator{background-color : %s}" % color)


class ThreadStream(QtCore.QRunnable):

    def __init__(self, camera_num, parent=None):
        """
        Stream image frames from connected camera.
        :param parent: (QWidget) Qt main window handle.
        """
        super().__init__()
        self.root = parent
        self.camera_num = camera_num
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
        Run thread.
        """
        while self.root.camera is None:
            time.sleep(0.01)

        while not self.root.is_closed:
            try:
                # Get frame and format it into RGB 8-bit
                self.root.raw_frame = eval("self.root.camera%i.current_frame.copy()" % self.camera_num)
                if self.root.drawn_frame.any():
                    img_array = self.root.drawn_frame.copy()
                else:
                    img_array = self.root.raw_frame.copy()
                if "16" in img_array.dtype.name:
                    img_array = (img_array / 256).astype('uint8')

                if img_array.any():
                    s = img_array.shape
                    if len(s) == 2:
                        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
                    elif len(s) == 3:
                        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)

                    # Convert np.array into QPixmap for main GUI
                    self.root.pixmap = QPixmap.fromImage(QImage(img_array, s[1], s[0], 3 * s[1], QImage.Format_RGB888))
                    pic = QGraphicsPixmapItem()
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
            cv2.imwrite(self.save_path, self.frame_to_save)


def launch_gui():
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_gui()
