import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from catboost import CatBoostRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json

# ---------------------------
# Load dataset
# ---------------------------
df = pd.read_csv("dataset.csv")

# Encode categorical variables
df['gender'] = LabelEncoder().fit_transform(df['gender'])
df['smoker'] = LabelEncoder().fit_transform(df['smoker'])
df['region'] = LabelEncoder().fit_transform(df['region'])

# ---------------------------
# Features & target (REGRESSION)
# ---------------------------
X = df.drop(columns=['insurance_price'])
y = df['insurance_price']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------------------
# Train model function (REGRESSION METRICS)
# ---------------------------
def train_model(model, name, filename_prefix):

    model.fit(X_train, y_train)
    joblib.dump(model, f"models/{filename_prefix}_model.pkl")

    # Feature importance
    plt.figure(figsize=(8,6))
    if hasattr(model, "feature_importances_"):
        sns.barplot(x=model.feature_importances_, y=X.columns)
    elif hasattr(model, "get_feature_importance"):
        sns.barplot(x=model.get_feature_importance(), y=X.columns)

    plt.title(f"{name} Feature Importance")
    plt.tight_layout()
    plt.savefig(f"static/{filename_prefix}_features.png")
    plt.close()

    # Predictions
    y_pred = model.predict(X_test)

    # REGRESSION METRICS
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(f"\n------ {name} ------")
    print("R2   :", round(r2, 3))
    print("MAE  :", round(mae, 2))
    print("RMSE :", round(rmse, 2))

    return {
        "r2": round(float(r2), 3),
        "mae": round(float(mae), 2),
        "rmse": round(float(rmse), 2)
    }

# ---------------------------
# Train all models
# ---------------------------
rf_metrics = train_model(
    RandomForestRegressor(n_estimators=200, random_state=42),
    "Random Forest",
    "rf"
)

gb_metrics = train_model(
    GradientBoostingRegressor(n_estimators=200, random_state=42),
    "Gradient Boosting",
    "gb"
)

cat_metrics = train_model(
    CatBoostRegressor(iterations=500, learning_rate=0.1, verbose=0),
    "CatBoost",
    "cat"
)

# ---------------------------
# Save metrics (FOR FLASK)
# ---------------------------
all_metrics = {
    "Random Forest": rf_metrics,
    "Gradient Boosting": gb_metrics,
    "CatBoost": cat_metrics
}

with open("models/metrics.json", "w") as f:
    json.dump(all_metrics, f, indent=4)

print("\n✅ All regression models trained successfully!")
