from . import gemini

def analyze_food_image(image, user_profile):
    prompt = f"""
    You are a nutritionist. Analyze the food in this image for a user with these details:
    - Age: {user_profile['age']}
    - Gender: {user_profile['gender']}
    - Weight: {user_profile['weight_kg']} kg
    - Height: {user_profile['height_cm']} cm
    - Medical conditions: {', '.join(user_profile['medical_conditions']) if user_profile['medical_conditions'] else 'none'}
    - Allergies: {', '.join(user_profile['allergies']) if user_profile['allergies'] else 'none'}
    - Dietary preference: {user_profile['dietary_preference']}
    - Gluten-free: {user_profile['gluten_free']}
    - Lactose intolerant: {user_profile['lactose_intolerant']}

    Please provide:
    - The most likely food(s) in the image
    - Estimated portion size (e.g., grams, pieces, cups, etc.)
    - Estimated total calories
    - Estimated macronutrients (carbs, protein, fat in grams)
    - Any warnings or notes based on the user's medical conditions, allergies, or dietary restrictions
    - Output in a clear, readable format
    """
    return gemini.generate_vision(prompt, image) 