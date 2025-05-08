def interpret_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def get_user_profile(
    age, gender, height_cm, weight_kg, med_conditions, allergies, sleep_hours,
    activity_level, diet_pref, gluten_free, lactose_intol, goal, target_weight, target_duration
):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    bmi_status = interpret_bmi(bmi)
    user_profile = {
        "age": age,
        "gender": gender,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "medical_conditions": [x.strip() for x in med_conditions.split(",")] if med_conditions.lower() != "none" else [],
        "allergies": [x.strip() for x in allergies.split(",")] if allergies.lower() != "none" else [],
        "sleep_hours": sleep_hours,
        "activity_level": activity_level,
        "dietary_preference": diet_pref,
        "gluten_free": gluten_free,
        "lactose_intolerant": lactose_intol,
        "goal": goal,
        "target_weight": target_weight,
        "target_duration_weeks": target_duration,
        "bmi": round(bmi, 2),
        "bmi_status": bmi_status
    }
    return user_profile 