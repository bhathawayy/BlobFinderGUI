import os, sys
from amcam_vars import *
from ctypes import *


class _Resolution(Structure):
    _fields_ = [('width', c_uint),
                ('height', c_uint)]


class _ModelV2(Structure):  # camera model v2 win32
    _fields_ = [('name', c_wchar_p),  # model name, in Windows, we use unicode
                ('flag', c_ulonglong),  # AMCAM_FLAG_xxx, 64 bits
                ('maxspeed', c_uint),
                # number of speed level, same as Amcam_get_MaxSpeed(), the speed range = [0, maxspeed], closed interval
                ('preview', c_uint),  # number of preview resolution, same as Amcam_get_ResolutionNumber()
                ('still', c_uint),  # number of still resolution, same as Amcam_get_StillResolutionNumber()
                ('maxfanspeed', c_uint),  # maximum fan speed
                ('ioctrol', c_uint),  # number of input/output control
                ('xpixsz', c_float),  # physical pixel size
                ('ypixsz', c_float),  # physical pixel size
                ('res', _Resolution * 16)]


class _DeviceV2(Structure):  # linux/mac
    _fields_ = [('displayname', c_char * 64),  # display name
                ('id', c_char * 64),  # unique and opaque id of a connected camera, for Amcam_Open
                ('model', POINTER(_ModelV2))]


class _FrameInfoV2(Structure):
    _fields_ = [('width', c_uint),
                ('height', c_uint),
                ('flag', c_uint),  # AMCAM_FRAMEINFO_FLAG_xxxx
                ('seq', c_uint),  # sequence number
                ('timestamp', c_longlong)]  # microsecond


class _RECT(Structure):
    _fields_ = [('left', c_int),
                ('top', c_int),
                ('right', c_int),
                ('bottom', c_int)]


class _AfParam(Structure):
    _fields_ = [('imax', c_int),  # maximum auto focus sensor board positon
                ('imin', c_int),  # minimum auto focus sensor board positon
                ('idef', c_int),  # conjugate calibration positon
                ('imaxabs', c_int),  # maximum absolute auto focus sensor board positon, micrometer
                ('iminabs', c_int),  # maximum absolute auto focus sensor board positon, micrometer
                ('zoneh', c_int),  # zone horizontal
                ('zonev', c_int)]  # zone vertical


class AmCAM:
    def __init__(self, device_id=None):
        # My variables
        self.lib = None
        self.error = None
        if type(device_id).__name__ == "str":
            self.device_id = c_wchar_p(device_id)
        elif type(device_id).__name__ == "int":
            self.device_id = c_wchar_p("cam%i" % device_id)
        else:
            self.device_id = device_id

        # Stupid variables
        self.__EVENT_CALLBACK = WINFUNCTYPE(None, c_uint, py_object)
        self.__PROGRESS_CALLBACK = WINFUNCTYPE(None, c_int, py_object)
        self.__progress = None
        
        self.open()

    def open(self):
        self.init_lib()
        if self.device_id is None:
            h = self.lib.Amcam_Open(None)
        else:
            h = self.lib.Amcam_Open(self.device_id)
        if h is None:
            return None
        return __class__(h)

    def error_check(self, result, fun, args):
        if result < 0:
            # raise HRESULTException(result)
            self.error = result
            print(result)
        return args
        
    def init_lib(self):
        if self.lib is None:
            try:
                directory = os.path.dirname(os.path.realpath(__file__))
                self.lib = windll.LoadLibrary(os.path.join(directory, 'amcam.dll'))
            except OSError:
                self.lib = windll.LoadLibrary('amcam.dll')
    
            self.lib.Amcam_Version.argtypes = None
            self.lib.Amcam_EnumV2.restype = c_uint
            self.lib.Amcam_EnumV2.argtypes = [_DeviceV2 * AMCAM_MAX]
            self.lib.Amcam_Open.restype = c_void_p
            self.lib.Amcam_Replug.restype = c_int
            self.lib.Amcam_Update.restype = c_int

            # For sys.platform == 'win32':
            self.lib.Amcam_Version.restype = c_wchar_p
            self.lib.Amcam_Open.argtypes = [c_wchar_p]
            self.lib.Amcam_Replug.argtypes = [c_wchar_p]
            self.lib.Amcam_Update.argtypes = [c_wchar_p, c_wchar_p, self.__PROGRESS_CALLBACK, py_object]
            # --------------------------- #

            self.lib.Amcam_Replug.errcheck = self.error_check
            self.lib.Amcam_Update.errcheck = self.error_check
            self.lib.Amcam_OpenByIndex.restype = c_void_p
            self.lib.Amcam_OpenByIndex.argtypes = [c_uint]
            self.lib.Amcam_Close.restype = None
            self.lib.Amcam_Close.argtypes = [c_void_p]
            self.lib.Amcam_StartPullModeWithCallback.restype = c_int
            self.lib.Amcam_StartPullModeWithCallback.errcheck = self.error_check
            self.lib.Amcam_StartPullModeWithCallback.argtypes = [c_void_p, self.__EVENT_CALLBACK, py_object]
            self.lib.Amcam_PullImageV2.restype = c_int
            self.lib.Amcam_PullImageV2.errcheck = self.error_check
            self.lib.Amcam_PullImageV2.argtypes = [c_void_p, c_char_p, c_int, POINTER(_FrameInfoV2)]
            self.lib.Amcam_PullStillImageV2.restype = c_int
            self.lib.Amcam_PullStillImageV2.errcheck = self.error_check
            self.lib.Amcam_PullStillImageV2.argtypes = [c_void_p, c_char_p, c_int, POINTER(_FrameInfoV2)]
            self.lib.Amcam_PullImageWithRowPitchV2.restype = c_int
            self.lib.Amcam_PullImageWithRowPitchV2.errcheck = self.error_check
            self.lib.Amcam_PullImageWithRowPitchV2.argtypes = [c_void_p, c_char_p, c_int, c_int, POINTER(_FrameInfoV2)]
            self.lib.Amcam_PullStillImageWithRowPitchV2.restype = c_int
            self.lib.Amcam_PullStillImageWithRowPitchV2.errcheck = self.error_check
            self.lib.Amcam_PullStillImageWithRowPitchV2.argtypes = [c_void_p, c_char_p, c_int, c_int,
                                                                    POINTER(_FrameInfoV2)]
            self.lib.Amcam_Stop.restype = c_int
            self.lib.Amcam_Stop.errcheck = self.error_check
            self.lib.Amcam_Stop.argtypes = [c_void_p]
            self.lib.Amcam_Pause.restype = c_int
            self.lib.Amcam_Pause.errcheck = self.error_check
            self.lib.Amcam_Pause.argtypes = [c_void_p, c_int]
            self.lib.Amcam_Snap.restype = c_int
            self.lib.Amcam_Snap.errcheck = self.error_check
            self.lib.Amcam_Snap.argtypes = [c_void_p, c_uint]
            self.lib.Amcam_SnapN.restype = c_int
            self.lib.Amcam_SnapN.errcheck = self.error_check
            self.lib.Amcam_SnapN.argtypes = [c_void_p, c_uint, c_uint]
            self.lib.Amcam_Trigger.restype = c_int
            self.lib.Amcam_Trigger.errcheck = self.error_check
            self.lib.Amcam_Trigger.argtypes = [c_void_p, c_ushort]
            self.lib.Amcam_put_Size.restype = c_int
            self.lib.Amcam_put_Size.errcheck = self.error_check
            self.lib.Amcam_put_Size.argtypes = [c_void_p, c_int, c_int]
            self.lib.Amcam_get_Size.restype = c_int
            self.lib.Amcam_get_Size.errcheck = self.error_check
            self.lib.Amcam_get_Size.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
            self.lib.Amcam_put_eSize.restype = c_int
            self.lib.Amcam_put_eSize.errcheck = self.error_check
            self.lib.Amcam_put_eSize.argtypes = [c_void_p, c_uint]
            self.lib.Amcam_get_eSize.restype = c_int
            self.lib.Amcam_get_eSize.errcheck = self.error_check
            self.lib.Amcam_get_eSize.argtypes = [c_void_p, POINTER(c_uint)]
            self.lib.Amcam_get_FinalSize.restype = c_int
            self.lib.Amcam_get_FinalSize.errcheck = self.error_check
            self.lib.Amcam_get_FinalSize.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
            self.lib.Amcam_get_ResolutionNumber.restype = c_int
            self.lib.Amcam_get_ResolutionNumber.errcheck = self.error_check
            self.lib.Amcam_get_ResolutionNumber.argtypes = [c_void_p]
            self.lib.Amcam_get_Resolution.restype = c_int
            self.lib.Amcam_get_Resolution.errcheck = self.error_check
            self.lib.Amcam_get_Resolution.argtypes = [c_void_p, c_uint, POINTER(c_int), POINTER(c_int)]
            self.lib.Amcam_get_ResolutionRatio.restype = c_int
            self.lib.Amcam_get_ResolutionRatio.errcheck = self.error_check
            self.lib.Amcam_get_ResolutionRatio.argtypes = [c_void_p, c_uint, POINTER(c_int), POINTER(c_int)]
            self.lib.Amcam_get_Field.restype = c_int
            self.lib.Amcam_get_Field.errcheck = self.error_check
            self.lib.Amcam_get_Field.argtypes = [c_void_p]
            self.lib.Amcam_get_RawFormat.restype = c_int
            self.lib.Amcam_get_RawFormat.errcheck = self.error_check
            self.lib.Amcam_get_RawFormat.argtypes = [c_void_p, POINTER(c_uint), POINTER(c_uint)]
            self.lib.Amcam_get_AutoExpoEnable.restype = c_int
            self.lib.Amcam_get_AutoExpoEnable.errcheck = self.error_check
            self.lib.Amcam_get_AutoExpoEnable.argtypes = [c_void_p, POINTER(c_int)]
            self.lib.Amcam_put_AutoExpoEnable.restype = c_int
            self.lib.Amcam_put_AutoExpoEnable.errcheck = self.error_check
            self.lib.Amcam_put_AutoExpoEnable.argtypes = [c_void_p, c_int]
            self.lib.Amcam_get_AutoExpoTarget.restype = c_int
            self.lib.Amcam_get_AutoExpoTarget.errcheck = self.error_check
            self.lib.Amcam_get_AutoExpoTarget.argtypes = [c_void_p, POINTER(c_ushort)]
            self.lib.Amcam_put_AutoExpoTarget.restype = c_int
            self.lib.Amcam_put_AutoExpoTarget.errcheck = self.error_check
            self.lib.Amcam_put_AutoExpoTarget.argtypes = [c_void_p, c_int]
            self.lib.Amcam_put_MaxAutoExpoTimeAGain.restype = c_int
            self.lib.Amcam_put_MaxAutoExpoTimeAGain.errcheck = self.error_check
            self.lib.Amcam_put_MaxAutoExpoTimeAGain.argtypes = [c_void_p, c_uint, c_ushort]
            self.lib.Amcam_get_MaxAutoExpoTimeAGain.restype = c_int
            self.lib.Amcam_get_MaxAutoExpoTimeAGain.errcheck = self.error_check
            self.lib.Amcam_get_MaxAutoExpoTimeAGain.argtypes = [c_void_p, POINTER(c_uint), POINTER(c_ushort)]
            self.lib.Amcam_put_MinAutoExpoTimeAGain.restype = c_int
            self.lib.Amcam_put_MinAutoExpoTimeAGain.errcheck = self.error_check
            self.lib.Amcam_put_MinAutoExpoTimeAGain.argtypes = [c_void_p, c_uint, c_ushort]
            self.lib.Amcam_get_MinAutoExpoTimeAGain.restype = c_int
            self.lib.Amcam_get_MinAutoExpoTimeAGain.errcheck = self.error_check
            self.lib.Amcam_get_MinAutoExpoTimeAGain.argtypes = [c_void_p, POINTER(c_uint), POINTER(c_ushort)]
            self.lib.Amcam_put_ExpoTime.restype = c_int
            self.lib.Amcam_put_ExpoTime.errcheck = self.error_check
            self.lib.Amcam_put_ExpoTime.argtypes = [c_void_p, c_uint]
            self.lib.Amcam_get_ExpoTime.restype = c_int
            self.lib.Amcam_get_ExpoTime.errcheck = self.error_check
            self.lib.Amcam_get_ExpoTime.argtypes = [c_void_p, POINTER(c_uint)]
            self.lib.Amcam_get_RealExpoTime.restype = c_int
            self.lib.Amcam_get_RealExpoTime.errcheck = self.error_check
            self.lib.Amcam_get_RealExpoTime.argtypes = [c_void_p, POINTER(c_uint)]
            self.lib.Amcam_get_ExpTimeRange.restype = c_int
            self.lib.Amcam_get_ExpTimeRange.errcheck = self.error_check
            self.lib.Amcam_get_ExpTimeRange.argtypes = [c_void_p, POINTER(c_uint), POINTER(c_uint), POINTER(c_uint)]
            self.lib.Amcam_put_ExpoAGain.restype = c_int
            self.lib.Amcam_put_ExpoAGain.errcheck = self.error_check
            self.lib.Amcam_put_ExpoAGain.argtypes = [c_void_p, c_ushort]
            self.lib.Amcam_get_ExpoAGain.restype = c_int
            self.lib.Amcam_get_ExpoAGain.errcheck = self.error_check
            self.lib.Amcam_get_ExpoAGain.argtypes = [c_void_p, POINTER(c_ushort)]
            self.lib.Amcam_get_ExpoAGainRange.restype = c_int
            self.lib.Amcam_get_ExpoAGainRange.errcheck = self.error_check
            self.lib.Amcam_get_ExpoAGainRange.argtypes = [c_void_p, POINTER(c_ushort), POINTER(c_ushort),
                                                          POINTER(c_ushort)]
            self.lib.Amcam_AwbOnce.restype = c_int
            self.lib.Amcam_AwbOnce.errcheck = self.error_check
            self.lib.Amcam_AwbOnce.argtypes = [c_void_p, c_void_p, c_void_p]
            self.lib.Amcam_AwbInit.restype = c_int
            self.lib.Amcam_AwbInit.errcheck = self.error_check
            self.lib.Amcam_AwbInit.argtypes = [c_void_p, c_void_p, c_void_p]
            self.lib.Amcam_put_TempTint.restype = c_int
            self.lib.Amcam_put_TempTint.errcheck = self.error_check
            self.lib.Amcam_put_TempTint.argtypes = [c_void_p, c_int, c_int]
            self.lib.Amcam_get_TempTint.restype = c_int
            self.lib.Amcam_get_TempTint.errcheck = self.error_check
            self.lib.Amcam_get_TempTint.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
            self.lib.Amcam_put_WhiteBalanceGain.restype = c_int
            self.lib.Amcam_put_WhiteBalanceGain.errcheck = self.error_check
            self.lib.Amcam_put_WhiteBalanceGain.argtypes = [c_void_p, (c_int * 3)]
            self.lib.Amcam_get_WhiteBalanceGain.restype = c_int
            self.lib.Amcam_get_WhiteBalanceGain.errcheck = self.error_check
            self.lib.Amcam_get_WhiteBalanceGain.argtypes = [c_void_p, (c_int * 3)]
            self.lib.Amcam_put_BlackBalance.restype = c_int
            self.lib.Amcam_put_BlackBalance.errcheck = self.error_check
            self.lib.Amcam_put_BlackBalance.argtypes = [c_void_p, (c_int * 3)]
            self.lib.Amcam_get_BlackBalance.restype = c_int
            self.lib.Amcam_get_BlackBalance.errcheck = self.error_check
            self.lib.Amcam_get_BlackBalance.argtypes = [c_void_p, (c_int * 3)]
            self.lib.Amcam_AbbOnce.restype = c_int
            self.lib.Amcam_AbbOnce.errcheck = self.error_check
            self.lib.Amcam_AbbOnce.argtypes = [c_void_p, c_void_p, c_void_p]
            self.lib.Amcam_FfcOnce.restype = c_int
            self.lib.Amcam_FfcOnce.errcheck = self.error_check
            self.lib.Amcam_FfcOnce.argtypes = [c_void_p]
            self.lib.Amcam_DfcOnce.restype = c_int
            self.lib.Amcam_DfcOnce.errcheck = self.error_check
            self.lib.Amcam_DfcOnce.argtypes = [c_void_p]
            self.lib.Amcam_FfcExport.restype = c_int
            self.lib.Amcam_FfcExport.errcheck = self.error_check
            self.lib.Amcam_FfcImport.restype = c_int
            self.lib.Amcam_FfcImport.errcheck = self.error_check
            self.lib.Amcam_DfcExport.restype = c_int
            self.lib.Amcam_DfcExport.errcheck = self.error_check
            self.lib.Amcam_DfcImport.restype = c_int
            self.lib.Amcam_DfcImport.errcheck = self.error_check

            # For sys.platform == 'win32':
            self.lib.Amcam_FfcExport.argtypes = [c_void_p, c_wchar_p]
            self.lib.Amcam_FfcImport.argtypes = [c_void_p, c_wchar_p]
            self.lib.Amcam_DfcExport.argtypes = [c_void_p, c_wchar_p]
            self.lib.Amcam_DfcImport.argtypes = [c_void_p, c_wchar_p]
            # --------------------------- #

            self.lib.Amcam_put_Hue.restype = c_int
            self.lib.Amcam_put_Hue.errcheck = self.error_check
            self.lib.Amcam_put_Hue.argtypes = [c_void_p, c_int]
            self.lib.Amcam_get_Hue.restype = c_int
            self.lib.Amcam_get_Hue.errcheck = self.error_check
            self.lib.Amcam_get_Hue.argtypes = [c_void_p, POINTER(c_int)]
            self.lib.Amcam_put_Saturation.restype = c_int
            self.lib.Amcam_put_Saturation.errcheck = self.error_check
            self.lib.Amcam_put_Saturation.argtypes = [c_void_p, c_int]
            self.lib.Amcam_get_Saturation.restype = c_int
            self.lib.Amcam_get_Saturation.errcheck = self.error_check
            self.lib.Amcam_get_Saturation.argtypes = [c_void_p, POINTER(c_int)]
            self.lib.Amcam_put_Brightness.restype = c_int
            self.lib.Amcam_put_Brightness.errcheck = self.error_check
            self.lib.Amcam_put_Brightness.argtypes = [c_void_p, c_int]
            self.lib.Amcam_get_Brightness.restype = c_int
            self.lib.Amcam_get_Brightness.errcheck = self.error_check
            self.lib.Amcam_get_Brightness.argtypes = [c_void_p, POINTER(c_int)]
            self.lib.Amcam_put_Contrast.restype = c_int
            self.lib.Amcam_put_Contrast.errcheck = self.error_check
            self.lib.Amcam_put_Contrast.argtypes = [c_void_p, c_int]
            self.lib.Amcam_get_Contrast.restype = c_int
            self.lib.Amcam_get_Contrast.errcheck = self.error_check
            self.lib.Amcam_get_Contrast.argtypes = [c_void_p, POINTER(c_int)]
            self.lib.Amcam_put_Gamma.restype = c_int
            self.lib.Amcam_put_Gamma.errcheck = self.error_check
            self.lib.Amcam_put_Gamma.argtypes = [c_void_p, c_int]
            self.lib.Amcam_get_Gamma.restype = c_int
            self.lib.Amcam_get_Gamma.errcheck = self.error_check
            self.lib.Amcam_get_Gamma.argtypes = [c_void_p, POINTER(c_int)]
            self.lib.Amcam_put_Chrome.restype = c_int
            self.lib.Amcam_put_Chrome.errcheck = self.error_check
            self.lib.Amcam_put_Chrome.argtypes = [c_void_p, c_int]
            self.lib.Amcam_get_Chrome.restype = c_int
            self.lib.Amcam_get_Chrome.errcheck = self.error_check
            self.lib.Amcam_get_Chrome.argtypes = [c_void_p, POINTER(c_int)]
            self.lib.Amcam_put_VFlip.restype = c_int
            self.lib.Amcam_put_VFlip.errcheck = self.error_check
            self.lib.Amcam_put_VFlip.argtypes = [c_void_p, c_int]
            self.lib.Amcam_get_VFlip.restype = c_int
            self.lib.Amcam_get_VFlip.errcheck = self.error_check
            self.lib.Amcam_get_VFlip.argtypes = [c_void_p, POINTER(c_int)]
            self.lib.Amcam_put_HFlip.restype = c_int
            self.lib.Amcam_put_HFlip.errcheck = self.error_check
            self.lib.Amcam_put_HFlip.argtypes = [c_void_p, c_int]
            self.lib.Amcam_get_HFlip.restype = c_int
            self.lib.Amcam_get_HFlip.errcheck = self.error_check
            self.lib.Amcam_get_HFlip.argtypes = [c_void_p, POINTER(c_int)]
            self.lib.Amcam_put_Negative.restype = c_int
            self.lib.Amcam_put_Negative.errcheck = self.error_check
            self.lib.Amcam_put_Negative.argtypes = [c_void_p, c_int]
            self.lib.Amcam_get_Negative.restype = c_int
            self.lib.Amcam_get_Negative.errcheck = self.error_check
            self.lib.Amcam_get_Negative.argtypes = [c_void_p, POINTER(c_int)]
            self.lib.Amcam_put_Speed.restype = c_int
            self.lib.Amcam_put_Speed.errcheck = self.error_check
            self.lib.Amcam_put_Speed.argtypes = [c_void_p, c_ushort]
            self.lib.Amcam_get_Speed.restype = c_int
            self.lib.Amcam_get_Speed.errcheck = self.error_check
            self.lib.Amcam_get_Speed.argtypes = [c_void_p, POINTER(c_ushort)]
            self.lib.Amcam_get_MaxSpeed.restype = c_int
            self.lib.Amcam_get_MaxSpeed.errcheck = self.error_check
            self.lib.Amcam_get_MaxSpeed.argtypes = [c_void_p]
            self.lib.Amcam_get_FanMaxSpeed.restype = c_int
            self.lib.Amcam_get_FanMaxSpeed.errcheck = self.error_check
            self.lib.Amcam_get_FanMaxSpeed.argtypes = [c_void_p]
            self.lib.Amcam_get_MaxBitDepth.restype = c_int
            self.lib.Amcam_get_MaxBitDepth.errcheck = self.error_check
            self.lib.Amcam_get_MaxBitDepth.argtypes = [c_void_p]
            self.lib.Amcam_put_HZ.restype = c_int
            self.lib.Amcam_put_HZ.errcheck = self.error_check
            self.lib.Amcam_put_HZ.argtypes = [c_void_p, c_int]
            self.lib.Amcam_get_HZ.restype = c_int
            self.lib.Amcam_get_HZ.errcheck = self.error_check
            self.lib.Amcam_get_HZ.argtypes = [c_void_p, POINTER(c_int)]
            self.lib.Amcam_put_Mode.restype = c_int
            self.lib.Amcam_put_Mode.errcheck = self.error_check
            self.lib.Amcam_put_Mode.argtypes = [c_void_p, c_int]
            self.lib.Amcam_get_Mode.restype = c_int
            self.lib.Amcam_get_Mode.errcheck = self.error_check
            self.lib.Amcam_get_Mode.argtypes = [c_void_p, POINTER(c_int)]
            self.lib.Amcam_put_AWBAuxRect.restype = c_int
            self.lib.Amcam_put_AWBAuxRect.errcheck = self.error_check
            self.lib.Amcam_put_AWBAuxRect.argtypes = [c_void_p, POINTER(_RECT)]
            self.lib.Amcam_get_AWBAuxRect.restype = c_int
            self.lib.Amcam_get_AWBAuxRect.errcheck = self.error_check
            self.lib.Amcam_get_AWBAuxRect.argtypes = [c_void_p, POINTER(_RECT)]
            self.lib.Amcam_put_AEAuxRect.restype = c_int
            self.lib.Amcam_put_AEAuxRect.errcheck = self.error_check
            self.lib.Amcam_put_AEAuxRect.argtypes = [c_void_p, POINTER(_RECT)]
            self.lib.Amcam_get_AEAuxRect.restype = c_int
            self.lib.Amcam_get_AEAuxRect.errcheck = self.error_check
            self.lib.Amcam_get_AEAuxRect.argtypes = [c_void_p, POINTER(_RECT)]
            self.lib.Amcam_put_ABBAuxRect.restype = c_int
            self.lib.Amcam_put_ABBAuxRect.errcheck = self.error_check
            self.lib.Amcam_put_ABBAuxRect.argtypes = [c_void_p, POINTER(_RECT)]
            self.lib.Amcam_get_ABBAuxRect.restype = c_int
            self.lib.Amcam_get_ABBAuxRect.errcheck = self.error_check
            self.lib.Amcam_get_ABBAuxRect.argtypes = [c_void_p, POINTER(_RECT)]
            self.lib.Amcam_get_MonoMode.restype = c_int
            self.lib.Amcam_get_MonoMode.errcheck = self.error_check
            self.lib.Amcam_get_MonoMode.argtypes = [c_void_p]
            self.lib.Amcam_get_StillResolutionNumber.restype = c_int
            self.lib.Amcam_get_StillResolutionNumber.errcheck = self.error_check
            self.lib.Amcam_get_StillResolutionNumber.argtypes = [c_void_p]
            self.lib.Amcam_get_StillResolution.restype = c_int
            self.lib.Amcam_get_StillResolution.errcheck = self.error_check
            self.lib.Amcam_get_StillResolution.argtypes = [c_void_p, c_uint, POINTER(c_int), POINTER(c_int)]
            self.lib.Amcam_put_RealTime.restype = c_int
            self.lib.Amcam_put_RealTime.errcheck = self.error_check
            self.lib.Amcam_put_RealTime.argtypes = [c_void_p, c_int]
            self.lib.Amcam_get_RealTime.restype = c_int
            self.lib.Amcam_get_RealTime.errcheck = self.error_check
            self.lib.Amcam_get_RealTime.argtypes = [c_void_p, POINTER(c_int)]
            self.lib.Amcam_Flush.restype = c_int
            self.lib.Amcam_Flush.errcheck = self.error_check
            self.lib.Amcam_Flush.argtypes = [c_void_p]
            self.lib.Amcam_put_Temperature.restype = c_int
            self.lib.Amcam_put_Temperature.errcheck = self.error_check
            self.lib.Amcam_put_Temperature.argtypes = [c_void_p, c_ushort]
            self.lib.Amcam_get_Temperature.restype = c_int
            self.lib.Amcam_get_Temperature.errcheck = self.error_check
            self.lib.Amcam_get_Temperature.argtypes = [c_void_p, POINTER(c_ushort)]
            self.lib.Amcam_get_Revision.restype = c_int
            self.lib.Amcam_get_Revision.errcheck = self.error_check
            self.lib.Amcam_get_Revision.argtypes = [c_void_p, POINTER(c_ushort)]
            self.lib.Amcam_get_SerialNumber.restype = c_int
            self.lib.Amcam_get_SerialNumber.errcheck = self.error_check
            self.lib.Amcam_get_SerialNumber.argtypes = [c_void_p, c_char * 32]
            self.lib.Amcam_get_FwVersion.restype = c_int
            self.lib.Amcam_get_FwVersion.errcheck = self.error_check
            self.lib.Amcam_get_FwVersion.argtypes = [c_void_p, c_char * 16]
            self.lib.Amcam_get_HwVersion.restype = c_int
            self.lib.Amcam_get_HwVersion.errcheck = self.error_check
            self.lib.Amcam_get_HwVersion.argtypes = [c_void_p, c_char * 16]
            self.lib.Amcam_get_ProductionDate.restype = c_int
            self.lib.Amcam_get_ProductionDate.errcheck = self.error_check
            self.lib.Amcam_get_ProductionDate.argtypes = [c_void_p, c_char * 16]
            self.lib.Amcam_get_FpgaVersion.restype = c_int
            self.lib.Amcam_get_FpgaVersion.errcheck = self.error_check
            self.lib.Amcam_get_FpgaVersion.argtypes = [c_void_p, c_char * 16]
            self.lib.Amcam_get_PixelSize.restype = c_int
            self.lib.Amcam_get_PixelSize.errcheck = self.error_check
            self.lib.Amcam_get_PixelSize.argtypes = [c_void_p, c_int, POINTER(c_float), POINTER(c_float)]
            self.lib.Amcam_put_LevelRange.restype = c_int
            self.lib.Amcam_put_LevelRange.errcheck = self.error_check
            self.lib.Amcam_put_LevelRange.argtypes = [c_void_p, (c_ushort * 4), (c_ushort * 4)]
            self.lib.Amcam_get_LevelRange.restype = c_int
            self.lib.Amcam_get_LevelRange.errcheck = self.error_check
            self.lib.Amcam_get_LevelRange.argtypes = [c_void_p, (c_ushort * 4), (c_ushort * 4)]
            self.lib.Amcam_put_LevelRangeV2.restype = c_int
            self.lib.Amcam_put_LevelRangeV2.errcheck = self.error_check
            self.lib.Amcam_put_LevelRangeV2.argtypes = [c_void_p, c_ushort, POINTER(_RECT), (c_ushort * 4),
                                                        (c_ushort * 4)]
            self.lib.Amcam_get_LevelRangeV2.restype = c_int
            self.lib.Amcam_get_LevelRangeV2.errcheck = self.error_check
            self.lib.Amcam_get_LevelRangeV2.argtypes = [c_void_p, POINTER(c_ushort), POINTER(_RECT), (c_ushort * 4),
                                                        (c_ushort * 4)]
            self.lib.Amcam_LevelRangeAuto.restype = c_int
            self.lib.Amcam_LevelRangeAuto.errcheck = self.error_check
            self.lib.Amcam_LevelRangeAuto.argtypes = [c_void_p]
            self.lib.Amcam_put_LEDState.restype = c_int
            self.lib.Amcam_put_LEDState.errcheck = self.error_check
            self.lib.Amcam_put_LEDState.argtypes = [c_void_p, c_ushort, c_ushort, c_ushort, c_ushort]
            self.lib.Amcam_write_EEPROM.restype = c_int
            self.lib.Amcam_write_EEPROM.errcheck = self.error_check
            self.lib.Amcam_write_EEPROM.argtypes = [c_void_p, c_uint, c_char_p, c_uint]
            self.lib.Amcam_read_EEPROM.restype = c_int
            self.lib.Amcam_read_EEPROM.errcheck = self.error_check
            self.lib.Amcam_read_EEPROM.argtypes = [c_void_p, c_uint, c_char_p, c_uint]
            self.lib.Amcam_read_Pipe.restype = c_int
            self.lib.Amcam_read_Pipe.errcheck = self.error_check
            self.lib.Amcam_read_Pipe.argtypes = [c_void_p, c_uint, c_char_p, c_uint]
            self.lib.Amcam_write_Pipe.restype = c_int
            self.lib.Amcam_write_Pipe.errcheck = self.error_check
            self.lib.Amcam_write_Pipe.argtypes = [c_void_p, c_uint, c_char_p, c_uint]
            self.lib.Amcam_feed_Pipe.restype = c_int
            self.lib.Amcam_feed_Pipe.errcheck = self.error_check
            self.lib.Amcam_feed_Pipe.argtypes = [c_void_p, c_uint]
            self.lib.Amcam_put_Option.restype = c_int
            self.lib.Amcam_put_Option.errcheck = self.error_check
            self.lib.Amcam_put_Option.argtypes = [c_void_p, c_uint, c_int]
            self.lib.Amcam_get_Option.restype = c_int
            self.lib.Amcam_get_Option.errcheck = self.error_check
            self.lib.Amcam_get_Option.argtypes = [c_void_p, c_uint, POINTER(c_int)]
            self.lib.Amcam_put_Roi.restype = c_int
            self.lib.Amcam_put_Roi.errcheck = self.error_check
            self.lib.Amcam_put_Roi.argtypes = [c_void_p, c_uint, c_uint, c_uint, c_uint]
            self.lib.Amcam_get_Roi.restype = c_int
            self.lib.Amcam_get_Roi.errcheck = self.error_check
            self.lib.Amcam_get_Roi.argtypes = [c_void_p, POINTER(c_uint), POINTER(c_uint), POINTER(c_uint),
                                               POINTER(c_uint)]
            self.lib.Amcam_get_AfParam.restype = c_int
            self.lib.Amcam_get_AfParam.errcheck = self.error_check
            self.lib.Amcam_get_AfParam.argtypes = [c_void_p, POINTER(_AfParam)]
            self.lib.Amcam_IoControl.restype = c_int
            self.lib.Amcam_IoControl.errcheck = self.error_check
            self.lib.Amcam_IoControl.argtypes = [c_void_p, c_uint, c_uint, c_int, POINTER(c_int)]
            self.lib.Amcam_read_UART.restype = c_int
            self.lib.Amcam_read_UART.errcheck = self.error_check
            self.lib.Amcam_read_UART.argtypes = [c_void_p, c_char_p, c_uint]
            self.lib.Amcam_write_UART.restype = c_int
            self.lib.Amcam_write_UART.errcheck = self.error_check
            self.lib.Amcam_write_UART.argtypes = [c_void_p, c_char_p, c_uint]
            self.lib.Amcam_put_Linear.restype = c_int
            self.lib.Amcam_put_Linear.errcheck = self.error_check
            self.lib.Amcam_put_Linear.argtypes = [c_void_p, POINTER(c_ubyte), POINTER(c_ushort)]
            self.lib.Amcam_put_Curve.restype = c_int
            self.lib.Amcam_put_Curve.errcheck = self.error_check
            self.lib.Amcam_put_Curve.argtypes = [c_void_p, POINTER(c_ubyte), POINTER(c_ushort)]
            self.lib.Amcam_put_ColorMatrix.restype = c_int
            self.lib.Amcam_put_ColorMatrix.errcheck = self.error_check
            self.lib.Amcam_put_ColorMatrix.argtypes = [c_void_p, c_double * 9]
            self.lib.Amcam_put_InitWBGain.restype = c_int
            self.lib.Amcam_put_InitWBGain.errcheck = self.error_check
            self.lib.Amcam_put_InitWBGain.argtypes = [c_void_p, c_ushort * 3]
            self.lib.Amcam_get_FrameRate.restype = c_int
            self.lib.Amcam_get_FrameRate.errcheck = self.error_check
            self.lib.Amcam_get_FrameRate.argtypes = [c_void_p, POINTER(c_uint), POINTER(c_uint), POINTER(c_uint)]


if __name__ == "__main__":
    dev = AmCAM()
    print("pause")
