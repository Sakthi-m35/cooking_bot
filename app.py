import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()

SYSTEM_INSTRUCTION = """
You are Cooking Assistant, a strict domain-specific AI assistant.

YOUR ONLY ALLOWED DOMAIN:
Cooking and closely related food-preparation topics, including:
- recipes and cooking methods
- ingredients and ingredient substitutions
- meal planning and menu ideas
- baking, desserts, breads and pastry
- vegetarian, vegan and non-vegetarian cooking
- Indian, Tamil, South Indian and international cuisines
- spices, herbs, seasonings and flavor pairing
- kitchen techniques and equipment used for cooking
- preparation, marination, mixing, kneading, roasting, grilling, frying,
  steaming, boiling, baking, pressure cooking and slow cooking
- food storage and basic food-safety practices related to cooking
- cooking temperatures and doneness concepts
- portion scaling and recipe conversions
- cooking troubleshooting, such as why a cake sank or rice became sticky
- nutrition information only when directly connected to preparing or modifying food
- ingredient labels and common culinary terminology
- cooking academic/project questions.

STRICT DOMAIN RULE:
If the user's question is unrelated to cooking or closely related food
preparation, DO NOT answer it.

Reply exactly with:
"Sorry, I can only help with cooking and closely related food-preparation topics. Please ask a cooking question."

If the question is related to cooking, answer helpfully and accurately.
The user may ask in English, Tamil, Tanglish, or a mixture. Reply in the same
language/style when practical.

For recipes, give useful quantities, preparation steps, cooking method, approximate
time and serving size when enough information is available.
If an ingredient quantity is missing, make a reasonable culinary assumption and
state it clearly.
Do not invent product-specific facts.

FOOD SAFETY:
When relevant, mention practical food-safety precautions.
For severe allergies, medical conditions, infant feeding, or other high-stakes
health questions, do not present a cooking answer as medical advice. Keep the
response focused on safe food preparation and recommend professional advice when
appropriate.

Use headings, numbered steps, bullets and tables when useful.
"""

client = genai.Client(api_key=API_KEY) if API_KEY else None

NON_COOKING_KEYWORDS = {
    "python", "javascript", "java", "c++", "html", "css", "react",
    "flask", "django", "firebase", "sql", "programming", "coding",
    "football", "cricket", "movie", "music", "song", "gaming", "game",
    "politics", "stock market", "bitcoin", "cryptocurrency", "travel",
    "fashion", "relationship", "weather"
}

COOKING_KEYWORDS = {
    "cook", "cooking", "recipe", "recipes", "food", "dish", "meal", "breakfast",
    "lunch", "dinner", "snack", "dessert", "baking", "cake", "bread", "pizza",
    "pasta", "rice", "biryani", "sambar", "rasam", "idli", "dosa", "chapati",
    "roti", "curry", "gravy", "masala", "spice", "spices", "ingredient",
    "ingredients", "vegetarian", "vegan", "chicken", "mutton", "fish", "egg",
    "paneer", "tofu", "salad", "soup", "sauce", "chutney", "marinate",
    "marination", "fry", "fried", "roast", "grill", "steam", "boil", "bake",
    "pressure cook", "air fryer", "oven", "stove", "microwave", "kitchen",
    "substitute", "substitution", "calorie", "portion", "serving", "meal plan",
    "தமிழ்", "சமையல்", "சமைக்க", "சமையல் குறிப்பு", "சமையல் முறை",
    "உணவு", "சாப்பாடு", "காய்கறி", "மசாலா", "செய்முறை", "தேவையான பொருட்கள்",
    "அடுப்பு", "வறுக்க", "வேகவைக்க", "சுட", "இனிப்பு"
}

def obvious_domain_check(text: str):
    lowered = text.lower()
    if any(k in lowered for k in COOKING_KEYWORDS):
        return True
    if any(k in lowered for k in NON_COOKING_KEYWORDS):
        return False
    return None

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "gemini_configured": bool(API_KEY),
        "model": MODEL_NAME
    })

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please enter a cooking question."}), 400

    if len(message) > 5000:
        return jsonify({"error": "Please keep your question under 5000 characters."}), 400

    if not API_KEY or client is None:
        return jsonify({
            "error": "Gemini API key is not configured. Add GEMINI_API_KEY to your .env file."
        }), 500

    domain_check = obvious_domain_check(message)
    if domain_check is False:
        return jsonify({
            "answer": "Sorry, I can only help with cooking and closely related food-preparation topics. Please ask a cooking question.",
            "blocked": True
        })

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=1800,
            ),
        )

        answer = (response.text or "").strip()
        if not answer:
            answer = "I couldn't generate a response. Please try asking your cooking question again."

        return jsonify({"answer": answer, "blocked": False})

    except Exception as exc:
        app.logger.exception("Gemini API error")
        return jsonify({
            "error": "Unable to reach Gemini right now. Please check your API key, internet connection, and model availability.",
            "details": str(exc) if app.debug else None
        }), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
