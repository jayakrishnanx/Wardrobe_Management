from wardrobe.models import WardrobeItem
from accessories.models import Accessory
from .models import OutfitRecommendation, AccessoryRecommendation, ColorMatchingRule

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
# 🎨 COLOR MATCHING RULES (OVERRIDE ML)
# ==========================================================

def check_color_rules(top_color, bottom_color):
    """
    Returns a score if a specific rule matches, else None.
    High score = Good match.
    Low score = Bad match.
    """
    tc = normalize_color(top_color)
    bc = normalize_color(bottom_color)

    # 1. RED & GREEN (User specifically said this is BAD)
    if ('red' in tc and 'green' in bc) or ('green' in tc and 'red' in bc):
        return 0.20  # Poor

    # 2. BLACK & WHITE (User specifically said this is GOOD)
    if ('black' in tc and 'white' in bc) or ('white' in tc and 'black' in bc):
        return 0.90  # Excellent

    # 3. BLUE & WHITE (Classic)
    if ('blue' in tc and 'white' in bc) or ('white' in tc and 'blue' in bc):
        return 0.85

    # 4. NEUTRALS (Black, White, Grey match almost anything)
    neutrals = ['black', 'white', 'grey', 'gray', 'beige']
    
    # If both are neutral -> Good
    if any(n in tc for n in neutrals) and any(n in bc for n in neutrals):
        return 0.85

    # If one is neutral -> Safe/Good
    if any(n in tc for n in neutrals) or any(n in bc for n in neutrals):
        return 0.75
        
    # 4. BLUE & WHITE (Classic)
    if ('blue' in tc and 'white' in bc) or ('white' in tc and 'blue' in bc):
        return 0.85

    # No specific rule matched
    return None


# ==========================================================
# 🧠 HYBRID MATCH SCORE (RULES + ML)
# ==========================================================

def calculate_match_score(top, bottom, rules_list):
    
    top_color = normalize_color(top.color)
    bottom_color = normalize_color(bottom.color)

    # 1. CHECK HARDCODED RULES FIRST (User preferences)
    rule_score = check_color_rules(top.color, bottom.color)
    if rule_score is not None:
        return rule_score

    # 2. CHECK DATABASE RULES
    if rules_list:
        for c1, c2, score in rules_list:
            # Check both directions (A+B or B+A)
            if (c1 in top_color and c2 in bottom_color) or (c2 in top_color and c1 in bottom_color):
                return score

    # 3. FALLBACK TO ML MODEL
    if not (model and color_encoder and label_encoder):
        return 0.40  # fallback if ML missing

    # Handle unseen colors safely
    if (
        top_color not in color_encoder.classes_
        or bottom_color not in color_encoder.classes_
    ):
        return 0.40

    try:
        top_encoded = color_encoder.transform([top_color])[0]
        bottom_encoded = color_encoder.transform([bottom_color])[0]

        prediction = model.predict([[top_encoded, bottom_encoded]])[0]
        label = label_encoder.inverse_transform([prediction])[0]
        
        return LABEL_TO_SCORE.get(label, 0.40)
    except Exception:
        return 0.40

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

def generate_outfit_recommendations(user, occasion_id=None, season_id=None):
    """
    Generates recommendations for all combinations.
    Optionally filters by occasion/season if needed, 
    but currently generates all and views filter them.
    """
    tops = WardrobeItem.objects.filter(
        user=user, category__name__iexact="top"
    )
    bottoms = WardrobeItem.objects.filter(
        user=user, category__name__iexact="bottom"
    )
    
    # Optional: Apply filters at generation time for efficiency
    if occasion_id:
        tops = tops.filter(occasion_id=occasion_id)
        bottoms = bottoms.filter(occasion_id=occasion_id)
        
    if season_id:
        tops = tops.filter(season_id=season_id)
        bottoms = bottoms.filter(season_id=season_id)

    # Pre-fetch color rules for efficiency
    rules_query = ColorMatchingRule.objects.all()
    # Store as list of tuples: (normalized_c1, normalized_c2, score)
    rules_list = [
        (normalize_color(r.color_1), normalize_color(r.color_2), r.score) 
        for r in rules_query
    ]

    for top in tops:
        for bottom in bottoms:
            score = calculate_match_score(top, bottom, rules_list)

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
