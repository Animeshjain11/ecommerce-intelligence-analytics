from pathlib import Path

import pandas as pd
import streamlit as st


# Project directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ML_OUTPUT_DIR = PROJECT_ROOT / "python" / "ml" / "outputs"


@st.cache_data
def load_ml_data():
    """Load aggregated customer segmentation and forecasting outputs."""

    segment_summary_df = pd.read_csv(
        ML_OUTPUT_DIR / "ml_customer_segment_summary_k4.csv"
    )

    evaluation_df = pd.read_csv(
        ML_OUTPUT_DIR / "sales_forecast_model_evaluation.csv",
        index_col=0
    )

    forecast_df = pd.read_csv(
        ML_OUTPUT_DIR / "next_month_revenue_forecast.csv"
    )

    predictions_df = pd.read_csv(
        ML_OUTPUT_DIR / "sales_forecast_predictions.csv",
        parse_dates=["sales_month"]
    )

    return (
        segment_summary_df,
        evaluation_df,
        forecast_df,
        predictions_df
    )


def render_ml_dashboard():

    st.header("Machine Learning & Predictive Analytics")

    (
        segment_summary_df,
        evaluation_df,
        forecast_df,
        predictions_df
    ) = load_ml_data()

    # ---------------------------------
    # CUSTOMER SEGMENTATION
    # ---------------------------------

    st.subheader("Customer Segmentation - K-Means")

    total_customers = int(
        segment_summary_df["total_customers"].sum()
    )

    total_segments = segment_summary_df["ml_segment"].nunique()

    average_customer_value = (
        (
            segment_summary_df["avg_monetary"]
            * segment_summary_df["total_customers"]
        ).sum()
        / total_customers
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Customers",
        f"{total_customers:,}"
    )

    col2.metric(
        "ML Segments",
        total_segments
    )

    col3.metric(
        "Average Customer Value",
        f"R$ {average_customer_value:,.2f}"
    )

    st.markdown("### Customer Distribution by Segment")

    col1, col2 = st.columns(2)

    with col1:
        st.bar_chart(
            segment_summary_df.set_index("ml_segment")[
                ["total_customers"]
            ]
        )

    with col2:
        st.bar_chart(
            segment_summary_df.set_index("ml_segment")[
                ["total_revenue"]
            ]
        )

    st.markdown("### Segment Performance")

    st.dataframe(
        segment_summary_df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Segment Summary",
        data=segment_summary_df.to_csv(index=False).encode("utf-8"),
        file_name="customer_segment_summary.csv",
        mime="text/csv"
    )

    st.caption(
        "This dashboard displays aggregated segment-level information. "
        "Individual customer IDs and customer-level records are not exposed."
    )

    # ---------------------------------
    # SALES FORECASTING
    # ---------------------------------

    st.divider()

    st.subheader("Sales Forecasting")

    forecast = forecast_df.iloc[0]

    forecast_month = pd.to_datetime(
        forecast["forecast_month"]
    ).strftime("%B %Y")

    st.caption(
        f"Experimental historical forecast for {forecast_month}"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Baseline Forecast",
        f"R$ {forecast['baseline_prediction']:,.2f}"
    )

    col2.metric(
        "Linear Regression",
        f"R$ {forecast['linear_prediction']:,.2f}"
    )

    col3.metric(
        "Random Forest",
        f"R$ {forecast['random_forest_prediction']:,.2f}"
    )

    st.markdown("### Model Performance Comparison")

    st.dataframe(
        evaluation_df.style.format({
            "MAE": "R$ {:,.2f}",
            "RMSE": "R$ {:,.2f}",
            "MAPE (%)": "{:.2f}%"
        }),
        use_container_width=True
    )

    st.markdown("### Actual vs Predicted Revenue")

    chart_df = predictions_df.set_index("sales_month")[
        [
            "actual_revenue",
            "baseline_prediction",
            "linear_prediction",
            "random_forest_prediction"
        ]
    ]

    st.line_chart(chart_df)

    st.download_button(
        "Download Forecast Predictions",
        data=predictions_df.to_csv(index=False).encode("utf-8"),
        file_name="sales_forecast_predictions.csv",
        mime="text/csv"
    )

    st.info(
        "Forecasting uses a limited historical dataset. "
        "The four-month test period is small, so predictions "
        "should be treated as experimental rather than "
        "reliable future revenue commitments."
    )
