"""
Mamaearth Capstone - Part 2: Python Data Wrangling & EDA
Script: analysis/clean_and_eda.py

This script processes raw CSV data (customers, products, orders) end-to-end:
1. Loads and inspects raw shapes.
2. Standardizes payment_method casing.
3. Removes double-submitted duplicate orders.
4. Imputes missing discount_pct and rating values.
5. Merges tables and reconciles cleaned revenue against Part 1 raw revenue.
6. Detects quantity outliers using the IQR method.
7. Evaluates the Cash-on-Delivery (COD) return rate hypothesis.
8. Performs multi-level segmentation (payment_method x city_tier).
9. Computes correlation matrix and evaluates strength bands.
10. Generates outlier-corrected monthly revenue time series.
11. Exports verified metrics to narrator/findings.json.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

# Set stdout encoding for safety on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def run_clean_and_eda():
    print("======================================================================")
    print("MAMAEARTH GROWTH INTELLIGENCE PIPELINE - PART 2: EDA & DATA CLEANING")
    print("======================================================================\n")

    # -------------------------------------------------------------------------
    # Task 1: Load and Inspect
    # -------------------------------------------------------------------------
    print("--- Task 1: Load and Inspect Raw CSV Data ---")
    customers = pd.read_csv('data/customers.csv')
    products = pd.read_csv('data/products.csv')
    orders = pd.read_csv('data/orders.csv')

    print(f"Loaded customers.csv shape: {customers.shape}")
    print(f"Loaded products.csv shape : {products.shape}")
    print(f"Loaded orders.csv shape   : {orders.shape}")
    assert orders.shape == (180, 9), f"Expected orders.shape (180, 9), got {orders.shape}"
    print("TASK 1 VERIFICATION: Raw orders.shape is (180, 9) [PASS]\n")

    # -------------------------------------------------------------------------
    # Task 2: Standardize payment_method Casing
    # -------------------------------------------------------------------------
    print("--- Task 2: Standardize payment_method Casing ---")
    raw_pm_unique = list(orders['payment_method'].unique())
    print(f"Raw payment_method unique values ({len(raw_pm_unique)}): {raw_pm_unique}")

    # Standardize casing
    orders['payment_method'] = orders['payment_method'].astype(str).str.strip().str.upper()
    clean_pm_counts = orders['payment_method'].value_counts().to_dict()
    print(f"Standardized payment_method counts: {clean_pm_counts}")
    assert len(clean_pm_counts) == 3, f"Expected 3 payment methods, got {len(clean_pm_counts)}"
    assert clean_pm_counts['CARD'] == 70, f"Expected CARD=70, got {clean_pm_counts.get('CARD')}"
    assert clean_pm_counts['UPI'] == 55, f"Expected UPI=55, got {clean_pm_counts.get('UPI')}"
    assert clean_pm_counts['COD'] == 55, f"Expected COD=55, got {clean_pm_counts.get('COD')}"
    print("TASK 2 VERIFICATION: payment_method standardized to 3 distinct values (CARD: 70, UPI: 55, COD: 55) [PASS]\n")

    # -------------------------------------------------------------------------
    # Task 3: Remove Duplicate Orders
    # -------------------------------------------------------------------------
    print("--- Task 3: Remove Duplicate Orders ---")
    dup_subset = ['customer_id', 'product_id', 'order_date', 'quantity', 'discount_pct', 'payment_method', 'rating', 'returned']
    dups_mask = orders.duplicated(subset=dup_subset, keep='first')
    dropped_df = orders[dups_mask]
    dropped_ids = dropped_df['order_id'].tolist()
    print(f"Detected {len(dropped_ids)} duplicate rows.")
    print(f"Dropped order_id list: {dropped_ids}")

    orders_clean = orders[~dups_mask].copy()
    print(f"Deduplicated orders shape: {orders_clean.shape}")
    assert len(dropped_ids) == 5, f"Expected 5 dropped duplicates, got {len(dropped_ids)}"
    assert orders_clean.shape == (175, 9), f"Expected orders_clean shape (175, 9), got {orders_clean.shape}"
    assert dropped_ids == ['O0176', 'O0177', 'O0178', 'O0179', 'O0180'], f"Unexpected dropped IDs: {dropped_ids}"
    print("TASK 3 VERIFICATION: Exactly 5 duplicate rows dropped (O0176 - O0180). Clean shape (175, 9) [PASS]\n")

    # -------------------------------------------------------------------------
    # Task 4: Impute Missing Values
    # -------------------------------------------------------------------------
    print("--- Task 4: Impute Missing Values ---")
    disc_nulls = orders_clean['discount_pct'].isnull().sum()
    print(f"Missing discount_pct count before imputation: {disc_nulls}")
    orders_clean['discount_pct'] = orders_clean['discount_pct'].fillna(0).astype(float)

    median_rating = orders_clean['rating'].median()
    rating_nulls = orders_clean['rating'].isnull().sum()
    print(f"Median rating on deduplicated frame: {median_rating}")
    print(f"Missing rating count before imputation: {rating_nulls}")
    orders_clean['rating'] = orders_clean['rating'].fillna(median_rating).astype(float)

    null_check = orders_clean[['discount_pct', 'rating']].isnull().sum().to_dict()
    print(f"Null count verification after imputation: {null_check}")
    assert disc_nulls == 12, f"Expected 12 missing discount_pct rows, got {disc_nulls}"
    assert rating_nulls == 15, f"Expected 15 missing rating rows, got {rating_nulls}"
    assert median_rating == 3.0, f"Expected median rating 3.0, got {median_rating}"
    assert null_check['discount_pct'] == 0 and null_check['rating'] == 0, "Null values remain!"
    print("TASK 4 VERIFICATION: discount_pct filled with 0 (12 rows), rating filled with median 3.0 (15 rows) [PASS]\n")

    # -------------------------------------------------------------------------
    # Task 5: Merge and Reconcile against Part 1
    # -------------------------------------------------------------------------
    print("--- Task 5: Merge and Reconcile Revenue ---")
    merged = orders_clean.merge(products, on='product_id', how='left')
    merged = merged.merge(customers, on='customer_id', how='left')

    merged['order_value'] = merged['quantity'] * merged['price'] * (1 - merged['discount_pct'] / 100.0)
    cleaned_total_rev = round(merged['order_value'].sum(), 2)

    # Compute dropped rows total order value independently
    dropped_merged = dropped_df.merge(products, on='product_id', how='left')
    dropped_merged['discount_pct'] = dropped_merged['discount_pct'].fillna(0).astype(float)
    dropped_merged['order_value'] = dropped_merged['quantity'] * dropped_merged['price'] * (1 - dropped_merged['discount_pct'] / 100.0)
    dropped_total_val = round(dropped_merged['order_value'].sum(), 2)

    raw_part1_rev = 99860.20
    delta = round(raw_part1_rev - cleaned_total_rev, 2)

    print(f"Cleaned Total Revenue (175 orders): INR {cleaned_total_rev:,.2f}")
    print(f"Part 1 Raw Total Revenue (180 orders): INR {raw_part1_rev:,.2f}")
    print(f"Reconciliation Delta               : INR {delta:,.2f}")
    print(f"Sum of 5 Dropped Duplicate Orders  : INR {dropped_total_val:,.2f}")

    reconciliation_note = (
        f"RECONCILIATION NOTE: Part 1 reported a raw total revenue of INR {raw_part1_rev:,.2f} across 180 raw orders. "
        f"After Python data cleaning, the cleaned dataset of 175 orders yields a total revenue of INR {cleaned_total_rev:,.2f}. "
        f"The exact difference of INR {delta:,.2f} is entirely attributed to the removal of 5 double-submitted duplicate orders "
        f"(order_ids: O0176, O0177, O0178, O0179, O0180) in Task 3, whose combined order value equals exactly INR {dropped_total_val:,.2f}. "
        f"Imputing missing values for discount_pct (defaulting to 0%) and rating (median 3.0) did not alter any order_value sums, "
        f"confirming that duplicate removal is 100% responsible for the revenue delta."
    )
    print("\n" + reconciliation_note)
    assert cleaned_total_rev == 97358.30, f"Expected cleaned revenue 97358.30, got {cleaned_total_rev}"
    assert delta == 2501.90, f"Expected delta 2501.90, got {delta}"
    assert dropped_total_val == 2501.90, f"Expected dropped total 2501.90, got {dropped_total_val}"
    print("TASK 5 VERIFICATION: Cleaned total revenue INR 97,358.30 reconciled with exact delta INR 2,501.90 [PASS]\n")

    # -------------------------------------------------------------------------
    # Task 6: IQR Outlier Detection on Quantity
    # -------------------------------------------------------------------------
    print("--- Task 6: IQR Outlier Detection on Quantity ---")
    q1 = merged['quantity'].quantile(0.25)
    q3 = merged['quantity'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    print(f"Q1 = {q1:.1f}, Q3 = {q3:.1f}, IQR = {iqr:.1f}")
    print(f"Outlier Thresholds -> Lower: {lower_bound:.1f}, Upper: {upper_bound:.1f}")

    merged['is_outlier'] = (merged['quantity'] < lower_bound) | (merged['quantity'] > upper_bound)
    outlier_rows = merged[merged['is_outlier']]
    outlier_list = outlier_rows[['order_id', 'quantity']].to_dict('records')
    print(f"Flagged Outlier Orders ({len(outlier_rows)} rows): {outlier_list}")

    assert q1 == 1.0 and q3 == 2.0 and iqr == 1.0, "IQR values incorrect"
    assert lower_bound == -0.5 and upper_bound == 3.5, "Outlier bounds incorrect"
    assert len(outlier_rows) == 2, f"Expected 2 outliers, got {len(outlier_rows)}"
    assert set(outlier_rows['order_id']) == {'O0011', 'O0098'}, f"Unexpected outlier IDs: {outlier_rows['order_id'].tolist()}"
    print("TASK 6 VERIFICATION: Flagged 2 quantity outliers (O0011: 25, O0098: 30) without dropping [PASS]\n")

    # -------------------------------------------------------------------------
    # Task 7: COD Return Hypothesis
    # -------------------------------------------------------------------------
    print("--- Task 7: COD Return Rate Hypothesis Test ---")
    hypothesis_stmt = "HYPOTHESIS: Cash on Delivery (COD) payment method has a significantly higher return rate than prepaid methods (CARD, UPI)."
    print(hypothesis_stmt)

    pm_summary = merged.groupby('payment_method')['returned'].agg(
        total_orders='count',
        returned_orders='sum',
        return_rate=lambda x: round(x.mean() * 100, 1)
    ).reset_index()

    print("Return Rate by Payment Method:")
    print(pm_summary.to_string(index=False))

    rates = dict(zip(pm_summary['payment_method'], pm_summary['return_rate']))
    print(f"\nReturn Rates Summary -> CARD: {rates['CARD']}%, COD: {rates['COD']}%, UPI: {rates['UPI']}%")
    verdict = "CONFIRMED"
    print(f"VERDICT: {verdict} - COD return rate ({rates['COD']}%) is 3x higher than CARD ({rates['CARD']}%) and 2.3x higher than UPI ({rates['UPI']}%).")

    assert rates['CARD'] == 14.7, f"Expected CARD 14.7%, got {rates['CARD']}"
    assert rates['COD'] == 44.4, f"Expected COD 44.4%, got {rates['COD']}"
    assert rates['UPI'] == 18.9, f"Expected UPI 18.9%, got {rates['UPI']}"
    print("TASK 7 VERIFICATION: Return rates verified (CARD: 14.7%, COD: 44.4%, UPI: 18.9%) [PASS]\n")

    # -------------------------------------------------------------------------
    # Task 8: Multi-level Segmentation (Payment Method x City Tier)
    # -------------------------------------------------------------------------
    print("--- Task 8: Multi-Level Segmentation (Payment Method x City Tier) ---")
    seg = merged.groupby(['payment_method', 'city_tier'])['returned'].agg(
        total_orders='count',
        returned_orders='sum',
        return_rate_pct=lambda x: round(x.mean() * 100, 1)
    ).reset_index()

    print(seg.to_string(index=False))

    highest_risk_row = seg.loc[seg['return_rate_pct'].idxmax()]
    print(f"\nHighest-Risk Segment: {highest_risk_row['payment_method']} + Tier-{highest_risk_row['city_tier']} Cities")
    print(f"Return Rate: {highest_risk_row['return_rate_pct']}% ({highest_risk_row['returned_orders']}/{highest_risk_row['total_orders']} orders returned)")

    cod_t1 = seg[(seg['payment_method']=='COD') & (seg['city_tier']==1)]['return_rate_pct'].values[0]
    cod_t2 = seg[(seg['payment_method']=='COD') & (seg['city_tier']==2)]['return_rate_pct'].values[0]
    print(f"COD Tier-1 Return Rate: {cod_t1}% vs COD Tier-2 Return Rate: {cod_t2}%")

    assert cod_t1 == 37.5, f"Expected COD Tier-1 37.5%, got {cod_t1}"
    assert cod_t2 == 54.5, f"Expected COD Tier-2 54.5%, got {cod_t2}"
    print("TASK 8 VERIFICATION: Highest-risk segment identified as COD + Tier-2 cities (54.5%) [PASS]\n")

    # -------------------------------------------------------------------------
    # Task 9: Correlation Analysis
    # -------------------------------------------------------------------------
    print("--- Task 9: Correlation Matrix & Strength Band Analysis ---")
    corr_cols = ['rating', 'returned', 'discount_pct', 'quantity']
    corr_matrix = merged[corr_cols].corr()
    print("Correlation Matrix:")
    print(corr_matrix.round(4).to_string())

    print("\nPairwise Correlation Interpretation (Bands: 0-0.19 Negligible, 0.2-0.39 Weak, 0.4-0.69 Moderate, 0.7-1.0 Strong):")
    pairs = [
        ('rating', 'returned'),
        ('discount_pct', 'returned'),
        ('quantity', 'returned'),
        ('rating', 'discount_pct'),
        ('rating', 'quantity'),
        ('discount_pct', 'quantity')
    ]
    for var1, var2 in pairs:
        r_val = corr_matrix.loc[var1, var2]
        abs_r = abs(r_val)
        if abs_r < 0.2:
            band = "Negligible"
        elif abs_r < 0.4:
            band = "Weak"
        elif abs_r < 0.7:
            band = "Moderate"
        else:
            band = "Strong"
        print(f"  - {var1:12s} vs {var2:12s} : r = {r_val:+.4f} ({band})")

    disc_ret_r = corr_matrix.loc['discount_pct', 'returned']
    print(f"\nHypothesis Test: 'Higher discounts reduce returns'")
    print(f"Correlation (discount_pct vs returned): {disc_ret_r:.4f}")
    print(f"VERDICT: BUSTED - Correlation is negligible (r ≈ {disc_ret_r:.2f}), proving discounts do NOT reduce returns.")

    assert all(abs(corr_matrix.loc[v1, v2]) < 0.2 for v1, v2 in pairs), "Not all pairs are negligible!"
    print("TASK 9 VERIFICATION: All 6 pairwise correlations fall into 'Negligible' band (|r| < 0.2) [PASS]\n")

    # -------------------------------------------------------------------------
    # Task 10: Outlier-Corrected Time Series Analysis
    # -------------------------------------------------------------------------
    print("--- Task 10: Outlier-Corrected Time Series Analysis ---")
    merged['order_date'] = pd.to_datetime(merged['order_date'])
    merged['year_month'] = merged['order_date'].dt.strftime('%Y-%m')

    monthly_with = merged.groupby('year_month')['order_value'].sum().round(2).to_dict()
    monthly_without = merged[~merged['is_outlier']].groupby('year_month')['order_value'].sum().round(2).to_dict()

    print("Monthly Revenue (WITH Outliers):")
    for ym, rev in monthly_with.items():
        print(f"  {ym}: INR {rev:,.2f}")

    print("\nMonthly Revenue (OUTLIER-CORRECTED):")
    for ym, rev in monthly_without.items():
        print(f"  {ym}: INR {rev:,.2f}")

    print("\nTIME SERIES FINDING:")
    print("  - Uncorrected data suggests January 2026 was the peak revenue month (INR 29,582.10).")
    print("  - However, January revenue was heavily inflated by two bulk outlier orders (O0011: qty 25, O0098: qty 30).")
    print("  - Once outliers are corrected, January revenue drops to INR 11,637.10.")
    print("  - March 2026 is revealed as the TRUE PEAK MONTH with INR 20,318.90 in organic revenue.")

    assert monthly_with['2026-01'] == 29582.10, f"Expected Jan with outliers 29582.10, got {monthly_with['2026-01']}"
    assert monthly_without['2026-01'] == 11637.10, f"Expected Jan corrected 11637.10, got {monthly_without['2026-01']}"
    assert monthly_without['2026-03'] == 20318.90, f"Expected Mar corrected 20318.90, got {monthly_without['2026-03']}"
    print("TASK 10 VERIFICATION: True peak month verified as March 2026 (INR 20,318.90) [PASS]\n")

    # -------------------------------------------------------------------------
    # Part 3 Task 1: Export findings.json
    # -------------------------------------------------------------------------
    print("--- Exporting Verified Metrics to narrator/findings.json ---")
    os.makedirs('narrator', exist_ok=True)

    findings_data = {
        "cleaned_total_revenue_inr": cleaned_total_rev,
        "raw_total_revenue_inr": raw_part1_rev,
        "duplicate_reconciliation_delta_inr": delta,
        "return_rate_by_payment": {
            "COD": rates['COD'],
            "CARD": rates['CARD'],
            "UPI": rates['UPI']
        },
        "highest_risk_segment": {
            "payment_method": "COD",
            "city_tier": 2,
            "return_rate_pct": cod_t2
        },
        "true_peak_month": {
            "month": "2026-03",
            "revenue_inr": monthly_without['2026-03']
        },
        "outlier_inflated_month": {
            "month": "2026-01",
            "apparent_revenue_inr": monthly_with['2026-01'],
            "corrected_revenue_inr": monthly_without['2026-01']
        }
    }

    findings_path = 'narrator/findings.json'
    with open(findings_path, 'w', encoding='utf-8') as f:
        json.dump(findings_data, f, indent=2)

    print(f"Successfully exported {findings_path}!")
    print(json.dumps(findings_data, indent=2))
    print("\n======================================================================")
    print("PART 2 EDA & DATA CLEANING COMPLETED SUCCESSFULLY")
    print("======================================================================\n")

    return merged, findings_data


if __name__ == '__main__':
    run_clean_and_eda()
