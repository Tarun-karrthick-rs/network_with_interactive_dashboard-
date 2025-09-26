import pandas as pd
import numpy as np
import time
import pickle
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score

DATA_FILE = "dataset_clean.csv"
MODEL_FILE = "model.pkl"
FEATURES_FILE = "selected_features.pkl"
LOG_FILE = "train_log.json"

start_time = time.time()

print("📂 Loading dataset...")
df = pd.read_csv(DATA_FILE, low_memory=False)

target_col = "Label"
X = df.drop(columns=[target_col])
y = df[target_col]

# Encode categorical columns
for col in X.columns:
    if X[col].dtype == 'object' or X[col].dtype == 'O':
        X[col] = X[col].astype(str)
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
    else:
        X[col] = X[col].fillna(0)

# Encode target
if y.dtype == 'object' or y.dtype == 'O':
    y = y.astype(str)
    y = LabelEncoder().fit_transform(y)

# 🔍 Feature selection using only 10% sample
print("🔍 Finding top features (ExtraTrees) using sample...")
sample_frac = 0.1 if len(df) > 500000 else 1.0
df_sample = df.sample(frac=sample_frac, random_state=42)

X_sample = X.loc[df_sample.index]
y_sample = y[df_sample.index]

model_et = ExtraTreesClassifier(n_estimators=30, random_state=42, n_jobs=-1)
model_et.fit(X_sample, y_sample)
importances = model_et.feature_importances_

# Select top 12 features
indices = np.argsort(importances)[::-1][:12]
selected_features = X.columns[indices]
print(f"🏆 Selected top features: {list(selected_features)}")

with open(FEATURES_FILE, "wb") as f:
    pickle.dump(list(selected_features), f)

X_selected = X[selected_features]

print("✂ Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X_selected, y, test_size=0.2, random_state=42
)

# ⚡ Faster XGBoost configuration
print("⚡ Training XGBoost model with epoch logging...")

# 🆕 Put eval_metric in constructor to avoid old XGBoost issue
model = XGBClassifier(
    n_estimators=20,      # Number of boosting rounds
    max_depth=4,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    tree_method="hist",
    n_jobs=-1,
    random_state=42,
    verbosity=0,
    eval_metric="mlogloss"
)

# 🆕 Log training history
history = {"time": [], "train_acc": [], "test_acc": []}

# Train model and log accuracy per boosting round
epoch_start_time = time.time()
model.fit(
    X_train,
    y_train,
    eval_set=[(X_train, y_train), (X_test, y_test)],
    verbose=False
)
elapsed_total = time.time() - epoch_start_time

# Approximate time per epoch
time_per_epoch = elapsed_total / model.n_estimators

# Compute train & test accuracy per epoch
for epoch in range(model.n_estimators):
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    history["train_acc"].append(accuracy_score(y_train, y_pred_train))
    history["test_acc"].append(accuracy_score(y_test, y_pred_test))
    history["time"].append(time_per_epoch * (epoch + 1))

# 📝 Save training log for graphing
with open(LOG_FILE, "w") as f:
    json.dump(history, f)

# Save final model
with open(MODEL_FILE, "wb") as f:
    pickle.dump(model, f)

final_acc = accuracy_score(y_test, model.predict(X_test)) * 100
print(f"✅ Model trained & saved as {MODEL_FILE}")
print(f"📊 Final Test Accuracy: {final_acc:.2f}%")
print(f"⏱ Total training time: {time.time() - start_time:.2f} sec")
print(f"📝 Training log saved to {LOG_FILE}")
