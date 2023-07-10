# -*- coding: utf-8 -*-

import cv2, os, json, math
import numpy as np
import circle_fit

# Open gui_settings.json file to be used for defaults
try:
    with open(os.path.join(os.getcwd(), "blob_detection\\support\\gui_settings.json")) as f:
        json_settings = json.load(f)
except FileNotFoundError:
    with open(os.path.join(os.getcwd(), "..\\blob_detection\\support\\gui_settings.json")) as f:
        json_settings = json.load(f)


def convert_color_bit(image_array, color, bit_depth):
    """
    Convert input image array into the specified color and bit-depth.
    :param image_array: (np.array) Image array to convert.
    :param color: (str) Options: 'rgb' or 'mono'
    :param bit_depth: (int/str) Options: 8 or 16
    :return: (np.array) Converted image array.
    """
    if image_array.any():
        # Check bit depth and convert
        current_bd = image_array.dtype.name
        if "8" in str(bit_depth) and "8" not in current_bd:  # 16-bit to 8-bit
            image_array = (image_array / 256).astype('uint8')
        elif "16" in str(bit_depth) and "16" not in current_bd:  # 8-bit to 16-bit
            image_array = (image_array * 256).astype('uint16')

        # Check color and convert
        s = image_array.shape
        if len(s) == 2 and "rgb" in color.lower():
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
        elif len(s) == 3 and "mono" in color.lower():
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

        return image_array


def detect_blob(image_array, threshold=None, contour_limits=None, circle_limits=None, zero_point=None,
                m_point=None, fit_circle=False):
    """
    Detect blob in image array and report locations with drawn image array.
    :param image_array: (np.array) Image array to convert.
    :param threshold: (int) Lower threshold value for cv2.threshold.
    :param contour_limits: (int list) Lower and upper bounds for area size of found blob.
    :param circle_limits: (float list) Lower and upper bounds for circularity of found blob.
    :param zero_point: (int tuple) Point of reference.
    :param m_point: (int tuple) Measured point.
    :param fit_circle: (bool) Fit a least squares circle to found blob?
    :return: (np.array) image with drawn detections, (int tuple) center of found blob
    """
    # Define local variables
    blob_center = (0, 0)
    if threshold is None:
        threshold = json_settings["Detection"]["Threshold"]
    if contour_limits is None:
        contour_limits = json_settings["Detection"]["Limits"]
    poly_fit = json_settings["Detection"]["Poly Fit"]
    gauss = json_settings["Detection"]["Gaussian"]
    feature_sz = json_settings["Detection"]["Feature Size"]
    if circle_limits is None:
        circle_limits = json_settings["Detection"]["Circularity"]

    # Baseline image data
    if image_array.any():
        drawn_image = convert_color_bit(image_array.copy(), "rgb", 8)
        image_grey8 = convert_color_bit(image_array.copy(), "mono", 8)
        image_gauss = cv2.GaussianBlur(image_grey8, (gauss, gauss), 1)
        ret, thresh = cv2.threshold(image_gauss, threshold, 255, cv2.THRESH_BINARY)
        contours_found, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Detect blobs and their centers using input parameters
        for contour in contours_found:
            area = cv2.contourArea(contour)
            if contour_limits[0] < area < contour_limits[1]:
                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:
                    break
                approx = cv2.approxPolyDP(contour, poly_fit, True)

                if fit_circle:  # if the blob is expected to be circular
                    circularity = 4 * math.pi * (area / (perimeter * perimeter))
                    if circle_limits[0] < circularity < circle_limits[1]:
                        individual = np.array([pnt[0] for pnt in approx])
                        xc, yc, rc, sig = circle_fit.least_squares_circle(individual)
                        blob_center = (int(xc), int(yc))
                        cv2.circle(drawn_image, blob_center, int(rc), (255, 0, 0), feature_sz)
                        cv2.circle(drawn_image, blob_center, feature_sz, (255, 0, 0), feature_sz)
                else:
                    moment = cv2.moments(contour)
                    blob_center_x = moment["m10"] / moment["m00"]
                    blob_center_y = moment["m01"] / moment["m00"]
                    blob_center = (int(blob_center_x), int(blob_center_y))
                    cv2.circle(drawn_image, blob_center, feature_sz, (255, 0, 0), feature_sz)
                    cv2.drawContours(drawn_image, [approx], 0, (255, 0, 0), feature_sz)

        # Draw zero and last measurement
        if zero_point is not None and zero_point != (0, 0):
            cv2.circle(drawn_image, zero_point, feature_sz, (0, 255, 0), feature_sz)
        if m_point is not None and m_point != (0, 0):
            cv2.circle(drawn_image, m_point, feature_sz, (0, 0, 255), feature_sz)

        return drawn_image, blob_center
    else:
        return None, None
