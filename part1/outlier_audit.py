import pandas as pd
import numpy as np

df = pd.read_csv("cleaned_data.csv")

# ============================================================
# Our filtering rule for "continuous numeric measure":
#   INCLUDE a column only if it is numeric AND has meaningful spread.
#   EXCLUDE:
#     - ID / key columns (customer_id, order_id) -> identifiers, not measures
#     - text/categorical columns (state, city, status, timestamp) -> not numeric
#     - any numeric column with near-zero variance -> no meaningful outliers
#   The columns that survive here are: payment_value and delivery_days.
# ============================================================
candidate_cols = df.select_dtypes(include=[np.number]).columns.tolist()

continuous_cols = []
for col in candidate_cols:
    # exclude anything that looks like an id/key by name
    if "id" in col.lower():
        continue
    # exclude near-zero-variance columns
    if df[col].std() < 1e-9:
        continue
    continuous_cols.append(col)

print("Columns audited as continuous numeric measures:", continuous_cols)

# ============================================================
# Run BOTH methods on each surviving column
# ============================================================
for col in continuous_cols:
    data = df[col]

    # ---- Method 1: IQR ----
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    iqr_outliers = ((data < lower_fence) | (data > upper_fence)).sum()

    # ---- Method 2: Z-score ----
    mean = data.mean()
    std = data.std()
    z_scores = (data - mean) / std
    z_outliers = (z_scores.abs() > 3).sum()

    print(f"\n--- Column: {col} ---")
    print(f"  IQR method:  Q1={q1:.2f}, Q3={q3:.2f}, IQR={iqr:.2f}")
    print(f"               lower fence={lower_fence:.2f}, upper fence={upper_fence:.2f}")
    print(f"               outliers flagged: {iqr_outliers}")
    print(f"  Z-score method (|Z| > 3): outliers flagged: {z_outliers}")
    if iqr_outliers > z_outliers:
        print("  -> IQR flags MORE outliers (it is stricter / more sensitive here).")
    elif z_outliers > iqr_outliers:
        print("  -> Z-score flags MORE outliers.")
    else:
        print("  -> Both methods agree on the count.")