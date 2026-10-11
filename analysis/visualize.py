"""
Mamaearth Capstone - Part 2 Task 11: Data Visualizations
Generates two publication-ready visualizations in visualizations/:
1. return_rate_by_payment.png: Bar chart of return rates by payment method.
2. monthly_revenue_trend.png: Line chart of outlier-corrected monthly revenue trend.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def create_visualizations():
    print("======================================================================")
    print("GENERATING MAMAEARTH CAPSTONE VISUALIZATIONS (visualizations/)")
    print("======================================================================\n")

    os.makedirs('visualizations', exist_ok=True)

    # Load raw data and replicate clean logic
    customers = pd.read_csv('data/customers.csv')
    products = pd.read_csv('data/products.csv')
    orders = pd.read_csv('data/orders.csv')

    # Standardize casing & deduplicate
    orders['payment_method'] = orders['payment_method'].astype(str).str.strip().str.upper()
    dup_subset = ['customer_id', 'product_id', 'order_date', 'quantity', 'discount_pct', 'payment_method', 'rating', 'returned']
    orders_clean = orders[~orders.duplicated(subset=dup_subset, keep='first')].copy()

    # Impute missing
    orders_clean['discount_pct'] = orders_clean['discount_pct'].fillna(0).astype(float)

    # Merge
    merged = orders_clean.merge(products, on='product_id', how='left')
    merged = merged.merge(customers, on='customer_id', how='left')
    merged['order_value'] = merged['quantity'] * merged['price'] * (1 - merged['discount_pct'] / 100.0)

    # Outlier detection on quantity
    q1 = merged['quantity'].quantile(0.25)
    q3 = merged['quantity'].quantile(0.75)
    iqr = q3 - q1
    lower_b = q1 - 1.5 * iqr
    upper_b = q3 + 1.5 * iqr
    merged['is_outlier'] = (merged['quantity'] < lower_b) | (merged['quantity'] > upper_b)

    # Visualization 1: Return Rate by Payment Method
    pm_rates = merged.groupby('payment_method')['returned'].mean() * 100
    pm_rates = pm_rates.sort_values(ascending=False)

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)

    colors = ['#B5452F' if pm == 'COD' else '#2E6B4F' for pm in pm_rates.index]
    bars = ax.bar(pm_rates.index, pm_rates.values, color=colors, width=0.55, edgecolor='#17402F', linewidth=1.2)

    # Add percentages above bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 6),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=12, fontweight='bold', color='#1F2A24')

    ax.set_title("COD Returns at 44.4% — 3x Card", fontsize=15, fontweight='bold', color='#17402F', pad=15)
    ax.set_xlabel("Payment Method", fontsize=12, fontweight='bold', color='#1F2A24', labelpad=10)
    ax.set_ylabel("Return Rate (%)", fontsize=12, fontweight='bold', color='#1F2A24', labelpad=10)
    ax.set_ylim(0, 55)
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())

    # Styling grid
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    v1_path = 'visualizations/return_rate_by_payment.png'
    plt.tight_layout()
    plt.savefig(v1_path, dpi=300)
    plt.close()
    print(f"Saved {v1_path}")

    # -------------------------------------------------------------------------
    # Visualization 2: Outlier-Corrected Monthly Revenue Trend
    # -------------------------------------------------------------------------
    merged['order_date'] = pd.to_datetime(merged['order_date'])
    merged['year_month'] = merged['order_date'].dt.strftime('%Y-%m')

    monthly_clean = merged[~merged['is_outlier']].groupby('year_month')['order_value'].sum().round(2)
    monthly_raw = merged.groupby('year_month')['order_value'].sum().round(2)

    fig, ax = plt.subplots(figsize=(9.5, 5.5), dpi=300)

    # Plot Outlier-Corrected Line
    ax.plot(monthly_clean.index, monthly_clean.values, marker='o', markersize=8, color='#2E6B4F',
            linewidth=2.8, label='Outlier-Corrected Revenue (Organic)')

    # Plot Outlier-Inflated Line (dashed)
    ax.plot(monthly_raw.index, monthly_raw.values, marker='s', markersize=6, color='#E3A33B',
            linewidth=1.8, linestyle='--', label='Raw Revenue (With Bulk Outliers)')

    # Annotate peak month (March 2026)
    march_rev = monthly_clean['2026-03']
    ax.annotate(f'True Peak: March\nINR {march_rev:,.2f}',
                xy=('2026-03', march_rev),
                xytext=('2026-03', march_rev + 2200),
                ha='center', fontsize=10, fontweight='bold', color='#17402F',
                arrowprops=dict(arrowstyle='->', color='#17402F', lw=1.5))

    # Annotate January Outlier Distortion
    jan_raw_rev = monthly_raw['2026-01']
    ax.annotate(f'Jan Outlier Bulk Distortion\n(INR {jan_raw_rev:,.2f})',
                xy=('2026-01', jan_raw_rev),
                xytext=('2026-01', jan_raw_rev - 4000),
                ha='left', fontsize=9, fontstyle='italic', color='#C9822A',
                arrowprops=dict(arrowstyle='->', color='#C9822A', lw=1.2))

    ax.set_title("Outlier-Corrected Monthly Revenue — March Peak (INR 20,318.90)", fontsize=14, fontweight='bold', color='#17402F', pad=15)
    ax.set_xlabel("Month (2026)", fontsize=12, fontweight='bold', color='#1F2A24', labelpad=10)
    ax.set_ylabel("Total Order Revenue (INR)", fontsize=12, fontweight='bold', color='#1F2A24', labelpad=10)
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('INR {x:,.0f}'))
    ax.set_ylim(5000, 32000)

    ax.legend(frameon=True, facecolor='#EAF4EE', edgecolor='none', loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    v2_path = 'visualizations/monthly_revenue_trend.png'
    plt.tight_layout()
    plt.savefig(v2_path, dpi=300)
    plt.close()
    print(f"Saved {v2_path}")

    print("\nVISUALIZATIONS GENERATED SUCCESSFULLY!")


if __name__ == '__main__':
    create_visualizations()
