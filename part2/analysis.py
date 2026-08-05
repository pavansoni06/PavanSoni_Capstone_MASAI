import pandas as pd
import numpy as np

# ============================================================
# Task 1: Load the dataset and inspect it
# ============================================================
df = pd.read_csv("cleaned_data.csv")

print("=" * 60)
print("TASK 1: INITIAL INSPECTION")
print("=" * 60)

print("\n--- df.info() ---")
df.info()

print("\n--- df.describe(include='all') ---")
print(df.describe(include="all"))



# ============================================================
# Task 2: NumPy fundamentals
# ============================================================
print("\n" + "=" * 60)
print("TASK 2: NUMPY FUNDAMENTALS")
print("=" * 60)

# Convert the payment_value column into a NumPy ndarray
payments = df["payment_value"].to_numpy()
print("\nType of 'payments':", type(payments))
print("First 5 payment values:", payments[:5])

# --- Vectorized arithmetic: apply a 10% discount to EVERY value at once ---
# No Python loop; NumPy applies the operation across the whole array.
discounted = payments * 0.90
print("\nFirst 5 after 10% discount:", discounted[:5].round(2))

# --- Boolean-indexed filtering: two conditions combined with & ---
# Keep payments that are BETWEEN 100 and 500 (mid-range orders).
mid_range = payments[(payments >= 100) & (payments <= 500)]
print(f"\nPayments between 100 and 500: {len(mid_range)} values")
print("First 5 of those:", mid_range[:5].round(2))



# ============================================================
# Task 3: Descriptive statistics using NumPy (2 numeric columns)
# ============================================================
print("\n" + "=" * 60)
print("TASK 3: DESCRIPTIVE STATISTICS (NumPy)")
print("=" * 60)

for col in ["payment_value", "delivery_days"]:
    arr = df[col].to_numpy()
    print(f"\n--- {col} ---")
    print(f"  Mean:            {np.mean(arr):.2f}")
    print(f"  Median:          {np.median(arr):.2f}")
    print(f"  Std deviation:   {np.std(arr):.2f}")
    print(f"  Variance:        {np.var(arr):.2f}")
    print(f"  90th percentile: {np.percentile(arr, 90):.2f}")


# ============================================================
# Task 4: Feature engineering (new column from two columns)
# ============================================================
print("\n" + "=" * 60)
print("TASK 4: FEATURE ENGINEERING")
print("=" * 60)

# New column: payment per delivery day.
# Combines two existing columns (payment_value / delivery_days) into a
# "value density" measure — how much money the order represents per day
# it took to arrive. Guard against divide-by-zero with a small floor.
df["payment_per_day"] = df["payment_value"] / df["delivery_days"].clip(lower=0.5)

print("\nNew column 'payment_per_day' created from payment_value / delivery_days.")
print(df[["payment_value", "delivery_days", "payment_per_day"]].head())


# ============================================================
# Task 5: Grouped analysis (2 pivot tables + 1 multi-agg groupby)
# ============================================================
print("\n" + "=" * 60)
print("TASK 5: GROUPED ANALYSIS")
print("=" * 60)

# --- Pivot table 1: average payment_value per customer_state ---
pivot1 = df.pivot_table(
    index="customer_state",
    values="payment_value",
    aggfunc="mean"
)
print("\n--- Pivot 1: mean payment_value by state (top 5) ---")
print(pivot1.sort_values("payment_value", ascending=False).head())

# --- Pivot table 2: average delivery_days per order_status ---
pivot2 = df.pivot_table(
    index="order_status",
    values="delivery_days",
    aggfunc="mean"
)
print("\n--- Pivot 2: mean delivery_days by order_status ---")
print(pivot2.sort_values("delivery_days", ascending=False))

# --- Multi-aggregation groupby: 2+ functions across 2+ columns in ONE call ---
multi_agg = df.groupby("customer_state").agg({
    "payment_value": ["mean", "sum"],
    "delivery_days": ["mean", "max"]
})
print("\n--- Multi-agg groupby by state (top 5 by payment sum) ---")
print(multi_agg.sort_values(("payment_value", "sum"), ascending=False).head())



# ============================================================
# Task 6: Bucket segmentation (function + .apply())
# ============================================================
print("\n" + "=" * 60)
print("TASK 6: BUCKET SEGMENTATION")
print("=" * 60)

# A function that maps a payment amount into one of four labelled buckets.
def payment_bucket(value):
    if value < 50:
        return "Low (<50)"
    elif value < 150:
        return "Medium (50-150)"
    elif value < 500:
        return "High (150-500)"
    else:
        return "Very High (500+)"

# Apply the function across the payment_value column to create a new column.
df["payment_segment"] = df["payment_value"].apply(payment_bucket)

print("\nNew column 'payment_segment' created.")
print("\n--- Counts per segment ---")
print(df["payment_segment"].value_counts())

print("\n--- df.head() showing the new column ---")
print(df[["payment_value", "payment_segment"]].head())



# ============================================================
# Task 7: Correlation analysis
# ============================================================
print("\n" + "=" * 60)
print("TASK 7: CORRELATION ANALYSIS")
print("=" * 60)

# Pearson correlation matrix across all numeric columns
corr = df.corr(numeric_only=True)
print("\n--- Correlation matrix ---")
print(corr.round(3))

# Find highest and lowest correlated PAIRS, excluding the diagonal (self-corr = 1)
import itertools
pairs = []
for a, b in itertools.combinations(corr.columns, 2):
    value = corr.loc[a, b]
    if pd.notna(value):          # skip NaN correlations (e.g. zero-variance columns)
        pairs.append((a, b, value))

# Sort by absolute correlation
pairs_sorted = sorted(pairs, key=lambda x: abs(x[2]))

lowest = pairs_sorted[0]
highest = pairs_sorted[-1]

print(f"\nHighest |correlation| pair: {highest[0]} & {highest[1]} = {highest[2]:.3f}")
print(f"Lowest  |correlation| pair: {lowest[0]} & {lowest[1]} = {lowest[2]:.3f}")
print(f"\nTotal numeric-column pairs evaluated: {len(pairs)}")





# ============================================================
# Task 9: Run the hypothesis test (two-sample t-test)
# ============================================================
print("\n" + "=" * 60)
print("TASK 9: HYPOTHESIS TEST (SP vs RJ payment value)")
print("=" * 60)

from scipy import stats

# Two groups: payment values for SP customers vs RJ customers
sp_payments = df[df["customer_state"] == "SP"]["payment_value"]
rj_payments = df[df["customer_state"] == "RJ"]["payment_value"]

print(f"\nSP: n={len(sp_payments)}, mean={sp_payments.mean():.2f}")
print(f"RJ: n={len(rj_payments)}, mean={rj_payments.mean():.2f}")

# Quick assumption check: skewness of each group (one-line check, as allowed)
print(f"\nAssumption check (skew): SP skew={sp_payments.skew():.2f}, "
      f"RJ skew={rj_payments.skew():.2f}")
print("Both groups are right-skewed, but sample sizes are large (thousands),")
print("so by the Central Limit Theorem the t-test on the means is still valid.")

# Run the independent two-sample t-test.
# equal_var=False -> Welch's t-test, which does not assume equal variances (safer).
t_stat, p_value = stats.ttest_ind(sp_payments, rj_payments, equal_var=False)

alpha = 0.05
print(f"\nT-statistic: {t_stat:.4f}")
print(f"P-value:     {p_value:.6f}")
print(f"Significance level (alpha): {alpha}")

if p_value < alpha:
    print("\nDecision: REJECT H0 -> the mean payment values DIFFER significantly.")
else:
    print("\nDecision: FAIL TO REJECT H0 -> no significant difference in means.")





# ============================================================
# Task 10: Four labelled visualizations, saved as PNGs
# ============================================================
print("\n" + "=" * 60)
print("TASK 10: VISUALIZATIONS")
print("=" * 60)

import matplotlib
matplotlib.use("Agg")   # save-to-file backend, no popup windows needed
import matplotlib.pyplot as plt
import seaborn as sns

# --- (a) Correlation heatmap with annotations ---
plt.figure(figsize=(6, 5))
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Heatmap of Numeric Columns")
plt.tight_layout()
plt.savefig("chart_heatmap.png")
plt.close()
print("Saved chart_heatmap.png")

# --- (b) Scatter plot with hue by a categorical column ---
# Sample 2000 rows so the plot isn't overcrowded; hue splits by payment_segment.
sample = df.sample(2000, random_state=42)
plt.figure(figsize=(8, 6))
sns.scatterplot(data=sample, x="delivery_days", y="payment_value",
                hue="payment_segment", alpha=0.6)
plt.title("Payment Value vs Delivery Days (by Payment Segment)")
plt.xlabel("Delivery Days")
plt.ylabel("Payment Value (R$)")
plt.tight_layout()
plt.savefig("chart_scatter.png")
plt.close()
print("Saved chart_scatter.png")

# --- (c) Bar plot: average payment_value by state (top 10 states) ---
top_states = df.groupby("customer_state")["payment_value"].mean().sort_values(ascending=False).head(10)
plt.figure(figsize=(9, 5))
sns.barplot(x=top_states.index, y=top_states.values, hue=top_states.index, legend=False, palette="viridis")
plt.title("Average Payment Value by State (Top 10)")
plt.xlabel("Customer State")
plt.ylabel("Average Payment Value (R$)")
plt.tight_layout()
plt.savefig("chart_barplot.png")
plt.close()
print("Saved chart_barplot.png")

# --- (d) Distribution plot: histogram of payment_value ---
# Clip at 500 so the long tail doesn't flatten the visible distribution.
plt.figure(figsize=(8, 5))
sns.histplot(df[df["payment_value"] <= 500]["payment_value"], bins=50, kde=True)
plt.title("Distribution of Payment Value (up to R$500)")
plt.xlabel("Payment Value (R$)")
plt.ylabel("Number of Orders")
plt.tight_layout()
plt.savefig("chart_histogram.png")
plt.close()
print("Saved chart_histogram.png")

print("\nAll four charts saved.")


