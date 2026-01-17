from wardrobe.models import WardrobeItem
from accessories.models import Accessory
from .models import OutfitRecommendation, AccessoryRecommendation

import os
import joblib

# ==========================================================
# 📁 BASE DIRECTORY
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================================
# 🤖 LOAD ML FILES (REQUIRED FOR ML MODE)
# ==========================================================

MODEL_PATH = os.path.join(BASE_DIR, "fashion_model.pkl")
COLOR_ENCODER_PATH = os.path.join(BASE_DIR, "color_encoder.pkl")
LABEL_ENCODER_PATH = os.path.join(BASE_DIR, "label_encoder.pkl")

model = None
color_encoder = None
label_encoder = None

if (
    os.path.exists(MODEL_PATH)
    and os.path.exists(COLOR_ENCODER_PATH)
    and os.path.exists(LABEL_ENCODER_PATH)
):
    model = joblib.load(MODEL_PATH)
    color_encoder = joblib.load(COLOR_ENCODER_PATH)
    label_encoder = joblib.load(LABEL_ENCODER_PATH)

# ==========================================================
# 🔢 LABEL → SCORE
# ==========================================================

LABEL_TO_SCORE = {
    "bad": 0.25,
    "average": 0.50,
    "good": 0.70,
    "excellent": 0.85,
}

# ==========================================================
# 🎨 NORMALIZE COLOR (FOR ML CONSISTENCY)
# ==========================================================

def normalize_color(color):
    if not color:
        return ""
    return color.lower().strip()

# ==========================================================
# 🧠 ML-ONLY MATCH SCORE
# ==========================================================

def calculate_match_score(top, bottom):
    if not (model and color_encoder and label_encoder):
        return 0.40  # fallback if ML missing

    top_color = normalize_color(top.color)
    bottom_color = normalize_color(bottom.color)

    # Handle unseen colors safely
    if (
        top_color not in color_encoder.classes_
        or bottom_color not in color_encoder.classes_
    ):
        return 0.40

    top_encoded = color_encoder.transform([top_color])[0]
    bottom_encoded = color_encoder.transform([bottom_color])[0]

    prediction = model.predict([[top_encoded, bottom_encoded]])[0]
    label = label_encoder.inverse_transform([prediction])[0]

    return LABEL_TO_SCORE.get(label, 0.40)

# ==========================================================
# 🏷️ SCORE → LABEL (UI)
# ==========================================================

def score_to_label(score):
    if score >= 0.80:
        return "Excellent"
    if score >= 0.65:
        return "Good"
    if score >= 0.45:
        return "Average"
    return "Bad"

# ==========================================================
# 👕 OUTFIT GENERATION
# ==========================================================

def generate_outfit_recommendations(user):
    tops = WardrobeItem.objects.filter(
        user=user, category__name__iexact="top"
    )
    bottoms = WardrobeItem.objects.filter(
        user=user, category__name__iexact="bottom"
    )

    for top in tops:
        for bottom in bottoms:
            score = calculate_match_score(top, bottom)

            OutfitRecommendation.objects.update_or_create(
                user=user,
                top_item=top,
                bottom_item=bottom,
                defaults={"match_score": score},
            )

# ==========================================================
# 🎒 ACCESSORY RECOMMENDATION (UNCHANGED)
# ==========================================================

def recommend_accessories(outfit, top, bottom):
    accessories = Accessory.objects.filter(
        is_active=True, stock__gt=0
    )

    for accessory in accessories:
        score = 0.0

        if accessory.color:
            c = accessory.color.lower()
            if top.color and c in top.color.lower():
                score += 0.4
            if bottom.color and c in bottom.color.lower():
                score += 0.4

        if score >= 0.4:
            AccessoryRecommendation.objects.create(
                outfit=outfit,
                accessory=accessory,
                score=round(score, 2),
            )
