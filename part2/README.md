## Analysis Summary

**Initial inspection (Task 1):** `df.info()` and `df.describe(include='all')` confirm
99,440 rows, 8 columns, no missing values. Two numeric columns (`payment_value`,
`delivery_days`).

**NumPy fundamentals (Task 2):** `payment_value` converted to an ndarray; a vectorized
10% discount applied across the whole array in one line; Boolean-indexed filtering with
two conditions (`>= 100` **and** `<= 500`) returned 47,889 mid-range values.

**Descriptive statistics (Task 3, via NumPy):**

| Column         | Mean   | Median | Std    | Variance  | 90th pct |
|----------------|--------|--------|--------|-----------|----------|
| payment_value  | 160.99 | 105.29 | 221.95 | 49,261.86 | 308.24   |
| delivery_days  | 12.49  | 10.22  | 9.41   | 88.56     | 22.89    |

**Feature engineering (Task 4):** created `payment_per_day = payment_value / delivery_days`.

**Grouped analysis (Task 5):** two pivot tables (mean payment by state; mean delivery
days by order status) and one multi-aggregation `groupby().agg()` computing mean+sum on
`payment_value` and mean+max on `delivery_days` in a single call.

**Bucket segmentation (Task 6):** a function maps `payment_value` into four labelled
buckets (Low <50, Medium 50–150, High 150–500, Very High 500+), applied with `.apply()`
to create `payment_segment`. Medium is the largest segment (50,167 orders).

**Correlation analysis (Task 7):** Pearson matrix across the three numeric columns.
- **Highest |correlation| pair:** `payment_value` & `payment_per_day` = **0.699**
  (expected, since `payment_per_day` is derived from `payment_value`).
- **Lowest |correlation| pair:** `payment_value` & `delivery_days` = **0.066**.
- **Ties:** none. **NaN handling:** NaN correlations were skipped when identifying
  pairs; none occurred here (no zero-variance numeric column). The diagonal
  (self-correlation = 1) was excluded by only evaluating unique column pairs.

## Hypothesis Test (Tasks 8 & 9)

**Business claim:** The average order payment value differs between customers in
São Paulo (SP) and Rio de Janeiro (RJ).

- **H0 (null):** mean payment value for SP = mean for RJ (μ_SP = μ_RJ).
- **H1 (alternate):** the means differ (μ_SP ≠ μ_RJ).
- **Significance level:** α = 0.05.
- **Test used:** two-sample independent t-test (Welch's, `equal_var=False`), the
  appropriate test for comparing the means of two independent groups.
- **Assumption checked:** both groups are right-skewed (SP skew ≈ 7.2, RJ skew ≈ 17.4),
  but with large sample sizes (SP n=41,745; RJ n=12,852) the Central Limit Theorem makes
  the t-test on the means valid. Observations are independent (different customers).

**Result:**

| Group | n      | Mean payment |
|-------|--------|--------------|
| SP    | 41,745 | 143.69       |
| RJ    | 12,852 | 166.85       |

- **T-statistic:** −9.83
- **P-value:** < 0.000001
- **Decision:** **REJECT H0** — the difference in average payment value between SP and
  RJ is statistically significant at α = 0.05.

## Visualizations (Task 10)

Four labelled charts, each with a title and axis labels, saved as PNGs:

1. `chart_heatmap.png` — Seaborn correlation heatmap (`annot=True`).
2. `chart_scatter.png` — Seaborn scatter of payment value vs delivery days, `hue` split
   by payment segment.
3. `chart_barplot.png` — average payment value by state (top 10).
4. `chart_histogram.png` — distribution of payment value (with KDE).

## Insights & Recommendations (Task 11)

**1. Payment value is highly right-skewed.** Mean is R$161 but median is only R$105,
with 90% of orders under R$308 while the max reaches R$13,664. The histogram confirms a
strong right skew.
→ **Recommendation:** Build inventory and pricing strategy around the R$50–150 core
segment (50,167 of 99,440 orders), and create a separate handling flow for the rare
high-value orders rather than optimising for the average.

**2. São Paulo is high-volume but low-value per order; Rio is the opposite.** SP has the
lowest mean payment (R$143.69) yet the highest total revenue (R$6.0M) and fastest mean
delivery (8.8 days), while RJ averages more per order (R$166.85) but is slower (15.1 days).
The SP-vs-RJ payment difference is statistically significant (t = −9.83, p < 0.001).
→ **Recommendation:** Treat SP as a high-volume logistics strength and protect its speed
advantage; investigate RJ's slower delivery as a potential retention risk given its
higher order values.

**3. Payment value and delivery time are essentially uncorrelated (r = 0.066).**
Customers who pay more do not receive — or pay for — faster delivery.
→ **Recommendation:** Delivery speed is not currently priced in. Test premium expedited-
shipping options to capture willingness-to-pay, especially in the High and Very High
payment segments.


