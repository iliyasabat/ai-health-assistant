def calculate_ideal_weight_range(height_cm):
    height_m = height_cm / 100
    min_weight = 18.5 * (height_m ** 2)
    max_weight = 24.9 * (height_m ** 2)
    return (round(min_weight, 1), round(max_weight, 1))

def calculate_bmr(user_profile):
    weight = user_profile['weight_kg']
    height = user_profile['height_cm']
    age = user_profile['age']
    gender = user_profile['gender'].lower()
    if gender == 'm':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr

def get_activity_factor(activity_level):
    if activity_level == 'low':
        return 1.2
    elif activity_level == 'medium':
        return 1.55
    elif activity_level == 'high':
        return 1.725
    else:
        return 1.2  # default

def calculate_calorie_range(user_profile, ideal_weight_range):
    activity_factor = get_activity_factor(user_profile['activity_level'].lower())
    min_bmr = calculate_bmr({**user_profile, 'weight_kg': ideal_weight_range[0]})
    max_bmr = calculate_bmr({**user_profile, 'weight_kg': ideal_weight_range[1]})
    min_cal = int(min_bmr * activity_factor)
    max_cal = int(max_bmr * activity_factor)
    return (min_cal, max_cal)

def get_calorie_target(user_profile, calorie_range):
    if user_profile['goal'].lower() == 'weight loss':
        return calorie_range[0] - 500  # 500 kcal deficit
    elif user_profile['goal'].lower() == 'weight gain':
        return calorie_range[1] + 300  # 300 kcal surplus
    else:
        return int(sum(calorie_range) / 2)  # maintenance

def get_macros(calorie_target):
    # Example: 50% carbs, 20% protein, 30% fat
    carbs = int(0.5 * calorie_target / 4)
    protein = int(0.2 * calorie_target / 4)
    fat = int(0.3 * calorie_target / 9)
    return {'carbs_g': carbs, 'protein_g': protein, 'fat_g': fat} 