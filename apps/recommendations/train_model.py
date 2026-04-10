import pandas as pd
import joblib
import os

from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

# 📁 Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 📄 CSV path
DATA_PATH = os.path.join(BASE_DIR, "fashion_training_data.csv")

# Load dataset
df = pd.read_csv(DATA_PATH)

# 🔹 Normalize text (VERY IMPORTANT)
df["top_color"] = df["top_color"].str.lower().str.strip()
df["bottom_color"] = df["bottom_color"].str.lower().str.strip()
df["label"] = df["label"].str.lower().str.strip()

# 🔹 Fit encoder on ALL colors
all_colors = pd.concat([df["top_color"], df["bottom_color"]])

color_encoder = LabelEncoder()
color_encoder.fit(all_colors)

df["top_encoded"] = color_encoder.transform(df["top_color"])
df["bottom_encoded"] = color_encoder.transform(df["bottom_color"])

# 🔹 Encode labels
label_encoder = LabelEncoder()
df["label_encoded"] = label_encoder.fit_transform(df["label"])

X = df[["top_encoded", "bottom_encoded"]]
y = df["label_encoded"]

# 🔹 Train model
model = RandomForestClassifier(
    n_estimators=150,
    random_state=42
)
model.fit(X, y)

# 🔹 Save trained objects
joblib.dump(model, os.path.join(BASE_DIR, "fashion_model.pkl"))
joblib.dump(color_encoder, os.path.join(BASE_DIR, "color_encoder.pkl"))
joblib.dump(label_encoder, os.path.join(BASE_DIR, "label_encoder.pkl"))

print("✅ Model and encoders saved successfully")
