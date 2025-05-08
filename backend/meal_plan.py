from . import gemini
import json
import os
from datetime import datetime

def save_meal_plan(meal_plan_data):
    """Save the meal plan to a JSON file."""
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Create meal_plans directory if it doesn't exist
    if not os.path.exists('data/meal_plans'):
        os.makedirs('data/meal_plans')
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data/meal_plans/meal_plan_{timestamp}.json'
    
    # Save the meal plan
    with open(filename, 'w') as f:
        json.dump(meal_plan_data, f, indent=4)
    
    return filename

def get_saved_meal_plans():
    """Retrieve all saved meal plans."""
    if not os.path.exists('data/meal_plans'):
        return []
    
    meal_plans = []
    for filename in os.listdir('data/meal_plans'):
        if filename.endswith('.json'):
            with open(f'data/meal_plans/{filename}', 'r') as f:
                meal_plan = json.load(f)
                meal_plans.append(meal_plan)
    
    return sorted(meal_plans, key=lambda x: x['timestamp'], reverse=True)

def generate_weekly_meal_plan(user_profile, calorie_target, macros, custom_plan=None):
    """Generate a weekly meal plan based on user profile and targets, with optional customization."""
    custom_text = ""
    if custom_plan:
        if custom_plan.get('fasting_option') and custom_plan['fasting_option'] != 'None':
            custom_text += f"\nFasting/Meal Timing: {custom_plan['fasting_option']}"
        if custom_plan.get('fasting_option') == 'Custom' and custom_plan.get('custom_start') and custom_plan.get('custom_end'):
            custom_text += f" (Custom Time Range: {custom_plan['custom_start']} to {custom_plan['custom_end']})"
        if custom_plan.get('apply_to'):
            custom_text += f"\nApply to: {custom_plan['apply_to']}"
    prompt = f"""
    Generate a detailed weekly meal plan for a user with the following profile:
    - Age: {user_profile['age']}
    - Gender: {user_profile['gender']}
    - Height: {user_profile['height_cm']} cm
    - Weight: {user_profile['weight_kg']} kg
    - Activity Level: {user_profile['activity_level']}
    - Dietary preference: {user_profile['diet_pref']}
    - Gluten-free: {user_profile['gluten_free']}
    - Lactose intolerant: {user_profile['lactose_intol']}
    - Goal: {user_profile['goal']}
    - Target weight: {user_profile['target_weight']} kg
    - Target duration: {user_profile['target_duration']} weeks
    {custom_text}

    Daily calorie target: {calorie_target} kcal
    Daily macronutrient targets:
    - Protein: {macros['protein_g']}g
    - Carbs: {macros['carbs_g']}g
    - Fat: {macros['fat_g']}g

    Please provide a detailed meal plan for each day of the week, including:
    1. Breakfast
    2. Morning Snack
    3. Lunch
    4. Evening Snack
    5. Dinner

    For each meal, include:
    - Meal name
    - Ingredients and quantities
    - Preparation instructions
    - Estimated calories and macros
    - Any special notes or modifications

    If fasting or custom meal timing is specified, ensure all meals fit within the allowed eating window.

    After the meal plan, provide a comprehensive grocery list for the entire week, organized by categories:
    - Produce (fruits and vegetables)
    - Proteins (meat, fish, poultry, plant-based proteins)
    - Dairy and Alternatives
    - Grains and Bread
    - Pantry Items (spices, oils, condiments)
    - Snacks and Treats
    - Beverages

    For each item in the grocery list, include:
    - Item name
    - Quantity needed
    - Any specific notes (e.g., "organic preferred", "fresh")

    Format the response in a clear, structured way that's easy to follow.
    """
    meal_plan_text = gemini.generate_text(prompt)
    # Save the meal plan as before
    meal_plan_data = {
        'timestamp': datetime.now().isoformat(),
        'user_profile': user_profile,
        'calorie_target': calorie_target,
        'macros': macros,
        'custom_plan': custom_plan,
        'meal_plan': meal_plan_text
    }
    save_meal_plan(meal_plan_data)
    return meal_plan_text 