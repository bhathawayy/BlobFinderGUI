AMCAM_MAX = 128

AMCAM_FLAG_CMOS = 0x00000001  # cmos sensor
AMCAM_FLAG_CCD_PROGRESSIVE = 0x00000002  # progressive ccd sensor
AMCAM_FLAG_CCD_INTERLACED = 0x00000004  # interlaced ccd sensor
AMCAM_FLAG_ROI_HARDWARE = 0x00000008  # support hardware ROI
AMCAM_FLAG_MONO = 0x00000010  # monochromatic
AMCAM_FLAG_BINSKIP_SUPPORTED = 0x00000020  # support bin/skip mode
AMCAM_FLAG_USB30 = 0x00000040  # usb3.0
AMCAM_FLAG_TEC = 0x00000080  # Thermoelectric Cooler
AMCAM_FLAG_USB30_OVER_USB20 = 0x00000100  # usb3.0 camera connected to usb2.0 port
AMCAM_FLAG_ST4 = 0x00000200  # ST4
AMCAM_FLAG_GETTEMPERATURE = 0x00000400  # support to get the temperature of the sensor
AMCAM_FLAG_RAW10 = 0x00001000  # pixel format, RAW 10bits
AMCAM_FLAG_RAW12 = 0x00002000  # pixel format, RAW 12bits
AMCAM_FLAG_RAW14 = 0x00004000  # pixel format, RAW 14bits
AMCAM_FLAG_RAW16 = 0x00008000  # pixel format, RAW 16bits
AMCAM_FLAG_FAN = 0x00010000  # cooling fan
AMCAM_FLAG_TEC_ONOFF = 0x00020000  # Thermoelectric Cooler can be turn on or off, support to set the target temperature of TEC
AMCAM_FLAG_ISP = 0x00040000  # ISP (Image Signal Processing) chip
AMCAM_FLAG_TRIGGER_SOFTWARE = 0x00080000  # support software trigger
AMCAM_FLAG_TRIGGER_EXTERNAL = 0x00100000  # support external trigger
AMCAM_FLAG_TRIGGER_SINGLE = 0x00200000  # only support trigger single: one trigger, one image
AMCAM_FLAG_BLACKLEVEL = 0x00400000  # support set and get the black level
AMCAM_FLAG_AUTO_FOCUS = 0x00800000  # support auto focus
AMCAM_FLAG_BUFFER = 0x01000000  # frame buffer
AMCAM_FLAG_DDR = 0x02000000  # use very large capacity DDR (Double Data Rate SDRAM) for frame buffer
AMCAM_FLAG_CG = 0x04000000  # support Conversion Gain mode: HCG, LCG
AMCAM_FLAG_YUV411 = 0x08000000  # pixel format, yuv411
AMCAM_FLAG_VUYY = 0x10000000  # pixel format, yuv422, VUYY
AMCAM_FLAG_YUV444 = 0x20000000  # pixel format, yuv444
AMCAM_FLAG_RGB888 = 0x40000000  # pixel format, RGB888
AMCAM_FLAG_RAW8 = 0x80000000  # pixel format, RAW 8 bits
AMCAM_FLAG_GMCY8 = 0x0000000100000000  # pixel format, GMCY, 8 bits
AMCAM_FLAG_GMCY12 = 0x0000000200000000  # pixel format, GMCY, 12 bits
AMCAM_FLAG_UYVY = 0x0000000400000000  # pixel format, yuv422, UYVY
AMCAM_FLAG_CGHDR = 0x0000000800000000  # Conversion Gain: HCG, LCG, HDR
AMCAM_FLAG_GLOBALSHUTTER = 0x0000001000000000  # global shutter
AMCAM_FLAG_FOCUSMOTOR = 0x0000002000000000  # support focus motor
AMCAM_FLAG_PRECISE_FRAMERATE = 0x0000004000000000  # support precise framerate & bandwidth, see AMCAM_OPTION_PRECISE_FRAMERATE & AMCAM_OPTION_BANDWIDTH
AMCAM_FLAG_HEAT = 0x0000008000000000  # support heat to prevent fogging up
AMCAM_FLAG_LOW_NOISE = 0x0000010000000000  # support low noise mode (Higher signal noise ratio, lower frame rate)
AMCAM_FLAG_LEVELRANGE_HARDWARE = 0x0000020000000000  # hardware level range, put(get)_LevelRangeV2
AMCAM_FLAG_EVENT_HARDWARE = 0x0000040000000000  # hardware event, such as exposure start & stop

AMCAM_EVENT_EXPOSURE = 0x0001  # exposure time or gain changed
AMCAM_EVENT_TEMPTINT = 0x0002  # white balance changed, Temp/Tint mode
AMCAM_EVENT_CHROME = 0x0003  # reversed, do not use it
AMCAM_EVENT_IMAGE = 0x0004  # live image arrived, use Amcam_PullImage to get this image
AMCAM_EVENT_STILLIMAGE = 0x0005  # snap (still) frame arrived, use Amcam_PullStillImage to get this frame
AMCAM_EVENT_WBGAIN = 0x0006  # white balance changed, RGB Gain mode
AMCAM_EVENT_TRIGGERFAIL = 0x0007  # trigger failed
AMCAM_EVENT_BLACK = 0x0008  # black balance changed
AMCAM_EVENT_FFC = 0x0009  # flat field correction status changed
AMCAM_EVENT_DFC = 0x000a  # dark field correction status changed
AMCAM_EVENT_ROI = 0x000b  # roi changed
EVENT_LEVELRANGE = 0x000c  # level range changed
AMCAM_EVENT_ERROR = 0x0080  # generic error
AMCAM_EVENT_DISCONNECTED = 0x0081  # camera disconnected
AMCAM_EVENT_NOFRAMETIMEOUT = 0x0082  # no frame timeout error
AMCAM_EVENT_AFFEEDBACK = 0x0083  # auto focus sensor board positon
AMCAM_EVENT_AFPOSITION = 0x0084  # auto focus information feedback
AMCAM_EVENT_NOPACKETTIMEOUT = 0x0085  # no packet timeout
AMCAM_EVENT_EXPO_START = 0x4000  # exposure start
AMCAM_EVENT_EXPO_STOP = 0x4001  # exposure stop
AMCAM_EVENT_TRIGGER_ALLOW = 0x4002  # next trigger allow
AMCAM_EVENT_FACTORY = 0x8001  # restore factory settings

AMCAM_OPTION_NOFRAME_TIMEOUT = 0x01  # no frame timeout: 1 = enable; 0 = disable. default: disable
AMCAM_OPTION_THREAD_PRIORITY = 0x02  # set the priority of the internal thread which grab data from the usb device.
#   Win: iValue: 0 = THREAD_PRIORITY_NORMAL; 1 = THREAD_PRIORITY_ABOVE_NORMAL; 2 = THREAD_PRIORITY_HIGHEST; 3 = THREAD_PRIORITY_TIME_CRITICAL; default: 1; see: https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-setthreadpriority
#   Linux & macOS: The high 16 bits for the scheduling policy, and the low 16 bits for the priority; see: https://linux.die.net/man/3/pthread_setschedparam
AMCAM_OPTION_RAW = 0x04  # raw data mode, read the sensor "raw" data. This can be set only BEFORE Amcam_StartXXX(). 0 = rgb, 1 = raw, default value: 0
AMCAM_OPTION_HISTOGRAM = 0x05  # 0 = only one, 1 = continue mode
AMCAM_OPTION_BITDEPTH = 0x06  # 0 = 8 bits mode, 1 = 16 bits mode
AMCAM_OPTION_FAN = 0x07  # 0 = turn off the cooling fan, [1, max] = fan speed
AMCAM_OPTION_TEC = 0x08  # 0 = turn off the thermoelectric cooler, 1 = turn on the thermoelectric cooler
AMCAM_OPTION_LINEAR = 0x09  # 0 = turn off the builtin linear tone mapping, 1 = turn on the builtin linear tone mapping, default value: 1
AMCAM_OPTION_CURVE = 0x0a  # 0 = turn off the builtin curve tone mapping, 1 = turn on the builtin polynomial curve tone mapping, 2 = logarithmic curve tone mapping, default value: 2
AMCAM_OPTION_TRIGGER = 0x0b  # 0 = video mode, 1 = software or simulated trigger mode, 2 = external trigger mode, 3 = external + software trigger, default value = 0
AMCAM_OPTION_RGB = 0x0c  # 0 => RGB24; 1 => enable RGB48 format when bitdepth > 8; 2 => RGB32; 3 => 8 Bits Gray (only for mono camera); 4 => 16 Bits Gray (only for mono camera when bitdepth > 8)
AMCAM_OPTION_COLORMATIX = 0x0d  # enable or disable the builtin color matrix, default value: 1
AMCAM_OPTION_WBGAIN = 0x0e  # enable or disable the builtin white balance gain, default value: 1
AMCAM_OPTION_TECTARGET = 0x0f  # get or set the target temperature of the thermoelectric cooler, in 0.1 degree Celsius. For example, 125 means 12.5 degree Celsius, -35 means -3.5 degree Celsius
AMCAM_OPTION_AUTOEXP_POLICY = 0x10  # auto exposure policy:
#      0: Exposure Only
#      1: Exposure Preferred
#      2: Gain Only
#      3: Gain Preferred
#      default value: 1
AMCAM_OPTION_FRAMERATE = 0x11  # limit the frame rate, range=[0, 63], the default value 0 means no limit
AMCAM_OPTION_DEMOSAIC = 0x12  # demosaic method for both video and still image: BILINEAR = 0, VNG(Variable Number of Gradients) = 1, PPG(Patterned Pixel Grouping) = 2, AHD(Adaptive Homogeneity Directed) = 3, EA(Edge Aware) = 4, see https://en.wikipedia.org/wiki/Demosaicing, default value: 0
AMCAM_OPTION_DEMOSAIC_VIDEO = 0x13  # demosaic method for video
AMCAM_OPTION_DEMOSAIC_STILL = 0x14  # demosaic method for still image
AMCAM_OPTION_BLACKLEVEL = 0x15  # black level
AMCAM_OPTION_MULTITHREAD = 0x16  # multithread image processing
AMCAM_OPTION_BINNING = 0x17  # binning, 0x01 (no binning), 0x02 (add, 2*2), 0x03 (add, 3*3), 0x04 (add, 4*4), 0x05 (add, 5*5), 0x06 (add, 6*6), 0x07 (add, 7*7), 0x08 (add, 8*8), 0x82 (average, 2*2), 0x83 (average, 3*3), 0x84 (average, 4*4), 0x85 (average, 5*5), 0x86 (average, 6*6), 0x87 (average, 7*7), 0x88 (average, 8*8). The final image size is rounded down to an even number, such as 640/3 to get 212
AMCAM_OPTION_ROTATE = 0x18  # rotate clockwise: 0, 90, 180, 270
AMCAM_OPTION_CG = 0x19  # Conversion Gain mode: 0 = LCG, 1 = HCG, 2 = HDR
AMCAM_OPTION_PIXEL_FORMAT = 0x1a  # pixel format
AMCAM_OPTION_FFC = 0x1b  # flat field correction
#      set:
#          0: disable
#          1: enable
#          -1: reset
#          (0xff000000 | n): set the average number to n, [1~255]
#      get:
#          (val & 0xff): 0 -> disable, 1 -> enable, 2 -> inited
#          ((val & 0xff00) >> 8): sequence
#          ((val & 0xff0000) >> 8): average number
AMCAM_OPTION_DDR_DEPTH = 0x1c  # the number of the frames that DDR can cache
#     1: DDR cache only one frame
#     0: Auto:
#         ->one for video mode when auto exposure is enabled
#         ->full capacity for others
#     1: DDR can cache frames to full capacity
AMCAM_OPTION_DFC = 0x1d  # dark field correction
#     set:
#         0: disable
#         1: enable
#         -1: reset
#         (0xff000000 | n): set the average number to n, [1~255]
#     get:
#         (val & 0xff): 0 -> disable, 1 -> enable, 2 -> inited
#         ((val & 0xff00) >> 8): sequence
#         ((val & 0xff0000) >> 8): average number
AMCAM_OPTION_SHARPENING = 0x1e  # Sharpening: (threshold << 24) | (radius << 16) | strength)
#     strength: [0, 500], default: 0 (disable)
#     radius: [1, 10]
#     threshold: [0, 255]
AMCAM_OPTION_FACTORY = 0x1f  # restore the factory settings
AMCAM_OPTION_TEC_VOLTAGE = 0x20  # get the current TEC voltage in 0.1V, 59 mean 5.9V; readonly
AMCAM_OPTION_TEC_VOLTAGE_MAX = 0x21  # get the TEC maximum voltage in 0.1V; readonly
AMCAM_OPTION_DEVICE_RESET = 0x22  # reset usb device, simulate a replug
AMCAM_OPTION_UPSIDE_DOWN = 0x23  # upsize down:
#     1: yes
#     0: no
#     default: 1 (win), 0 (linux/macos)
AMCAM_OPTION_AFPOSITION = 0x24  # auto focus sensor board positon
AMCAM_OPTION_AFMODE = 0x25  # auto focus mode (0:manul focus; 1:auto focus; 2:once focus; 3:conjugate calibration)
AMCAM_OPTION_AFZONE = 0x26  # auto focus zone
AMCAM_OPTION_AFFEEDBACK = 0x27  # auto focus information feedback; 0:unknown; 1:focused; 2:focusing; 3:defocus; 4:up; 5:down
AMCAM_OPTION_TESTPATTERN = 0x28  # test pattern:
#     0: TestPattern Off
#     3: monochrome diagonal stripes
#     5: monochrome vertical stripes
#     7: monochrome horizontal stripes
#     9: chromatic diagonal stripes
AMCAM_OPTION_AUTOEXP_THRESHOLD = 0x29  # threshold of auto exposure, default value: 5, range = [2, 15]
AMCAM_OPTION_BYTEORDER = 0x2a  # Byte order, BGR or RGB: 0->RGB, 1->BGR, default value: 1(Win), 0(macOS, Linux, Android)
AMCAM_OPTION_NOPACKET_TIMEOUT = 0x2b  # no packet timeout: 0 = disable, positive value = timeout milliseconds. default: disable
AMCAM_OPTION_MAX_PRECISE_FRAMERATE = 0x2c  # precise frame rate maximum value in 0.1 fps, such as 115 means 11.5 fps. E_NOTIMPL means not supported
AMCAM_OPTION_PRECISE_FRAMERATE = 0x2d  # precise frame rate current value in 0.1 fps, range:[1~maximum]
AMCAM_OPTION_BANDWIDTH = 0x2e  # bandwidth, [1-100]%
AMCAM_OPTION_RELOAD = 0x2f  # reload the last frame in trigger mode
AMCAM_OPTION_CALLBACK_THREAD = 0x30  # dedicated thread for callback
AMCAM_OPTION_FRONTEND_DEQUE_LENGTH = 0x31  # frontend frame buffer deque length, range: [2, 1024], default: 3
AMCAM_OPTION_FRAME_DEQUE_LENGTH = 0x31  # alias of AMCAM_OPTION_FRONTEND_DEQUE_LENGTH
AMCAM_OPTION_MIN_PRECISE_FRAMERATE = 0x32  # precise frame rate minimum value in 0.1 fps, such as 15 means 1.5 fps
AMCAM_OPTION_SEQUENCER_ONOFF = 0x33  # sequencer trigger: on/off
AMCAM_OPTION_SEQUENCER_NUMBER = 0x34  # sequencer trigger: number, range = [1, 255]
AMCAM_OPTION_SEQUENCER_EXPOTIME = 0x01000000  # sequencer trigger: exposure time, iOption = AMCAM_OPTION_SEQUENCER_EXPOTIME | index, iValue = exposure time
#   For example, to set the exposure time of the third group to 50ms, call:
#     Amcam_put_Option(AMCAM_OPTION_SEQUENCER_EXPOTIME | 3, 50000)
AMCAM_OPTION_SEQUENCER_EXPOGAIN = 0x02000000  # sequencer trigger: exposure gain, iOption = AMCAM_OPTION_SEQUENCER_EXPOGAIN | index, iValue = gain
AMCAM_OPTION_DENOISE = 0x35  # denoise, strength range: [0, 100], 0 means disable
AMCAM_OPTION_HEAT_MAX = 0x36  # get maximum level: heat to prevent fogging up
AMCAM_OPTION_HEAT = 0x37  # heat to prevent fogging up
AMCAM_OPTION_LOW_NOISE = 0x38  # low noise mode (Higher signal noise ratio, lower frame rate): 1 => enable
AMCAM_OPTION_POWER = 0x39  # get power consumption, unit: milliwatt
AMCAM_OPTION_GLOBAL_RESET_MODE = 0x3a  # global reset mode
AMCAM_OPTION_OPEN_USB_ERRORCODE = 0x3b  # open usb error code
AMCAM_OPTION_LINUX_USB_ZEROCOPY = 0x3c  # global option for linux platform:
#   enable or disable usb zerocopy (helps to reduce memory copy and improve efficiency. Requires kernel version >= 4.6 and hardware platform support)
#   if the image is wrong, this indicates that the hardware platform does not support this feature, please disable it when the program starts:
#      Amcam_put_Option((this is a global option, the camera handle parameter is not required, use nullptr), AMCAM_OPTION_LINUX_USB_ZEROCOPY, 0)
#   default value:
#      disable(0): android or arm32
#      enable(1):  others
AMCAM_OPTION_FLUSH = 0x3d  # 1 = hard flush, discard frames cached by camera DDR (if any)
# 2 = soft flush, discard frames cached by amcam.dll (if any)
# 3 = both flush
# Amcam_Flush means 'both flush'
AMCAM_OPTION_NUMBER_DROP_FRAME = 0x3e  # get the number of frames that have been grabbed from the USB but dropped by the software
AMCAM_OPTION_DUMP_CFG = 0x3f  # explicitly dump configuration to ini, json, or EEPROM. when camera is closed, it will dump configuration automatically
AMCAM_OPTION_DEFECT_PIXEL = 0x40  # Defect Pixel Correction: 0 => disable, 1 => enable; default: 1
AMCAM_OPTION_BACKEND_DEQUE_LENGTH = 0x41  # backend frame buffer deque length (Only available in pull mode), range: [2, 1024], default: 3

AMCAM_PIXELFORMAT_RAW8 = 0x00
AMCAM_PIXELFORMAT_RAW10 = 0x01
AMCAM_PIXELFORMAT_RAW12 = 0x02
AMCAM_PIXELFORMAT_RAW14 = 0x03
AMCAM_PIXELFORMAT_RAW16 = 0x04
AMCAM_PIXELFORMAT_YUV411 = 0x05
AMCAM_PIXELFORMAT_VUYY = 0x06
AMCAM_PIXELFORMAT_YUV444 = 0x07
AMCAM_PIXELFORMAT_RGB888 = 0x08
AMCAM_PIXELFORMAT_GMCY8 = 0x09
AMCAM_PIXELFORMAT_GMCY12 = 0x0a
AMCAM_PIXELFORMAT_UYVY = 0x0b

AMCAM_FRAMEINFO_FLAG_SEQ = 0x01  # sequence number
AMCAM_FRAMEINFO_FLAG_TIMESTAMP = 0x02

AMCAM_IOCONTROLTYPE_GET_SUPPORTEDMODE = 0x01  # 0x01->Input, 0x02->Output, (0x01 | 0x02)->support both Input and Output
AMCAM_IOCONTROLTYPE_GET_GPIODIR = 0x03  # 0x01->Input, 0x02->Output
AMCAM_IOCONTROLTYPE_SET_GPIODIR = 0x04
AMCAM_IOCONTROLTYPE_GET_FORMAT = 0x05  # 0x00-> not connected
# 0x01-> Tri-state: Tri-state mode (Not driven)
# 0x02-> TTL: TTL level signals
# 0x03-> LVDS: LVDS level signals
# 0x04-> RS422: RS422 level signals
# 0x05-> Opto-coupled
AMCAM_IOCONTROLTYPE_SET_FORMAT = 0x06
AMCAM_IOCONTROLTYPE_GET_OUTPUTINVERTER = 0x07  # boolean, only support output signal
AMCAM_IOCONTROLTYPE_SET_OUTPUTINVERTER = 0x08
AMCAM_IOCONTROLTYPE_GET_INPUTACTIVATION = 0x09  # 0x01->Positive, 0x02->Negative
AMCAM_IOCONTROLTYPE_SET_INPUTACTIVATION = 0x0a
AMCAM_IOCONTROLTYPE_GET_DEBOUNCERTIME = 0x0b  # debouncer time in microseconds, [0, 20000]
AMCAM_IOCONTROLTYPE_SET_DEBOUNCERTIME = 0x0c
AMCAM_IOCONTROLTYPE_GET_TRIGGERSOURCE = 0x0d  # 0x00-> Opto-isolated input
# 0x01-> GPIO0
# 0x02-> GPIO1
# 0x03-> Counter
# 0x04-> PWM
# 0x05-> Software
AMCAM_IOCONTROLTYPE_SET_TRIGGERSOURCE = 0x0e
AMCAM_IOCONTROLTYPE_GET_TRIGGERDELAY = 0x0f  # Trigger delay time in microseconds, [0, 5000000]
AMCAM_IOCONTROLTYPE_SET_TRIGGERDELAY = 0x10
AMCAM_IOCONTROLTYPE_GET_BURSTCOUNTER = 0x11  # Burst Counter: 1, 2, 3 ... 1023
AMCAM_IOCONTROLTYPE_SET_BURSTCOUNTER = 0x12
AMCAM_IOCONTROLTYPE_GET_COUNTERSOURCE = 0x13  # 0x00-> Opto-isolated input, 0x01-> GPIO0, 0x02-> GPIO1
AMCAM_IOCONTROLTYPE_SET_COUNTERSOURCE = 0x14
AMCAM_IOCONTROLTYPE_GET_COUNTERVALUE = 0x15  # Counter Value: 1, 2, 3 ... 1023
AMCAM_IOCONTROLTYPE_SET_COUNTERVALUE = 0x16
AMCAM_IOCONTROLTYPE_SET_RESETCOUNTER = 0x18
AMCAM_IOCONTROLTYPE_GET_PWM_FREQ = 0x19
AMCAM_IOCONTROLTYPE_SET_PWM_FREQ = 0x1a
AMCAM_IOCONTROLTYPE_GET_PWM_DUTYRATIO = 0x1b
AMCAM_IOCONTROLTYPE_SET_PWM_DUTYRATIO = 0x1c
AMCAM_IOCONTROLTYPE_GET_PWMSOURCE = 0x1d  # 0x00-> Opto-isolated input, 0x01-> GPIO0, 0x02-> GPIO1
AMCAM_IOCONTROLTYPE_SET_PWMSOURCE = 0x1e
AMCAM_IOCONTROLTYPE_GET_OUTPUTMODE = 0x1f  # 0x00-> Frame Trigger Wait
# 0x01-> Exposure Active
# 0x02-> Strobe
# 0x03-> User output
AMCAM_IOCONTROLTYPE_SET_OUTPUTMODE = 0x20
AMCAM_IOCONTROLTYPE_GET_STROBEDELAYMODE = 0x21  # boolean, 1 -> delay, 0 -> pre-delay; compared to exposure active signal
AMCAM_IOCONTROLTYPE_SET_STROBEDELAYMODE = 0x22
AMCAM_IOCONTROLTYPE_GET_STROBEDELAYTIME = 0x23  # Strobe delay or pre-delay time in microseconds, [0, 5000000]
AMCAM_IOCONTROLTYPE_SET_STROBEDELAYTIME = 0x24
AMCAM_IOCONTROLTYPE_GET_STROBEDURATION = 0x25  # Strobe duration time in microseconds, [0, 5000000]
AMCAM_IOCONTROLTYPE_SET_STROBEDURATION = 0x26
AMCAM_IOCONTROLTYPE_GET_USERVALUE = 0x27  # bit0-> Opto-isolated output
# bit1-> GPIO0 output
# bit2-> GPIO1 output
AMCAM_IOCONTROLTYPE_SET_USERVALUE = 0x28
AMCAM_IOCONTROLTYPE_GET_UART_ENABLE = 0x29  # enable: 1-> on; 0-> off
AMCAM_IOCONTROLTYPE_SET_UART_ENABLE = 0x2a
AMCAM_IOCONTROLTYPE_GET_UART_BAUDRATE = 0x2b  # baud rate: 0-> 9600; 1-> 19200; 2-> 38400; 3-> 57600; 4-> 115200
AMCAM_IOCONTROLTYPE_SET_UART_BAUDRATE = 0x2c
AMCAM_IOCONTROLTYPE_GET_UART_LINEMODE = 0x2d  # line mode: 0-> TX(GPIO_0)/RX(GPIO_1); 1-> TX(GPIO_1)/RX(GPIO_0)
AMCAM_IOCONTROLTYPE_SET_UART_LINEMODE = 0x2e

# hardware level range mode
AMCAM_LEVELRANGE_MANUAL = 0x0000  # manual
AMCAM_LEVELRANGE_ONCE = 0x0001  # once
AMCAM_LEVELRANGE_CONTINUE = 0x0002  # continue
AMCAM_LEVELRANGE_ROI = 0xffff  # update roi rect only

# TEC target range
AMCAM_TEC_TARGET_MIN = (-300)  # -30.0 degrees Celsius
AMCAM_TEC_TARGET_DEF = 0  # 0.0 degrees Celsius
AMCAM_TEC_TARGET_MAX = 300  # 30.0 degrees Celsius