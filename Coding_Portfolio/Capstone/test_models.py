import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score

# Load data
df = pd.read_pickle("final_features.pkl")
X = df.drop(columns=['target', 'Lead_ID', 'Opportunity_ID'], errors='ignore')
y = df['target']

# Setup CV
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=99)

rf_aucs = []
lgbm_aucs = []
ensemble_aucs = []

for train_idx, val_idx in kf.split(X, y):
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=99)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict_proba(X_val)[:,1]
    rf_auc = roc_auc_score(y_val, rf_preds)
    rf_aucs.append(rf_auc)

    # LightGBM
    lgbm = LGBMClassifier(n_estimators=100, max_depth=5, random_state=99)
    lgbm.fit(X_train, y_train)
    lgbm_preds = lgbm.predict_proba(X_val)[:,1]
    lgbm_auc = roc_auc_score(y_val, lgbm_preds)
    lgbm_aucs.append(lgbm_auc)

    # Simple average ensemble
    ensemble_preds = (rf_preds + lgbm_preds) / 2
    ensemble_auc = roc_auc_score(y_val, ensemble_preds)
    ensemble_aucs.append(ensemble_auc)

print(f"Random Forest CV ROC AUC: {np.mean(rf_aucs):.4f}")
print(f"LightGBM CV ROC AUC: {np.mean(lgbm_aucs):.4f}")
print(f"Ensemble CV ROC AUC: {np.mean(ensemble_aucs):.4f}")

