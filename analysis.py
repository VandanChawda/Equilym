import pandas as pd


# ============================================================
# PART A — DATA LOADING & VALIDATION
# ============================================================

REQUIRED_COLUMNS = [
    "month",
    "district",
    "anc_coverage",
    "institutional_delivery",
    "immunization",
    "high_risk_cases"
]

INDICATOR_COLUMNS = [
    "anc_coverage",
    "institutional_delivery",
    "immunization",
    "high_risk_cases"
]


def load_data(file_path):
    """
    Load the healthcare CSV file and prepare the data.
    """

    df = pd.read_csv(file_path)

    # Convert month column to datetime
    df["month"] = pd.to_datetime(df["month"])

    return df


def validate_data(df):
    """
    Validate the structure and contents of the dataset.

    Returns:
        list: Validation errors.
    """

    errors = []

   
    # 1. Check required columns
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(
            f"Missing required columns: {missing_columns}"
        )

        # Cannot continue validation if columns are missing
        return errors

    # --------------------------------------------------------
    # 2. Check missing values
    

    missing_values = df[REQUIRED_COLUMNS].isnull().sum()

    for column, count in missing_values.items():

        if count > 0:
            errors.append(
                f"{column} contains {count} missing value(s)"
            )

    # --------------------------------------------------------
    # 3. Check numeric columns
    # --------------------------------------------------------

    for column in INDICATOR_COLUMNS:

        if not pd.api.types.is_numeric_dtype(df[column]):

            errors.append(
                f"{column} must contain numeric values"
            )

    # --------------------------------------------------------
    # 4. Check duplicate district-month combinations
    # --------------------------------------------------------

    duplicates = df.duplicated(
        subset=["district", "month"]
    ).sum()

    if duplicates > 0:

        errors.append(
            f"Found {duplicates} duplicate district-month row(s)"
        )

    return errors


def get_missing_value_report(df):

    return df.isnull().sum()


# ============================================================
# PART B — TREND DETECTION
# ============================================================

def detect_trends(df, threshold=10):


    trends = []

    # Make a copy so original dataframe is not modified
    data = df.copy()

    # Sort data so previous/current months are in correct order
    data = data.sort_values(
        by=["district", "month"]
    )

    # --------------------------------------------------------
    # Process every district
    # --------------------------------------------------------

    for district in data["district"].unique():

        district_data = data[
            data["district"] == district
        ].sort_values("month")

        # ----------------------------------------------------
        # Process every indicator
        # ----------------------------------------------------

        for indicator in INDICATOR_COLUMNS:

            previous_value = None
            previous_month = None

            # ------------------------------------------------
            # Compare consecutive months
            # ------------------------------------------------

            for _, row in district_data.iterrows():

                current_value = row[indicator]
                current_month = row["month"]

                # We need a previous value for comparison
                if previous_value is not None:

                    # Avoid division by zero
                    if previous_value != 0:

                        pct_change = (
                            (current_value - previous_value)
                            / previous_value
                        ) * 100

                        is_significant = (
                            abs(pct_change) >= threshold
                        )

                        # Add only significant trends
                        if is_significant:

                            trends.append({
                                "district": district,
                                "indicator": indicator,
                                "previous_month": previous_month,
                                "current_month": current_month,
                                "previous_value": previous_value,
                                "current_value": current_value,
                                "pct_change": round(
                                    pct_change, 2
                                ),
                                "is_significant": True
                            })

                # Current becomes previous for next iteration
                previous_value = current_value
                previous_month = current_month

    return pd.DataFrame(trends)

# ============================================================
# PART C — OUTLIER DETECTION
# ============================================================

def detect_outliers_iqr(df):
 

    outliers = []

    # Check every numerical indicator
    for indicator in INDICATOR_COLUMNS:

        # Calculate Q1 and Q3
        q1 = df[indicator].quantile(0.25)
        q3 = df[indicator].quantile(0.75)

        # Calculate IQR
        iqr = q3 - q1

        # Calculate lower and upper boundaries
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Find values outside the boundaries
        indicator_outliers = df[
            (df[indicator] < lower_bound)
            |
            (df[indicator] > upper_bound)
        ]

        # Store every detected outlier
        for _, row in indicator_outliers.iterrows():

            outliers.append({
                "district": row["district"],
                "indicator": indicator,
                "month": row["month"],
                "value": row[indicator],
                "q1": round(q1, 2),
                "q3": round(q3, 2),
                "iqr": round(iqr, 2),
                "lower_bound": round(lower_bound, 2),
                "upper_bound": round(upper_bound, 2)
            })

    return pd.DataFrame(outliers)


# ============================================================
# PART D — CORRELATION DETECTION
# ============================================================

def calculate_correlation_matrix(df):
    """
    Calculate Pearson correlation matrix
    for all numerical indicators.
    """

    correlation_matrix = df[INDICATOR_COLUMNS].corr(
        method="pearson"
    )

    return correlation_matrix


def detect_correlations(df, threshold=0.70):


    correlation_matrix = calculate_correlation_matrix(df)

    correlations = []

    # Compare every unique pair of indicators
    for i in range(len(INDICATOR_COLUMNS)):

        for j in range(i + 1, len(INDICATOR_COLUMNS)):

            indicator_1 = INDICATOR_COLUMNS[i]
            indicator_2 = INDICATOR_COLUMNS[j]

            correlation_value = correlation_matrix.loc[
                indicator_1,
                indicator_2
            ]

            # Skip if correlation cannot be calculated
            if pd.isna(correlation_value):
                continue

            # Check configurable threshold
            if abs(correlation_value) >= threshold:

                correlations.append({
                    "indicator_1": indicator_1,
                    "indicator_2": indicator_2,
                    "correlation": round(
                        correlation_value,
                        3
                    ),
                    "absolute_correlation": round(
                        abs(correlation_value),
                        3
                    )
                })

    return pd.DataFrame(correlations)