from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import math

BASIC_COLORS = {
    'red': (220, 20, 20),
    'dark red': (139, 0, 0),
    'green': (34, 139, 34),
    'light green': (144, 238, 144),
    'blue': (0, 0, 205),
    'light blue': (135, 206, 235),
    'navy': (0, 0, 128),
    'yellow': (255, 215, 0),
    'orange': (255, 140, 0),
    'pink': (255, 105, 180),
    'purple': (128, 0, 128),
    'brown': (139, 69, 19),
    'light brown': (210, 180, 140),
    'black': (30, 30, 30),
    'white': (245, 245, 245),
    'gray': (128, 128, 128),
    'light gray': (211, 211, 211),
    'dark gray': (80, 80, 80),
    'beige': (245, 245, 220),
    'maroon': (128, 0, 0),
    'teal': (0, 128, 128),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'olive': (128, 128, 0),
}

def classify_color(rgb):
    """
    Classify an RGB tuple to the nearest perceptual color using the
    'redmean' approximation for human visual perception.
    """
    r, g, b = [float(x) for x in rgb]
    min_dist = float('inf')
    best_color = 'gray'
    
    for name, (cr, cg, cb) in BASIC_COLORS.items():
        rmean = (r + cr) / 2
        r_diff = r - cr
        g_diff = g - cg
        b_diff = b - cb
        
        weight_r = 2 + rmean / 256
        weight_g = 4.0
        weight_b = 2 + (255 - rmean) / 256
        
        dist = math.sqrt(weight_r * (r_diff**2) + weight_g * (g_diff**2) + weight_b * (b_diff**2))
        
        if dist < min_dist:
            min_dist = dist
            best_color = name
            
    return best_color

def extract_dominant_color(image_path):
    img = Image.open(image_path).convert('RGB')
    # Resize to speed up calculation and smooth out noise
    img = img.resize((150, 150))
    
    pixels = np.array(img)
    h, w, _ = pixels.shape
    
    # 1. Identify Background Color from Edges
    edges = np.concatenate([
        pixels[0, :],      # Top
        pixels[-1, :],     # Bottom
        pixels[:, 0],      # Left
        pixels[:, -1]      # Right
    ])
    
    # Use 4 clusters to separate item, background, shadows, and highlights
    pixels_flat = pixels.reshape(-1, 3)
    kmeans = KMeans(n_clusters=4, n_init=10, random_state=42)
    kmeans.fit(pixels_flat)
    
    # Predict clusters for edges to find the background cluster
    edge_labels = kmeans.predict(edges)
    bg_cluster = np.bincount(edge_labels).argmax()
    
    # 2. Extract item color from Center
    # We focus on the central 50% of the image which highly likely contains the item
    center = pixels[h//4:3*h//4, w//4:3*w//4]
    center_flat = center.reshape(-1, 3)
    center_labels = kmeans.predict(center_flat)
    
    counts = np.bincount(center_labels, minlength=4)
    
    # Suppress the background cluster so it isn't picked as the dominant color
    counts[bg_cluster] = 0
    
    if np.max(counts) == 0:
        # Fallback if the entire center is somehow the background color
        dominant_cluster = bg_cluster
    else:
        dominant_cluster = np.argmax(counts)
        
    dominant_rgb = kmeans.cluster_centers_[dominant_cluster]
    return classify_color(dominant_rgb)

