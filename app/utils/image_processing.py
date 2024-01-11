'''
Module: utils
Author: Elliot H. Ha
Created on: Dec 27, 2023

Description:
This file provides utility functions for image processing for use in sorting.
It includes functions for extracting Image URLs and their dominant color, convert RGB to LAB, and calculate LAB color distance

Functions:
- download_image(image_url): returns the PIL Image of the playlist image URL passed as an argument

- rgb_to_lab(rgb_color): returns the LAB color space equivalent to the RGB value passed as an argument

- lab_color_distance(lab1, lab2): returns the linear distance between two LAB values in color space

- get_dominant_color(image, palette_size): returns the RGB values of the dominant color in a given PIL Image 
'''

import cv2
import requests
import numpy as np

from PIL import Image
from io import BytesIO

# ---- IMAGE PROCESSING -----------------------------------------------
def download_image(image_url):
    response = requests.get(image_url)

    img = Image.open(BytesIO(response.content))
    return img


# ---- COLOR PROCESSING -----------------------------------------------
def rgb_to_lab(rgb_color):
    bgr_color = rgb_color[::-1]

    lab_color = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2LAB)[0][0]
    return lab_color


def lab_color_distance(lab1, lab2):
    lab1 = np.array(lab1, dtype=np.float64)
    lab2 = np.array(lab2, dtype=np.float64)

    return np.sqrt(np.sum((lab1 - lab2) ** 2))


def get_dominant_color(image, palette_size=16):
    image.thumbnail((300, 300))

    paletted = image.convert('P', palette=Image.ADAPTIVE, colors=palette_size)
    # palette = [R1, G1, B1, R2, G2, B2, ...] with values in range [0, 255]. slice to get each color
    palette = paletted.getpalette()

    color_counts = sorted(paletted.getcolors(), reverse=True)
    dominant_idx = color_counts[0][1]

    dominant_color = palette[dominant_idx*3:dominant_idx*3+3]
    return dominant_color
