# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form_sep.ui'
##
## Created by: Qt User Interface Compiler version 6.4.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QDoubleSpinBox, QGraphicsView,
    QLabel, QPushButton, QRadioButton, QSizePolicy,
    QSlider, QSpinBox, QTabWidget, QTextEdit,
    QToolButton, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(500, 640)
        self.stream_window = QGraphicsView(Widget)
        self.stream_window.setObjectName(u"stream_window")
        self.stream_window.setGeometry(QRect(20, 40, 459, 336))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stream_window.sizePolicy().hasHeightForWidth())
        self.stream_window.setSizePolicy(sizePolicy)
        self.stream_window.setMouseTracking(True)
        self.stream_window.setFocusPolicy(Qt.NoFocus)
        self.stream_window.setAutoFillBackground(False)
        self.stream_window.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.stream_window.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.stream_window.verticalScrollBar().setEnabled(False)
        self.stream_window.horizontalScrollBar().setEnabled(False)
        self.stream_window.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.stream_window.setInteractive(True)
        # self.stream_window.setSceneRect(QRectF(0, 0, 0, 0))
        self.stream_window.setDragMode(QGraphicsView.ScrollHandDrag)
        self.stream_window.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.stream_window.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.stream_label = QLabel(Widget)
        self.stream_label.setObjectName(u"stream_label")
        self.stream_label.setGeometry(QRect(20, 10, 170, 24))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.stream_label.setFont(font)
        self.control_tab_box = QTabWidget(Widget)
        self.control_tab_box.setObjectName(u"control_tab_box")
        self.control_tab_box.setGeometry(QRect(20, 430, 461, 191))
        self.control_tab_box.setAutoFillBackground(False)
        self.measure_tab = QWidget()
        self.measure_tab.setObjectName(u"measure_tab")
        self.measure_detected_label = QLabel(self.measure_tab)
        self.measure_detected_label.setObjectName(u"measure_detected_label")
        self.measure_detected_label.setGeometry(QRect(10, 20, 100, 24))
        self.measure_detected_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.measure_zero_label = QLabel(self.measure_tab)
        self.measure_zero_label.setObjectName(u"measure_zero_label")
        self.measure_zero_label.setGeometry(QRect(10, 50, 100, 24))
        self.measure_zero_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.measure_detected_position = QLabel(self.measure_tab)
        self.measure_detected_position.setObjectName(u"measure_detected_position")
        self.measure_detected_position.setGeometry(QRect(110, 20, 121, 24))
        self.measure_detected_position.setAlignment(Qt.AlignCenter)
        self.measure_zero_position = QLabel(self.measure_tab)
        self.measure_zero_position.setObjectName(u"measure_zero_position")
        self.measure_zero_position.setGeometry(QRect(110, 50, 121, 24))
        self.measure_zero_position.setAlignment(Qt.AlignCenter)
        self.measure_zero_button = QPushButton(self.measure_tab)
        self.measure_zero_button.setObjectName(u"measure_zero_button")
        self.measure_zero_button.setGeometry(QRect(240, 50, 90, 25))
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.measure_zero_button.sizePolicy().hasHeightForWidth())
        self.measure_zero_button.setSizePolicy(sizePolicy1)
        self.measure_zero_button.setAutoDefault(False)
        self.measure_delta_position = QLabel(self.measure_tab)
        self.measure_delta_position.setObjectName(u"measure_delta_position")
        self.measure_delta_position.setGeometry(QRect(110, 80, 121, 24))
        self.measure_delta_position.setAlignment(Qt.AlignCenter)
        self.measure_freeze_button = QPushButton(self.measure_tab)
        self.measure_freeze_button.setObjectName(u"measure_freeze_button")
        self.measure_freeze_button.setGeometry(QRect(240, 80, 90, 25))
        sizePolicy1.setHeightForWidth(self.measure_freeze_button.sizePolicy().hasHeightForWidth())
        self.measure_freeze_button.setSizePolicy(sizePolicy1)
        self.measure_freeze_button.setAutoDefault(False)
        self.measure_delta_label = QLabel(self.measure_tab)
        self.measure_delta_label.setObjectName(u"measure_delta_label")
        self.measure_delta_label.setGeometry(QRect(10, 80, 100, 24))
        self.measure_delta_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.measure_save_button = QPushButton(self.measure_tab)
        self.measure_save_button.setObjectName(u"measure_save_button")
        self.measure_save_button.setGeometry(QRect(340, 120, 90, 25))
        sizePolicy1.setHeightForWidth(self.measure_save_button.sizePolicy().hasHeightForWidth())
        self.measure_save_button.setSizePolicy(sizePolicy1)
        self.measure_save_button.setAutoDefault(False)
        self.measure_file_name_entry = QTextEdit(self.measure_tab)
        self.measure_file_name_entry.setObjectName(u"measure_file_name_entry")
        self.measure_file_name_entry.setGeometry(QRect(120, 120, 211, 24))
        self.measure_file_name_entry.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.measure_file_name_entry.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.measure_file_name_label = QLabel(self.measure_tab)
        self.measure_file_name_label.setObjectName(u"measure_file_name_label")
        self.measure_file_name_label.setGeometry(QRect(10, 120, 100, 24))
        self.measure_file_name_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.control_tab_box.addTab(self.measure_tab, "")
        self.camera_tab = QWidget()
        self.camera_tab.setObjectName(u"camera_tab")
        self.camera_exposure_label = QLabel(self.camera_tab)
        self.camera_exposure_label.setObjectName(u"camera_exposure_label")
        self.camera_exposure_label.setGeometry(QRect(10, 50, 100, 24))
        self.camera_exposure_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.camera_gamma_label = QLabel(self.camera_tab)
        self.camera_gamma_label.setObjectName(u"camera_gamma_label")
        self.camera_gamma_label.setGeometry(QRect(10, 80, 100, 24))
        self.camera_gamma_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.camera_exposure_slider = QSlider(self.camera_tab)
        self.camera_exposure_slider.setObjectName(u"camera_exposure_slider")
        self.camera_exposure_slider.setGeometry(QRect(120, 50, 201, 23))
        self.camera_exposure_slider.setTabletTracking(False)
        self.camera_exposure_slider.setAcceptDrops(False)
        self.camera_exposure_slider.setMinimum(500)
        self.camera_exposure_slider.setMaximum(250000)
        self.camera_exposure_slider.setSingleStep(10000)
        self.camera_exposure_slider.setPageStep(10)
        self.camera_exposure_slider.setValue(16667)
        self.camera_exposure_slider.setOrientation(Qt.Horizontal)
        self.camera_exposure_slider.setTickPosition(QSlider.TicksBelow)
        self.camera_exposure_slider.setTickInterval(10000)
        self.camera_exposure_spin = QSpinBox(self.camera_tab)
        self.camera_exposure_spin.setObjectName(u"camera_exposure_spin")
        self.camera_exposure_spin.setGeometry(QRect(330, 50, 75, 23))
        self.camera_exposure_spin.setMinimum(500)
        self.camera_exposure_spin.setMaximum(250000)
        self.camera_exposure_spin.setSingleStep(1000)
        self.camera_exposure_spin.setValue(16667)
        self.camera_gamma_slider = QSlider(self.camera_tab)
        self.camera_gamma_slider.setObjectName(u"camera_gamma_slider")
        self.camera_gamma_slider.setGeometry(QRect(120, 80, 201, 23))
        self.camera_gamma_slider.setMinimum(10)
        self.camera_gamma_slider.setMaximum(30)
        self.camera_gamma_slider.setSingleStep(1)
        self.camera_gamma_slider.setValue(10)
        self.camera_gamma_slider.setOrientation(Qt.Horizontal)
        self.camera_gamma_slider.setTickPosition(QSlider.TicksBelow)
        self.camera_gamma_slider.setTickInterval(1)
        self.camera_gamma_spin = QDoubleSpinBox(self.camera_tab)
        self.camera_gamma_spin.setObjectName(u"camera_gamma_spin")
        self.camera_gamma_spin.setGeometry(QRect(330, 80, 75, 23))
        self.camera_gamma_spin.setDecimals(1)
        self.camera_gamma_spin.setMinimum(1.000000000000000)
        self.camera_gamma_spin.setMaximum(3.000000000000000)
        self.camera_gamma_spin.setSingleStep(0.100000000000000)
        self.camera_gamma_spin.setValue(1.000000000000000)
        self.camera_capture_button = QPushButton(self.camera_tab)
        self.camera_capture_button.setObjectName(u"camera_capture_button")
        self.camera_capture_button.setGeometry(QRect(200, 120, 75, 25))
        self.camera_connect_indicator = QRadioButton(self.camera_tab)
        self.camera_connect_indicator.setObjectName(u"camera_connect_indicator")
        self.camera_connect_indicator.setGeometry(QRect(290, 20, 16, 25))
        self.camera_connect_indicator.setCursor(QCursor(Qt.ForbiddenCursor))
        self.camera_connect_indicator.setFocusPolicy(Qt.StrongFocus)
        self.camera_connect_indicator.setLayoutDirection(Qt.RightToLeft)
        self.camera_connect_indicator.setAutoFillBackground(False)
        self.camera_connect_indicator.setStyleSheet(u"QRadioButton::indicator{background-color : gray}")
        self.camera_connect_indicator.setCheckable(False)
        self.camera_connect_indicator.setAutoExclusive(True)
        self.camera_connect_button = QPushButton(self.camera_tab)
        self.camera_connect_button.setObjectName(u"camera_connect_button")
        self.camera_connect_button.setGeometry(QRect(200, 20, 90, 25))
        sizePolicy1.setHeightForWidth(self.camera_connect_button.sizePolicy().hasHeightForWidth())
        self.camera_connect_button.setSizePolicy(sizePolicy1)
        self.camera_connect_button.setAutoDefault(False)
        self.camera_id_label = QLabel(self.camera_tab)
        self.camera_id_label.setObjectName(u"camera_id_label")
        self.camera_id_label.setGeometry(QRect(10, 20, 100, 24))
        self.camera_id_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.camera_com_spin = QSpinBox(self.camera_tab)
        self.camera_com_spin.setObjectName(u"camera_com_spin")
        self.camera_com_spin.setEnabled(False)
        self.camera_com_spin.setGeometry(QRect(121, 20, 70, 23))
        self.camera_com_spin.setMaximum(10)
        self.camera_com_spin.setValue(1)
        self.control_tab_box.addTab(self.camera_tab, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.settings_contour_limits_label = QLabel(self.tab)
        self.settings_contour_limits_label.setObjectName(u"settings_contour_limits_label")
        self.settings_contour_limits_label.setGeometry(QRect(10, 20, 100, 24))
        self.settings_contour_limits_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.settings_threshold_label = QLabel(self.tab)
        self.settings_threshold_label.setObjectName(u"settings_threshold_label")
        self.settings_threshold_label.setGeometry(QRect(10, 50, 100, 24))
        self.settings_threshold_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.settings_contour_limits_min_spin = QSpinBox(self.tab)
        self.settings_contour_limits_min_spin.setObjectName(u"settings_contour_limits_min_spin")
        self.settings_contour_limits_min_spin.setGeometry(QRect(120, 20, 75, 23))
        self.settings_contour_limits_min_spin.setMinimum(0)
        self.settings_contour_limits_min_spin.setMaximum(9999999)
        self.settings_contour_limits_min_spin.setSingleStep(1000)
        self.settings_contour_limits_min_spin.setValue(1000)
        self.settings_contour_limits_max_spin = QSpinBox(self.tab)
        self.settings_contour_limits_max_spin.setObjectName(u"settings_contour_limits_max_spin")
        self.settings_contour_limits_max_spin.setGeometry(QRect(210, 20, 75, 23))
        self.settings_contour_limits_max_spin.setMinimum(1)
        self.settings_contour_limits_max_spin.setMaximum(10000000)
        self.settings_contour_limits_max_spin.setSingleStep(1000)
        self.settings_contour_limits_max_spin.setValue(15000)
        self.settings_threshold_spin = QSpinBox(self.tab)
        self.settings_threshold_spin.setObjectName(u"settings_threshold_spin")
        self.settings_threshold_spin.setGeometry(QRect(120, 50, 75, 23))
        self.settings_threshold_spin.setMinimum(0)
        self.settings_threshold_spin.setMaximum(255)
        self.settings_threshold_spin.setSingleStep(1)
        self.settings_threshold_spin.setValue(175)
        self.settings_circularity_label = QLabel(self.tab)
        self.settings_circularity_label.setObjectName(u"settings_circularity_label")
        self.settings_circularity_label.setGeometry(QRect(10, 80, 100, 24))
        self.settings_circularity_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.settings_circularity_min_spin = QDoubleSpinBox(self.tab)
        self.settings_circularity_min_spin.setObjectName(u"settings_circularity_min_spin")
        self.settings_circularity_min_spin.setGeometry(QRect(120, 80, 75, 22))
        self.settings_circularity_min_spin.setMaximum(2.000000000000000)
        self.settings_circularity_min_spin.setValue(0.600000000000000)
        self.settings_circularity_max_spin = QDoubleSpinBox(self.tab)
        self.settings_circularity_max_spin.setObjectName(u"settings_circularity_max_spin")
        self.settings_circularity_max_spin.setGeometry(QRect(210, 80, 75, 22))
        self.settings_circularity_max_spin.setMinimum(0.010000000000000)
        self.settings_circularity_max_spin.setMaximum(2.000000000000000)
        self.settings_circularity_max_spin.setSingleStep(0.010000000000000)
        self.settings_circularity_max_spin.setValue(1.200000000000000)
        self.control_tab_box.addTab(self.tab, "")
        self.browse_button = QToolButton(Widget)
        self.browse_button.setObjectName(u"browse_button")
        self.browse_button.setGeometry(QRect(450, 390, 24, 24))
        self.save_path_entry = QTextEdit(Widget)
        self.save_path_entry.setObjectName(u"save_path_entry")
        self.save_path_entry.setGeometry(QRect(90, 390, 351, 24))
        self.save_path_entry.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.save_path_entry.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.save_path_label = QLabel(Widget)
        self.save_path_label.setObjectName(u"save_path_label")
        self.save_path_label.setGeometry(QRect(9, 390, 71, 24))
        self.save_path_label.setLayoutDirection(Qt.LeftToRight)
        self.save_path_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.retranslateUi(Widget)

        self.control_tab_box.setCurrentIndex(0)
        self.measure_zero_button.setDefault(False)
        self.measure_freeze_button.setDefault(False)
        self.measure_save_button.setDefault(False)
        self.camera_connect_button.setDefault(False)


        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.stream_label.setText(QCoreApplication.translate("Widget", u"Camera Stream", None))
        self.measure_detected_label.setText(QCoreApplication.translate("Widget", u"Detected (x, y):", None))
        self.measure_zero_label.setText(QCoreApplication.translate("Widget", u"Saved Zero (x, y):", None))
        self.measure_detected_position.setText(QCoreApplication.translate("Widget", u"(0.000, 0.000)", None))
        self.measure_zero_position.setText(QCoreApplication.translate("Widget", u"(0.000, 0.000)", None))
        self.measure_zero_button.setText(QCoreApplication.translate("Widget", u"Set Zero", None))
        self.measure_delta_position.setText(QCoreApplication.translate("Widget", u"(0.000, 0.000)", None))
        self.measure_freeze_button.setText(QCoreApplication.translate("Widget", u"Freeze", None))
        self.measure_delta_label.setText(QCoreApplication.translate("Widget", u"Delta (x, y):", None))
        self.measure_save_button.setText(QCoreApplication.translate("Widget", u"Save!", None))
        self.measure_file_name_label.setText(QCoreApplication.translate("Widget", u"File Name:", None))
        self.control_tab_box.setTabText(self.control_tab_box.indexOf(self.measure_tab), QCoreApplication.translate("Widget", u"Measure", None))
        self.camera_exposure_label.setText(QCoreApplication.translate("Widget", u"Exposure (us):", None))
        self.camera_gamma_label.setText(QCoreApplication.translate("Widget", u"Gamma:", None))
        self.camera_capture_button.setText(QCoreApplication.translate("Widget", u"Capture!", None))
        self.camera_connect_indicator.setText("")
        self.camera_connect_button.setText(QCoreApplication.translate("Widget", u"Connect/Close", None))
        self.camera_id_label.setText(QCoreApplication.translate("Widget", u"Device ID:", None))
        self.control_tab_box.setTabText(self.control_tab_box.indexOf(self.camera_tab), QCoreApplication.translate("Widget", u"Camera", None))
        self.settings_contour_limits_label.setText(QCoreApplication.translate("Widget", u"Contour Limits:", None))
        self.settings_threshold_label.setText(QCoreApplication.translate("Widget", u"Threshold:", None))
        self.settings_circularity_label.setText(QCoreApplication.translate("Widget", u"Circularity:", None))
        self.control_tab_box.setTabText(self.control_tab_box.indexOf(self.tab), QCoreApplication.translate("Widget", u"Settings", None))
        self.browse_button.setText(QCoreApplication.translate("Widget", u"...", None))
        self.save_path_label.setText(QCoreApplication.translate("Widget", u"Save Path:", None))
    # retranslateUi

