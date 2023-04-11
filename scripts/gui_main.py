# NOTE: I have not included the img_processing script to protect our blob detection algorithm.

import PySide6, os, time, cv2, sys, ctypes, matplotlib
import hardware as hw
import img_processing as ip
import numpy as np
import qimage2ndarray as qt2a
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFileDialog, QGraphicsColorizeEffect, QGraphicsPixmapItem, QGraphicsScene)
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (QWidget, QApplication)
from PySide6.QtGui import (QPixmap, QImage)
from gui_layout import Ui_Widget
from datetime import datetime

matplotlib.use('tkagg')


class Widget(QWidget):
    def __init__(self, parent=None, pi_sn=119039336, dc1_com="COM7"):
        super(Widget, self).__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.threadpool = QtCore.QThreadPool()

        # Variables ------------------------------------------------------------------------------------------------- #
        self.pi_stage_sn = pi_sn
        self.pxl_size_mm = 0.00345
        self.dc1_com = dc1_com
        self.zoom = 0
        self.stages = None
        self.camera = None
        self.dc4100 = None
        self.pixmap = None
        self.is_align_running = False
        self.is_ok = False
        self.is_aborted = False
        self.is_closed = False
        self.is_test = False
        self.is_dialog_open = False
        self.dialog_answer = True
        self.csv_data = []
        self.raw_frame = np.array([])
        self.drawn_frame = np.array([])
        self.kpi_stage_positions = {
            '1': {'name': 'L-406.40DG10', "l1": 15.0, "dif": 45.25, "l2": 45.25, "align": None, "cpc": None,
                  "icg": None},
            '2': {'name': 'L-406.40DG10', "l1": 50.25, "dif": 50.25, "l2": 50.25, "align": None, "cpc": None,
                  "icg": None},
            '3': {'name': 'L-406.40DG10', "l1": 35.0, "dif": 35.0, "l2": 13.877, "align": 13.877, "cpc": 13.877,
                  "icg": 13.877},
            '4': {'name': 'M-605.2DD', "l1": 31.9, "dif": 16.195, "l2": 16.195, "align": 16.195, "cpc": 14.195,
                  "icg": 14.195}
        }
        self.defaults = {
            "exposure_us": 160000, "gain": 0.0, "gamma": 1, "fps": 6.0, "led_currents": [20, 15, 1000],
            "cpc_exposure_us_r": 13000, "cpc_exposure_us_l": 22000,
            "thresholds": [252, 9, 80, 83, 5, 40, 15], "l1_roi_rad": [2080, 2215], "l2_roi_rad": [0, 3000],
            "cpc_centers_r": [(2408, 2366), (2582, 1962), (2359, 1596)],
            "cpc_centers_l": [(1839, 1734), (1648, 2131), (1856, 2505)],
            "icg_centers_r": [(1888, 1628), (1682, 2025), (1888, 2408)],
            "icg_centers_l": [(2351, 2487), (2542, 2091), (2348, 1715)]
        }

        # Buttons --------------------------------------------------------------------------------------------------- #
        self.ui.hardware_stage_button.clicked.connect(self.thread_connect_stages)
        self.ui.hardware_camera_button.clicked.connect(self.thread_connect_camera)
        self.ui.hardware_dc4100_button.clicked.connect(self.thread_connect_dc1)

        self.ui.camera_capture_button.clicked.connect(self.click_capture)

        self.ui.stage_lensx_move.clicked.connect(lambda: self.click_move_abs(1))
        self.ui.stage_lensy_move.clicked.connect(lambda: self.click_move_abs(2))
        self.ui.stage_lensz_move.clicked.connect(lambda: self.click_move_abs(3))
        self.ui.stage_camz_move.clicked.connect(lambda: self.click_move_abs(4))
        self.ui.stage_lensx_step_n.clicked.connect(lambda: self.click_move_rel(1, neg=True))
        self.ui.stage_lensy_step_n.clicked.connect(lambda: self.click_move_rel(2, neg=True))
        self.ui.stage_lensz_step_n.clicked.connect(lambda: self.click_move_rel(3, neg=True))
        self.ui.stage_camz_step_n.clicked.connect(lambda: self.click_move_rel(4, neg=True))
        self.ui.stage_lensx_step_p.clicked.connect(lambda: self.click_move_rel(1))
        self.ui.stage_lensy_step_p.clicked.connect(lambda: self.click_move_rel(2))
        self.ui.stage_lensz_step_p.clicked.connect(lambda: self.click_move_rel(3))
        self.ui.stage_camz_step_p.clicked.connect(lambda: self.click_move_rel(4))

        self.ui.alignment_folder_button.clicked.connect(self.click_browse)
        self.ui.alignment_abort_button.clicked.connect(self.click_abort)

        self.ui.centers_l1_ok_button.clicked.connect(self.click_ok)
        self.ui.centers_l2_ok_button.clicked.connect(self.click_ok)
        self.ui.centers_correction_move_button.clicked.connect(self.click_ok)
        self.ui.centers_cpc_ok_button.clicked.connect(self.click_ok)
        self.ui.centers_icg_ok_button.clicked.connect(self.click_ok)

        # Sliders --------------------------------------------------------------------------------------------------- #
        self.ui.camera_exposure_slider.sliderReleased.connect(self.change_exposure)
        self.ui.camera_gain_slider.sliderReleased.connect(self.change_gain)
        self.ui.camera_gamma_slider.sliderReleased.connect(self.change_gamma)
        self.ui.camera_exposure_slider.valueChanged.connect(lambda: self.change_exposure(just_label=True))
        self.ui.camera_gain_slider.valueChanged.connect(lambda: self.change_gain(just_label=True))
        self.ui.camera_gamma_slider.valueChanged.connect(lambda: self.change_gamma(just_label=True))

        # Spin Boxes ------------------------------------------------------------------------------------------------ #
        self.ui.led_red_current_spin.setValue(self.defaults["led_currents"][0])
        self.ui.led_green_current_spin.setValue(self.defaults["led_currents"][1])
        self.ui.led_ir_current_spin.setValue(self.defaults["led_currents"][2])
        self.ui.led_red_current_spin.valueChanged.connect(self.change_led_current)
        self.ui.led_green_current_spin.valueChanged.connect(self.change_led_current)
        self.ui.led_ir_current_spin.valueChanged.connect(self.change_led_current)

        # Check Boxes ----------------------------------------------------------------------------------------------- #
        self.ui.led_red_enable_check.clicked.connect(self.click_led_enable)
        self.ui.led_green_enable_check.clicked.connect(self.click_led_enable)
        self.ui.led_ir_enable_check.clicked.connect(self.click_led_enable)

        # Other(s) -------------------------------------------------------------------------------------------------- #
        self.change_gamma(just_label=True)

        # Threads --------------------------------------------------------------------------------------------------- #
        if self.is_test:
            self.ui.alignment_start_button.clicked.connect(self.do_pass)
            self.pixmap = QPixmap.fromImage(QImage(u"../test_alignment/L1.png"))
            self.ui.scene.addPixmap(self.pixmap)
            self.ui.stream_window.fitInView(0, 0, self.ui.stream_window.size().height() / 2,
                                            self.ui.stream_window.size().width() / 2, Qt.KeepAspectRatio)
        else:
            self.ui.alignment_start_button.clicked.connect(self.click_start)
            self.thread_connect_camera()
            self.thread_connect_stages()
            self.thread_connect_dc1()

    def closeEvent(self, event: QCloseEvent):
        """
        Custom call for when close event is called on main window.
        :param event: (QCloseEvent) Qt flag of closing event.
        """
        self.hide()
        self.is_closed = True
        time.sleep(0.3)

        if self.camera is not None:
            self.camera.stop_stream()
            self.camera.close()

        if self.stages is not None:
            self.stages.close()

        if self.dc4100 is not None:
            self.dc4100.close()

        print("CLOSED")

    def wheelEvent(self, event):
        """
        Custom call for scrolling wheel on mouse. Applies to only region with live stream.
        :param event: (QEvent) Qt flag for any event.
        """
        if self.pixmap is not None:
            if (30 < event.position().x() < 500) and (30 < event.position().y() < 500):
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

    def change_exposure(self, just_label=False):
        """
        Change the exposure of the connected camera. Option for changing just the label.
        :param just_label: (bool) Change just the exposure value label or not.
        """
        new_value = int(self.ui.camera_exposure_slider.value())
        self.ui.camera_exposure_val_label.setText(str(new_value))
        if not just_label:
            if self.camera is not None:
                self.camera.set_exposure(new_value=(new_value))
            else:
                print("(NO CAM) EXPOSURE VALUE SET TO %i" % new_value)

    def change_gain(self, just_label=False):
        """
        Change the gain of the connected camera. Option for changing just the label.
        :param just_label: (bool) Change just the gain value label or not.
        """
        new_value = int(self.ui.camera_gain_slider.value())
        self.ui.camera_gain_val_label.setText(str(new_value))
        if not just_label:
            if self.camera is not None:
                self.camera.set_gain(new_value=new_value)
            else:
                print("(NO CAM) GAIN VALUE SET TO %i" % new_value)

    def change_gamma(self, just_label=False):
        """
        Change the gamma of the connected camera. Option for changing just the label.
        :param just_label: (bool) Change just the gamma value label or not.
        """
        new_value = float(self.ui.camera_gamma_slider.value()) / 10
        self.ui.camera_gamma_val_label.setText(str(new_value))
        if not just_label:
            if self.camera is not None:
                self.camera.set_gamma(new_value=new_value)
            else:
                print("(NO CAM) GAMMA VALUE SET TO %.1f" % new_value)

    def change_led_current(self):
        """
        Change the LED currents via Thorlabs DC Controller.
        """
        r_current = int(self.ui.led_red_current_spin.value())
        g_current = int(self.ui.led_green_current_spin.value())
        ir_current = int(self.ui.led_ir_current_spin.value())
        if self.dc4100 is not None:
            self.dc4100.set_constant_current(0, r_current)
            self.dc4100.set_constant_current(1, g_current)
            self.dc4100.set_constant_current(2, ir_current)
        else:
            print("(NO DC4100) LED CURRENTS: [%i, %i, %i]" % (r_current, g_current, ir_current))

    def click_abort(self):
        """
        Action for clicking the abort button.
        """
        if self.is_align_running:
            self.is_aborted = True
            self.ui.alignment_abort_button.setEnabled(False)

    def click_browse(self):
        """
        Action for clicking the folder browse button.
        """
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path != "":
            self.ui.alignment_folder_entry.setText(folder_path)

    def click_capture(self):
        """
        Action for clicking the image capture button.
        """
        if self.camera is not None:
            folder = self.ui.alignment_folder_entry.text()
            exposure_us = int(self.ui.camera_exposure_val_label.text())
            gain_db = int(self.ui.camera_gain_val_label.text())
            gamma_10 = int(float(self.ui.camera_gamma_val_label.text()))
            now = datetime.now()
            image_name = "image_%s_%sus_%sdB_%s.png" % (now.strftime("%Y%m%d-%H%M%S"), exposure_us, gain_db, gamma_10)

            self.thread_save_image(make_file_path(folder, image_name), self.camera.current_frame.copy())

    def click_led_enable(self):
        """
        Action for clicking the LED enable/disable buttons.
        """
        r_status = int(self.ui.led_red_enable_check.isChecked())
        g_status = int(self.ui.led_green_enable_check.isChecked())
        ir_status = int(self.ui.led_ir_enable_check.isChecked())
        if self.dc4100 is not None:
            self.dc4100.set_led(0, r_status)
            self.dc4100.set_led(1, g_status)
            self.dc4100.set_led(2, ir_status)
        else:
            print("(NO DC4100) LED STATUS: [%i, %i, %i]" % (r_status, g_status, ir_status))

    def click_move_abs(self, axis):
        """
        Action for clicking the absolute move buttons.
        :param axis: (str) The axis name to move; EX: "1", "2", "3", or "4"
        """
        try:
            if axis == 1:
                step = float(self.ui.stage_lensx_entry.text())
                end_pos = step + float(self.ui.stage_lensx_position.text().split(" ")[0])
            elif axis == 2:
                step = float(self.ui.stage_lensy_entry.text())
                end_pos = step + float(self.ui.stage_lensx_position.text().split(" ")[0])
            elif axis == 3:
                step = float(self.ui.stage_lensz_entry.text())
                end_pos = step + float(self.ui.stage_lensx_position.text().split(" ")[0])
            elif axis == 4:
                step = float(self.ui.stage_camz_entry.text())
                end_pos = step + float(self.ui.stage_lensx_position.text().split(" ")[0])

        except ValueError:
            self.dialog("Invalid input for stage motion.\nPlease re-enter.", 1)
            return

        if 0 <= end_pos <= 100:
            if self.stages is not None:
                self.stages.move_to(str(axis), step)
            else:
                print("(NO STAGES) STAGE %i ABS MOVE TO %.3f" % (axis, float(step)))
        else:
            self.dialog("Step entry will send stage out of range.\nPlease re-enter.", 1)

    def click_move_rel(self, axis, neg=False):
        """
        Action for clicking the relative move buttons.
        :param axis: (str) The axis name to move; EX: "1", "2", "3", or "4"
        :param neg: (bool) Is this a negative or positive step?
        """
        f = 1
        if neg:
            f = -1

        try:
            if axis == 1:
                step = float(self.ui.stage_lensx_entry.text()) * f
                end_pos = step + float(self.ui.stage_lensx_position.text().split(" ")[0])
            elif axis == 2:
                step = float(self.ui.stage_lensy_entry.text()) * f
                end_pos = step + float(self.ui.stage_lensx_position.text().split(" ")[0])
            elif axis == 3:
                step = float(self.ui.stage_lensz_entry.text()) * f
                end_pos = step + float(self.ui.stage_lensx_position.text().split(" ")[0])
            elif axis == 4:
                step = float(self.ui.stage_camz_entry.text()) * f
                end_pos = step + float(self.ui.stage_lensx_position.text().split(" ")[0])

        except ValueError:
            self.dialog("Invalid input for stage motion.\nPlease re-enter.", 1)
            return

        if 0 <= end_pos <= 100:
            if self.stages is not None:
                self.stages.move_by(str(axis), step)
            else:
                print("(NO STAGES) STAGE %i REL MOVE BY %.3f" % (axis, float(step)))
        else:
            self.dialog("Step entry will send stage out of range.\nPlease re-enter.", 1)

    def click_ok(self):
        """
        Action for clicking the OK buttons.
        """
        if self.is_align_running:
            self.is_ok = True

    def click_start(self):
        """
        Action for clicking the start button.
        """
        if self.is_align_running:
            pass
        else:
            worker = ThreadAlign(parent=self)
            self.threadpool.start(worker)

    def dialog(self, message, level=0):
        """
        Ctypes dialog box to prompt or inform the user.
        :param message: (str) Message to display in box.
        :param level: (int) 0 = prompt, 1 = warning, 2 = error
        :return: (bool) answer
        """
        MB_OK = 0x0
        MB_OKCXL = 0x01
        # MB_YESNOCXL = 0x03
        # MB_YESNO = 0x04
        # MB_HELP = 0x4000
        MB_SYSTEMMODAL = 0x00001000
        ICON_EXCLAIM = 0x30
        ICON_INFO = 0x40
        ICON_STOP = 0x10

        message = bytes(message, 'utf-8')
        if level == 0:
            title = b"Action Required"
            button = MB_OKCXL
            icon = ICON_INFO
        else:
            button = MB_OK
            if level == 1:
                title = b"Warning"
                icon = ICON_EXCLAIM
            elif level == 2:
                title = b"ERROR"
                icon = ICON_STOP
        self.dialog_answer = ctypes.windll.user32.MessageBoxA(0, message, title, button | icon | MB_SYSTEMMODAL)

        return self.dialog_answer

        # dialog = QMessageBox(self)
        # if level == 0:
        #     title = "Action Required"
        #     dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        #     dialog.setIcon(QMessageBox.Information)
        # else:
        #     dialog.setStandardButtons(QMessageBox.Ok)
        #     if level == 1:
        #         title = "Warning"
        #         dialog.setIcon(QMessageBox.Warning)
        #     elif level == 2:
        #         title = "ERROR"
        #         dialog.setIcon(QMessageBox.Critical)
        # dialog.setWindowTitle(title)
        # dialog.setText(message)
        # button = dialog.exec()
        #
        # if button == QMessageBox.Ok:
        #     self.dialog_answer = True
        # else:
        #     self.dialog_answer = False

    def do_pass(self, args=None):
        """
        Does nothing; Used for debugging.
        :param args: None
        """
        pass

    def set_defaults(self, device=3):
        """
        Sets the defaults settigs depending on if init was successful for that device.
        :param device: (int) Clarifies which device is being initialized.
        """
        if self.camera is not None and (device == 1 or device == 3):
            self.camera.set_fps(new_value=self.defaults["fps"])
            self.camera.set_exposure(new_value=self.defaults["exposure_us"])
            self.camera.set_gain(new_value=self.defaults["gain"])
            self.camera.set_gamma(new_value=self.defaults["gamma"])

        if self.dc4100 is not None and (device == 2 or device == 3):
            self.change_led_current()

    def thread_connect_camera(self):
        """
        Thread call for connecting and initializing the camera.
        """
        worker = ThreadLoadHW(1, parent=self)
        self.threadpool.start(worker)

    def thread_connect_dc1(self):
        """
        Thread call for connecting and initializing the DC Controller.
        """
        worker = ThreadLoadHW(2, parent=self)
        self.threadpool.start(worker)

    def thread_connect_stages(self):
        """
        Thread call for connecting and initializing the PI stages.
        """
        worker = ThreadLoadHW(0, parent=self)
        self.threadpool.start(worker)

    def thread_save_image(self, save_path, frame_to_save):
        """
        Thread call for saving an image.
        :param save_path: (str) Path to where image should be saved including file name.
        :param frame_to_save: (np.array) Image frame to save.
        """
        worker = ThreadSave(save_path, frame_to_save, parent=self)
        self.threadpool.start(worker)

    def thread_stage_position(self):
        """
        Thread call for reading feedback from PI stages.
        """
        worker = ThreadPosition(parent=self)
        self.threadpool.start(worker)

    def thread_stream(self):
        """
        Thread call for starting the camera stream to UI main window..
        """
        worker = ThreadStream(parent=self)
        self.threadpool.start(worker)

    def reset_alignment(self, before_run=False):
        """
        Reset values that changed during alignment thread.
        :param before_run: (bool) Is this resetting for pre-alignment or post?
        """
        if before_run:
            self.set_defaults()
            self.ui.alignment_abort_button.setEnabled(True)

            self.ui.centers_l1_pos_label.setText("(0, 0)")
            self.ui.centers_l2_pos_label.setText("(0, 0)")
            self.ui.centers_correction_pos_label.setText("(0.000, 0.000)")

            self.ui.centers_rcpc_pos_label.setText("(0, 0)")
            self.ui.centers_gcpc_pos_label.setText("(0, 0)")
            self.ui.centers_bcpc_pos_label.setText("(0, 0)")

            self.ui.centers_ricg_pos_label.setText("(0, 0)")
            self.ui.centers_gicg_pos_label.setText("(0, 0)")
            self.ui.centers_bicg_pos_label.setText("(0, 0)")

            self.ui.centers_rdelta_pos_label.setText("(0.000, 0.000)")
            self.ui.centers_gdelta_pos_label.setText("(0.000, 0.000)")
            self.ui.centers_bdelta_pos_label.setText("(0.000, 0.000)")
        else:
            self.is_align_running = False
            self.is_aborted = False
            self.is_ok = False
            self.drawn_frame = np.array([])

            self.ui.centers_l1_ok_button.setEnabled(False)
            self.ui.centers_l2_ok_button.setEnabled(False)
            self.ui.centers_correction_move_button.setEnabled(False)
            self.ui.centers_cpc_ok_button.setEnabled(False)
            self.ui.centers_icg_ok_button.setEnabled(False)

            self.ui.alignment_abort_button.setEnabled(False)


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
        Run thread.
        """
        # Connect to PI stages
        if self.device == 0:
            if self.root.stages is None:
                self.root.stages = hw.PIStageC884(self.root.pi_stage_sn)
                if self.root.stages.device is not None:
                    print("STAGE SUCCESS")
                    self.change_color(self.root.ui.hardware_stage_indicator, "green")
                    self.root.thread_stage_position()
                else:
                    print("STAGE FAILURE")
                    self.change_color(self.root.ui.hardware_stage_indicator, "red")
                    self.root.stages = None
            else:
                self.change_color(self.root.ui.hardware_stage_indicator, "gray")
                self.root.stages.close()
                self.root.stages = None

        # Connect to camera
        elif self.device == 1:
            if self.root.camera is None:
                self.root.camera = hw.AtlasCam()
                if self.root.camera.device is not None:
                    print("CAMERA SUCCESS")
                    self.change_color(self.root.ui.hardware_camera_indicator, "green")
                    self.root.thread_stream()
                else:
                    print("CAMERA FAILURE")
                    self.change_color(self.root.ui.hardware_camera_indicator, "red")
                    self.root.camera = None
            else:
                self.change_color(self.root.ui.hardware_camera_indicator, "gray")
                self.root.camera.close()
                self.root.camera = None

        # Connect to DC controller
        elif self.device == 2:
            if self.root.dc4100 is None:
                try:
                    self.root.dc4100 = hw.DC4100(self.root.dc1_com)
                    self.root.dc4100.open()
                    print("DC4100 SUCCESS")
                    self.change_color(self.root.ui.hardware_dc4100_indicator, "green")
                except Exception:
                    print("DC4100 FAILURE")
                    self.change_color(self.root.ui.hardware_dc4100_indicator, "red")
                    self.root.dc4100 = None
            else:
                self.change_color(self.root.ui.hardware_dc4100_indicator, "gray")
                self.root.dc4100.close()
                self.root.dc4100 = None

        self.root.set_defaults(self.device)

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
                self.root.raw_frame = self.root.camera.current_frame.copy()
                if self.root.drawn_frame.any():
                    img_array = self.root.drawn_frame
                else:
                    img_array = self.root.raw_frame
                    img_array = (img_array / 256).astype('uint8')

                if img_array.any():
                    s = img_array.shape
                    if len(s) == 2:
                        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)

                    # Convert np.array into QPixmap for main GUI
                    self.root.pixmap = QPixmap.fromImage(qt2a.array2qimage(img_array))
                    scene = QGraphicsScene()
                    pic = QGraphicsPixmapItem()
                    pic.setPixmap(self.root.pixmap)
                    scene.addItem(pic)
                    self.root.ui.stream_window.setScene(scene)
                    # self.root.ui.stream_window.fitInView(0, 0, self.root.ui.stream_window.size().height() / 2,
                    #                                      self.root.ui.stream_window.size().width() / 2,
                    #                                      Qt.KeepAspectRatio)
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


class ThreadPosition(QtCore.QRunnable):
    def __init__(self, parent=None):
        """
        Read feedback from connected stages.
        :param parent: (QWidget) Qt main window handle.
        """
        super().__init__()
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
        Run thread.
        """
        while not self.root.is_closed and self.root.stages is not None:
            _, axes_data = self.root.stages.get_axes_data()
            filler = "%s (mm)"
            self.root.ui.stage_lensx_position.setText(filler % str(axes_data["1"]["pos"]))
            self.root.ui.stage_lensy_position.setText(filler % str(axes_data["2"]["pos"]))
            self.root.ui.stage_lensz_position.setText(filler % str(axes_data["3"]["pos"]))
            self.root.ui.stage_camz_position.setText(filler % str(axes_data["4"]["pos"]))


class ThreadAlign(QtCore.QRunnable):
    def __init__(self, parent=None):
        """
        Main alignment routine.
        :param parent: (QWidget) Qt main window handle.
        """
        super().__init__()
        now = datetime.now()
        self.root = parent
        self.folder_path = self.root.ui.alignment_folder_entry.text()
        self.side = "R"
        self.cpc_passed = False
        self.defaults = self.root.defaults
        self.root.is_align_running = True
        self.root.csv_data = [["Folder:", self.folder_path],
                              ["Date:", now.strftime("%m/%d/%Y")],
                              ["Time:", now.strftime("%H:%M:%S")],
                              ["SN:", self.root.ui.alignment_sn_entry.text()],
                              ["Side:", self.side],
                              [""],
                              ["Image", "Type", "CX (pxl)", "CY (pxl)", "CR (mm)", "Exposure (us)", "Gain (dB)",
                               "Gamma", "Threshold", "CPC to ICG (mm)"]]

        self.make_file_paths()

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
        start = time.time()
        if (self.root.stages and self.root.camera and self.root.dc4100) is not None:
            self.root.reset_alignment(before_run=True)
            ok = self.step_check_side()
            if ok:
                ok1 = self.step_l1_align()
                if ok1:
                    ok2 = self.step_l2_align()
                    if ok2:
                        ok3 = self.step_correction()
                        if ok3:
                            ok4 = self.step_cpc_detect()
                            if ok4:
                                ok5 = self.step_icg_detect()
                                if ok5:
                                    self.add_kpi_pos_to_csv()
                                    ip.write_to_csv(self.csv_path, self.root.csv_data)
            self.leds_on_off(rgir=[0, 0, 0])
        else:
            self.root.dialog("Check hardware connections and try again.", level=1)

        self.root.reset_alignment()
        print("total time: %0.2f min" % ((time.time() - start) / 60))

    def step_l1_align(self):
        """
        Step 1: Detect L1 center.
        """
        ok = self.root.dialog("Turn ON the ring light (0.75 A).\nClick 'OK' to continue.")
        if ok == 1:
            self.leds_on_off(rgir=[0, 0, 0])
            self.move_axes_to_positions(["4", "3", "1", "2"], "l1")

            # Detect L1 base first
            l1_base_center = []
            while len(l1_base_center) == 0 and not self.root.is_aborted:
                l1_base_drawn, l1_base_center, l1_base_rad = \
                    ip.detect_l1_baseline(self.root.raw_frame, threshold=self.defaults["thresholds"][0])

            if self.root.is_aborted:
                return False
            else:
                self.update_roi_settings(roi_center=l1_base_center[0], roi_rads=self.defaults["l1_roi_rad"],
                                         threshold=self.defaults["thresholds"][1])
                self.root.thread_save_image(self.l1_base_path, l1_base_drawn)

            # Detect L1
            self.root.ui.centers_l1_ok_button.setEnabled(True)
            while not (self.root.is_ok or self.root.is_aborted):
                roi_center = [self.root.ui.roi_center_spin_x.value(), self.root.ui.roi_center_spin_y.value()]
                roi_rads = [self.root.ui.roi_range_spin_min.value(), self.root.ui.roi_range_spin_max.value()]
                threshold = self.root.ui.roi_threshold_spin.value()
                try:
                    self.root.drawn_frame, l1_center, l1_rad = ip.detect_l1(self.root.raw_frame, roi_center=roi_center,
                                                                            roi_rads=roi_rads, threshold=threshold)
                    if len(l1_center) > 0:
                        self.root.ui.centers_l1_pos_label.setText(str(l1_center[0]))
                except Exception as er:
                    print("PASSED:", er)
                    pass

            if not len(l1_center) > 0:
                print("BAD L1 DETECTION")
                return False

            if self.root.is_aborted:
                return False
            else:
                self.root.thread_save_image(self.l1_path, self.root.raw_frame)
                self.root.thread_save_image(self.l1_drawn_path, self.root.drawn_frame)
                self.add_or_get_csv_data(self.l1_base_path, l1_base_center, thresh=self.defaults["thresholds"][0])
                self.add_or_get_csv_data(self.l1_drawn_path, l1_center)
                self.l1_center = l1_center
        else:
            return False

        self.root.drawn_frame = np.array([])
        self.root.is_ok = False

        return True

    def step_l2_align(self):
        """
        Step 2: Detect L2 center.
        """
        self.move_axes_to_positions(["4", "1", "2", "3"], "dif")
        ok = self.root.dialog("Apply diffuser, then click 'OK' to continue.")
        if ok == 1:
            self.move_axes_to_positions(["4", "1", "2", "3"], "l2")
            self.root.ui.centers_l2_ok_button.setEnabled(True)
            self.update_roi_settings(threshold=self.defaults["thresholds"][2])
            while not (self.root.is_ok or self.root.is_aborted):
                try:
                    threshold = self.root.ui.roi_threshold_spin.value()
                    self.root.drawn_frame, l2_center, l2_rad = ip.detect_l2(self.root.raw_frame, threshold=threshold)
                    if len(l2_center) > 0:
                        self.root.ui.centers_l2_pos_label.setText(str(l2_center[0]))
                except Exception as er:
                    print("PASSED:", er)
                    pass

            if not len(l2_center) > 0:
                print("BAD L2 DETECTION")
                return False

            if self.root.is_aborted:
                return False
            else:
                self.root.thread_save_image(self.l2_path, self.root.raw_frame)
                self.root.thread_save_image(self.l2_drawn_path, self.root.drawn_frame)
                self.add_or_get_csv_data(self.l2_drawn_path, l2_center)
                self.l2_center = l2_center
        else:
            return False

        self.root.drawn_frame = np.array([])
        self.root.is_ok = False

        return True

    def step_correction(self):
        """
        Step 3: Make stage correction to align L2 to L1.
        """
        # Wait for move click
        move_x = round((self.l2_center[0][0] - self.l1_center[0][0]) * self.root.pxl_size_mm, 6)
        move_y = round((self.l2_center[0][1] - self.l1_center[0][1]) * self.root.pxl_size_mm, 6)
        new_x = self.root.kpi_stage_positions["1"]["l2"] + move_x
        new_y = self.root.kpi_stage_positions["2"]["l2"] + move_y
        if abs(move_x) > 1 or abs(move_y) > 1:
            color_effect = QGraphicsColorizeEffect()
            color_effect.setColor(Qt.red)
            self.root.ui.centers_correction_pos_label.setGraphicsEffect(color_effect)

        self.root.ui.centers_correction_pos_label.setText(str((move_x, move_y)))
        self.root.ui.centers_correction_move_button.setEnabled(True)
        while not (self.root.is_ok or self.root.is_aborted):
            time.sleep(0.1)
        if self.root.is_aborted:
            return False

        # Update positions
        for each in ["align", "cpc", "icg"]:
            self.root.kpi_stage_positions["1"][each] = new_x
            self.root.kpi_stage_positions["2"][each] = new_y
        self.move_axes_to_positions(["1", "2"], "align")

        # Detect aligned center
        self.root.thread_save_image(self.align_path, self.root.raw_frame)
        align_center = []
        while len(align_center) == 0 and not self.root.is_aborted:
            align_drawn, align_center, align_rad = ip.detect_l2(self.root.raw_frame)
        if self.root.is_aborted:
            return False
        self.root.thread_save_image(self.align_drawn_path, align_drawn)
        self.add_or_get_csv_data(self.align_drawn_path, align_center)

        # Remove diffuser
        ok = self.root.dialog("Remove diffuser, then click 'OK' to continue.")
        if ok == 1:
            self.align_center = align_center
            self.align_rad = align_rad
            self.root.drawn_frame = np.array([])
            self.root.is_ok = False
        else:
            return False

        return True

    def step_cpc_detect(self):
        """
        Step 4.1: Detect locations of CPCs.
        """
        # TODO: need to fully test with CPCs present
        if self.root.ui.roi_cpc_check.isChecked():
            if self.side == "R":
                self.root.ui.camera_exposure_slider.setValue(int(self.defaults["cpc_exposure_us_r"]))
            else:
                self.root.ui.camera_exposure_slider.setValue(int(self.defaults["cpc_exposure_us_l"]))
            self.root.change_exposure()
            self.move_axes_to_positions(["1", "2", "3", "4"], "cpc")
            self.update_roi_settings(roi_center=self.align_center[0], roi_rads=[0, self.align_rad[0]],
                                     threshold=self.defaults["thresholds"][3])
            self.root.ui.centers_cpc_ok_button.setEnabled(True)
            while not (self.root.is_ok or self.root.is_aborted):
                roi_center = [self.root.ui.roi_center_spin_x.value(), self.root.ui.roi_center_spin_y.value()]
                roi_rads = [self.root.ui.roi_range_spin_min.value(), self.root.ui.roi_range_spin_max.value()]
                threshold = self.root.ui.roi_threshold_spin.value()
                try:
                    self.root.drawn_frame, cpc_centers, _ = ip.detect_cpc(self.root.raw_frame, roi_center=roi_center,
                                                                          roi_rads=roi_rads, threshold=threshold,
                                                                          side=self.side)
                    if len(cpc_centers) > 2:
                        if self.side == "R":
                            golden_cpc = self.defaults["cpc_centers_r"]
                        else:
                            golden_cpc = self.defaults["cpc_centers_l"]
                        sorted_data = self.add_or_get_csv_data("cpc", cpc_centers, ["", "", ""], get=True,
                                                               golden_cpc=golden_cpc)
                        if len(sorted_data) == 3:
                            for each in sorted_data:
                                new_label = "(%i, %i)" % (each[2], each[3])
                                if "RCPC" in each:
                                    self.root.ui.centers_rcpc_pos_label.setText(new_label)
                                elif "GCPC" in each:
                                    self.root.ui.centers_gcpc_pos_label.setText(new_label)
                                elif "BCPC" in each:
                                    self.root.ui.centers_bcpc_pos_label.setText(new_label)
                except Exception as er:
                    print("PASSED:", er)
                    pass

                if not self.root.ui.roi_cpc_check.isChecked():
                    self.root.ui.centers_cpc_ok_button.setEnabled(False)
                    return True

            if self.root.is_aborted or not len(cpc_centers) > 2:
                return False

            self.root.thread_save_image(self.cpc_path, self.root.raw_frame)
            self.root.thread_save_image(self.cpc_drawn_path, self.root.drawn_frame)
            cpc_cr = [round(ip.get_distance(cpc, self.align_center[0]), 6) * self.root.pxl_size_mm for cpc in
                      cpc_centers]
            self.add_or_get_csv_data(self.cpc_drawn_path, cpc_centers, cpc_cr, golden_cpc=golden_cpc)
            self.cpc_passed = True

        self.root.drawn_frame = np.array([])
        self.root.is_ok = False

        return True

    def step_icg_detect(self):
        """
        Step 4.2: Detect locations of ICGs.
        """
        # self.align_center = [(2178, 2049)]
        # self.align_rad = [1078]
        # self.root.kpi_stage_positions = {
        #     '1': {'name': 'L-406.40DG10', 'l1': 15.0, 'dif': 45.25, 'l2': 45.25, 'align': 45.595, 'cpc': 45.595,
        #           'icg': 45.595},
        #     '2': {'name': 'L-406.40DG10', 'l1': 50.25, 'dif': 50.25, 'l2': 50.25, 'align': 50.40525, 'cpc': 50.40525,
        #           'icg': 50.40525},
        #     '3': {'name': 'L-406.40DG10', "l1": 35.0, "dif": 35.0, "l2": 13.877, "align": 13.877, "cpc": 13.877,
        #           "icg": 13.877},
        #     '4': {'name': 'M-605.2DD', "l1": 31.9, "dif": 16.195, "l2": 16.195, "align": 16.195, "cpc": 14.195,
        #           "icg": 14.195}
        # }

        ok = self.root.dialog("Turn OFF the ring light (0.75 A).\nClick 'OK' to continue.")
        if ok == 1:
            self.root.ui.camera_exposure_slider.setValue(self.defaults["exposure_us"])
            self.root.change_exposure()
            self.move_axes_to_positions(["1", "2", "3", "4"], "icg")
            self.update_roi_settings(roi_center=self.align_center[0], roi_rads=[0, self.align_rad[0]],
                                     threshold=self.defaults["thresholds"][4])
            if self.side == "R":
                golden_icg = self.defaults["icg_centers_r"]
            else:
                golden_icg = self.defaults["icg_centers_l"]
            self.root.ui.centers_icg_ok_button.setEnabled(True)

            icg_centers = [[], [], []]
            colors = ["R", "G", "B"]
            for color in colors:
                if color == "R":
                    self.leds_on_off(rgir=[0, 0, 1])
                else:
                    self.leds_on_off(rgir=[0, 1, 0])
                    if color == "G":
                        self.update_roi_settings(threshold=self.defaults["thresholds"][5])
                    elif color == "B":
                        self.update_roi_settings(threshold=self.defaults["thresholds"][6])
                label = eval("self.root.ui.centers_%sicg_pos_label" % color.lower())
                img_path = eval("self.%s_icg_path" % color.lower())
                drawn_path = eval("self.%s_icg_drawn_path" % color.lower())

                while not (self.root.is_ok or self.root.is_aborted):
                    roi_center = [self.root.ui.roi_center_spin_x.value(), self.root.ui.roi_center_spin_y.value()]
                    roi_rads = [self.root.ui.roi_range_spin_min.value(), self.root.ui.roi_range_spin_max.value()]
                    threshold = self.root.ui.roi_threshold_spin.value()
                    self.root.drawn_frame, r_icg_center, _ = ip.detect_icg(self.root.raw_frame, roi_center=roi_center,
                                                                           roi_rads=roi_rads, side=self.side,
                                                                           threshold=threshold)
                    sorted_data = self.add_or_get_csv_data("icg", r_icg_center, ["", "", ""], get=True,
                                                           golden_icg=golden_icg)
                    for each in sorted_data:
                        new_label = "(%i, %i)" % (each[2], each[3])
                        if "%sICG" % color.upper() in each:
                            label.setText(new_label)
                            icg_centers[colors.index(color)] = [each[2], each[3]]

                if self.root.is_aborted:
                    return False

                self.root.thread_save_image(img_path, self.root.raw_frame)
                self.root.thread_save_image(drawn_path, self.root.drawn_frame)
                self.root.is_ok = False

            icg_cr = [round(ip.get_distance(icg, self.align_center[0]), 6) * self.root.pxl_size_mm for icg in
                      icg_centers if icg != []]
            self.add_or_get_csv_data(img_path, icg_centers, icg_cr, golden_icg=golden_icg)

            if self.cpc_passed:
                self.root.csv_data = ip.icg_cpc_distance(self.root.csv_data, pxl_to_mm=self.root.pxl_size_mm)
                for entry in self.csv_data:
                    if len(entry) > 2:
                        new_label = "%.6f (mm)" % round(entry[-1], 6)
                        if "ICG" in entry[1]:
                            if entry[1][0] == "R":
                                self.root.ui.centers_rdelta_pos_label.setText(new_label)
                            elif entry[1][0] == "G":
                                self.root.ui.centers_gdelta_pos_label.setText(new_label)
                            elif entry[1][0] == "B":
                                self.root.ui.centers_bdelta_pos_label.setText(new_label)
        else:
            return False

        self.root.drawn_frame = np.array([])
        self.root.is_ok = False

        return True

    def step_check_side(self, dark_limit=300):
        """
        Step 0: Determine side of binocle.
        """
        ok = self.root.dialog("Turn OFF the ring light (0.75 A).\nClick 'OK' to continue.")
        if ok == 1:
            self.leds_on_off(rgir=[1, 1, 1])
            self.move_axes_to_positions(["4", "1", "2", "3"], "l2")
            time.sleep(1)
            frame_check = self.root.raw_frame.copy()
            brightness = np.sum(frame_check, dtype='uint64') / frame_check.size
            if brightness > dark_limit:
                self.side = "R"
            else:
                self.side = "L"
            self.root.csv_data[4] = ["Side:", self.side]
            self.leds_on_off(rgir=[0, 0, 0])
        else:
            return False

        return True

    def move_axes_to_positions(self, order, kpi_step):
        """
        Move stages to positions in kpi_stage_positions variable.
        :param order: (list) Order in which to move the stages.
        :param kpi_step: (str) Which step/key in kpi_stage_positions.
        """
        if self.root.stages is not None:
            for axis in order:
                if self.root.is_aborted:
                    self.root.stages.device.StopAll(noraise=True)
                    break
                self.root.stages.move_to(axis, self.root.kpi_stage_positions[axis][kpi_step])

            while self.root.stages.device.IsMoving(order[-1])[order[-1]]:
                time.sleep(0.1)
            time.sleep(1)

    def update_roi_settings(self, roi_center=None, roi_rads=None, threshold=None):
        """
        Update ROI widget values.
        :param roi_center: (tuple/list) Tuple of values for ROI center (X, Y).
        :param roi_rads: (tuple/list) Tuple of values for ROI range (min, max).
        :param threshold: (int) Threshold value.
        """
        if roi_center is not None:
            self.root.ui.roi_center_spin_x.setValue(int(roi_center[0]))
            self.root.ui.roi_center_spin_y.setValue(int(roi_center[1]))

        if roi_rads is not None:
            self.root.ui.roi_range_spin_min.setValue(int(roi_rads[0]))
            self.root.ui.roi_range_spin_max.setValue(int(roi_rads[1]))

        if threshold is not None:
            self.root.ui.roi_threshold_spin.setValue(int(threshold))

    def make_file_paths(self):
        """
        Make local file paths for alignment images and CSV.
        """
        self.l1_base_path = make_file_path(self.folder_path, "L1_base.png")
        self.l1_path = make_file_path(self.folder_path, "L1.png")
        self.l1_drawn_path = make_file_path(self.folder_path, "L1_center.png")

        self.l2_path = make_file_path(self.folder_path, "L2.png")
        self.l2_drawn_path = make_file_path(self.folder_path, "L2_center.png")

        self.align_path = make_file_path(self.folder_path, "aligned.png")
        # self.align_diff_path = make_file_path(self.folder, "aligned_diffuser.png")
        self.align_drawn_path = make_file_path(self.folder_path, "aligned_center.png")

        self.cpc_path = make_file_path(self.folder_path, "cpc.png")
        self.cpc_drawn_path = make_file_path(self.folder_path, "cpc_centers.png")

        self.r_icg_path = make_file_path(self.folder_path, "r_icg.png")
        self.r_icg_drawn_path = make_file_path(self.folder_path, "r_icg_center.png")
        self.g_icg_path = make_file_path(self.folder_path, "g_icg.png")
        self.g_icg_drawn_path = make_file_path(self.folder_path, "g_icg_center.png")
        self.b_icg_path = make_file_path(self.folder_path, "b_icg.png")
        self.b_icg_drawn_path = make_file_path(self.folder_path, "b_icg_center.png")

        self.csv_path = make_file_path(self.folder_path, "detection_data.csv")

    def leds_on_off(self, rgir=[1, 1, 1]):
        """
        Turn off or on specified LEDs.
        :param rgir: (list) Boolean list corresponding to LEDs: red, green, and IR.
        """
        self.root.ui.led_red_enable_check.setChecked(bool(rgir[0]))
        self.root.ui.led_green_enable_check.setChecked(bool(rgir[1]))
        self.root.ui.led_ir_enable_check.setChecked(bool(rgir[2]))

        self.root.click_led_enable()

    def add_or_get_csv_data(self, image_path, center, radius=[""], get=False, thresh=None, golden_cpc=None,
                            golden_icg=None):
        """
        Add data to CSV data or retrieve what that data would be.
        :param image_path: (str) Path to image or image name.
        :param center: (list(tuples)) Center coordinate(s).
        :param radius: (list(tuples)) Radial distance(s) from center.
        :param get: (bool) Just get data or append data?
        :param thresh: (int) Used threshold value.
        :param golden_cpc: (list(tuples)) Known locations of good CPCs.
        :param golden_icg: (list(tuples)) Known locations of good ICGs.
        :return: (list) Data that would normally be added to CSV data.
        """
        exposure = self.root.ui.camera_exposure_slider.value()
        gain = self.root.ui.camera_gain_slider.value()
        gamma = float(self.root.ui.camera_gamma_slider.value()) / 10
        if thresh is None:
            thresh = self.root.ui.roi_threshold_spin.value()

        new_data = ip.arrange_data(image_path, center, radius, exposure, gain, gamma, thresh,
                                   golden_cpc=golden_cpc, golden_icg=golden_icg)
        if not get:
            self.root.csv_data = self.root.csv_data + new_data

        return new_data

    def add_kpi_pos_to_csv(self):
        """
        Append the stage positions from kpi_stage_positions to CSV data.
        """
        self.root.csv_data.append([""])
        self.root.csv_data.append(["Stage", "Name", "L1 (mm)", "L2 (mm)", "Aligned (mm)", "CPC (mm)", "ICG (mm)"])
        for stage in self.root.kpi_stage_positions:
            self.root.csv_data.append([int(stage), self.root.kpi_stage_positions[stage]["name"],
                                       self.root.kpi_stage_positions[stage]["l1"],
                                       self.root.kpi_stage_positions[stage]["l2"],
                                       self.root.kpi_stage_positions[stage]["align"],
                                       self.root.kpi_stage_positions[stage]["cpc"],
                                       self.root.kpi_stage_positions[stage]["icg"]])


def launch_GUI():
    """
    Creates QApp and launches main GUI.
    """
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())


def make_file_path(folder, file_name):
    """
    Make folder if DNE and change file name if already exists.
    :param folder: (str) Path to folder.
    :param file_name: (str) File name with extension.
    :return: (str) Corrected file path.
    """
    if not os.path.exists(folder):
        os.mkdir(folder)
    out_path = hw.check_path(os.path.join(folder, file_name))

    return out_path


if __name__ == "__main__":
    launch_GUI()
