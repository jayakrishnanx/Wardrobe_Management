from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import colorsys

COLOR_NAMES = {
    'black': lambda h, s, v: v < 0.2,
    'white': lambda h, s, v: v > 0.85 and s < 0.15,
    'gray':  lambda h, s, v: s < 0.2,
    'red':   lambda h, s, v: h < 0.05 or h > 0.95,
    'yellow':lambda h, s, v: 0.10 < h < 0.18,
    'green': lambda h, s, v: 0.18 < h < 0.45,
    'blue':  lambda h, s, v: 0.45 < h < 0.75,
    'brown': lambda h, s, v: 0.05 < h < 0.15 and v < 0.6,
}

def rgb_to_hsv(rgb):
    r, g, b = [x / 255 for x in rgb]
    return colorsys.rgb_to_hsv(r, g, b)

def classify_color(rgb):
    h, s, v = rgb_to_hsv(rgb)
    for name, rule in COLOR_NAMES.items():
        if rule(h, s, v):
            return name
    return 'gray'

def extract_dominant_color(image_path):
    img = Image.open(image_path).convert('RGB')
    img = img.resize((100, 100))

    pixels = np.array(img)

    # 🔥 Ignore background edges (crop center)
    h, w, _ = pixels.shape
    pixels = pixels[h//6:5*h//6, w//6:5*w//6]
    pixels = pixels.reshape(-1, 3)

    # 🔥 KMeans clustering
    kmeans = KMeans(n_clusters=3, n_init=10)
    kmeans.fit(pixels)

    dominant_rgb = kmeans.cluster_centers_[np.argmax(
        np.bincount(kmeans.labels_)
    )]

    return classify_color(dominant_rgb)
