import streamlit as st
st.set_page_config(page_title="AI Health & Nutrition Assistant", layout="wide", initial_sidebar_state="expanded")
import backend.user_profile as user_profile_mod
import backend.calculations as calc
import backend.meal_plan as meal_plan_mod
import backend.food_analysis as food_analysis
import pandas as pd
from datetime import date, datetime
import backend.gemini as gemini
import backend.image_analysis as image_analysis
from PIL import Image
import io
import altair as alt
import backend.database as db
import os

# Initialize session state for current page at the very top
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "🏠 Home"

# Initialize the database
db.init_db()

# Add at the top, after imports and session_state initializations
if 'show_auth' not in st.session_state:
    st.session_state['show_auth'] = False

# --- Authentication Page ---
def show_auth_page():
    st.markdown("""
        <style>
        .auth-container {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            border-radius: 15px;
            padding: 2em 2em 1.5em 2em;
            box-shadow: 0 4px 15px rgba(0,0,0,0.07);
            max-width: 400px;
            margin: 4em auto 2em auto;
        }
        .auth-title {
            color: #4facfe;
            font-size: 2em;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.5em;
        }
        .auth-switch {
            color: #636e72;
            text-align: center;
            margin-top: 1em;
        }
        .auth-switch a {
            color: #4facfe;
            font-weight: 600;
            cursor: pointer;
            text-decoration: underline;
        }
        </style>
    """, unsafe_allow_html=True)
    if 'auth_mode' not in st.session_state:
        st.session_state['auth_mode'] = 'login'
    if 'auth_error' not in st.session_state:
        st.session_state['auth_error'] = ''
    if 'auth_success' not in st.session_state:
        st.session_state['auth_success'] = ''
    with st.container():
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        if st.session_state['auth_mode'] == 'login':
            st.markdown('<div class="auth-title">Sign In</div>', unsafe_allow_html=True)
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                login_btn = st.form_submit_button("Sign In", use_container_width=True)
            if login_btn:
                user_id = db.authenticate_user(email, password)
                if user_id:
                    st.session_state['user_id'] = user_id
                    st.session_state['auth_error'] = ''
                    st.session_state['auth_success'] = 'Login successful!'
                    st.session_state['current_page'] = '👤 User Profile'
                    st.session_state['show_auth'] = False
                    st.rerun()
                else:
                    st.session_state['auth_error'] = 'Invalid email or password.'
            if st.session_state['auth_error']:
                st.error(st.session_state['auth_error'])
            if st.session_state['auth_success']:
                st.success(st.session_state['auth_success'])
            st.markdown('<div class="auth-switch">Don\'t have an account? <a href="#" onclick="window.location.reload();">Sign up</a></div>', unsafe_allow_html=True)
            if st.button("Switch to Sign Up", key="switch_to_signup"):
                st.session_state['auth_mode'] = 'signup'
                st.session_state['auth_error'] = ''
                st.session_state['auth_success'] = ''
                st.rerun()
        else:
            st.markdown('<div class="auth-title">Sign Up</div>', unsafe_allow_html=True)
            with st.form("signup_form"):
                email = st.text_input("Email", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_password")
                confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
                signup_btn = st.form_submit_button("Sign Up", use_container_width=True)
            if signup_btn:
                if password != confirm_password:
                    st.session_state['auth_error'] = 'Passwords do not match.'
                elif not email or not password:
                    st.session_state['auth_error'] = 'Email and password are required.'
                else:
                    success = db.register_user(email, password)
                    if success:
                        st.session_state['auth_error'] = ''
                        st.session_state['auth_success'] = 'Account created! Please sign in.'
                        st.session_state['auth_mode'] = 'login'
                        st.session_state['current_page'] = '👤 User Profile'
                        st.session_state['show_auth'] = False
                        st.rerun()
                    else:
                        st.session_state['auth_error'] = 'Email already registered.'
            if st.session_state['auth_error']:
                st.error(st.session_state['auth_error'])
            if st.session_state['auth_success']:
                st.success(st.session_state['auth_success'])
            st.markdown('<div class="auth-switch">Already have an account? <a href="#" onclick="window.location.reload();">Sign in</a></div>', unsafe_allow_html=True)
            if st.button("Switch to Sign In", key="switch_to_login"):
                st.session_state['auth_mode'] = 'login'
                st.session_state['auth_error'] = ''
                st.session_state['auth_success'] = ''
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
# Show auth page if show_auth is True and user is not logged in (must be after function definition)
if st.session_state.get('show_auth', False) and 'user_id' not in st.session_state:
    show_auth_page()
    st.stop()

# --- Block access to app until login ---
# Only show auth page if user tries to access a protected page and is not logged in
protected_pages = ["👤 User Profile", "🍽️ Meal Plan Generator", "🥗 Food Analysis", "📊 Tracking & Analytics", "💡 Recommendations", "🤖 AI Chat Coach", "🍲 AI Meal & Recipe Suggestion", "🏋️ Home Workout Suggestion", "⭐ Favorite Recipes"]
if st.session_state["current_page"] in protected_pages and 'user_id' not in st.session_state:
    show_auth_page()
    st.stop()

# Show logout button in sidebar after login
if 'user_id' in st.session_state:
    with st.sidebar:
        st.markdown("<div style='margin-bottom:1em;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ("auth_mode", "auth_error", "auth_success"):
                    del st.session_state[key]
            st.rerun()

# Enhanced modern UI with improved color scheme and animations
st.markdown("""
    <style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
    }
    
    /* Card-like containers */
    .stForm, div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.5em;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stForm:hover, div[data-testid="stExpander"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border-radius: 10px;
        font-weight: 600;
        border: none;
        padding: 0.7em 1.5em;
        margin-top: 0.5em;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(79,172,254,0.2);
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(79,172,254,0.3);
    }
    
    /* Input fields styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        padding: 0.5em 1em;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
        border-color: #4facfe;
        box-shadow: 0 0 0 2px rgba(79,172,254,0.2);
    }
    
    /* Radio buttons styling */
    div[role="radiogroup"] > label {
        background: #fff;
        border-radius: 10px;
        margin-bottom: 8px;
        padding: 10px 15px;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    div[role="radiogroup"] > label[data-selected="true"] {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white !important;
        box-shadow: 0 2px 8px rgba(79,172,254,0.2);
        border: none;
    }
    
    /* Headers styling */
    h1, h2, h3 {
        color: #2d3748;
        font-weight: 600;
    }
    
    /* Success message styling */
    .stSuccess {
        background: linear-gradient(90deg, #00b09b 0%, #96c93d 100%);
        color: white;
        padding: 1em;
        border-radius: 10px;
        margin: 1em 0;
    }
    
    /* Warning message styling */
    .stWarning {
        background: linear-gradient(90deg, #f6d365 0%, #fda085 100%);
        color: white;
        padding: 1em;
        border-radius: 10px;
        margin: 1em 0;
    }
    
    /* Custom container for health metrics */
    .health-metrics {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 15px;
        padding: 1.5em;
        margin: 1em 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    /* Custom container for meal plan */
    .meal-plan-container {
        background: white;
        border-radius: 15px;
        padding: 1.5em;
        margin: 1em 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# Change the app title in the top left
st.markdown("<h2 style='font-weight:700; margin-bottom:0.5em;'>Fitbot</h2>", unsafe_allow_html=True)

# On app start, always show Home page first
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "🏠 Home"

# Initialize session state for favorites if not exists
if "favorite_recipes" not in st.session_state:
    st.session_state.favorite_recipes = []

# Add to menu
menu = [
    "🏠 Home",
    "👤 User Profile",
    "🍽️ Meal Plan Generator",
    "🥗 Food Analysis",
    "📊 Tracking & Analytics",
    "💡 Recommendations",
    "🤖 AI Chat Coach",
    "🍲 AI Meal & Recipe Suggestion",
    "🏋️ Home Workout Suggestion",
    "⭐ Favorite Recipes"  # New menu item
]

# If on Home, show centered navigation and skip sidebar
if st.session_state["current_page"] == "🏠 Home":
    st.markdown(
        """
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:70vh; text-align:center;">
            <h1 style="color:#4facfe; font-size:3.5em; margin-bottom:0.2em; background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AI Health & Nutrition Assistant</h1>
            <p style="font-size:1.4em; color:#4a5568; margin-bottom:2em; max-width:600px;">Your personal AI-powered health companion for better nutrition, meal planning, and wellness tracking.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Add sign in/up prompt if not logged in
    if 'user_id' not in st.session_state:
        # Use Streamlit container for the welcome box
        with st.container():
            st.markdown("""
                <div style='background: linear-gradient(90deg, #f8fafc 0%, #e0eafc 100%); border-radius: 18px; padding: 2.2em 2.5em 1.5em 2.5em; margin-bottom: 1.5em; border: 1.5px solid #b2e0f7; text-align:center; box-shadow: 0 2px 12px rgba(79,172,254,0.07);'>
                    <div style='font-size:1.25em; color:#222; font-weight:600; margin-bottom:0.2em;'>Welcome to Fitbot.</div>
                    <div style='font-size:1.08em; color:#444; margin-bottom:1.1em;'>Sign in to unlock personalized plans, smart tracking, and real results.</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("""
                <style>
                div[data-testid="stButton"] button.fitbot-small-btn {
                    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%) !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 18px !important;
                    padding: 0.3em 1.1em !important;
                    font-size: 0.95em !important;
                    font-weight: 600 !important;
                    cursor: pointer !important;
                    box-shadow: 0 2px 8px rgba(79,172,254,0.13) !important;
                    transition: background 0.3s !important;
                    margin-top: 0.2em !important;
                }
                div[data-testid="stButton"] button.fitbot-small-btn:hover {
                    background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%) !important;
                }
                </style>
            """, unsafe_allow_html=True)
            # Place the button visually inside the welcome box
            btn_clicked = st.button("Sign In to Get Started", key="home_auth_btn", help="Access personalized features", use_container_width=False)
            if btn_clicked:
                st.session_state['show_auth'] = True
                st.rerun()
            # Inject class for the button
            st.markdown("""
                <script>
                const btns = window.parent.document.querySelectorAll('button[kind="secondary"]');
                btns.forEach(btn => { if(btn.innerText.includes('Sign In to Get Started')) btn.classList.add('fitbot-small-btn'); });
                </script>
            """, unsafe_allow_html=True)
    # Create a grid layout for navigation buttons
    cols = st.columns(3)
    for i, page in enumerate(menu[1:]):  # skip Home itself
        with cols[i % 3]:
            if st.button(page, key=f"home_{page}", use_container_width=True):
                st.session_state["current_page"] = page
                st.rerun()
    st.stop()

# Show auth page if show_auth is True and user is not logged in
if st.session_state.get('show_auth', False) and 'user_id' not in st.session_state:
    show_auth_page()
    st.stop()

# --- Sidebar for all other pages ---
choice = st.sidebar.radio("Navigation", menu, index=menu.index(st.session_state["current_page"]), key="unique_key_1")
if choice != st.session_state["current_page"]:
    st.session_state["current_page"] = choice
    st.rerun()

choice_clean = st.session_state["current_page"].split(" ", 1)[1]
st.markdown(f"## {st.session_state['current_page']}")

user_id = st.session_state['user_id']

if choice_clean == "User Profile":
    st.markdown("### 👤 User Profile", unsafe_allow_html=True)
    
    # Get existing profile from database
    profile_defaults = db.get_user_profile(user_id)
    
    with st.form("user_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input(
                "Age", min_value=1.0, max_value=120.0,
                value=float(profile_defaults.get('age')) if profile_defaults and profile_defaults.get('age') is not None else 30.0
            )
            height_cm = st.number_input(
                "Height (cm)", min_value=100.0, max_value=250.0,
                value=float(profile_defaults.get('height_cm')) if profile_defaults and profile_defaults.get('height_cm') is not None else 170.0
            )
            weight_kg = st.number_input(
                "Weight (kg)", min_value=30.0, max_value=250.0,
                value=float(profile_defaults.get('weight_kg')) if profile_defaults and profile_defaults.get('weight_kg') is not None else 70.0
            )
            activity_level = st.selectbox(
                "Daily activity level", ["low", "medium", "high"],
                index=["low", "medium", "high"].index(profile_defaults.get('activity_level', "low")) if profile_defaults and profile_defaults.get('activity_level') is not None else 0
            )
            diet_pref = st.selectbox(
                "Dietary preference", ["veg", "non-veg", "vegan"],
                index=["veg", "non-veg", "vegan"].index(profile_defaults.get('diet_pref', "veg")) if profile_defaults and profile_defaults.get('diet_pref') is not None else 0
            )
        
        with col2:
            gender = st.selectbox(
                "Gender", ["M", "F", "Other"],
                index=["M", "F", "Other"].index(profile_defaults.get('gender', "M")) if profile_defaults and profile_defaults.get('gender') is not None else 0
            )
            med_conditions = st.text_input(
                "Medical conditions (comma separated) or 'none'",
                profile_defaults.get('med_conditions', "none") if profile_defaults and profile_defaults.get('med_conditions') is not None else "none"
            )
            allergies = st.text_input(
                "Allergies (comma separated) or 'none'",
                profile_defaults.get('allergies', "none") if profile_defaults and profile_defaults.get('allergies') is not None else "none"
            )
            sleep_hours = st.number_input(
                "Average sleep hours per night", min_value=0.0, max_value=24.0,
                value=float(profile_defaults.get('sleep_hours')) if profile_defaults and profile_defaults.get('sleep_hours') is not None else 7.0
            )
        
        st.markdown("### Dietary Restrictions")
        col3, col4 = st.columns(2)
        with col3:
            gluten_free = st.checkbox(
                "Gluten-free?", value=bool(profile_defaults.get('gluten_free', False)) if profile_defaults and profile_defaults.get('gluten_free') is not None else False
            )
        with col4:
            lactose_intol = st.checkbox(
                "Lactose intolerant?", value=bool(profile_defaults.get('lactose_intol', False)) if profile_defaults and profile_defaults.get('lactose_intol') is not None else False
            )
        
        st.markdown("### Goals")
        col5, col6 = st.columns(2)
        with col5:
            goal = st.selectbox(
                "Goal", ["Weight Loss", "Weight Gain", "Maintain"],
                index=["Weight Loss", "Weight Gain", "Maintain"].index(profile_defaults.get('goal', "Weight Loss")) if profile_defaults and profile_defaults.get('goal') is not None else 0
            )
        with col6:
            target_weight = st.number_input(
                "Target weight (kg)", min_value=30.0, max_value=250.0,
                value=float(profile_defaults.get('target_weight')) if profile_defaults and profile_defaults.get('target_weight') is not None else 65.0
            )
        
        target_duration = st.number_input(
            "Target duration (weeks)", min_value=1.0, max_value=104.0,
            value=float(profile_defaults.get('target_duration')) if profile_defaults and profile_defaults.get('target_duration') is not None else 12.0
        )
        
        submitted = st.form_submit_button("Save Profile", use_container_width=True)
    if submitted:
        profile = user_profile_mod.get_user_profile(
            age, gender, height_cm, weight_kg, med_conditions, allergies, sleep_hours,
            activity_level, diet_pref, gluten_free, lactose_intol, goal, target_weight, target_duration
        )
        
        # Save to database
        user_data = {
            'age': age,
            'gender': gender,
            'height_cm': height_cm,
            'weight_kg': weight_kg,
            'med_conditions': med_conditions,
            'allergies': allergies,
            'sleep_hours': sleep_hours,
            'activity_level': activity_level,
            'diet_pref': diet_pref,
            'gluten_free': gluten_free,
            'lactose_intol': lactose_intol,
            'goal': goal,
            'target_weight': target_weight,
            'target_duration': target_duration,
            'bmi': profile['bmi'],
            'bmi_status': profile['bmi_status']
        }
        db.save_user_profile(user_id, user_data)
        
        # --- Health Snapshot Calculation ---
        ideal_weight_range = calc.calculate_ideal_weight_range(height_cm)
        ideal_calorie_range = calc.calculate_calorie_range(profile, ideal_weight_range)
        calorie_target = calc.get_calorie_target(profile, ideal_calorie_range)

        st.markdown(
            f"""
            <div style="background: #e3f6fc; border-radius: 12px; padding: 1.5em; margin-bottom: 1em; border: 1.5px solid #b2e0f7;">
                <h3 style="color:#2193b0; margin-top:0;">🩺 Health Snapshot</h3>
                <ul style="list-style:none; padding-left:0;">
                    <li><b>🧮 BMI:</b> <span style="color:#2d3436;">{profile['bmi']} <i>({profile['bmi_status']})</i></span></li>
                    <li><b>⚖️ Ideal Weight Range:</b> <span style="color:#2d3436;">{ideal_weight_range[0]:.1f}–{ideal_weight_range[1]:.1f} kg</span></li>
                    <li><b>🔥 Calorie Needs for Ideal BMI ({activity_level} activity):</b> <span style="color:#2d3436;">{ideal_calorie_range[0]:.0f}–{ideal_calorie_range[1]:.0f} kcal/day</span></li>
                    <li><b>🎯 Current Goal:</b> <span style="color:#2d3436;">{goal}</span></li>
                    <li><b>🥗 Personalized Calorie Target:</b> <span style="color:#2d3436;">{calorie_target} kcal/day</span></li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

if choice_clean == "Meal Plan Generator":
    st.markdown("### 🍽️ Meal Plan Generator", unsafe_allow_html=True)
    # Subtle customization button (top-right)
    col_title, col_custom = st.columns([8, 1])
    with col_title:
        st.markdown("#### AI-Powered Weekly Meal Plan")
    with col_custom:
        if st.button("⚙️ Customize", key="customize_meal_plan", help="Customize meal timing and fasting options", use_container_width=True):
            st.session_state['show_customizer'] = not st.session_state.get('show_customizer', False)
    # Customization expander (not prominent)
    if st.session_state.get('show_customizer', False):
        with st.expander("Meal Plan Customization", expanded=True):
            fasting_option = st.radio(
                "Fasting/Meal Timing Option",
                ["None", "16:8 (12:00pm–8:00pm)", "18:6", "14:10", "OMAD (One Meal A Day)", "Custom"],
                key="fasting_option"
            )
            custom_start, custom_end = None, None
            if fasting_option == "Custom":
                custom_start = st.time_input("Start Time", key="custom_start_time")
                custom_end = st.time_input("End Time", key="custom_end_time")
            apply_to = st.radio("Apply To", ["Today", "Entire Week"], key="apply_to")
            col_apply, col_save, col_cancel = st.columns(3)
            with col_apply:
                if st.button("Apply", key="apply_custom_meal_plan"):
                    st.session_state['custom_meal_plan'] = {
                        'fasting_option': fasting_option,
                        'custom_start': str(custom_start) if custom_start else None,
                        'custom_end': str(custom_end) if custom_end else None,
                        'apply_to': apply_to
                    }
                    st.session_state['show_customizer'] = False
                    st.success("Customization applied!")
            with col_save:
                if st.button("Save", key="save_custom_meal_plan"):
                    st.session_state['custom_meal_plan'] = {
                        'fasting_option': fasting_option,
                        'custom_start': str(custom_start) if custom_start else None,
                        'custom_end': str(custom_end) if custom_end else None,
                        'apply_to': apply_to
                    }
                    st.session_state['show_customizer'] = False
                    st.success("Customization saved!")
            with col_cancel:
                if st.button("Cancel", key="cancel_custom_meal_plan"):
                    st.session_state['show_customizer'] = False
    # Create tabs for generating new plan and viewing saved plans
    tab1, tab2 = st.tabs(["Generate New Plan", "View Saved Plans"])
    
    with tab1:
        profile = db.get_user_profile(user_id)
        if profile:
            ideal_weight_range = calc.calculate_ideal_weight_range(profile['height_cm'])
            ideal_calorie_range = calc.calculate_calorie_range(profile, ideal_weight_range)
            calorie_target = calc.get_calorie_target(profile, ideal_calorie_range)
            macros = calc.get_macros(calorie_target)
            st.markdown(f"**Ideal Weight Range:** {ideal_weight_range[0]}–{ideal_weight_range[1]} kg")
            st.markdown(f"**Calorie Needs for Ideal BMI:** {ideal_calorie_range[0]}–{ideal_calorie_range[1]} kcal/day")
            st.markdown(f"**Personalized Calorie Target:** {calorie_target} kcal/day")
            st.markdown(f"**Macros:** {macros['carbs_g']}g carbs, {macros['protein_g']}g protein, {macros['fat_g']}g fat")
            st.markdown("---")
            # Pass customization to meal plan generator if set
            custom_plan = st.session_state.get('custom_meal_plan', None)
            if st.button("Generate New Meal Plan"):
                with st.spinner("Generating your personalized meal plan..."):
                    meal_plan = meal_plan_mod.generate_weekly_meal_plan(profile, calorie_target, macros, custom_plan)
                    st.write(meal_plan)
        else:
            st.warning("Please fill out your User Profile first!")
    
    with tab2:
        st.markdown("### 📋 Saved Meal Plans")
        saved_plans = meal_plan_mod.get_saved_meal_plans()
        
        if not saved_plans:
            st.info("No saved meal plans found. Generate a new plan to get started!")
        else:
            for plan in saved_plans:
                plan_time = datetime.fromisoformat(plan['timestamp']).strftime('%B %d, %Y %H:%M')
                with st.expander(f"Meal Plan from {plan_time}"):
                    st.markdown("#### Meal Plan")
                    st.write(plan['meal_plan'])
                    st.markdown("#### Nutrition Targets")
                    st.markdown(f"**Calorie Target:** {plan['calorie_target']} kcal/day")
                    st.markdown(f"**Macros:** {plan['macros']['carbs_g']}g carbs, {plan['macros']['protein_g']}g protein, {plan['macros']['fat_g']}g fat")
                    # Add delete button
                    plan_filename = f"data/meal_plans/meal_plan_{datetime.fromisoformat(plan['timestamp']).strftime('%Y%m%d_%H%M%S')}.json"
                    if st.button("🗑️ Delete Plan", key=f"delete_{plan['timestamp']}"):
                        if os.path.exists(plan_filename):
                            os.remove(plan_filename)
                            st.success("Meal plan deleted.")
                            st.rerun()

if choice_clean == "Food Analysis":
    st.markdown("### 🥗 Food Analysis", unsafe_allow_html=True)
    profile = db.get_user_profile(user_id)
    if profile:
        # --- Text/Ingredient Analysis Form ---
        with st.form("food_analysis_form"):
            food_name = st.text_input("Food name (e.g., 'roti', 'chicken breast')")
            ingredients = st.text_input("Ingredients (comma separated)")
            quantity = st.text_input("Quantity consumed (e.g., '2 pieces', '150 grams', '1 sandwich')")
            prep_method = st.text_input("Preparation method (e.g., 'grilled', 'fried', 'baked', or leave blank)")
            submitted = st.form_submit_button("Analyze Food")
        if submitted:
            user_profile = profile
            ingredient_list = [x.strip() for x in ingredients.split(",") if x.strip()]
            result = food_analysis.analyze_food_structured(food_name, ingredient_list, quantity, prep_method, user_profile)
            st.markdown("### Nutrition Analysis Result")
            st.write(result)

        # --- Image Analysis Form ---
        st.markdown("---")
        st.markdown("### 📷 Food Image Analysis")
        with st.form("image_analysis_form"):
            uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])
            img_submitted = st.form_submit_button("Analyze Image")
        if img_submitted and uploaded_file:
            user_profile = profile
            image = Image.open(uploaded_file)
            result = image_analysis.analyze_food_image(image, user_profile)
            st.markdown("### Nutrition Analysis Result from Image")
            st.write(result)
        elif img_submitted:
            st.warning("Please upload an image.")
    else:
        st.warning("Please fill out your User Profile first!")

if choice_clean == "Tracking & Analytics":
    st.markdown("### 📊 Tracking & Analytics", unsafe_allow_html=True)
    profile = db.get_user_profile(user_id)
    calorie_target = None
    if profile:
        ideal_weight_range = calc.calculate_ideal_weight_range(profile['height_cm'])
        ideal_calorie_range = calc.calculate_calorie_range(profile, ideal_weight_range)
        calorie_target = calc.get_calorie_target(profile, ideal_calorie_range)
        st.markdown(f"**Your Daily Calorie Target:** <span style='color:#4facfe;font-weight:600'>{calorie_target} kcal</span>", unsafe_allow_html=True)
    selected_date = st.date_input("Select Date", value=date.today(), key="track_date")
    st.markdown("#### Log a Meal for the Day")
    with st.form("meal_log_form_generic"):
        meal_desc = st.text_input("Meal Description", key="desc_generic")
        meal_cal = st.number_input("Estimated Calories", min_value=0.0, value=0.0, key="cal_generic")
        meal_submit = st.form_submit_button("Log Meal")
    if meal_submit:
        if not meal_desc.strip():
            st.warning("Please enter a meal description.")
        elif meal_cal <= 0:
            st.warning("Please enter a valid calorie value.")
        else:
            meal_data = {
                "date": str(selected_date),
                "meal_type": "Meal",
                "description": meal_desc,
                "calories": meal_cal
            }
            db.save_meal_log(user_id, meal_data)
            st.success("Meal logged!")
            st.rerun()
    # AI calorie estimation dialog
    with st.expander("Estimate Calories with AI", expanded=False):
        st.markdown("Enter details for AI calorie estimation:")
        ai_food_name = st.text_input("Food Name", key="ai_food_name")
        ai_prep_method = st.selectbox("Preparation Method", ["Not applied", "Baked", "Fried", "Grilled"], key="ai_prep_method")
        ai_ingredients = st.text_input("Ingredients (comma separated)", key="ai_ingredients")
        ai_quantity = st.text_input("Quantity Consumed (e.g., '2 pieces', '150 grams')", key="ai_quantity")
        if st.button("Estimate Calories", key="ai_estimate_btn"):
            ai_prompt = f"Estimate the calories for the following food:\nFood: {ai_food_name}\nPreparation: {ai_prep_method}\nIngredients: {ai_ingredients}\nQuantity: {ai_quantity}"
            ai_cal = gemini.generate_text(ai_prompt)
            st.info(f"AI Estimate: {ai_cal} kcal")
    st.markdown("#### Log Water Intake for the Day")
    with st.form("water_log_form"):
        water_ml = st.number_input("Water Intake (ml)", min_value=0.0, value=0.0, key="water_ml")
        water_submit = st.form_submit_button("Log Water Intake")
    if water_submit:
        if water_ml <= 0:
            st.warning("Please enter a valid water intake value.")
        else:
            water_data = {
                "date": str(selected_date),
                "ml": water_ml
            }
            db.save_water_log(user_id, water_data)
            st.success("Water intake logged!")
            st.rerun()
    st.markdown("---")
    st.markdown(f"### Meals for {selected_date}")
    meal_logs = [log for log in db.get_meal_logs(user_id) if log['date'] == str(selected_date)]
    if meal_logs:
        df_meals = pd.DataFrame(meal_logs)
        if 'description' in df_meals.columns and 'calories' in df_meals.columns:
            st.dataframe(df_meals[['description', 'calories']].rename(columns={'description': 'Description', 'calories': 'Calories'}))
            total_cal = df_meals['calories'].sum()
            st.markdown(f"**Total Calories Consumed:** <span style='color:#4facfe;font-weight:600'>{total_cal} kcal</span>", unsafe_allow_html=True)
            if calorie_target and total_cal > calorie_target:
                st.warning(f"You have exceeded your daily calorie target by {int(total_cal - calorie_target)} kcal!")
        else:
            st.info("No valid meal logs for this day.")
    else:
        st.info("No meals logged for this day.")

    st.markdown(f"### Water Intake for {selected_date}")
    water_logs = [log for log in db.get_water_logs(user_id) if log['date'] == str(selected_date)]
    if water_logs:
        total_water = sum([log['ml'] for log in water_logs if log.get('ml', 0) > 0])
        st.markdown(f"**Total Water Intake:** <span style='color:#4facfe;font-weight:600'>{total_water} ml</span>", unsafe_allow_html=True)
    else:
        st.info("No water intake logged for this day.")

    st.markdown(f"### Weight Log for {selected_date}")
    with st.form("weight_log_form"):
        weight_val = st.number_input("Weight (kg)", min_value=0.0, value=0.0, key="weight_val")
        weight_submit = st.form_submit_button("Log Weight")
    if weight_submit:
        if weight_val <= 0:
            st.warning("Please enter a valid weight value.")
        else:
            weight_data = {
                "date": str(selected_date),
                "weight": weight_val
            }
            db.save_weight_log(user_id, weight_data)
            st.success("Weight logged!")
            st.rerun()
    weight_logs = [log for log in db.get_weight_logs(user_id) if log['date'] == str(selected_date) and log.get('weight', 0) > 0]
    if weight_logs:
        df_weight = pd.DataFrame(weight_logs)
        st.dataframe(df_weight[['weight']].rename(columns={'weight': 'Weight (kg)'}))
    else:
        st.info("No weight logged for this day.")

if choice_clean == "Recommendations":
    st.markdown("### 💡 Recommendations", unsafe_allow_html=True)
    st.info("This page will provide personalized recommendations based on your logs and goals.")
    # Show most recent entries for demo
    if "meal_log" in st.session_state and st.session_state.meal_log:
        st.markdown("**Most Recent Meal:**")
        st.write(st.session_state.meal_log[-1])
    if "weight_log" in st.session_state and st.session_state.weight_log:
        st.markdown("**Most Recent Weight:**")
        st.write(st.session_state.weight_log[-1])
    if "water_log" in st.session_state and st.session_state.water_log:
        st.markdown("**Most Recent Water Intake:**")
        st.write(st.session_state.water_log[-1])

if choice_clean == "AI Chat Coach":
    st.markdown("### 🤖 AI Chat Coach", unsafe_allow_html=True)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    user_input = st.text_input("Ask your AI health coach a question:")
    if st.button("Send") and user_input:
        # Optionally, add more context from logs
        context = ""
        if "meal_log" in st.session_state and st.session_state.meal_log:
            context += f"\nRecent meal: {st.session_state.meal_log[-1]}"
        if "weight_log" in st.session_state and st.session_state.weight_log:
            context += f"\nRecent weight: {st.session_state.weight_log[-1]}"
        if "water_log" in st.session_state and st.session_state.water_log:
            context += f"\nRecent water: {st.session_state.water_log[-1]}"
        prompt = f"You are a friendly, expert AI health coach. {context}\nUser: {user_input}"
        ai_response = gemini.generate_text(prompt)
        st.session_state.chat_history.append((user_input, ai_response))
    st.markdown("---")
    for user, ai in st.session_state.chat_history[::-1]:
        st.markdown(f"**You:** {user}")
        st.markdown(f"**AI Coach:** {ai}")

if choice_clean == "AI Meal & Recipe Suggestion":
    st.markdown("### 🍲 AI Meal & Recipe Suggestion", unsafe_allow_html=True)
    profile = db.get_user_profile(user_id)
    if profile:
        st.markdown("#### 📝 Customize Your Suggestion")
        meal_type = st.selectbox(
            "🍽️ Meal Type",
            ["None", "Breakfast", "Lunch", "Dinner", "Snacks", "Dessert", "Smoothies/Drinks", "Pre/Post Workout", "Quick Meals (Under 15 mins)", "Meal Prep Friendly", "Kid-Friendly"]
        )
        diet_pref = st.selectbox(
            "🥗 Diet Preference",
            ["None", "Vegetarian", "Non-Vegetarian", "Vegan", "Keto", "Low-Carb", "High-Protein", "Gluten-Free", "Dairy-Free"]
        )
        cuisine_type = st.selectbox(
            "🧑‍🍳 Cuisine Type",
            ["None", "Indian", "Italian", "Mediterranean", "Asian", "American", "Middle Eastern", "Chinese", "Korean"]
        )
        prep_time = st.selectbox(
            "🕐 Prep Time",
            ["None", "Under 15 minutes", "Under 30 minutes", "30–60 minutes", "Over 1 hour"]
        )
        goal = st.selectbox(
            "🎯 Goal-Based",
            ["None", "Weight Loss", "Muscle Gain", "Maintenance", "Diabetic-Friendly", "Heart-Healthy"]
        )
        # --- Filter-based Suggestion Button ---
        if st.button("Get Meal & Recipe Suggestion"):
            filter_summary = ""
            if meal_type != "None":
                filter_summary += f"\nMeal Type: {meal_type}"
            if diet_pref != "None":
                filter_summary += f"\nDiet Preference: {diet_pref}"
            if cuisine_type != "None":
                filter_summary += f"\nCuisine Type: {cuisine_type}"
            if prep_time != "None":
                filter_summary += f"\nPrep Time: {prep_time}"
            if goal != "None":
                filter_summary += f"\nGoal: {goal}"
            prompt = (
                f"Suggest a healthy meal and recipe for this user profile: {profile}."
                f"{filter_summary}\nPlease include ingredients and preparation steps."
            )
            suggestion = gemini.generate_text(prompt)
            st.session_state['last_suggestion'] = suggestion
            st.session_state['last_filters'] = {
                "meal_type": meal_type,
                "diet_pref": diet_pref,
                "cuisine_type": cuisine_type,
                "prep_time": prep_time,
                "goal": goal
            }
            st.markdown("#### Suggested Meal & Recipe")
            st.write(suggestion)
        # Show Add to Favorites button if a suggestion exists
        if 'last_suggestion' in st.session_state:
            if st.button("⭐ Add to Favorites", key="add_filtered"):
                recipe_data = {
                    "title": f"{st.session_state['last_filters']['meal_type']} Recipe" if st.session_state['last_filters']['meal_type'] != "None" else "Custom Recipe",
                    "content": st.session_state['last_suggestion'],
                    "filters": st.session_state['last_filters']
                }
                db.save_favorite_recipe(user_id, recipe_data)
                st.success("Recipe added to favorites!")
                st.rerun()
        # --- Manual Recipe Request Interface ---
        st.markdown("""
            <div style="background: #f0f8ff; border-radius: 10px; padding: 1em; margin-top: 1.5em; margin-bottom: 0.5em;">
                <h4 style="color:#2193b0; margin-bottom:0.2em;">👋 Hey, what are you craving today?</h4>
                <span style="color:#636e72; font-style:italic;">"Good food is the foundation of genuine happiness." – Auguste Escoffier</span>
            </div>
        """, unsafe_allow_html=True)
        manual_query = st.text_input("Type any dish, ingredient, or craving and I'll suggest a recipe!", key="manual_recipe_query")
        if st.button("Get Recipe for Your Craving"):
            if manual_query.strip():
                prompt = (
                    f"User profile: {profile}.\n"
                    f"User is craving: {manual_query.strip()}.\n"
                    "Suggest a healthy, delicious recipe. Include ingredients and preparation steps."
                )
                suggestion = gemini.generate_text(prompt)
                st.session_state['manual_suggestion'] = suggestion
                st.session_state['manual_query'] = manual_query.strip()
                st.markdown("#### 🍽️ Recipe for Your Craving")
                st.write(suggestion)
            else:
                st.info("Please type what you're craving!")
        # Show Add to Favorites button for manual query if suggestion exists
        if 'manual_suggestion' in st.session_state:
            if st.button("⭐ Add to Favorites", key="add_manual"):
                recipe_data = {
                    "title": st.session_state['manual_query'],
                    "content": st.session_state['manual_suggestion'],
                    "filters": {
                        "meal_type": "Custom",
                        "diet_pref": "None",
                        "cuisine_type": "None",
                        "prep_time": "None",
                        "goal": "None"
                    },
                    "date_added": str(date.today())
                }
                db.save_favorite_recipe(user_id, recipe_data)
                st.success("Recipe added to favorites!")
                st.rerun()
    else:
        st.warning("Please fill out your User Profile first!")

if choice_clean == "Home Workout Suggestion":
    st.markdown("### 🏋️ Home Workout Suggestion", unsafe_allow_html=True)
    profile = db.get_user_profile(user_id)
    if profile:
        if st.button("Get Home Workout Suggestion"):
            prompt = (
                f"Suggest a home workout plan for this user profile: {profile}."
                " Please include exercises, sets, and reps."
            )
            suggestion = gemini.generate_text(prompt)
            st.markdown("#### Suggested Home Workout")
            st.write(suggestion)
    else:
        st.warning("Please fill out your User Profile first!")

# Add new section for Favorite Recipes
if choice_clean == "Favorite Recipes":
    st.markdown("### ⭐ Favorite Recipes", unsafe_allow_html=True)
    
    favorite_recipes = db.get_favorite_recipes(user_id)
    if not favorite_recipes:
        st.info("You haven't added any recipes to your favorites yet!")
    else:
        # Create tabs for different views
        tab1, tab2 = st.tabs(["📋 List View", "🎯 Grid View"])
        
        with tab1:
            for recipe in favorite_recipes:
                with st.expander(f"📖 {recipe['title']} (Added on {recipe['date_added']})"):
                    st.write(recipe['content'])
                    if st.button("🗑️ Delete Recipe", key=f"delete_{recipe['recipe_id']}"):
                        db.delete_favorite_recipe(user_id, recipe['recipe_id'])
                        st.rerun()
        
        with tab2:
            cols = st.columns(2)
            for idx, recipe in enumerate(favorite_recipes):
                with cols[idx % 2]:
                    st.markdown(f"""
                        <div style="background: white; border-radius: 10px; padding: 1em; margin: 1em 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <h4 style="color: #4facfe; margin-bottom: 0.5em;">{recipe['title']}</h4>
                            <p style="color: #666; font-size: 0.9em;">Added on {recipe['date_added']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.write(recipe['content'])
                    if st.button("🗑️ Delete Recipe", key=f"delete_grid_{recipe['recipe_id']}"):
                        db.delete_favorite_recipe(user_id, recipe['recipe_id'])
                        st.rerun() 