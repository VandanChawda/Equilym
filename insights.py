import pandas as pd
# PART E — AUTOMATED INSIGHT GENERATION


def get_severity_from_percentage(change_pct, threshold):
    """
    Determine severity based on the size of the percentage change
    relative to the configured threshold.

    Low    : below 2 × threshold
    Medium : 2 × threshold to below 3 × threshold
    High   : 3 × threshold or more
    """

    magnitude = abs(change_pct)

    if magnitude >= threshold * 3:
        return "High"

    elif magnitude >= threshold * 2:
        return "Medium"

    else:
        return "Low"


def get_outlier_severity(value, lower_bound, upper_bound, iqr):
    """
    Determine outlier severity based on how far the value
    lies outside the IQR boundaries.
    """

    if value > upper_bound:
        distance = value - upper_bound

    else:
        distance = lower_bound - value

    # Avoid division by zero
    if iqr == 0:
        return "High"

    relative_distance = distance / iqr

    if relative_distance >= 1.5:
        return "High"

    elif relative_distance >= 0.5:
        return "Medium"

    else:
        return "Low"


def get_correlation_severity(correlation, threshold):
    """
    Determine correlation severity based on the strength
    of the detected correlation relative to the threshold.
    """

    strength = abs(correlation)

    if strength >= threshold * 1.25:
        return "High"

    elif strength >= threshold:
        return "Medium"

    return "Low"


def generate_insights(
    trend_results,
    outlier_results,
    correlation_results,
    trend_threshold=10,
    correlation_threshold=0.70
):
 

    insights = []

    insight_number = 1

    # ========================================================
    # TREND INSIGHTS
    # ========================================================

    for _, row in trend_results.iterrows():

        change_pct = row["pct_change"]

        severity = get_severity_from_percentage(
            change_pct,
            trend_threshold
        )

        indicator = row["indicator"]
        district = row["district"]

        current_value = row["current_value"]
        previous_value = row["previous_value"]

        current_month = row["current_month"]

        # Determine increase/decrease
        if change_pct >= 0:
            direction = "increased"
        else:
            direction = "decreased"

        explanation = (
            f"{indicator.replace('_', ' ').title()} "
            f"in {district} {direction} by "
            f"{abs(change_pct):.1f}% from "
            f"{previous_value:g} to {current_value:g}, "
            f"exceeding the {trend_threshold}% "
            f"significant-change threshold."
        )

        insights.append({
            "insight_id": f"INS-{insight_number:04d}",
            "type": "trend",
            "indicator": indicator,
            "entity": district,
            "period": current_month.strftime("%Y-%m"),
            "value": float(current_value),
            "prev_value": float(previous_value),
            "change_pct": float(change_pct),
            "severity": severity,
            "explanation": explanation
})

        insight_number += 1

    # ========================================================
    # OUTLIER INSIGHTS
    # ========================================================

    for _, row in outlier_results.iterrows():

        value = row["value"]

        lower_bound = row["lower_bound"]
        upper_bound = row["upper_bound"]
        iqr = row["iqr"]

        severity = get_outlier_severity(
            value,
            lower_bound,
            upper_bound,
            iqr
        )

        indicator = row["indicator"]
        district = row["district"]

        month = row["month"]

        # Determine whether the value is high or low
        if value > upper_bound:
            position = "above"

            deviation = value - upper_bound

        else:
            position = "below"

            deviation = lower_bound - value

        explanation = (
            f"{district}'s "
            f"{indicator.replace('_', ' ').title()} "
            f"value of {value:g} in "
            f"{month.strftime('%Y-%m')} is an outlier, "
            f"falling {deviation:.2f} units {position} "
            f"the IQR boundary."
        )

        insights.append({
    "insight_id": f"INS-{insight_number:04d}",
    "type": "outlier",
    "indicator": indicator,
    "entity": district,
    "period": month.strftime("%Y-%m"),
    "value": float(value),
    "prev_value": None,
    "change_pct": None,
    "severity": severity,
    "explanation": explanation
})

        insight_number += 1

    # ========================================================
    # CORRELATION INSIGHTS
    # ========================================================

    for _, row in correlation_results.iterrows():

        indicator_1 = row["indicator_1"]
        indicator_2 = row["indicator_2"]

        correlation = row["correlation"]

        severity = get_correlation_severity(
            correlation,
            correlation_threshold
        )

        # Determine positive or negative relationship
        if correlation > 0:
            relationship = "positive"
        else:
            relationship = "negative"

        explanation = (
            f"{indicator_1.replace('_', ' ').title()} and "
            f"{indicator_2.replace('_', ' ').title()} show a "
            f"{relationship} Pearson correlation of "
            f"{correlation:.2f}, exceeding the "
            f"|r| ≥ {correlation_threshold:.2f} threshold."
        )

        insights.append({
    "insight_id": f"INS-{insight_number:04d}",
    "type": "correlation",
    "indicator": (
        f"{indicator_1}:{indicator_2}"
    ),
    "entity": "All districts",
    "period": "Dataset",
    "value": float(correlation),
    "prev_value": None,
    "change_pct": None,
    "severity": severity,
    "explanation": explanation
})

        insight_number += 1

    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    columns = [
    "insight_id",
    "type",
    "indicator",
    "entity",
    "period",
    "value",
    "prev_value",
    "change_pct",
    "severity",
    "explanation"
]

    return pd.DataFrame(
        insights,
        columns=columns
    )