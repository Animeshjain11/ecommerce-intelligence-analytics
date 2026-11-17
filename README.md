# E-Commerce Intelligence Platform

An end-to-end e-commerce analytics and machine learning project built using the Olist Brazilian E-Commerce dataset.

The platform combines SQL, Python, Machine Learning, Power BI and Streamlit to transform raw e-commerce data into business insights and interactive analytics.

## Project Objectives

- Analyze e-commerce sales and business performance.
- Understand customer purchasing behavior and segments.
- Evaluate product, category and seller performance.
- Measure delivery and payment performance.
- Build customer segmentation and revenue forecasting models.
- Present business insights through an interactive dashboard.

## Technology Stack

| Area | Tools |
|---|---|
| Database | PostgreSQL |
| Querying | SQL |
| Data Analysis | Python, Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Machine Learning | Scikit-learn, K-Means, Random Forest, Linear Regression |
| Dashboard | Streamlit |
| BI | Power BI |
| Version Control | Git, GitHub |

## Project Architecture

Raw CSV Data → PostgreSQL Raw Tables → Staging Tables → Analytics Views → Python & Machine Learning → Power BI / Streamlit

## Key Features

### 1. SQL Analytics
- Raw data ingestion and staging.
- Data quality checks.
- Business analysis queries.
- Analytical views and KPI calculations.

### 2. Python Exploratory Data Analysis
- Monthly sales analysis.
- Customer RFM analysis.
- Product and category performance.
- Seller performance.
- Payment and delivery analysis.
- Freight cost analysis.

### 3. Machine Learning
- K-Means customer segmentation.
- Customer segment profiling.
- Revenue forecasting using baseline, Linear Regression and Random Forest.
- Model evaluation and comparison.

### 4. Interactive Dashboard
- Executive overview.
- Monthly sales trends.
- Customer segmentation.
- Delivery performance.
- State-wise delivery analysis.
- Seller performance.
- Product and category analytics.
- Machine learning and predictive analytics.

### 5. Power BI
Prepared analytical CSV exports for business intelligence reporting.

## Key Business Metrics

| Metric | Value |
|---|---:|
| Total Orders | 99,441 |
| Delivered Orders | 96,478 |
| Total Product Revenue | R$13.59 Million |
| Average Order Value | R$159.33 |
| Total Customers (RFM) | 93,358 |
| Total Products | 32,951 |
| Total Sellers | 3,095 |
| Average Review Score | 4.09 / 5 |
| On-time Delivery Rate | 91.89% |

## Selected Business Insights

- Approximately 97% of analyzed customers placed only one order.
- Champions and Cannot Lose Them RFM segments contributed approximately 60.91% of customer revenue.
- Health & Beauty was the highest-revenue product category.
- On-time delivery performance was approximately 91.89%.
- Freight costs represented approximately 16.57% of product revenue.

## Machine Learning Notes

Customer segmentation uses K-Means clustering on transformed RFM features. Segment names are heuristic interpretations of cluster profiles, not verified churn labels.

Revenue forecasting uses historical monthly revenue and chronological model evaluation. The available time series is small, so forecasts are exploratory rather than reliable business commitments.

## Project Structure

```text
ecommerce-intelligence-analytics/
├── data/
│   └── raw/                  # Original dataset (not included in Git)
├── sql/                      # SQL scripts
├── python/
│   ├── ml/
│   │   ├── models/
│   │   ├── outputs/
│   │   └── src/
│   └── outputs/              # Analysis exports
├── powerbi/
│   └── exports/              # Power BI source CSVs
├── streamlit_app/
│   ├── assets/
│   ├── pages/
│   └── db.py
├── app.py
├── 01_ecommerce_eda.ipynb
├── requirements.txt
└── README.md
```

## Run Locally

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ecommerce-intelligence-analytics
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Prepare PostgreSQL

Create a PostgreSQL database named `ecommerce_analytics`.

Run the SQL scripts in the appropriate order to create raw tables, import the dataset, create staging tables and build analytics.

The original Olist CSV files must be downloaded separately and placed in `data/raw/`.

### 5. Configure environment variables

Create a local `.env` file:

```env
DB_USER=postgres
DB_PASSWORD=your_local_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce_analytics
```

Never commit `.env` or database credentials.

### 6. Launch the dashboard

```bash
python -m streamlit run app.py
```

## Dataset

This project uses the Brazilian E-Commerce Public Dataset by Olist, containing approximately 100,000 orders and related customer, seller, product, payment, review and geolocation information.

Dataset source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

## Limitations

- The dataset represents historical transactions, not live business activity.
- Customer segments are based on historical RFM behavior.
- Customer inactivity does not automatically mean confirmed churn.
- Revenue forecasting has a limited number of monthly observations.
- Portuguese review text requires language-aware processing for reliable sentiment analysis.
- Some orders contain multiple sellers, which affects seller-level aggregation.

## Author

Developed as an end-to-end portfolio project focused on Data Analytics, Data Science and Machine Learning.
