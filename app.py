from flask import Flask, render_template, request
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# =========================================================
# CREATE FLASK APPLICATION
# =========================================================

app = Flask(__name__)

# =========================================================
# LOAD DATASET
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

df = pd.read_csv(
    os.path.join(BASE_DIR, "tourism_dataset_5000.csv")
)

# =========================================================
# CLEAN COLUMN NAMES
# =========================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

print("\n========== DATASET COLUMNS ==========")
print(df.columns.tolist())

# =========================================================
# HANDLE MISSING VALUES
# =========================================================

important_columns = [
    "site_name",
    "interests",
    "preferred_tour_duration",
    "accessibility",
    "tourist_rating"
]

for col in important_columns:
    if col in df.columns:
        df[col] = df[col].fillna("unknown")

# =========================================================
# CONVERT RATINGS TO NUMERIC
# =========================================================

df["tourist_rating"] = pd.to_numeric(
    df["tourist_rating"],
    errors="coerce"
).fillna(0)

# =========================================================
# FEATURE ENGINEERING
# =========================================================

def build_features(row):

    interests = " ".join(
        [str(row.get("interests", ""))] * 4
    )

    duration = str(
        row.get("preferred_tour_duration", "")
    )

    accessibility = str(
        row.get("accessibility", "")
    )

    combined = f"""
    {interests}
    {duration}
    {accessibility}
    """

    return combined.lower()

# Create feature column
df["combined_features"] = df.apply(
    build_features,
    axis=1
)

# =========================================================
# TF-IDF VECTORIZATION
# =========================================================

vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    max_features=5000
)

tfidf_matrix = vectorizer.fit_transform(
    df["combined_features"]
)

print("\n✅ TF-IDF Model Built Successfully")
print(f"✅ Total Destinations: {len(df)}")

# =========================================================
# RECOMMENDATION FUNCTION
# =========================================================

def get_recommendations(
    interests,
    duration,
    accessibility,
    top_n=8
):

    # Create user profile

    user_profile = f"""
    {' '.join([interests] * 4)}
    {duration}
    {accessibility}
    """

    user_profile = user_profile.lower()

    # Convert user profile into vector

    user_vector = vectorizer.transform(
        [user_profile]
    )

    # Cosine similarity

    similarity_scores = cosine_similarity(
        user_vector,
        tfidf_matrix
    ).flatten()

    # Sort results

    top_indices = similarity_scores.argsort()[::-1]

    results = []
    seen_places = set()

    for idx in top_indices:

        # Ignore weak matches
        if similarity_scores[idx] < 0.05:
            continue

        row = df.iloc[idx]

        place_name = str(
            row.get("site_name", "Unknown Place")
        )

        # Avoid duplicates
        if place_name in seen_places:
            continue

        seen_places.add(place_name)

        # Better score calculation

        rating = float(
            row.get("tourist_rating", 0)
        )

        similarity_percent = (
            similarity_scores[idx] * 85
        )

        rating_bonus = rating * 3

        final_score = (
            similarity_percent + rating_bonus
        )

        # Limit maximum score

        if final_score > 98:
            final_score = 98

        # Store recommendation

        results.append({

            "place_name": place_name,

            "tourist_rating": round(
                rating,
                1
            ),

            "interests": str(
                row.get("interests", "N/A")
            ),

            "duration": str(
                row.get(
                    "preferred_tour_duration",
                    "N/A"
                )
            ),

            "accessibility": str(
                row.get("accessibility", "N/A")
            ),

            "similarity": round(
                final_score,
                1
            )
        })

        if len(results) >= top_n:
            break

    return results

# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():

    interests = request.form.get(
        "interests",
        ""
    )

    duration = request.form.get(
        "duration",
        ""
    )

    accessibility = request.form.get(
        "accessibility",
        ""
    )

    recommendations = get_recommendations(
        interests,
        duration,
        accessibility
    )

    return render_template(
        "result.html",

        recommendations=recommendations,

        user_prefs={
            "interests": interests,
            "duration": duration,
            "accessibility": accessibility
        }
    )

# =========================================================
# RUN FLASK APP
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)