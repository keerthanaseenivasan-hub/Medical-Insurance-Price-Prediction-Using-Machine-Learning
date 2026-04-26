import json
from flask import Flask, render_template, request, redirect, session
import joblib
import pandas as pd
from flask import url_for
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session



app = Flask(__name__)
app.secret_key = "secret123"

# -----------------------------
# REGION MAP (STRING → NUMBER)
# -----------------------------
REGION_MAP = {
    "Ariyalur": 0, "Chengalpattu": 1, "Chennai": 2, "Coimbatore": 3,
    "Cuddalore": 4, "Dharmapuri": 5, "Dindigul": 6, "Erode": 7,
    "Kallakurichi": 8, "Kancheepuram": 9, "Karur": 10, "Krishnagiri": 11,
    "Madurai": 12, "Mayiladuthurai": 13, "Nagapattinam": 14,
    "Namakkal": 15, "Nilgiris": 16, "Perambalur": 17,
    "Pudukkottai": 18, "Ramanathapuram": 19, "Ranipet": 20,
    "Salem": 21, "Sivaganga": 22, "Tenkasi": 23,
    "Thanjavur": 24, "Theni": 25, "Thoothukudi": 26,
    "Tiruchirappalli": 27, "Tirunelveli": 28,
    "Tirupattur": 29, "Tiruppur": 30,
    "Tiruvallur": 31, "Tiruvannamalai": 32,
    "Tiruvarur": 33, "Vellore": 34,
    "Viluppuram": 35, "Virudhunagar": 36
}
# -----------------------------
# Insurance Company Details
# -----------------------------
INSURANCE_COMPANIES = [
    {
        "name": "Star Health Insurance",
        "website": "https://www.starhealth.in",
        "min_cover": 0,
        "max_cover": 500000
    },
    {
        "name": "HDFC ERGO Health Insurance",
        "website": "https://www.hdfcergo.com",
        "min_cover": 300000,
        "max_cover": 1000000
    },
    {
        "name": "ICICI Lombard Health Insurance",
        "website": "https://www.icicilombard.com",
        "min_cover": 200000,
        "max_cover": 800000
    },
    {
        "name": "New India Assurance",
        "website": "https://www.newindia.co.in",
        "min_cover": 100000,
        "max_cover": 700000
    },
    {
        "name": "Care Health Insurance",
        "website": "https://www.careinsurance.com",
        "min_cover": 400000,
        "max_cover": 1500000
    },
    {
        "name": "Bajaj Allianz Health Insurance",
        "website": "https://www.bajajallianz.com",
        "min_cover": 300000,
        "max_cover": 1200000
    },
    {
        "name": "Religare Health Insurance",
        "website": "https://www.religarehealthinsurance.com",
        "min_cover": 200000,
        "max_cover": 900000
    },
    {
        "name": "Max Bupa Health Insurance",
        "website": "https://www.maxbupa.com",
        "min_cover": 500000,
        "max_cover": 2000000
    }
]

def get_region(val):
    if val.isdigit():
        return int(val)
    return REGION_MAP.get(val, 0)

# -----------------------------
# Load trained models
# -----------------------------
rf_model = joblib.load("models/rf_model.pkl")
gb_model = joblib.load("models/gb_model.pkl")
cat_model = joblib.load("models/cat_model.pkl")

def format_inr(number):
    """
    Format number in Indian style with commas.
    Example: 1234567.00 → 12,34,567.00
    """
    # Round to 2 decimals
    number = round(number, 2)
    
    # Separate integer and decimal parts
    parts = f"{number:.2f}".split(".")
    integer_part = parts[0]
    decimal_part = parts[1]
    
    # If integer part is <=3 digits, no change
    if len(integer_part) <= 3:
        return integer_part + "." + decimal_part

    # Last 3 digits
    last_three = integer_part[-3:]
    rest = integer_part[:-3]
    
    # Split rest in 2 digits from right
    rest_parts = []
    while len(rest) > 2:
        rest_parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        rest_parts.insert(0, rest)
    
    formatted_integer = ",".join(rest_parts) + "," + last_three
    return formatted_integer + "." + decimal_part

# -----------------------------
# Page 1: Home / Select Algorithm
# -----------------------------
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE CREATE ----------
def create_db():
    conn = sqlite3.connect("users.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            password TEXT
        )
    """)
    conn.close()

create_db()


# ---------- HOME ----------
@app.route('/')
def home():
    return render_template("home.html")


# ---------- REGISTER ----------
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("users.db")
        conn.execute(
            "INSERT INTO users (username,email,password) VALUES (?,?,?)",
            (username,email,password)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("users.db")
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        ).fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return "Invalid Username or Password"

    return render_template("login.html")



# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template("index.html")

    return render_template("index.html")

@app.route('/select', methods=['POST'])
def select():
    session['algorithm'] = request.form['algorithm']
    session['insurance_type'] = request.form['insurance_type']
    return redirect('/user_details')

# -----------------------------
# Page 2: User Details
# -----------------------------
@app.route('/user_details', methods=['GET', 'POST'])
def user_details():
    if request.method == 'POST':

        insurance_type = request.form.get(
            'insurance_type',
            session.get('insurance_type')
        )
        session['insurance_type'] = insurance_type

        session['users'] = []

        if insurance_type == 'single':
            session['users'].append({
                'age': int(request.form['age']),
                'gender': request.form['gender'],
                'bmi': float(request.form['bmi']),
                'children': int(request.form['children']),
                'region': get_region(request.form['region']),
                'smoker': request.form['smoker']
            })

        elif insurance_type == 'family':
            count = int(request.form.get('family_count', 0))

            for i in range(1, count + 1):
                session['users'].append({
                    'age': int(request.form[f'age_{i}']),
                    'gender': request.form[f'gender_{i}'],
                    'bmi': float(request.form[f'bmi_{i}']),
                    'children': int(request.form[f'children_{i}']),
                    'region': get_region(request.form[f'region_{i}']),
                    'smoker': request.form[f'smoker_{i}']
                })

        return redirect(url_for('risk_factor'))

    return render_template(
        "user_details.html",
        region=REGION_MAP,
        session=session
    )

# -----------------------------
# Page 3: Risk Factor
# -----------------------------
@app.route('/risk_factor', methods=['GET', 'POST'])
def risk_factor():
    if request.method == 'POST':
        risk = 0
        risk += len(request.form.getlist('family_history')) * 5
        risk += len(request.form.getlist('current_history')) * 3

        if request.form['exercise'] == 'none':
            risk += 2
        if request.form['alcohol'] == 'high':
            risk += 2
        if request.form['location'] == 'urban':
            risk += 1

        session['risk_factor'] = risk
        return redirect('/final_result')

    return render_template("risk_factor.html")

# -----------------------------
# Page 4: Final Result
# -----------------------------
@app.route('/final_result')
def final_result():
    algo = session['algorithm']
    risk_factor = session['risk_factor']
    users = session['users']
    insurance_type = session['insurance_type']

    model = rf_model if algo == 'rf' else gb_model if algo == 'gb' else cat_model
    model_name = "Random Forest" if algo == 'rf' else "Gradient Boosting" if algo == 'gb' else "CatBoost"

    total_price = 0
    total_age = 0
    predicted_prices = []
    user_labels = []

    for idx, u in enumerate(users):
        gender = 1 if u['gender'] == 'male' else 0
        smoker = 1 if u['smoker'] == 'yes' else 0
        features = [[u['age'], gender, u['bmi'], u['children'], smoker, u['region']]]
        predicted = model.predict(features)[0]
        predicted_prices.append(predicted)
        user_labels.append(f"User {idx+1}")
        total_price += predicted
        total_age += u['age']

    avg_age = total_age / len(users)

    # -----------------------------
    # FRAUD DETECTION MODULE
    # -----------------------------
    fraud_score = 0
    if avg_age < 25 and risk_factor > 10:
        fraud_score += 40
    if insurance_type == "family" and len(users) >= 4 and risk_factor > 15:
        fraud_score += 30
    smoker_count = sum(1 for u in users if u['smoker'] == 'yes')
    if smoker_count == len(users):
        fraud_score += 20
    if insurance_type == "family":
        ages = [u['age'] for u in users]
        if max(ages) - min(ages) < 5:
            fraud_score += 20
    fraud_status = ("High Risk - Suspicious Application" if fraud_score >= 70
                    else "Medium Risk - Needs Verification" if fraud_score >= 40
                    else "Low Risk - Normal Application")

    # -----------------------------
    # SUM INSURED
    # -----------------------------
    base_sum = 500000 if insurance_type == 'single' else 800000
    sum_insured = base_sum + (risk_factor * 10000) + (avg_age * 5000)

    # -----------------------------
    # CLAIM PROBABILITY
    # -----------------------------
    claim_score = min(avg_age, 100)*0.4 + min(risk_factor, 20)*2 + (smoker_count/len(users))*20
    claim_probability = round(min(claim_score, 100))

    # -----------------------------
    # POLICY DURATION
    # -----------------------------
    if claim_probability <= 30:
        duration = "3 Years"
    elif claim_probability <= 60:
        duration = "2 Years"
    else:
        duration = "1 Year"

    # -----------------------------
    # PREMIUM
    # -----------------------------
    if risk_factor < 5:
        premium_rate = 0.03
        deductible = 5000
        co_payment = "10%"
        network = "Local hospitals"
        exclusions = "Cosmetic treatments"
    elif risk_factor <= 10:
        premium_rate = 0.05
        deductible = 10000
        co_payment = "10%"
        network = "State hospitals"
        exclusions = "Cosmetic & Dental"
    else:
        premium_rate = 0.08
        deductible = 15000
        co_payment = "5%"
        network = "All Network Hospitals"
        exclusions = "Minimal exclusions"

    premium = sum_insured * premium_rate
    final_price = total_price - (risk_factor * 50)

    # -----------------------------
    # Load algorithm metrics
    # -----------------------------
    with open("models/metrics.json") as f:
        metrics = json.load(f)
    algo_metrics = (metrics["Random Forest"] if algo == 'rf'
                    else metrics["Gradient Boosting"] if algo == 'gb'
                    else metrics["CatBoost"])

    # -----------------------------
    # Company Recommendation
    recommended_companies = []

    for company in INSURANCE_COMPANIES:
        if company["min_cover"] <= sum_insured <= company["max_cover"]:
            recommended_companies.append(company)

    # Show only top 3 companies
    recommended_companies = recommended_companies[:3]

    # -----------------------------
    user_labels = [f"User {i+1}" for i in range(len(users))]
    predicted_prices = [...]  # your predicted values
    user_risk_factors = [risk_factor for u in users]  # same for all or calculate per user
    user_ages = [u['age'] for u in users]
    user_regions = [u['region'] for u in users]
    user_smokers = [u['smoker'] for u in users]


    # Render final result
    # -----------------------------
    return render_template(
        "final_result.html",
        model_name=model_name,
        price=format_inr(final_price),
        fraud_score=fraud_score,
        fraud_status=fraud_status,
        sum_insured=format_inr(sum_insured),
        premium=format_inr(premium),
        deductible=format_inr(deductible),
        co_payment=co_payment,
        network_hospital=network,
        exclusions=exclusions,
        risk_factor=risk_factor,
        r2=algo_metrics["r2"],
        mae=algo_metrics["mae"],
        rmse=algo_metrics["rmse"],
        predicted_prices=predicted_prices,
        user_labels=user_labels,
        companies=recommended_companies,
        claim_probability=f"{claim_probability}%",
        duration=duration
    )
# -----------------------------
# Algorithm explanation page
# -----------------------------
@app.route('/algorithm_explanation')
def algorithm_explanation():
    return render_template("algorithm.html")

@app.route('/algorithm_performance')
def algorithm_performance():
    with open("models/metrics.json") as f:
        metrics = json.load(f)

    return render_template(
        "algorithm_performance.html",
        metrics=metrics
    )


# -----------------------------
# Metrics page (charts)
# -----------------------------
@app.route("/metrics")
def metrics_page():
    with open("models/metrics.json") as f:
        metrics = json.load(f)

    labels = ["R2", "MAE", "RMSE"]


    rf_values  = list(metrics["Random Forest"].values())
    gb_values  = list(metrics["Gradient Boosting"].values())
    cat_values = list(metrics["CatBoost"].values())

    return render_template(
        "metrics.html",
        labels=labels,
        rf=rf_values,
        gb=gb_values,
        cat=cat_values
    )

# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
