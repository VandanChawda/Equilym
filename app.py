import streamlit as st
from insights import generate_insights

from analysis import (
    load_data,
    validate_data,
    get_missing_value_report,
    detect_trends,
    detect_outliers_iqr,
    calculate_correlation_matrix,
    detect_correlations,
    INDICATOR_COLUMNS
)


from analysis import (
    load_data,
    validate_data,
    get_missing_value_report,
    detect_trends
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Automated Insight Generation",
    page_icon="📊",
    layout="wide"
)


st.title("📊 Automated Insight Generation")
st.subheader("Healthcare Performance Analytics")


# ============================================================
# LOAD DATA
# ============================================================

DATA_PATH = "data/healthcare_data.csv"

df = load_data(DATA_PATH)


# ============================================================
# PART A — DATA VALIDATION
# ============================================================

st.header("Part A — Data Loading & Validation")


# Display first rows
st.subheader("Dataset Preview")

st.dataframe(
    df.head(),
    use_container_width=True
)


# Display dataset information
st.subheader("Dataset Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Rows",
        df.shape[0]
    )

with col2:
    st.metric(
        "Columns",
        df.shape[1]
    )

with col3:
    st.metric(
        "Districts",
        df["district"].nunique()
    )


# Missing-value report
st.subheader("Missing Values")

missing_report = get_missing_value_report(df)

st.dataframe(
    missing_report.rename("Missing Values"),
    use_container_width=True
)


# Validation
validation_errors = validate_data(df)

if validation_errors:

    st.error("Dataset validation failed.")

    for error in validation_errors:
        st.write(f"❌ {error}")

else:

    st.success("✅ Dataset validation successful!")


# ============================================================
# FILTERS
# ============================================================

st.header("Filters")


col1, col2, col3 = st.columns(3)


# District filter
with col1:

    districts = sorted(
        df["district"].unique()
    )

    selected_district = st.multiselect(
        "District",
        districts,
        default=districts
    )


# Month filter
with col2:

    months = sorted(
        df["month"].dt.strftime("%Y-%m").unique()
    )

    selected_month = st.multiselect(
        "Month",
        months,
        default=months
    )


# Indicator filter
with col3:

    indicators = [
        "anc_coverage",
        "institutional_delivery",
        "immunization",
        "high_risk_cases"
    ]

    selected_indicator = st.multiselect(
        "Indicator",
        indicators,
        default=indicators
    )


# ============================================================
# APPLY FILTERS
# ============================================================

# ============================================================
# APPLY LIVE FILTERS
# ============================================================

# Data filtered by district and month
# ============================================================
# APPLY LIVE FILTERS
# ============================================================

filtered_df = df[
    df["district"].isin(selected_district)
    &
    df["month"].dt.strftime("%Y-%m").isin(selected_month)
]

# Keep only selected indicators plus required columns
columns_to_keep = [
    "month",
    "district"
] + selected_indicator

filtered_df = filtered_df[columns_to_keep]


st.subheader("Filtered Dataset")

st.dataframe(
    filtered_df,
    use_container_width=True
)


# ============================================================
# PART B — TREND DETECTION
# ============================================================

st.header("Part B — Trend Detection")


# Configurable threshold
threshold = st.slider(
    "Significant Change Threshold (%)",
    min_value=1,
    max_value=100,
    value=10,
    step=1
)


st.write(
    f"Current threshold: **{threshold}%**"
)


# Run trend detection
trend_results = detect_trends(
    filtered_df,
    threshold=threshold
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

st.subheader("Significant Trends")


if trend_results.empty:

    st.info(
        "No significant trends found "
        "for the selected filters."
    )

else:

    st.dataframe(
        trend_results,
        use_container_width=True
    )

# ============================================================
# PART C — OUTLIER DETECTION
# ============================================================

st.header("Part C — Outlier Detection")

st.write(
    "Outliers are detected using the IQR "
    "(Interquartile Range) method."
)


# Detect outliers
outlier_results = detect_outliers_iqr(
    filtered_df
)


# Display results
st.subheader("Detected Outliers")


if outlier_results.empty:

    st.info(
        "No outliers found for the selected filters."
    )

else:

    # Show only the important columns first
    display_columns = [
        "district",
        "indicator",
        "month",
        "value",
        "lower_bound",
        "upper_bound"
    ]

    st.dataframe(
        outlier_results[display_columns],
        use_container_width=True
    )


# PART D — CORRELATION DETECTION


st.header("Part D — Correlation Detection")

st.write(
    "Pearson correlation is calculated across "
    "the numerical healthcare indicators."
)


# ------------------------------------------------------------
# Correlation threshold
# ------------------------------------------------------------

correlation_threshold = st.slider(
    "Correlation Threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.70,
    step=0.05
)


st.write(
    f"Current correlation threshold: "
    f"**{correlation_threshold:.2f}**"
)


# ------------------------------------------------------------
# Correlation matrix


st.subheader("Pearson Correlation Matrix")


correlation_matrix = calculate_correlation_matrix(
    filtered_df
)


st.dataframe(
    correlation_matrix,
    use_container_width=True
)


# ------------------------------------------------------------
# Flag strong correlations


correlation_results = detect_correlations(
    filtered_df,
    threshold=correlation_threshold
)


st.subheader("Significant Correlations")


if correlation_results.empty:

    st.info(
        "No correlation pairs found "
        "above the selected threshold."
    )

else:

    st.dataframe(
        correlation_results,
        use_container_width=True
    )


# Important limitation

st.warning(
    "Correlation results should be interpreted carefully. "
    "The sample dataset contains only 2 months × 6 districts, "
    "so Pearson correlations may be unstable."
)

# ============================================================
# PART E — AUTOMATED INSIGHT GENERATION
# ============================================================

st.header("Part E — Automated Insight Generation")

st.write(
    "Insights are generated dynamically from the "
    "detected trends, outliers and correlations."
)


# ============================================================
# GENERATE INSIGHTS
# ============================================================

insights_df = generate_insights(
    trend_results=trend_results,
    outlier_results=outlier_results,
    correlation_results=correlation_results,
    trend_threshold=threshold,
    correlation_threshold=correlation_threshold
)


# ============================================================
# DISPLAY INSIGHTS
# ============================================================

st.subheader("Generated Insights")


if insights_df.empty:

    st.info(
        "No insights were generated for the "
        "selected filters and thresholds."
    )

else:

    st.dataframe(
        insights_df,
        use_container_width=True
    )


# ============================================================
# DOWNLOAD INSIGHTS
# ============================================================

if not insights_df.empty:

    csv_data = insights_df.to_csv(
        index=False
    )

    st.download_button(
        label="Download Insights CSV",
        data=csv_data,
        file_name="insights.csv",
        mime="text/csv"
    )

# ============================================================
# PART F — UI & VISUALIZATION
# ============================================================

st.header("Part F — Visualizations")


# ------------------------------------------------------------
# 1. INSIGHT LIST
# ------------------------------------------------------------

st.subheader("Generated Insights")

if insights_df.empty:
    st.info("No insights found.")
else:
    st.dataframe(
        insights_df,
        use_container_width=True
    )

# ============================================================
# 2. SEVERITY COUNTS — BAR CHART
# ============================================================

st.subheader("Severity Counts")

if insights_df.empty:
    st.info("No severity data available.")

else:
    severity_counts = (
        insights_df["severity"]
        .value_counts()
        .reindex(
            ["Low", "Medium", "High"],
            fill_value=0
        )
        .reset_index()
    )

    severity_counts.columns = [
        "Severity",
        "Count"
    ]

    st.bar_chart(
        severity_counts,
        x="Severity",
        y="Count"
    )

# ------------------------------------------------------------
# 3. CORRELATION HEATMAP
# ------------------------------------------------------------

st.subheader("Correlation Heatmap")

import plotly.express as px

fig = px.imshow(
    correlation_matrix,
    text_auto=True,
    title="Pearson Correlation"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ------------------------------------------------------------
# 4. PER-DISTRICT LINE CHART
# ------------------------------------------------------------

st.subheader("District Trend")

district = st.selectbox(
    "Select District",
    df["district"].unique()
)

indicator = st.selectbox(
    "Select Indicator",
    INDICATOR_COLUMNS
)

chart_data = df[
    df["district"] == district
].sort_values("month")

fig = px.line(
    chart_data,
    x="month",
    y=indicator,
    markers=True,
    title=f"{indicator} - {district}"
)

st.plotly_chart(
    fig,
    use_container_width=True
)