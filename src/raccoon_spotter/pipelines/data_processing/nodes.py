from typing import Dict

import cv2
import numpy as np


def reshape_image_arrays(image_arrays: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Add a color channel for greyscale images.

    Parameters:
    - image_arrays (np.ndarray): A numpy array containing image arrays, x for images, y for labels.

    Returns:
    - reshaped_dict (str, np.ndarray): A dictionary containing x (reshaped array of images) and y (labels).
    """
    GRAYSCALE_CHANNELS = 2
    RGB_CHANNELS = 3
    reshaped_arrays = []
    for img_array in image_arrays["x"]:
        if len(img_array.shape) == GRAYSCALE_CHANNELS:
            converted_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            reshaped_arrays.append(converted_array)
        elif len(img_array.shape) != RGB_CHANNELS:
            raise ValueError(
                f"Image array does not have three dimensions: {img_array.shape}"
            )
        else:
            reshaped_arrays.append(img_array)
    return {
        "x": np.array(reshaped_arrays, dtype=object),
        "y": image_arrays["y"],
    }


def _letterbox_image(img, inp_dim):
    """resize image with unchanged aspect ratio using padding"""
    img_h, img_w = img.shape[:2]
    w, h = inp_dim
    scale = min(w / img_w, h / img_h)
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)
    pad_x = (w - new_w) // 2
    pad_y = (h - new_h) // 2

    resized_image = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    canvas = np.full((h, w, 3), 128, dtype=np.uint8)
    canvas[pad_y : pad_y + new_h, pad_x : pad_x + new_w] = resized_image
    return canvas, pad_x, pad_y, scale


def resize_image_arrays(
    resize_image_config: dict, image_array: np.ndarray
) -> Dict[str, np.ndarray]:
    """
    Resize the image while adjusting the corresponding bounding box.

    Args:
    - image_array (np.ndarray): The image array to be resized.
    - target_width (int): The target width for resizing (default: 600).
    - target_height (int): The target height for resizing (default: 400).

    Returns:
     - A dictionary containing x (resized image array) and y (adjusted labels).
    """
    resized_arrays = []
    pad_x_y = []
    target_width = resize_image_config["target_width"]
    target_height = resize_image_config["target_height"]

    for img in image_array["x"]:
        resized_img, pad_x, pad_y, scale = _letterbox_image(
            img, (target_width, target_height)
        )
        resized_arrays.append(resized_img)
        pad_x_y.append((pad_x, pad_y, scale))

    resized_boxes = []
    for bbox, (pad_x, pad_y, scale) in zip(image_array["y"], pad_x_y):
        resized_bbox = [
            int((bbox[0] * scale) + pad_x),
            int((bbox[1] * scale) + pad_x),
            int((bbox[2] * scale) + pad_y),
            int((bbox[3] * scale) + pad_y),
        ]
        resized_boxes.append(resized_bbox)

    return {"x": np.stack(resized_arrays, axis=0), "y": np.array(resized_boxes)}
