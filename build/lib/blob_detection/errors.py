import os

ERRORS = {
    0: "",
    101: "LCOS: Device already in use. Close any active sessions.",
    102: "LCOS: Check power connection to reference board.",
    103: "LCOS: Check Aardvark communication with 'Control Center'.",
    104: "LCOS: Check video communication with 'Putty'.",
    151: "Prosilica Cam: No device detected.",
    152: "Prosilica Cam: Incompatible with OpenCV formatting.",
    201: "Atlas Cam: No device detected.",
    # 202: "HW CAM: No IDS camera device found.",
    203: "Atlas Cam: Device already in use. Close any active sessions.",
    205: "Atlas Cam: Invalid input for setting(s).",
    251: "IDS U3 Cam: No device detected.",
    252: "IDS U3 Cam: Error streaming from device. Check pixel format.",
    253: "IDS U3 Cam: Exposure time out of range: [0.03, 1900.16]",
    254: "IDS U3 Cam: Device already in use. Close any active sessions.",
    301: "PI Stage: No device detected.",
    302: "PI Stage: Only C-887 and C-884 are supported.",
    404: "HW: UNKNOWN",
    501: "TL Stage: No device detected.",
    502: "TL Stage: Move type options: 'ABS' and 'REL'.",
    551: "TL PM: No device detected.",
    601: "Robot Arm: No device detected.",
    602: "Robot Arm: Communication error.",
    603: "Robot Arm: Move type options: 'Joints' and 'Pose'.",
    604: "Robot Arm: Invalid position given.",
    701: "Spectrometer: No device detected.",
    702: "Spectrometer: Integration time out of range.",
    703: "Spectrometer: Spectrum averaging value out of range.",
    751: "Newmark: No device detected.",
    752: "Newmark: (RB) Movement out of range: +/-30 deg.",
    753: "Newmark: Move type options: 'ABS' and 'REL'.",
    754: "Newmark: (RM) Movement out of range: +/-360 deg.",
    801: "Amscope: Device already in use. Close any active sessions.",
    802: "Amscope: Could not read frame. Check connections.",
    901: "Video Routine: Invalid file path to config file.",
    902: "Video Routine: A valid camera handle is required.",
    903: "Video Routine: A valid LCOS handle is required.",
    904: "Video Routine: A valid stage handle is required."
}


def error_check(error_num, frame_info):
    """
    Checks for error and reports if present.
    :param error_num: (int) Error number corresponding to ERRORS dictionary.
    :param frame_info: (obj) Frame object for debugging; use currentframe() from inspect
    :return: error_num (int)
    """
    # Assign error to unknown if not in dict
    if error_num not in ERRORS.keys():
        error_num = 404

    # Print error and frame info
    error_msg = ERRORS[error_num]
    if error_msg:
        file = os.path.split(frame_info.f_code.co_filename)[1]
        func = frame_info.f_code.co_name
        line = frame_info.f_back.f_lineno
        error_msg = "ERROR %s [%s, %s(), %i]" % (error_msg, file, func, line)
        print(error_msg)

    # Reset error number
    error_num = 0

    return error_num
