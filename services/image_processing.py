from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import interpolation as inter

from config import get_logger


def _ensure_pil(image_path: str) -> Image.Image:
    return Image.open(image_path)


def image_normalizer(input_path: str, output_path: str) -> str:
    img = cv2.imread(input_path)
    normalized_img = np.zeros((img.shape[0], img.shape[1]))
    img = cv2.normalize(img, normalized_img, 0, 255, cv2.NORM_MINMAX)
    Image.fromarray(img).save(output_path)
    return output_path


def correct_skew(input_path: str, output_path: str, delta: int = 1, limit: int = 5) -> str:
    image = cv2.imread(input_path)

    def score_for_angle(arr: np.ndarray, angle: float) -> float:
        data = inter.rotate(arr, angle, reshape=False, order=0)
        histogram = np.sum(data, axis=1, dtype=float)
        return float(np.sum((histogram[1:] - histogram[:-1]) ** 2, dtype=float))

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    angles = np.arange(-limit, limit + delta, delta)
    scores = [score_for_angle(thresh, angle) for angle in angles]
    best_angle = float(angles[int(np.argmax(scores))])

    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, best_angle, 1.0)
    corrected = cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )

    Image.fromarray(corrected).save(output_path)
    return output_path


def image_scaler(input_path: str, output_path: str) -> str:
    img = _ensure_pil(input_path)
    length_x, width_y = img.size
    factor = min(1, float(1024.0 / length_x))
    size = int(factor * length_x), int(factor * width_y)
    img.resize(size, Image.Resampling.LANCZOS).save(output_path, dpi=(300, 300))
    return output_path


def noise_remover(input_path: str, output_path: str) -> str:
    img = cv2.imread(input_path)
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 15)
    Image.fromarray(denoised).save(output_path)
    return output_path


def image_thinner_skeletonizer(input_path: str, output_path: str) -> str:
    img = cv2.imread(input_path, 0)
    kernel = np.ones((2, 2), np.uint8)
    erosion = cv2.erode(img, kernel, iterations=1)
    Image.fromarray(erosion).save(output_path)
    return output_path


def image_greyscaler(input_path: str, output_path: str) -> str:
    img = cv2.imread(input_path)
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    Image.fromarray(grey).save(output_path)
    return output_path


def process_image(image_path: str) -> str:
    logger = get_logger()
    base = Path(image_path)
    root = base.parent

    enhanced = str(root / "enhanced.png")
    corrected = str(root / "corrected.png")
    scaled = str(root / "scaled.png")
    noise_removed = str(root / "noise-removed.png")
    thinner = str(root / "thinner.png")
    grey = str(root / "grey.png")

    try:
        logger.info("Normalizing image")
        image_normalizer(image_path, enhanced)

        logger.info("Correcting skew")
        correct_skew(enhanced, corrected)

        logger.info("Scaling image")
        image_scaler(corrected, scaled)

        logger.info("Removing noise")
        noise_remover(scaled, noise_removed)

        logger.info("Thinning image")
        image_thinner_skeletonizer(noise_removed, thinner)

        logger.info("Converting to greyscale")
        image_greyscaler(thinner, grey)
    except Exception as exc:
        logger.error(f"Error processing image: {exc}")
        raise

    return grey
