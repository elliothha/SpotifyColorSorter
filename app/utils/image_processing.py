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
    # INPUT rgb_color = tuple (R, G, B) each value in range [0, 255]
    # OUTPUT lab_color = NP array with 3 int elements [L, a, b] in LAB space
    bgr_color = rgb_color[::-1]

    lab_color = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2LAB)[0][0]
    return lab_color


def lab_color_distance(lab1, lab2):
    lab1 = np.array(lab1, dtype=np.float64)
    lab2 = np.array(lab2, dtype=np.float64)

    return np.sqrt(np.sum((lab1 - lab2) ** 2))


def get_dominant_colors(image, palette_size=16, top_colors=3):
    image.thumbnail((300, 300))

    paletted = image.convert('P', palette=Image.ADAPTIVE, colors=palette_size)
    # palette = [R1, G1, B1, R2, G2, B2, ...] 
    # with values in range [0, 255]. slice to get each color
    palette = paletted.getpalette()

    # .getcolors() returns a list of tuples: [(freq (int), idx (int))]
    # the idx is the index of the color in the palette
    # the sort is by frequency of color count in descending order (most frequent -> leasta)
    color_counts = sorted(paletted.getcolors(), reverse=True)

    num_extract = min(len(color_counts), top_colors)

    # top_color_indices will be [idx_1, idx_2, idx_3] of the top 3 most dominant colors
    # top_3_colors will slice palette according to these indices to return a list of tuples
    # top_3_colors = [(R_top1, G_top1, B_top1), ..., (R_top3, G_top3, B_top3)]
    top_color_indices = [color_count[1] for color_count in color_counts[:num_extract]]
    top_colors = [palette[idx*3:idx*3+3] for idx in top_color_indices]

    return top_colors
