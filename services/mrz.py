from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import cv2
import numpy as np
from passporteye import read_mrz

from config import get_logger


def _detect_mrz_region(image_path: str) -> str:
    logger = get_logger()

    logger.info("Reading image for MRZ detection")
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not read image for MRZ detection")

    height = 600
    ratio = height / float(image.shape[0])
    image = cv2.resize(image, (int(image.shape[1] * ratio), height))

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
    sq_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))

    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rect_kernel)

    grad_x = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    grad_x = np.absolute(grad_x)
    min_val, max_val = np.min(grad_x), np.max(grad_x)
    grad_x = (255 * ((grad_x - min_val) / (max_val - min_val))).astype("uint8")

    grad_x = cv2.morphologyEx(grad_x, cv2.MORPH_CLOSE, rect_kernel)
    thresh = cv2.threshold(grad_x, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sq_kernel)
    thresh = cv2.erode(thresh, None, iterations=4)

    p = int(image.shape[1] * 0.05)
    thresh[:, 0:p] = 0
    thresh[:, image.shape[1] - p :] = 0

    cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

    roi = image.copy()
    logger.info("Detecting MRZ region")
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        ar = w / float(h)
        cr_width = w / float(gray.shape[1])
        if ar > 5 and cr_width > 0.75:
            p_x = int((x + w) * 0.1)
            p_y = int((y + h) * 0.1)
            x, y = x - p_x, y - p_y
            w, h = w + (p_x * 2), h + (p_y * 2)
            roi = image[y : y + h, x : x + w].copy()
            break

    out_path = str(Path(image_path).parent / "mrz.png")
    cv2.imwrite(out_path, roi)
    return out_path


def _extract_mrz_data(image_path: str) -> Optional[Dict[str, Any]]:
    logger = get_logger()
    logger.info("Extracting MRZ data")

    mrz = read_mrz(image_path)
    if mrz is None:
        logger.error("PassportEye could not read MRZ data")
        return None

    data = mrz.to_dict()
    try:
        return {
            "type": data["mrz_type"],
            "confidence_score": data["valid_score"],
            "id_type": data["type"][0],
            "country": data["country"],
            "id_number": str(data["number"]).replace("<", "").replace(">", ""),
            "date_of_birth": data["date_of_birth"],
            "expiration_date": data["expiration_date"],
            "nationality": data["nationality"],
            "sex": data["sex"],
            "names": data["names"].split("  ")[0],
            "surname": data["surname"],
            "id_is_valid": data["valid_number"],
            "dob_is_valid": data["valid_date_of_birth"],
            "expiration_is_valid": data["valid_expiration_date"],
        }
    except KeyError as exc:
        logger.error(f"Unexpected MRZ data format: {exc}")
        return None


def detect_and_extract_mrz(image_path: str) -> Optional[Dict[str, Any]]:
    region_path = _detect_mrz_region(image_path)
    return _extract_mrz_data(region_path)
