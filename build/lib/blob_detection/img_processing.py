import cv2, os, json, math
import numpy as np
import circle_fit

with open(os.path.join(os.getcwd(), "blob_detection\\support\\gui_settings.json")) as f:
    json_settings = json.load(f)


def convert_color_bit(img_array, color, bit_depth):
    if img_array.any():
        # Check bit depth
        current_bd = img_array.dtype.name
        if "8" in str(bit_depth) and "8" not in current_bd:  # 16-bit to 8-bit
            img_array = (img_array / 256).astype('uint8')
        elif "16" in str(bit_depth) and "16" not in current_bd:  # 8-bit to 16-bit
            img_array = (img_array * 256).astype('uint16')

        # Check color
        s = img_array.shape
        if len(s) == 2 and "rgb" in color.lower():
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        elif len(s) == 3 and "gray" in color.lower():
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        return img_array


def detect_blob(image_array, threshold=None, contours=None, circle_limits=None, zero_point=None):
    # Variables
    blob_center = (0, 0)
    if threshold is None:
        threshold = json_settings["Detection"]["Threshold"]
    if contours is None:
        contours = json_settings["Detection"]["Limits"]
    poly_fit = json_settings["Detection"]["Poly Fit"]
    gauss = json_settings["Detection"]["Gaussian"]
    feature_sz = json_settings["Detection"]["Feature Size"]
    if circle_limits is None:
        circle_limits = json_settings["Detection"]["Circularity"]

    # Baseline image data
    if image_array.any():
        drawn_image = convert_color_bit(image_array.copy(), "rgb", 8)
        image_grey8 = convert_color_bit(image_array.copy(), "gray", 8)
        image_gauss = cv2.GaussianBlur(image_grey8, (gauss, gauss), 1)
        ret, thresh = cv2.threshold(image_gauss, threshold, 255, cv2.THRESH_BINARY)
        contours_found, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Detect blobs and their centers
        for contour in contours_found:
            area = cv2.contourArea(contour)
            # print(area)
            if contours[0] < area < contours[1]:
                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:
                    break
                circularity = 4 * math.pi * (area / (perimeter * perimeter))
                if circle_limits[0] < circularity < circle_limits[1]:
                    approx = cv2.approxPolyDP(contour, poly_fit, True)
                    individual = np.array([pnt[0] for pnt in approx])
                    xc, yc, rc, sig = circle_fit.least_squares_circle(individual)
                    blob_center = (int(xc), int(yc))

                    # Draw features
                    # cv2.drawContours(drawn_image, [approx], 0, (0, 255, 0), feature_sz)
                    cv2.circle(drawn_image, blob_center, int(rc), (0, 0, 255), feature_sz)
                    cv2.circle(drawn_image, blob_center, feature_sz, (0, 0, 255), feature_sz)

        # Always draw zero
        if zero_point is not None and zero_point != (0, 0):
            cv2.circle(drawn_image, zero_point, feature_sz, (0, 255, 0), feature_sz)

        return drawn_image, blob_center
    else:
        return None, None


if __name__ == "__main__":
    import time
    img = cv2.imread("c:\\users\\lab\\desktop\\image_20230626-183725_200000us_1.png")
    window_name = "blob"

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 600, 500)
    for i in range(150, 200):
        print(i)
        shown_img, _ = detect_blob(img.copy(), i)
        cv2.imshow(window_name, shown_img)
        cv2.waitKey(1)
        time.sleep(0.5)
