# -*- coding: utf-8 -*-

import os


# Define global errors
ERRORS = {
    0: "",
    404: "HW: UNKNOWN",
    801: "Amscope: Device already in use. Close any active sessions.",
    802: "Amscope: Could not read frame. Check connections."
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

    return error_num
