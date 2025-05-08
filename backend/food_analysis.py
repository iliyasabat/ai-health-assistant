from . import gemini

def analyze_food_structured(food_name, ingredient_list, quantity, prep_method, user_profile):
    prompt = f"""
    You are a nutritionist. Analyze the following food input for a user with these details:
    - Age: {user_profile['age']}
    - Gender: {user_profile['gender']}
    - Weight: {user_profile['weight_kg']} kg
    - Height: {user_profile['height_cm']} cm
    - Medical conditions: {', '.join(user_profile['medical_conditions']) if user_profile['medical_conditions'] else 'none'}
    - Allergies: {', '.join(user_profile['allergies']) if user_profile['allergies'] else 'none'}
    - Dietary preference: {user_profile['dietary_preference']}
    - Gluten-free: {user_profile['gluten_free']}
    - Lactose intolerant: {user_profile['lactose_intolerant']}

    Food details:
    - Food name: {food_name}
    - Quantity consumed: {quantity}
    - Preparation method: {prep_method if prep_method else 'Not specified'}
    - Ingredients: {', '.join(ingredient_list)}

    Please provide:
    - Estimated total calories
    - Estimated macronutrients (carbs, protein, fat in grams)
    - Any warnings or notes based on the user's medical conditions or allergies
    - Output in a clear, readable format
    """
    return gemini.generate_text(prompt) 