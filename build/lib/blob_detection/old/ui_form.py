# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QDoubleSpinBox, QFrame,
    QGraphicsView, QLabel, QPushButton, QRadioButton,
    QSizePolicy, QSlider, QSpinBox, QTabWidget,
    QTextEdit, QToolButton, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(1000, 640)
        self.cam1_stream_window = QGraphicsView(Widget)
        self.cam1_stream_window.setObjectName(u"cam1_stream_window")
        self.cam1_stream_window.setGeometry(QRect(20, 40, 459, 336))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cam1_stream_window.sizePolicy().hasHeightForWidth())
        self.cam1_stream_window.setSizePolicy(sizePolicy)
        self.cam1_stream_window.setMouseTracking(True)
        self.cam1_stream_window.setFocusPolicy(Qt.NoFocus)
        self.cam1_stream_window.setAutoFillBackground(False)
        self.cam1_stream_window.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cam1_stream_window.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cam1_stream_window.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.cam1_stream_window.setInteractive(True)
        # self.cam1_stream_window.setSceneRect(QRectF(0, 0, 0, 0))
        self.cam1_stream_window.setDragMode(QGraphicsView.ScrollHandDrag)
        self.cam1_stream_window.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.cam1_stream_window.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.cam1_stream_label = QLabel(Widget)
        self.cam1_stream_label.setObjectName(u"cam1_stream_label")
        self.cam1_stream_label.setGeometry(QRect(20, 10, 170, 24))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.cam1_stream_label.setFont(font)
        self.cam1_control_tab_box = QTabWidget(Widget)
        self.cam1_control_tab_box.setObjectName(u"cam1_control_tab_box")
        self.cam1_control_tab_box.setGeometry(QRect(20, 430, 461, 191))
        self.cam1_control_tab_box.setAutoFillBackground(False)
        self.lcos_tab = QWidget()
        self.lcos_tab.setObjectName(u"lcos_tab")
        self.cam1_measure_detected_label = QLabel(self.lcos_tab)
        self.cam1_measure_detected_label.setObjectName(u"cam1_measure_detected_label")
        self.cam1_measure_detected_label.setGeometry(QRect(10, 20, 100, 24))
        self.cam1_measure_detected_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam1_measure_zero_label = QLabel(self.lcos_tab)
        self.cam1_measure_zero_label.setObjectName(u"cam1_measure_zero_label")
        self.cam1_measure_zero_label.setGeometry(QRect(10, 50, 100, 24))
        self.cam1_measure_zero_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam1_measure_detected_position = QLabel(self.lcos_tab)
        self.cam1_measure_detected_position.setObjectName(u"cam1_measure_detected_position")
        self.cam1_measure_detected_position.setGeometry(QRect(110, 20, 121, 24))
        self.cam1_measure_detected_position.setAlignment(Qt.AlignCenter)
        self.cam1_measure_zero_position = QLabel(self.lcos_tab)
        self.cam1_measure_zero_position.setObjectName(u"cam1_measure_zero_position")
        self.cam1_measure_zero_position.setGeometry(QRect(110, 50, 121, 24))
        self.cam1_measure_zero_position.setAlignment(Qt.AlignCenter)
        self.cam1_measure_zero_button = QPushButton(self.lcos_tab)
        self.cam1_measure_zero_button.setObjectName(u"cam1_measure_zero_button")
        self.cam1_measure_zero_button.setGeometry(QRect(240, 50, 90, 25))
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cam1_measure_zero_button.sizePolicy().hasHeightForWidth())
        self.cam1_measure_zero_button.setSizePolicy(sizePolicy1)
        self.cam1_measure_zero_button.setAutoDefault(False)
        self.cam1_measure_delta_position = QLabel(self.lcos_tab)
        self.cam1_measure_delta_position.setObjectName(u"cam1_measure_delta_position")
        self.cam1_measure_delta_position.setGeometry(QRect(110, 80, 121, 24))
        self.cam1_measure_delta_position.setAlignment(Qt.AlignCenter)
        self.cam1_freeze_delta_button = QPushButton(self.lcos_tab)
        self.cam1_freeze_delta_button.setObjectName(u"cam1_freeze_delta_button")
        self.cam1_freeze_delta_button.setGeometry(QRect(240, 80, 90, 25))
        sizePolicy1.setHeightForWidth(self.cam1_freeze_delta_button.sizePolicy().hasHeightForWidth())
        self.cam1_freeze_delta_button.setSizePolicy(sizePolicy1)
        self.cam1_freeze_delta_button.setAutoDefault(False)
        self.cam1_measure_delta_label = QLabel(self.lcos_tab)
        self.cam1_measure_delta_label.setObjectName(u"cam1_measure_delta_label")
        self.cam1_measure_delta_label.setGeometry(QRect(10, 80, 100, 24))
        self.cam1_measure_delta_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam1_save_button = QPushButton(self.lcos_tab)
        self.cam1_save_button.setObjectName(u"cam1_save_button")
        self.cam1_save_button.setGeometry(QRect(340, 80, 90, 25))
        sizePolicy1.setHeightForWidth(self.cam1_save_button.sizePolicy().hasHeightForWidth())
        self.cam1_save_button.setSizePolicy(sizePolicy1)
        self.cam1_save_button.setAutoDefault(False)
        self.cam1_control_tab_box.addTab(self.lcos_tab, "")
        self.camera_tab = QWidget()
        self.camera_tab.setObjectName(u"camera_tab")
        self.cam1_camera_exposure_label = QLabel(self.camera_tab)
        self.cam1_camera_exposure_label.setObjectName(u"cam1_camera_exposure_label")
        self.cam1_camera_exposure_label.setGeometry(QRect(10, 50, 100, 24))
        self.cam1_camera_exposure_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam1_camera_gamma_label = QLabel(self.camera_tab)
        self.cam1_camera_gamma_label.setObjectName(u"cam1_camera_gamma_label")
        self.cam1_camera_gamma_label.setGeometry(QRect(10, 80, 100, 24))
        self.cam1_camera_gamma_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam1_camera_exposure_slider = QSlider(self.camera_tab)
        self.cam1_camera_exposure_slider.setObjectName(u"cam1_camera_exposure_slider")
        self.cam1_camera_exposure_slider.setGeometry(QRect(120, 50, 201, 23))
        self.cam1_camera_exposure_slider.setTabletTracking(False)
        self.cam1_camera_exposure_slider.setAcceptDrops(False)
        self.cam1_camera_exposure_slider.setMinimum(500)
        self.cam1_camera_exposure_slider.setMaximum(250000)
        self.cam1_camera_exposure_slider.setSingleStep(10000)
        self.cam1_camera_exposure_slider.setPageStep(10)
        self.cam1_camera_exposure_slider.setValue(16667)
        self.cam1_camera_exposure_slider.setOrientation(Qt.Horizontal)
        self.cam1_camera_exposure_slider.setTickPosition(QSlider.TicksBelow)
        self.cam1_camera_exposure_slider.setTickInterval(10000)
        self.cam1_camera_exposure_spin = QSpinBox(self.camera_tab)
        self.cam1_camera_exposure_spin.setObjectName(u"cam1_camera_exposure_spin")
        self.cam1_camera_exposure_spin.setGeometry(QRect(330, 50, 75, 23))
        self.cam1_camera_exposure_spin.setMinimum(500)
        self.cam1_camera_exposure_spin.setMaximum(250000)
        self.cam1_camera_exposure_spin.setSingleStep(1000)
        self.cam1_camera_exposure_spin.setValue(16667)
        self.cam1_camera_gamma_slider = QSlider(self.camera_tab)
        self.cam1_camera_gamma_slider.setObjectName(u"cam1_camera_gamma_slider")
        self.cam1_camera_gamma_slider.setGeometry(QRect(120, 80, 201, 23))
        self.cam1_camera_gamma_slider.setMinimum(10)
        self.cam1_camera_gamma_slider.setMaximum(30)
        self.cam1_camera_gamma_slider.setSingleStep(1)
        self.cam1_camera_gamma_slider.setValue(10)
        self.cam1_camera_gamma_slider.setOrientation(Qt.Horizontal)
        self.cam1_camera_gamma_slider.setTickPosition(QSlider.TicksBelow)
        self.cam1_camera_gamma_slider.setTickInterval(1)
        self.cam1_camera_gamma_spin = QDoubleSpinBox(self.camera_tab)
        self.cam1_camera_gamma_spin.setObjectName(u"cam1_camera_gamma_spin")
        self.cam1_camera_gamma_spin.setGeometry(QRect(330, 80, 75, 23))
        self.cam1_camera_gamma_spin.setDecimals(1)
        self.cam1_camera_gamma_spin.setMinimum(1.000000000000000)
        self.cam1_camera_gamma_spin.setMaximum(3.000000000000000)
        self.cam1_camera_gamma_spin.setSingleStep(0.100000000000000)
        self.cam1_camera_gamma_spin.setValue(1.000000000000000)
        self.cam1_camera_capture_button = QPushButton(self.camera_tab)
        self.cam1_camera_capture_button.setObjectName(u"cam1_camera_capture_button")
        self.cam1_camera_capture_button.setGeometry(QRect(200, 120, 75, 25))
        self.cam1_camera_connect_indicator = QRadioButton(self.camera_tab)
        self.cam1_camera_connect_indicator.setObjectName(u"cam1_camera_connect_indicator")
        self.cam1_camera_connect_indicator.setGeometry(QRect(290, 20, 16, 25))
        self.cam1_camera_connect_indicator.setCursor(QCursor(Qt.ForbiddenCursor))
        self.cam1_camera_connect_indicator.setFocusPolicy(Qt.StrongFocus)
        self.cam1_camera_connect_indicator.setLayoutDirection(Qt.RightToLeft)
        self.cam1_camera_connect_indicator.setAutoFillBackground(False)
        self.cam1_camera_connect_indicator.setStyleSheet(u"QRadioButton::indicator{background-color : gray}")
        self.cam1_camera_connect_indicator.setCheckable(False)
        self.cam1_camera_connect_indicator.setAutoExclusive(True)
        self.cam1_camera_connect_button = QPushButton(self.camera_tab)
        self.cam1_camera_connect_button.setObjectName(u"cam1_camera_connect_button")
        self.cam1_camera_connect_button.setGeometry(QRect(200, 20, 90, 25))
        sizePolicy1.setHeightForWidth(self.cam1_camera_connect_button.sizePolicy().hasHeightForWidth())
        self.cam1_camera_connect_button.setSizePolicy(sizePolicy1)
        self.cam1_camera_connect_button.setAutoDefault(False)
        self.cam1_camera_id_label = QLabel(self.camera_tab)
        self.cam1_camera_id_label.setObjectName(u"cam1_camera_id_label")
        self.cam1_camera_id_label.setGeometry(QRect(10, 20, 100, 24))
        self.cam1_camera_id_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam1_camera_com_spin = QSpinBox(self.camera_tab)
        self.cam1_camera_com_spin.setObjectName(u"cam1_camera_com_spin")
        self.cam1_camera_com_spin.setEnabled(False)
        self.cam1_camera_com_spin.setGeometry(QRect(121, 20, 70, 23))
        self.cam1_camera_com_spin.setMaximum(10)
        self.cam1_camera_com_spin.setValue(1)
        self.cam1_control_tab_box.addTab(self.camera_tab, "")
        self.cam1_browse_button = QToolButton(Widget)
        self.cam1_browse_button.setObjectName(u"cam1_browse_button")
        self.cam1_browse_button.setGeometry(QRect(450, 390, 24, 24))
        self.cam1_save_path_entry = QTextEdit(Widget)
        self.cam1_save_path_entry.setObjectName(u"cam1_save_path_entry")
        self.cam1_save_path_entry.setGeometry(QRect(90, 390, 351, 24))
        self.cam1_save_path_entry.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cam1_save_path_entry.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cam1_save_path_label = QLabel(Widget)
        self.cam1_save_path_label.setObjectName(u"cam1_save_path_label")
        self.cam1_save_path_label.setGeometry(QRect(9, 390, 71, 24))
        self.cam1_save_path_label.setLayoutDirection(Qt.LeftToRight)
        self.cam1_save_path_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam2_stream_label = QLabel(Widget)
        self.cam2_stream_label.setObjectName(u"cam2_stream_label")
        self.cam2_stream_label.setGeometry(QRect(520, 10, 170, 24))
        self.cam2_stream_label.setFont(font)
        self.line = QFrame(Widget)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(490, 10, 20, 621))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.cam2_browse_button = QToolButton(Widget)
        self.cam2_browse_button.setObjectName(u"cam2_browse_button")
        self.cam2_browse_button.setGeometry(QRect(950, 390, 24, 24))
        self.cam2_save_path_label = QLabel(Widget)
        self.cam2_save_path_label.setObjectName(u"cam2_save_path_label")
        self.cam2_save_path_label.setGeometry(QRect(509, 390, 71, 24))
        self.cam2_save_path_label.setLayoutDirection(Qt.LeftToRight)
        self.cam2_save_path_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam2_stream_window = QGraphicsView(Widget)
        self.cam2_stream_window.setObjectName(u"cam2_stream_window")
        self.cam2_stream_window.setGeometry(QRect(520, 40, 459, 336))
        sizePolicy.setHeightForWidth(self.cam2_stream_window.sizePolicy().hasHeightForWidth())
        self.cam2_stream_window.setSizePolicy(sizePolicy)
        self.cam2_stream_window.setMouseTracking(True)
        self.cam2_stream_window.setFocusPolicy(Qt.NoFocus)
        self.cam2_stream_window.setAutoFillBackground(False)
        self.cam2_stream_window.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cam2_stream_window.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cam2_stream_window.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.cam2_stream_window.setInteractive(True)
        # self.cam2_stream_window.setSceneRect(QRectF(0, 0, 0, 0))
        self.cam2_stream_window.setDragMode(QGraphicsView.ScrollHandDrag)
        self.cam2_stream_window.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.cam2_stream_window.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.cam2_control_tab_box = QTabWidget(Widget)
        self.cam2_control_tab_box.setObjectName(u"cam2_control_tab_box")
        self.cam2_control_tab_box.setGeometry(QRect(520, 430, 461, 191))
        self.cam2_control_tab_box.setAutoFillBackground(False)
        self.lcos_tab_2 = QWidget()
        self.lcos_tab_2.setObjectName(u"lcos_tab_2")
        self.cam2_measure_detected_label = QLabel(self.lcos_tab_2)
        self.cam2_measure_detected_label.setObjectName(u"cam2_measure_detected_label")
        self.cam2_measure_detected_label.setGeometry(QRect(10, 20, 100, 24))
        self.cam2_measure_detected_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam2_measure_zero_label = QLabel(self.lcos_tab_2)
        self.cam2_measure_zero_label.setObjectName(u"cam2_measure_zero_label")
        self.cam2_measure_zero_label.setGeometry(QRect(10, 50, 100, 24))
        self.cam2_measure_zero_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam2_measure_detected_position = QLabel(self.lcos_tab_2)
        self.cam2_measure_detected_position.setObjectName(u"cam2_measure_detected_position")
        self.cam2_measure_detected_position.setGeometry(QRect(110, 20, 121, 24))
        self.cam2_measure_detected_position.setAlignment(Qt.AlignCenter)
        self.cam2_measure_zero_position = QLabel(self.lcos_tab_2)
        self.cam2_measure_zero_position.setObjectName(u"cam2_measure_zero_position")
        self.cam2_measure_zero_position.setGeometry(QRect(110, 50, 121, 24))
        self.cam2_measure_zero_position.setAlignment(Qt.AlignCenter)
        self.cam2_measure_zero_button = QPushButton(self.lcos_tab_2)
        self.cam2_measure_zero_button.setObjectName(u"cam2_measure_zero_button")
        self.cam2_measure_zero_button.setGeometry(QRect(240, 50, 90, 25))
        sizePolicy1.setHeightForWidth(self.cam2_measure_zero_button.sizePolicy().hasHeightForWidth())
        self.cam2_measure_zero_button.setSizePolicy(sizePolicy1)
        self.cam2_measure_zero_button.setAutoDefault(False)
        self.cam2_measure_delta_position = QLabel(self.lcos_tab_2)
        self.cam2_measure_delta_position.setObjectName(u"cam2_measure_delta_position")
        self.cam2_measure_delta_position.setGeometry(QRect(110, 80, 121, 24))
        self.cam2_measure_delta_position.setAlignment(Qt.AlignCenter)
        self.cam2_freeze_delta_button = QPushButton(self.lcos_tab_2)
        self.cam2_freeze_delta_button.setObjectName(u"cam2_freeze_delta_button")
        self.cam2_freeze_delta_button.setGeometry(QRect(240, 80, 90, 25))
        sizePolicy1.setHeightForWidth(self.cam2_freeze_delta_button.sizePolicy().hasHeightForWidth())
        self.cam2_freeze_delta_button.setSizePolicy(sizePolicy1)
        self.cam2_freeze_delta_button.setAutoDefault(False)
        self.cam2_measure_delta_label = QLabel(self.lcos_tab_2)
        self.cam2_measure_delta_label.setObjectName(u"cam2_measure_delta_label")
        self.cam2_measure_delta_label.setGeometry(QRect(10, 80, 100, 24))
        self.cam2_measure_delta_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam2_save_button = QPushButton(self.lcos_tab_2)
        self.cam2_save_button.setObjectName(u"cam2_save_button")
        self.cam2_save_button.setGeometry(QRect(340, 80, 90, 25))
        sizePolicy1.setHeightForWidth(self.cam2_save_button.sizePolicy().hasHeightForWidth())
        self.cam2_save_button.setSizePolicy(sizePolicy1)
        self.cam2_save_button.setAutoDefault(False)
        self.cam2_control_tab_box.addTab(self.lcos_tab_2, "")
        self.camera_tab_2 = QWidget()
        self.camera_tab_2.setObjectName(u"camera_tab_2")
        self.cam2_camera_exposure_label = QLabel(self.camera_tab_2)
        self.cam2_camera_exposure_label.setObjectName(u"cam2_camera_exposure_label")
        self.cam2_camera_exposure_label.setGeometry(QRect(10, 50, 100, 24))
        self.cam2_camera_exposure_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam2_camera_gamma_label = QLabel(self.camera_tab_2)
        self.cam2_camera_gamma_label.setObjectName(u"cam2_camera_gamma_label")
        self.cam2_camera_gamma_label.setGeometry(QRect(10, 80, 100, 24))
        self.cam2_camera_gamma_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam2_camera_exposure_slider = QSlider(self.camera_tab_2)
        self.cam2_camera_exposure_slider.setObjectName(u"cam2_camera_exposure_slider")
        self.cam2_camera_exposure_slider.setGeometry(QRect(120, 50, 201, 23))
        self.cam2_camera_exposure_slider.setTabletTracking(False)
        self.cam2_camera_exposure_slider.setAcceptDrops(False)
        self.cam2_camera_exposure_slider.setMinimum(500)
        self.cam2_camera_exposure_slider.setMaximum(250000)
        self.cam2_camera_exposure_slider.setSingleStep(10000)
        self.cam2_camera_exposure_slider.setPageStep(10)
        self.cam2_camera_exposure_slider.setValue(16667)
        self.cam2_camera_exposure_slider.setOrientation(Qt.Horizontal)
        self.cam2_camera_exposure_slider.setTickPosition(QSlider.TicksBelow)
        self.cam2_camera_exposure_slider.setTickInterval(10000)
        self.cam2_camera_exposure_spin = QSpinBox(self.camera_tab_2)
        self.cam2_camera_exposure_spin.setObjectName(u"cam2_camera_exposure_spin")
        self.cam2_camera_exposure_spin.setGeometry(QRect(330, 50, 75, 23))
        self.cam2_camera_exposure_spin.setMinimum(500)
        self.cam2_camera_exposure_spin.setMaximum(250000)
        self.cam2_camera_exposure_spin.setSingleStep(1000)
        self.cam2_camera_exposure_spin.setValue(16667)
        self.cam2_camera_gamma_slider = QSlider(self.camera_tab_2)
        self.cam2_camera_gamma_slider.setObjectName(u"cam2_camera_gamma_slider")
        self.cam2_camera_gamma_slider.setGeometry(QRect(120, 80, 201, 23))
        self.cam2_camera_gamma_slider.setMinimum(10)
        self.cam2_camera_gamma_slider.setMaximum(30)
        self.cam2_camera_gamma_slider.setSingleStep(1)
        self.cam2_camera_gamma_slider.setValue(10)
        self.cam2_camera_gamma_slider.setOrientation(Qt.Horizontal)
        self.cam2_camera_gamma_slider.setTickPosition(QSlider.TicksBelow)
        self.cam2_camera_gamma_slider.setTickInterval(1)
        self.cam2_camera_gamma_spin = QDoubleSpinBox(self.camera_tab_2)
        self.cam2_camera_gamma_spin.setObjectName(u"cam2_camera_gamma_spin")
        self.cam2_camera_gamma_spin.setGeometry(QRect(330, 80, 75, 23))
        self.cam2_camera_gamma_spin.setDecimals(1)
        self.cam2_camera_gamma_spin.setMinimum(1.000000000000000)
        self.cam2_camera_gamma_spin.setMaximum(3.000000000000000)
        self.cam2_camera_gamma_spin.setSingleStep(0.100000000000000)
        self.cam2_camera_gamma_spin.setValue(1.000000000000000)
        self.cam2_camera_capture_button = QPushButton(self.camera_tab_2)
        self.cam2_camera_capture_button.setObjectName(u"cam2_camera_capture_button")
        self.cam2_camera_capture_button.setGeometry(QRect(200, 120, 75, 25))
        self.cam2_camera_connect_indicator = QRadioButton(self.camera_tab_2)
        self.cam2_camera_connect_indicator.setObjectName(u"cam2_camera_connect_indicator")
        self.cam2_camera_connect_indicator.setGeometry(QRect(290, 20, 16, 25))
        self.cam2_camera_connect_indicator.setCursor(QCursor(Qt.ForbiddenCursor))
        self.cam2_camera_connect_indicator.setFocusPolicy(Qt.StrongFocus)
        self.cam2_camera_connect_indicator.setLayoutDirection(Qt.RightToLeft)
        self.cam2_camera_connect_indicator.setAutoFillBackground(False)
        self.cam2_camera_connect_indicator.setStyleSheet(u"QRadioButton::indicator{background-color : gray}")
        self.cam2_camera_connect_indicator.setCheckable(False)
        self.cam2_camera_connect_indicator.setAutoExclusive(True)
        self.cam2_camera_connect_button = QPushButton(self.camera_tab_2)
        self.cam2_camera_connect_button.setObjectName(u"cam2_camera_connect_button")
        self.cam2_camera_connect_button.setGeometry(QRect(200, 20, 90, 25))
        sizePolicy1.setHeightForWidth(self.cam2_camera_connect_button.sizePolicy().hasHeightForWidth())
        self.cam2_camera_connect_button.setSizePolicy(sizePolicy1)
        self.cam2_camera_connect_button.setAutoDefault(False)
        self.cam2_camera_id_label = QLabel(self.camera_tab_2)
        self.cam2_camera_id_label.setObjectName(u"cam2_camera_id_label")
        self.cam2_camera_id_label.setGeometry(QRect(10, 20, 100, 24))
        self.cam2_camera_id_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cam2_camera_com_spin = QSpinBox(self.camera_tab_2)
        self.cam2_camera_com_spin.setObjectName(u"cam2_camera_com_spin")
        self.cam2_camera_com_spin.setEnabled(False)
        self.cam2_camera_com_spin.setGeometry(QRect(120, 20, 70, 23))
        self.cam2_camera_com_spin.setMaximum(10)
        self.cam2_camera_com_spin.setValue(2)
        self.cam2_control_tab_box.addTab(self.camera_tab_2, "")
        self.cam2_save_path_entry = QTextEdit(Widget)
        self.cam2_save_path_entry.setObjectName(u"cam2_save_path_entry")
        self.cam2_save_path_entry.setGeometry(QRect(590, 390, 351, 24))
        self.cam2_save_path_entry.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cam2_save_path_entry.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.retranslateUi(Widget)

        self.cam1_control_tab_box.setCurrentIndex(1)
        self.cam1_measure_zero_button.setDefault(False)
        self.cam1_freeze_delta_button.setDefault(False)
        self.cam1_save_button.setDefault(False)
        self.cam1_camera_connect_button.setDefault(False)
        self.cam2_control_tab_box.setCurrentIndex(1)
        self.cam2_measure_zero_button.setDefault(False)
        self.cam2_freeze_delta_button.setDefault(False)
        self.cam2_save_button.setDefault(False)
        self.cam2_camera_connect_button.setDefault(False)


        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.cam1_stream_label.setText(QCoreApplication.translate("Widget", u"Camera 1 Detection", None))
        self.cam1_measure_detected_label.setText(QCoreApplication.translate("Widget", u"Detected (x, y):", None))
        self.cam1_measure_zero_label.setText(QCoreApplication.translate("Widget", u"Saved Zero (x, y):", None))
        self.cam1_measure_detected_position.setText(QCoreApplication.translate("Widget", u"(0.000, 0.000)", None))
        self.cam1_measure_zero_position.setText(QCoreApplication.translate("Widget", u"(0.000, 0.000)", None))
        self.cam1_measure_zero_button.setText(QCoreApplication.translate("Widget", u"Set Zero", None))
        self.cam1_measure_delta_position.setText(QCoreApplication.translate("Widget", u"(0.000, 0.000)", None))
        self.cam1_freeze_delta_button.setText(QCoreApplication.translate("Widget", u"Freeze", None))
        self.cam1_measure_delta_label.setText(QCoreApplication.translate("Widget", u"Delta (x, y):", None))
        self.cam1_save_button.setText(QCoreApplication.translate("Widget", u"Save!", None))
        self.cam1_control_tab_box.setTabText(self.cam1_control_tab_box.indexOf(self.lcos_tab), QCoreApplication.translate("Widget", u"Measure", None))
        self.cam1_camera_exposure_label.setText(QCoreApplication.translate("Widget", u"Exposure (us):", None))
        self.cam1_camera_gamma_label.setText(QCoreApplication.translate("Widget", u"Gamma:", None))
        self.cam1_camera_capture_button.setText(QCoreApplication.translate("Widget", u"Capture!", None))
        self.cam1_camera_connect_indicator.setText("")
        self.cam1_camera_connect_button.setText(QCoreApplication.translate("Widget", u"Connect/Close", None))
        self.cam1_camera_id_label.setText(QCoreApplication.translate("Widget", u"Device ID:", None))
        self.cam1_control_tab_box.setTabText(self.cam1_control_tab_box.indexOf(self.camera_tab), QCoreApplication.translate("Widget", u"Camera", None))
        self.cam1_browse_button.setText(QCoreApplication.translate("Widget", u"...", None))
        self.cam1_save_path_label.setText(QCoreApplication.translate("Widget", u"Save Path:", None))
        self.cam2_stream_label.setText(QCoreApplication.translate("Widget", u"Camera 2 Detection", None))
        self.cam2_browse_button.setText(QCoreApplication.translate("Widget", u"...", None))
        self.cam2_save_path_label.setText(QCoreApplication.translate("Widget", u"Save Path:", None))
        self.cam2_measure_detected_label.setText(QCoreApplication.translate("Widget", u"Detected (x, y):", None))
        self.cam2_measure_zero_label.setText(QCoreApplication.translate("Widget", u"Saved Zero (x, y):", None))
        self.cam2_measure_detected_position.setText(QCoreApplication.translate("Widget", u"(0.000, 0.000)", None))
        self.cam2_measure_zero_position.setText(QCoreApplication.translate("Widget", u"(0.000, 0.000)", None))
        self.cam2_measure_zero_button.setText(QCoreApplication.translate("Widget", u"Set Zero", None))
        self.cam2_measure_delta_position.setText(QCoreApplication.translate("Widget", u"(0.000, 0.000)", None))
        self.cam2_freeze_delta_button.setText(QCoreApplication.translate("Widget", u"Freeze", None))
        self.cam2_measure_delta_label.setText(QCoreApplication.translate("Widget", u"Delta (x, y):", None))
        self.cam2_save_button.setText(QCoreApplication.translate("Widget", u"Save!", None))
        self.cam2_control_tab_box.setTabText(self.cam2_control_tab_box.indexOf(self.lcos_tab_2), QCoreApplication.translate("Widget", u"Measure", None))
        self.cam2_camera_exposure_label.setText(QCoreApplication.translate("Widget", u"Exposure (us):", None))
        self.cam2_camera_gamma_label.setText(QCoreApplication.translate("Widget", u"Gamma:", None))
        self.cam2_camera_capture_button.setText(QCoreApplication.translate("Widget", u"Capture!", None))
        self.cam2_camera_connect_indicator.setText("")
        self.cam2_camera_connect_button.setText(QCoreApplication.translate("Widget", u"Connect/Close", None))
        self.cam2_camera_id_label.setText(QCoreApplication.translate("Widget", u"Device ID:", None))
        self.cam2_control_tab_box.setTabText(self.cam2_control_tab_box.indexOf(self.camera_tab_2), QCoreApplication.translate("Widget", u"Camera", None))
    # retranslateUi
