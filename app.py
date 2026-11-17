
import streamlit as st
from pathlib import Path
import pandas as pd

from streamlit_app.db import get_engine
from streamlit_app.pages.ml_dashboard import render_ml_dashboard

st.set_page_config(
    page_title="E-Commerce Intelligence Platform",
    page_icon="🛒",
    layout="wide"
)

# Load custom dashboard theme
CSS_PATH = (
    Path(__file__).parent
    / "streamlit_app"
    / "assets"
    / "custom.css"
)

with open(CSS_PATH, "r", encoding="utf-8") as css_file:
    st.markdown(
        f"<style>{css_file.read()}</style>",
        unsafe_allow_html=True
    )

# Premium Hero Header
st.markdown("""
<div class="hero-banner">
    <div class="hero-content">
        <p class="hero-label">BUSINESS INTELLIGENCE PLATFORM</p>
        <h1>E-Commerce Intelligence</h1>
        <p class="hero-description">
            Transforming e-commerce data into actionable business insights
            using SQL, Python, Analytics and Machine Learning.
        </p>
        <div class="hero-tags">
            <span>SQL Analytics</span>
            <span>Python &amp; ML</span>
            <span>Business Intelligence</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_data(query):
    return pd.read_sql(query, get_engine())


try:
    # Executive Overview
    kpi_df = load_data(
        "SELECT * FROM analytics.executive_kpis"
    )
    kpis = kpi_df.iloc[0]

    st.subheader("Executive Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", f"{int(kpis['total_orders']):,}")
    col2.metric("Delivered Orders", f"{int(kpis['delivered_orders']):,}")
    col3.metric("Total Customers", f"{int(kpis['total_customers']):,}")
    col4.metric("Total Products", f"{int(kpis['total_products']):,}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Product Revenue", f"R$ {kpis['total_product_revenue']:,.2f}")
    col2.metric("Average Order Value", f"R$ {kpis['average_order_value']:,.2f}")
    col3.metric("Average Review", f"{kpis['average_review_score']:.2f}/5")
    col4.metric("On-Time Delivery", f"{kpis['on_time_delivery_percentage']:.2f}%")

    st.divider()

    # Monthly Sales
    st.subheader("📈 Monthly Sales Trend")

    monthly_df = load_data("""
        SELECT *
        FROM analytics.monthly_sales
        WHERE sales_month < DATE '2018-09-01'
        ORDER BY sales_month
    """)

    monthly_df["sales_month"] = pd.to_datetime(monthly_df["sales_month"])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Monthly Product Revenue**")
        st.line_chart(
            monthly_df.set_index("sales_month")[["total_product_revenue"]]
        )

    with col2:
        st.markdown("**Monthly Orders**")
        st.line_chart(
            monthly_df.set_index("sales_month")[["total_orders", "delivered_orders"]]
        )

    st.divider()

    # Customer Segmentation
    st.subheader("👥 Customer Segmentation Analysis")

    segment_df = load_data("""
        SELECT
            customer_segment,
            COUNT(*) AS total_customers,
            ROUND(SUM(monetary)::numeric, 2) AS total_revenue,
            ROUND(AVG(monetary)::numeric, 2) AS avg_customer_value,
            ROUND(AVG(recency_days)::numeric, 1) AS avg_recency_days
        FROM analytics.customer_segments
        GROUP BY customer_segment
        ORDER BY total_customers DESC
    """)

    col1, col2 = st.columns(2)
    col1.metric("Segmented Customers", f"{int(segment_df['total_customers'].sum()):,}")
    col2.metric("Segment Revenue", f"R$ {segment_df['total_revenue'].sum():,.2f}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Customers by Segment**")
        st.bar_chart(
            segment_df.set_index("customer_segment")[["total_customers"]]
        )

    with col2:
        st.markdown("**Revenue by Segment**")
        st.bar_chart(
            segment_df.sort_values("total_revenue", ascending=False)
            .set_index("customer_segment")[["total_revenue"]]
        )

    st.dataframe(segment_df, use_container_width=True, hide_index=True)

    st.divider()

    # Delivery Performance
    st.subheader("🚚 Delivery Performance Analysis")

    delivery_kpi = load_data("""
        SELECT
            COUNT(*) AS total_delivered_orders,
            ROUND(AVG(delivery_days)::numeric, 2) AS avg_delivery_days,
            COUNT(*) FILTER (WHERE delivered_on_time = TRUE) AS on_time_orders,
            COUNT(*) FILTER (WHERE delivered_on_time = FALSE) AS delayed_orders,
            COUNT(*) FILTER (WHERE delivered_on_time IS NULL) AS missing_status,
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE delivered_on_time = TRUE)
                / NULLIF(COUNT(*), 0), 2
            ) AS on_time_percentage
        FROM analytics.delivery_performance
        WHERE order_status = 'delivered'
    """).iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Delivered Orders", f"{int(delivery_kpi['total_delivered_orders']):,}")
    col2.metric("Average Delivery", f"{delivery_kpi['avg_delivery_days']:.2f} days")
    col3.metric("On-Time Delivery", f"{delivery_kpi['on_time_percentage']:.2f}%")
    col4.metric("Delayed Orders", f"{int(delivery_kpi['delayed_orders']):,}")

    status_df = load_data("""
        SELECT
            delivery_status,
            COUNT(*) AS total_orders,
            ROUND(AVG(delivery_days)::numeric, 2) AS avg_delivery_days
        FROM analytics.delivery_performance
        WHERE order_status = 'delivered'
        GROUP BY delivery_status
        ORDER BY total_orders DESC
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Orders by Delivery Status**")
        st.bar_chart(status_df.set_index("delivery_status")[["total_orders"]])

    with col2:
        st.markdown("**Average Delivery Days by Status**")
        st.bar_chart(
            status_df.dropna(subset=["avg_delivery_days"])
            .set_index("delivery_status")[["avg_delivery_days"]]
        )

    st.dataframe(status_df, use_container_width=True, hide_index=True)
    st.info(f"Orders with missing delivery status: {int(delivery_kpi['missing_status'])}")

    st.divider()

    # State-wise Delivery Performance
    st.subheader("🌎 State-wise Delivery Performance")

    state_df = load_data("""
        SELECT
            c.customer_state,
            COUNT(*) AS delivered_orders,
            ROUND(AVG(d.delivery_days)::numeric, 2) AS avg_delivery_days,
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE d.delivered_on_time = TRUE)
                / NULLIF(COUNT(*), 0), 2
            ) AS on_time_percentage
        FROM analytics.delivery_performance d
        JOIN staging.orders o ON d.order_id = o.order_id
        JOIN staging.customers c ON o.customer_id = c.customer_id
        WHERE d.order_status = 'delivered'
        GROUP BY c.customer_state
        ORDER BY avg_delivery_days ASC
    """)

    fastest = state_df.loc[state_df["avg_delivery_days"].idxmin()]
    slowest = state_df.loc[state_df["avg_delivery_days"].idxmax()]
    best = state_df.loc[state_df["on_time_percentage"].idxmax()]
    worst = state_df.loc[state_df["on_time_percentage"].idxmin()]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Fastest State", fastest["customer_state"], f"{fastest['avg_delivery_days']:.2f} days")
    col2.metric("Slowest State", slowest["customer_state"], f"{slowest['avg_delivery_days']:.2f} days")
    col3.metric("Best On-Time State", best["customer_state"], f"{best['on_time_percentage']:.2f}%")
    col4.metric("Lowest On-Time State", worst["customer_state"], f"{worst['on_time_percentage']:.2f}%")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Average Delivery Days by State**")
        st.bar_chart(
            state_df.sort_values("avg_delivery_days", ascending=False)
            .set_index("customer_state")[["avg_delivery_days"]]
        )

    with col2:
        st.markdown("**On-Time Delivery Percentage by State**")
        st.bar_chart(
            state_df.sort_values("on_time_percentage", ascending=False)
            .set_index("customer_state")[["on_time_percentage"]]
        )

    st.markdown("**Delivered Orders by State**")
    st.bar_chart(
        state_df.sort_values("delivered_orders", ascending=False)
        .set_index("customer_state")[["delivered_orders"]]
    )

    st.markdown("**Complete State-wise Performance Table**")
    st.dataframe(state_df, use_container_width=True, hide_index=True)

    st.success("Dashboard connected to PostgreSQL successfully!")

    # Seller Performance Analysis
    st.divider()
    st.subheader("🏪 Seller Performance Analysis")

    seller_df = load_data("""
        SELECT *
        FROM analytics.seller_performance
    """)

    # Seller KPIs
    seller_kpis = load_data("""
        SELECT
            COUNT(*) AS total_sellers,
            SUM(total_orders) AS total_seller_orders,
            ROUND(SUM(total_product_revenue), 2) AS total_revenue,
            ROUND(AVG(avg_review_score), 2) AS avg_review_score,
            ROUND(AVG(avg_delivery_days), 2) AS avg_delivery_days
        FROM analytics.seller_performance
    """).iloc[0]

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Sellers", f"{int(seller_kpis['total_sellers']):,}")
    col2.metric("Seller Orders", f"{int(seller_kpis['total_seller_orders']):,}")
    col3.metric("Product Revenue", f"R$ {seller_kpis['total_revenue']:,.2f}")
    col4.metric("Average Rating", f"{seller_kpis['avg_review_score']:.2f}/5")
    col5.metric("Avg Delivery", f"{seller_kpis['avg_delivery_days']:.2f} days")

    # Top 10 Sellers
    st.markdown("**🏆 Top 10 Sellers by Revenue**")

    top_sellers = seller_df.sort_values(
        "total_product_revenue", ascending=False
    ).head(10)

    st.bar_chart(
        top_sellers.set_index("seller_city")[["total_product_revenue"]]
    )

    st.dataframe(top_sellers, use_container_width=True, hide_index=True)

    # State-wise Seller Revenue
    st.markdown("**🌎 State-wise Seller Revenue**")

    seller_state_df = load_data("""
        SELECT
            seller_state,
            COUNT(*) AS total_sellers,
            ROUND(SUM(total_product_revenue), 2) AS total_revenue,
            ROUND(AVG(avg_review_score), 2) AS avg_review_score
        FROM analytics.seller_performance
        GROUP BY seller_state
        ORDER BY total_revenue DESC
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Revenue by State**")
        st.bar_chart(
            seller_state_df.set_index("seller_state")[["total_revenue"]]
        )

    with col2:
        st.markdown("**Sellers by State**")
        st.bar_chart(
            seller_state_df.set_index("seller_state")[["total_sellers"]]
        )

    st.dataframe(seller_state_df, use_container_width=True, hide_index=True)


    # Interactive Seller Search and Filters
    st.markdown("**🔎 Individual Seller Search & Filters**")

    col1, col2 = st.columns(2)

    with col1:
        seller_search = st.text_input(
            "Search by Seller ID",
            placeholder="Enter full or partial Seller ID"
        )

    with col2:
        selected_state = st.selectbox(
            "Filter by Seller State",
            ["All States"] + sorted(
                seller_df["seller_state"].dropna().unique().tolist()
            )
        )

    col1, col2 = st.columns(2)

    with col1:
        min_revenue = st.number_input(
            "Minimum Product Revenue (R$)",
            min_value=0.0,
            value=0.0,
            step=100.0
        )

    with col2:
        min_rating = st.slider(
            "Minimum Review Rating",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.5
        )

    filtered_sellers = seller_df.copy()

    if seller_search.strip():
        filtered_sellers = filtered_sellers[
            filtered_sellers["seller_id"].str.contains(
                seller_search.strip(), case=False, na=False
            )
        ]

    if selected_state != "All States":
        filtered_sellers = filtered_sellers[
            filtered_sellers["seller_state"] == selected_state
        ]

    filtered_sellers = filtered_sellers[
        (filtered_sellers["total_product_revenue"] >= min_revenue)
        & (
            filtered_sellers["avg_review_score"].fillna(-1)
            >= min_rating
        )
    ]

    st.metric("Matching Sellers", f"{len(filtered_sellers):,}")

    st.dataframe(
        filtered_sellers.sort_values(
            "total_product_revenue", ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

    # Seller Revenue Comparison
    st.divider()
    st.subheader("📊 Top 10 vs Bottom 10 Sellers")

    comparison_df = seller_df.dropna(
        subset=["total_product_revenue"]
    ).copy()

    top_10 = comparison_df.nlargest(
        10, "total_product_revenue"
    ).copy()

    bottom_10 = comparison_df.nsmallest(
        10, "total_product_revenue"
    ).copy()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🏆 Top 10 Sellers by Revenue**")
        st.bar_chart(
            top_10.sort_values("total_product_revenue")
            .set_index("seller_city")[["total_product_revenue"]]
        )

    with col2:
        st.markdown("**📉 Bottom 10 Sellers by Revenue**")
        st.bar_chart(
            bottom_10.sort_values("total_product_revenue")
            .set_index("seller_city")[["total_product_revenue"]]
        )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Highest Rated Sellers**")
        highest_rated = comparison_df.dropna(
            subset=["avg_review_score"]
        ).nlargest(10, "avg_review_score")

        st.dataframe(
            highest_rated[
                ["seller_city", "seller_state", "avg_review_score",
                 "total_product_revenue"]
            ],
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.markdown("**Lowest Rated Sellers**")
        lowest_rated = comparison_df.dropna(
            subset=["avg_review_score"]
        ).nsmallest(10, "avg_review_score")

        st.dataframe(
            lowest_rated[
                ["seller_city", "seller_state", "avg_review_score",
                 "total_product_revenue"]
            ],
            use_container_width=True,
            hide_index=True
        )

    # Product Analytics
    st.divider()
    st.subheader("📦 Product & Category Performance")

    product_kpis = load_data("""
        SELECT
            COUNT(*) AS total_products,
            SUM(total_items_sold) AS total_items_sold,
            ROUND(SUM(total_revenue), 2) AS total_revenue,
            ROUND(AVG(avg_selling_price), 2) AS avg_selling_price
        FROM analytics.product_performance_detailed
    """).iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", f"{int(product_kpis['total_products']):,}")
    col2.metric("Items Sold", f"{int(product_kpis['total_items_sold']):,}")
    col3.metric("Product Revenue", f"R$ {product_kpis['total_revenue']:,.2f}")
    col4.metric("Avg Selling Price", f"R$ {product_kpis['avg_selling_price']:,.2f}")

    # Category filter
    category_df = load_data("""
        SELECT *
        FROM analytics.category_product_performance
        ORDER BY total_revenue DESC
    """)

    selected_category = st.selectbox(
        "Filter by Product Category",
        ["All Categories"] + sorted(category_df["category_name"].dropna().unique().tolist())
    )

    if selected_category == "All Categories":
        filtered_category_df = category_df.copy()
    else:
        filtered_category_df = category_df[
            category_df["category_name"] == selected_category
        ]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🏆 Category Revenue**")
        st.bar_chart(
            filtered_category_df.sort_values("total_revenue", ascending=False)
            .set_index("category_name")[["total_revenue"]]
        )

    with col2:
        st.markdown("**📦 Items Sold by Category**")
        st.bar_chart(
            filtered_category_df.sort_values("total_items_sold", ascending=False)
            .set_index("category_name")[["total_items_sold"]]
        )

    st.markdown("**Category Performance Table**")
    st.dataframe(
        filtered_category_df,
        use_container_width=True,
        hide_index=True
    )

    # Interactive Product Search and Filters
    st.divider()
    st.markdown("### 🔎 Product Search & Advanced Filters")

    all_products_df = load_data("""
        SELECT
            product_id,
            category_name,
            total_items_sold,
            total_orders,
            total_sellers,
            total_revenue,
            avg_selling_price
        FROM analytics.product_performance_detailed
        ORDER BY total_revenue DESC
    """)

    col1, col2 = st.columns(2)

    with col1:
        product_search = st.text_input(
            "Search Product ID",
            placeholder="Enter full or partial Product ID"
        )

    with col2:
        product_category = st.selectbox(
            "Select Product Category",
            ["All Categories"] +
            sorted(all_products_df["category_name"].dropna().unique().tolist())
        )

    col1, col2 = st.columns(2)

    with col1:
        min_product_revenue = st.number_input(
            "Minimum Product Revenue (R$)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            key="product_min_revenue"
        )

    with col2:
        min_items_sold = st.number_input(
            "Minimum Items Sold",
            min_value=0,
            value=0,
            step=10,
            key="product_min_items_sold"
        )

    filtered_products = all_products_df.copy()

    if product_search.strip():
        filtered_products = filtered_products[
            filtered_products["product_id"].str.contains(
                product_search.strip(),
                case=False,
                na=False
            )
        ]

    if product_category != "All Categories":
        filtered_products = filtered_products[
            filtered_products["category_name"] == product_category
        ]

    filtered_products = filtered_products[
        (filtered_products["total_revenue"] >= min_product_revenue)
        & (filtered_products["total_items_sold"] >= min_items_sold)
    ]

    st.metric("Matching Products", f"{len(filtered_products):,}")

    st.dataframe(
        filtered_products,
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered_products.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Products CSV",
        data=csv_data,
        file_name="filtered_product_analysis.csv",
        mime="text/csv"
    )

    # Top products
    top_products_df = load_data("""
        SELECT
            product_id,
            category_name,
            total_items_sold,
            total_orders,
            total_revenue,
            avg_selling_price
        FROM analytics.product_performance_detailed
        ORDER BY total_revenue DESC
        LIMIT 10
    """)

    best_selling_df = load_data("""
        SELECT
            product_id,
            category_name,
            total_items_sold,
            total_orders,
            total_revenue,
            avg_selling_price
        FROM analytics.product_performance_detailed
        ORDER BY total_items_sold DESC
        LIMIT 10
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**💰 Top 10 Products by Revenue**")
        st.bar_chart(
            top_products_df.set_index("product_id")[["total_revenue"]]
        )
        st.dataframe(top_products_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**🔥 Top 10 Best-Selling Products**")
        st.bar_chart(
            best_selling_df.set_index("product_id")[["total_items_sold"]]
        )
        st.dataframe(best_selling_df, use_container_width=True, hide_index=True)

    # Product segments
    st.markdown("**🎯 Product Segment Analysis**")

    product_segment_df = load_data("""
        SELECT
            product_segment,
            COUNT(*) AS total_products,
            SUM(total_items_sold) AS total_items_sold,
            ROUND(SUM(total_revenue), 2) AS total_revenue
        FROM analytics.product_segments
        GROUP BY product_segment
        ORDER BY total_revenue DESC
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.bar_chart(
            product_segment_df.set_index("product_segment")[["total_products"]]
        )

    with col2:
        st.bar_chart(
            product_segment_df.set_index("product_segment")[["total_revenue"]]
        )

    st.dataframe(
        product_segment_df,
        use_container_width=True,
        hide_index=True
    )

    # Machine Learning & Predictive Analytics
    st.divider()
    render_ml_dashboard()

    # Business Insights & Strategic Recommendations
    st.divider()
    st.header("Business Insights & Recommendations")

    st.markdown(
        "Key findings from the e-commerce data and recommended business actions."
    )

    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:
        st.subheader("1. Customer Retention")
        st.markdown("""
        **Finding**
        - Approximately 97% of customers placed only one order.
        - Repeat customers represent approximately 3% of customers.

        **Recommendation**
        - Introduce personalized follow-up campaigns.
        - Offer loyalty benefits to encourage repeat purchases.
        - Identify high-value customers for targeted retention.
        """)

        st.subheader("2. Revenue Concentration")
        st.markdown("""
        **Finding**
        - Champions and Cannot Lose Them segments contribute
          approximately 60.91% of customer revenue.

        **Recommendation**
        - Prioritize retention of high-value customers.
        - Use personalized offers and premium customer support.
        - Monitor changes in high-value customer activity.
        """)

        st.subheader("3. Delivery Performance")
        st.markdown("""
        **Finding**
        - On-time delivery performance is approximately 91.89%.

        **Recommendation**
        - Investigate delayed deliveries.
        - Monitor seller and regional delivery performance.
        - Improve logistics coordination.
        """)

    with insight_col2:
        st.subheader("4. Product Strategy")
        st.markdown("""
        **Finding**
        - Health & Beauty is the highest-revenue product category.
        - Watches & Gifts is another major revenue contributor.

        **Recommendation**
        - Monitor inventory for high-performing categories.
        - Identify products with high revenue but low sales volume.
        - Improve product visibility for promising categories.
        """)

        st.subheader("5. Freight Cost")
        st.markdown("""
        **Finding**
        - Freight represents approximately 16.57% of product revenue.

        **Recommendation**
        - Analyze freight costs by seller and customer state.
        - Identify expensive delivery routes.
        - Explore more efficient shipping options.
        """)

        st.subheader("6. Business Monitoring")
        st.markdown("""
        **Finding**
        - The platform tracks sales, customers, sellers,
          products and delivery performance.

        **Recommendation**
        - Review KPIs monthly.
        - Track customer retention and delivery delays.
        - Compare actual performance against business targets.
        """)

    st.info(
        "Note: These recommendations are based on historical "
        "Olist dataset patterns. They are suggestions for "
        "business investigation, not proven causal outcomes."
    )


except Exception as e:
    st.error(f"Dashboard error: {e}")
