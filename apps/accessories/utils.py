from PIL import Image
import os

COLOR_MAP = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'green': (0, 128, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'brown': (165, 42, 42),
    'gray': (128, 128, 128),
}


def closest_color(rgb):
    r, g, b = rgb
    min_dist = float('inf')
    color_name = None

    for name, (cr, cg, cb) in COLOR_MAP.items():
        dist = (r - cr)**2 + (g - cg)**2 + (b - cb)**2
        if dist < min_dist:
            min_dist = dist
            color_name = name

    return color_name


def extract_dominant_color(image_path):
    img = Image.open(image_path).convert('RGB')
    img = img.resize((50, 50))
    pixels = list(img.getdata())

    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)

    return closest_color((r, g, b))
