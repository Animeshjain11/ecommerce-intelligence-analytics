import joblib
import json
import numpy as np
import pandas as pd
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parents[1] / "models"

def load_customer_model():
    model = joblib.load(
        MODEL_DIR / "kmeans_customer_model.pkl"
    )

    scaler = joblib.load(
        MODEL_DIR / "customer_scaler.pkl"
    )

    with open(
        MODEL_DIR / "customer_segment_mapping.json",
        "r"
    ) as file:
        mapping = json.load(file)

    return model, scaler, mapping


def predict_customer_segments(customer_data):
    required_columns = [
        "frequency",
        "monetary",
        "recency_days"
    ]

    if not set(required_columns).issubset(customer_data.columns):
        raise ValueError("Required customer features are missing.")

    if customer_data[required_columns].isnull().any().any():
        raise ValueError("Customer features contain missing values.")

    if (customer_data[required_columns] < 0).any().any():
        raise ValueError("Customer features cannot be negative.")

    model, scaler, mapping = load_customer_model()

    features = customer_data[required_columns].copy()

    transformed_features = np.log1p(features)

    scaled_features = pd.DataFrame(
        scaler.transform(transformed_features),
        columns=required_columns,
        index=customer_data.index
    )

    predictions = model.predict(scaled_features)

    result = customer_data.copy()
    result["predicted_cluster"] = predictions
    result["predicted_segment"] = [
        mapping[str(cluster)] for cluster in predictions
    ]

    return result
