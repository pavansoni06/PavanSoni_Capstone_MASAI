import pandas as pd

# --- Load the exported CSV ---
df = pd.read_csv("joined_export.csv")
print("Loaded shape (rows, columns):", df.shape)

# ============================================================
# Task 7a: report missing values (count and percentage) per column
# ============================================================
print("\n--- Missing values BEFORE cleaning ---")
missing_count = df.isnull().sum()
missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
missing_report = pd.DataFrame({
    "missing_count": missing_count,
    "missing_percent": missing_pct
})
print(missing_report)

# ============================================================
# Task 7b: impute missing values
#   - numeric columns  -> median (robust to outliers)
#   - text columns     -> the literal string "unknown"
# ============================================================
for col in df.columns:
    if df[col].isnull().sum() == 0:
        continue  # nothing missing, skip
    if pd.api.types.is_numeric_dtype(df[col]):
        median_value = df[col].median()
        df[col] = df[col].fillna(median_value)
        print(f"Filled numeric column '{col}' with median = {median_value}")
    else:
        df[col] = df[col].fillna("unknown")
        print(f"Filled text column '{col}' with 'unknown'")

# Confirm no missing values remain
print("\n--- Missing values AFTER imputation (should all be 0) ---")
print(df.isnull().sum())

# ============================================================
# Task 7c: detect and remove duplicate rows
# ============================================================
before = len(df)
df = df.drop_duplicates()
after = len(df)
print(f"\nDuplicate removal: {before} rows before, {after} rows after "
      f"({before - after} duplicates removed)")

# Save the cleaned result for later use (Part 2)
df.to_csv("cleaned_data.csv", index=False)
print("\nSaved cleaned data to cleaned_data.csv")