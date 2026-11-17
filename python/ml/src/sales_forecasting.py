
import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


FEATURE_COLUMNS = [
    "revenue_lag_1",
    "revenue_lag_2",
    "revenue_lag_3",
    "revenue_rolling_mean_3",
    "orders_lag_1"
]


def prepare_forecasting_data(monthly_df):
    """Clean monthly data and create historical features."""

    df = monthly_df.copy()

    df["sales_month"] = pd.to_datetime(df["sales_month"])
    df = df.sort_values("sales_month")

    # Use complete historical period
    df = df[
        (df["sales_month"] >= "2017-01-01") &
        (df["sales_month"] <= "2018-08-01")
    ].copy()

    df["revenue_lag_1"] = df["total_product_revenue"].shift(1)
    df["revenue_lag_2"] = df["total_product_revenue"].shift(2)
    df["revenue_lag_3"] = df["total_product_revenue"].shift(3)

    df["revenue_rolling_mean_3"] = (
        df["total_product_revenue"]
        .shift(1)
        .rolling(3)
        .mean()
    )

    df["orders_lag_1"] = df["total_orders"].shift(1)

    return df.dropna().reset_index(drop=True)


def evaluate_forecasting_models(model_df, test_months=4):
    """Train and evaluate forecasting models chronologically."""

    if len(model_df) <= test_months:
        raise ValueError("Not enough records for the requested test period.")

    X = model_df[FEATURE_COLUMNS]
    y = model_df["total_product_revenue"]

    split_index = len(model_df) - test_months

    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    # Baseline
    baseline_predictions = X_test["revenue_lag_1"].to_numpy()

    # Linear Regression
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)
    linear_predictions = linear_model.predict(X_test)

    # Random Forest
    rf_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=3,
        min_samples_leaf=2,
        random_state=42
    )
    rf_model.fit(X_train, y_train)
    rf_predictions = rf_model.predict(X_test)

    predictions = pd.DataFrame({
        "sales_month": model_df["sales_month"].iloc[split_index:].values,
        "actual_revenue": y_test.values,
        "baseline_prediction": baseline_predictions,
        "linear_prediction": linear_predictions,
        "random_forest_prediction": rf_predictions
    })

    def metrics(actual, predicted):
        actual = np.asarray(actual, dtype=float)
        predicted = np.asarray(predicted, dtype=float)

        return {
            "MAE": mean_absolute_error(actual, predicted),
            "RMSE": np.sqrt(mean_squared_error(actual, predicted)),
            "MAPE (%)": np.mean(
                np.abs((actual - predicted) / actual)
            ) * 100
        }

    evaluation = pd.DataFrame({
        "Baseline": metrics(y_test, baseline_predictions),
        "Linear Regression": metrics(y_test, linear_predictions),
        "Random Forest": metrics(y_test, rf_predictions)
    }).T

    return predictions, evaluation


def forecast_next_month(monthly_df):
    """Train models on all prepared data and predict next month revenue."""

    model_df = prepare_forecasting_data(monthly_df)

    X = model_df[FEATURE_COLUMNS]
    y = model_df["total_product_revenue"]

    # Build features for the next month
    next_features = pd.DataFrame([{
        "revenue_lag_1": model_df["total_product_revenue"].iloc[-1],
        "revenue_lag_2": model_df["total_product_revenue"].iloc[-2],
        "revenue_lag_3": model_df["total_product_revenue"].iloc[-3],
        "revenue_rolling_mean_3": (
            model_df["total_product_revenue"].tail(3).mean()
        ),
        "orders_lag_1": model_df["total_orders"].iloc[-1]
    }])

    # Train models on all available historical records
    linear_model = LinearRegression()
    linear_model.fit(X, y)

    rf_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=3,
        min_samples_leaf=2,
        random_state=42
    )
    rf_model.fit(X, y)

    last_month = model_df["sales_month"].max()
    next_month = last_month + pd.offsets.MonthBegin(1)

    return pd.DataFrame({
        "forecast_month": [next_month],
        "baseline_prediction": [next_features["revenue_lag_1"].iloc[0]],
        "linear_prediction": [linear_model.predict(next_features)[0]],
        "random_forest_prediction": [rf_model.predict(next_features)[0]]
    })
