from wardrobe.models import WardrobeItem
from accessories.models import Accessory
from .models import OutfitRecommendation, AccessoryRecommendation, ColorMatchingRule
from django.db.models import Q

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
        user=user, category__name__iexact="top", clean_status=True
    )
    bottoms = WardrobeItem.objects.filter(
        user=user, category__name__iexact="bottom", clean_status=True
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

            outfit, created = OutfitRecommendation.objects.update_or_create(
                user=user,
                top_item=top,
                bottom_item=bottom,
                defaults={"match_score": score},
            )
            
            # Generate accessory recommendations for this outfit
            recommend_accessories(outfit, top, bottom)

# ==========================================================
# 🎒 ACCESSORY RECOMMENDATION (UNCHANGED)
# ==========================================================

def recommend_accessories(outfit, top, bottom):
    """
    Recommends 1-3 accessories that match the outfit's gender and color.
    """
    user = outfit.user
    
    # 1. Clear existing accessory recommendations for this outfit
    AccessoryRecommendation.objects.filter(outfit=outfit).delete()

    # 2. Base filter: Active, in stock, and gender-appropriate
    # Also exclude clothing categories based on name or category
    clothing_keywords = [
        'shirt', 'pant', 'jeans', 't-shirt', 'trouser', 'dress', 
        'top', 'bottom', 'jacket', 'coat', 'sweatshirt', 'hoodie'
    ]
    
    gender_q = Q(gender='other')
    if user.gender == 'male':
        gender_q |= Q(gender='male')
    elif user.gender == 'female':
        gender_q |= Q(gender='female')
    else:
        gender_q |= Q(gender='male') | Q(gender='female')

    accessories = Accessory.objects.filter(
        gender_q,
        is_active=True, 
        stock__gt=0
    )

    # Exclude items that sound like clothing
    for keyword in clothing_keywords:
        accessories = accessories.exclude(category__icontains=keyword).exclude(name__icontains=keyword)

    # 3. Match based on color and optionally occasion/season
    results = []
    for accessory in accessories:
        score = 0.0

        # Color matching (0.4 if matches top, 0.4 if matches bottom)
        if accessory.color and (top.color or bottom.color):
            a_color = accessory.color.lower()
            if top.color and a_color in top.color.lower():
                score += 0.4
            if bottom.color and a_color in bottom.color.lower():
                score += 0.4
        
        # Style matching (0.2 if matches occasion, 0.2 if matches season)
        if accessory.occasion_id == top.occasion_id or accessory.occasion_id == bottom.occasion_id:
            score += 0.1
        if accessory.season_id == top.season_id or accessory.season_id == bottom.season_id:
            score += 0.1

        if score >= 0.2: # Minimum threshold to suggest
            results.append((accessory, score))

    # 4. Save top 3 recommendations
    results.sort(key=lambda x: x[1], reverse=True)
    for accessory, score in results[:3]:
        AccessoryRecommendation.objects.create(
            outfit=outfit,
            accessory=accessory,
            score=round(score, 2),
        )

# ==========================================================
# 🤖 AI CHATBOT INTEGRATION (GROQ / GEMINI)
# ==========================================================
import google.generativeai as genai
from groq import Groq
import os
from dotenv import load_dotenv
import json

def get_ai_response(system_instruction, use_json=True):
    """
    Tries Gemini first, then Groq on failure (failover).
    """
    load_dotenv()
    gemini_key = os.environ.get('GEMINI_API_KEY')
    groq_key = os.environ.get('GROQ_API_KEY')

    # --- 1. TRY GEMINI ---
    if gemini_key and gemini_key != 'YOUR_API_KEY_HERE':
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(system_instruction)
            text_resp = response.text.strip()
            # Clean markdown
            if text_resp.startswith('```json'): text_resp = text_resp[7:]
            if text_resp.endswith('```'): text_resp = text_resp[:-3]
            return json.loads(text_resp.strip())
        except Exception as e:
            error_msg = str(e)
            # If not a quota error, we might still want to try Groq
            # If it IS a quota error, we definitely try Groq
            if "429" not in error_msg and "quota" not in error_msg.lower():
                # Non-quota error but still failed, maybe try Groq anyway?
                # User specifically asked "if gemini overuse switch to groq"
                pass 

    # --- 2. TRY GROQ (FAILOVER) ---
    if groq_key and groq_key != 'YOUR_API_KEY_HERE':
        try:
            client = Groq(api_key=groq_key)
            params = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": system_instruction}],
            }
            if use_json:
                params["response_format"] = {"type": "json_object"}
                
            completion = client.chat.completions.create(**params)
            text_resp = completion.choices[0].message.content
            return json.loads(text_resp.strip())
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                return "quota_limited"
            raise e # Let the caller handle other Groq errors

    return "no_provider"

def generate_ai_chat_response(prompt, user):
    # 1. Gather User's Top and Bottom Items
    tops = WardrobeItem.objects.filter(user=user, category__name__iexact='top', clean_status=True)
    bottoms = WardrobeItem.objects.filter(user=user, category__name__iexact='bottom', clean_status=True)
    
    # 2. Gather Gender-Appropriate Accessories from Suppliers (Exclude clothing)
    clothing_keywords = [
        'shirt', 'pant', 'jeans', 't-shirt', 'trouser', 'dress', 
        'top', 'bottom', 'jacket', 'coat', 'sweatshirt', 'hoodie'
    ]

    accessories = Accessory.objects.filter(
        Q(gender=user.gender) | Q(gender='other'),
        is_active=True, 
        stock__gt=0
    )

    for keyword in clothing_keywords:
        accessories = accessories.exclude(category__icontains=keyword).exclude(name__icontains=keyword)

    accessories = accessories[:10] # Suggest top 10 matching accessories
    
    inventory_str = 'Tops available:\n'
    for t in tops:
        inventory_str += f'- ID: {t.id}, Type: {t.item_type}, Color: {t.color}\n'
        
    inventory_str += '\nBottoms available:\n'
    for b in bottoms:
        inventory_str += f'- ID: {b.id}, Type: {b.item_type}, Color: {b.color}\n'
        
    accessory_str = '\nAvailable Accessories from Suppliers:\n'
    for a in accessories:
        accessory_str += f'- {a.name} ({a.category}), Price: ₹{a.price}, Color: {a.color}, Supplier: {a.supplier.username}\n'

    system_instruction = f"""You are a helpful fashion stylist AI. 
The user ({user.username}, Gender: {user.get_gender_display()}) is asking for an outfit recommendation based on their prompt: '{prompt}'

Here is their current clean wardrobe inventory:
{inventory_str}

{accessory_str}

Please respond like a friendly chatbot. 
CRITICAL: You MUST start your 'message' with "Hi {user.username}, ".

Suggest 1 or 2 complete outfits using exclusively the items listed above. 
For EACH outfit, explicitly explain WHY you are recommending it.

In your response message, you MUST also suggest 1 or 2 matching accessories from the "Available Accessories from Suppliers" list above that complement the suggested outfits. Mention the supplier name and price.

IMPORTANT: You MUST respond purely in valid JSON format with NO markdown wrapping. 
Structure:
{{
    "message": "Hi {user.username}, [Friendly conversation, reasoning, and accessories recommendations...]",
    "outfits": [
        {{"top_id": X, "bottom_id": Y}}
    ]
}}
"""

    try:
        resp = get_ai_response(system_instruction)
        if resp == "quota_limited" or resp == "no_provider":
             return {"message": "todays quata limited", "outfits": []}
        return resp
    except Exception as e:
        return {"message": f"Oops! I ran into an error trying to process your request: {str(e)}", "outfits": []}

def analyze_feedback_with_ai(feedback):
    """
    Analyzes a user's feedback text using AI to determine a recommended
    color matching score and updates the color rules.
    """
    top_color = normalize_color(feedback.recommendation.top_item.color)
    bottom_color = normalize_color(feedback.recommendation.bottom_item.color)
    text = feedback.feedback_text
    rating = feedback.rating # 1.0 to 5.0

    system_instruction = f"""You are a fashion expert AI. 
Analyze the following user feedback regarding a color combination.
Top Color: {top_color}
Bottom Color: {bottom_color}
User Rating: {rating}/5.0
User Comment: "{text}"

Based on the comment and rating, suggest a 'match_score' for this specific color combination from 0.0 (Worst/Hated) to 1.0 (Best/Loved).

Respond ONLY in valid JSON format:
{{
    "suggested_score": float,
    "reasoning": "brief explanation"
}}
"""

    try:
        resp = get_ai_response(system_instruction)
        if resp == "quota_limited" or resp == "no_provider":
            return False, "todays quata limited"
            
        suggested_score = float(resp.get('suggested_score', 0.5))
        reasoning = resp.get('reasoning', 'AI analysis complete.')

        colors = sorted([top_color, bottom_color])
        rule, created = ColorMatchingRule.objects.update_or_create(
            color_1=colors[0],
            color_2=colors[1],
            defaults={'score': suggested_score}
        )

        feedback.ai_review = reasoning
        feedback.is_read = True
        feedback.save()

        return True, f"AI suggests a score of {suggested_score}. Reasoning: {reasoning}"
    except Exception as e:
        return False, f"AI Analysis failed: {str(e)}"
