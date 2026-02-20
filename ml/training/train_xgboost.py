"""XGBoost training pipeline for warranty claim fraud detection.

Usage:
    python ml/training/train_xgboost.py [--data data/processed/synthetic_claims.json]
"""

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    classification_report,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml.training.feature_engineering import extract_features


def load_data(data_path: str) -> tuple[pd.DataFrame, np.ndarray]:
    """Load claims and extract features."""
    with open(data_path) as f:
        claims = json.load(f)

    print(f"Loaded {len(claims)} claims")

    # Extract features
    X = extract_features(claims)

    # Create binary labels: 0 = legitimate, 1 = fraudulent
    y = np.array([1 if c["label"] == "fraudulent" else 0 for c in claims])

    print(f"Features shape: {X.shape}")
    print(f"Label distribution: legitimate={sum(y == 0)}, fraudulent={sum(y == 1)}")

    return X, y


def train_model(
    X: pd.DataFrame,
    y: np.ndarray,
    calibrate: bool = True,
) -> tuple:
    """Train XGBoost with cross-validation and optional probability calibration."""
    # Train/test split (stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    print(f"\nTrain set: {len(X_train)} samples")
    print(f"Test set:  {len(X_test)} samples")

    # XGBoost parameters tuned for fraud detection
    # (favor recall on fraud class while maintaining reasonable precision)
    params = {
        "objective": "binary:logistic",
        "eval_metric": "aucpr",
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 200,
        "min_child_weight": 3,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "scale_pos_weight": sum(y_train == 0) / max(sum(y_train == 1), 1),
        "random_state": 42,
        "verbosity": 0,
    }

    model = xgb.XGBClassifier(**params)

    # Train with early stopping
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    # Probability calibration using isotonic regression
    if calibrate:
        print("\nCalibrating probabilities...")
        calibrated = CalibratedClassifierCV(
            model, method="isotonic", cv=3
        )
        calibrated.fit(X_train, y_train)
        final_model = calibrated
    else:
        final_model = model

    return final_model, model, X_train, X_test, y_train, y_test


def evaluate_model(
    model,
    raw_model: xgb.XGBClassifier,
    X_test: pd.DataFrame,
    y_test: np.ndarray,
    feature_names: list[str],
) -> dict:
    """Evaluate model and print metrics."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    # Classification report
    print("\nClassification Report:")
    print(classification_report(
        y_test, y_pred, target_names=["legitimate", "fraudulent"]
    ))

    # ROC-AUC
    auc = roc_auc_score(y_test, y_prob)
    print(f"ROC-AUC: {auc:.4f}")

    # Precision/recall at different thresholds
    print("\nThreshold Analysis:")
    for threshold in [0.3, 0.4, 0.5, 0.6, 0.7]:
        preds_at_thresh = (y_prob >= threshold).astype(int)
        prec, rec, f1, _ = precision_recall_fscore_support(
            y_test, preds_at_thresh, average="binary", zero_division=0
        )
        flagged = sum(preds_at_thresh)
        print(
            f"  t={threshold:.1f}: precision={prec:.3f} recall={rec:.3f} "
            f"f1={f1:.3f} flagged={flagged}/{len(y_test)}"
        )

    # Feature importance (from raw XGBoost model)
    importance = raw_model.feature_importances_
    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": importance,
    }).sort_values("importance", ascending=False)

    print("\nTop 15 Features:")
    for _, row in importance_df.head(15).iterrows():
        bar_len = int(row["importance"] * 50)
        bar = "#" * bar_len
        print(f"  {row['feature']:30s} {row['importance']:.4f} {bar}")

    metrics = {
        "roc_auc": auc,
        "precision": float(precision_recall_fscore_support(
            y_test, y_pred, average="binary", zero_division=0
        )[0]),
        "recall": float(precision_recall_fscore_support(
            y_test, y_pred, average="binary", zero_division=0
        )[1]),
        "f1": float(precision_recall_fscore_support(
            y_test, y_pred, average="binary", zero_division=0
        )[2]),
        "test_size": len(y_test),
        "feature_importance": importance_df.to_dict("records"),
    }

    return metrics


def save_artifacts(
    model,
    raw_model: xgb.XGBClassifier,
    metrics: dict,
    feature_names: list[str],
    output_dir: str,
) -> None:
    """Save trained model and metadata."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Save calibrated model
    joblib.dump(model, out / "model_calibrated.joblib")
    print(f"\nSaved calibrated model to {out / 'model_calibrated.joblib'}")

    # Save raw XGBoost model (for feature importance inspection)
    raw_model.save_model(str(out / "model_raw.json"))
    print(f"Saved raw XGBoost model to {out / 'model_raw.json'}")

    # Save feature names
    with open(out / "feature_names.json", "w") as f:
        json.dump(feature_names, f, indent=2)

    # Save metrics
    # Convert numpy types for JSON serialization
    clean_metrics = {}
    for k, v in metrics.items():
        if isinstance(v, (np.floating, np.integer)):
            clean_metrics[k] = float(v)
        elif isinstance(v, list):
            clean_metrics[k] = [
                {kk: float(vv) if isinstance(vv, (np.floating, np.integer)) else vv
                 for kk, vv in item.items()} if isinstance(item, dict) else item
                for item in v
            ]
        else:
            clean_metrics[k] = v

    with open(out / "metrics.json", "w") as f:
        json.dump(clean_metrics, f, indent=2)
    print(f"Saved metrics to {out / 'metrics.json'}")

    # Save threshold config
    thresholds = {
        "auto_approve_threshold": 0.8,
        "auto_flag_threshold": 0.4,
        "description": "Scores represent probability of LEGITIMACY. "
                       "High score = likely legitimate, low score = likely fraud.",
    }
    with open(out / "thresholds.json", "w") as f:
        json.dump(thresholds, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train XGBoost fraud detector")
    parser.add_argument(
        "--data",
        type=str,
        default="data/processed/synthetic_claims.json",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/models",
    )
    parser.add_argument("--no-calibrate", action="store_true")
    args = parser.parse_args()

    X, y = load_data(args.data)
    feature_names = list(X.columns)

    final_model, raw_model, X_train, X_test, y_train, y_test = train_model(
        X, y, calibrate=not args.no_calibrate
    )

    metrics = evaluate_model(final_model, raw_model, X_test, y_test, feature_names)

    save_artifacts(final_model, raw_model, metrics, feature_names, args.output)
    print("\nTraining complete!")


if __name__ == "__main__":
    main()
