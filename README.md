# Mamaearth Returns & Growth Intelligence Pipeline
> **Capstone Project — Data Analytics with AI & Gen AI**  
> **IIT Roorkee & Masai School** 

---

## Executive Overview

This repository implements an end-to-end analytics and GenAI intelligence pipeline for Mamaearth. The pipeline investigates product return patterns, reconciles revenue metrics across relational and Python layers, and generates executive business narratives formatted under the **Situation–Complication–Resolution (SCR)** framework.

### Connected Three-Layer Architecture
```
[Raw CSVs] (data/)
    │
    ├──> [Layer 1: SQL Relational Layer] (sql/) ──> Schema, Seed Data & 9 SQL Reports
    │
    ├──> [Layer 2: Python Wrangling & EDA] (analysis/) ──> Cleaning, Reconciling, Outlier IQR, EDA & Charts
    │                                                        │
    │                                                        ▼
    │                                                narrator/findings.json
    │                                                        │
    └────────────────────────────────────────────────────────┴──> [Layer 3: GenAI Insight Narrator] (narrator/)
                                                                      - Gemini API (Online)
                                                                      - Keyless Offline Fallback
                                                                      - Numeric Accuracy Verification
```

---

## Repository Structure

```text
<repo>/
├── README.md
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── reports.sql
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── orders.csv
├── analysis/
│   ├── clean_and_eda.py
│   └── visualize.py
├── visualizations/
│   ├── return_rate_by_payment.png
│   └── monthly_revenue_trend.png
└── narrator/
    ├── findings.json
    └── generate_narrative.py
```

---

## Layer-to-Layer Pipeline Data Flow

The three layers in this pipeline are strictly decoupled yet linked through automated data handoffs:

```
[data/ (Raw CSVs)]
       │
       ├──► 1. SQL Relational Layer (sql/)
       │      │   - schema.sql defines tables with strict constraints & keys
       │      │   - seed_data.sql populates raw relational records
       │      │   - reports.sql produces 9 baseline analytical reports
       │      ▼
       │     Produces: Baseline raw metrics (180 orders, INR 99,860.20 raw revenue)
       │
       ├──► 2. Python Wrangling & EDA Layer (analysis/)
       │      │   - clean_and_eda.py reads raw CSVs, standardizes casing, drops 5 duplicate
       │      │     orders (O0176–O0180), imputes nulls, flags bulk outliers (O0011, O0098)
       │      │   - Reconciles cleaned revenue (INR 97,358.30) against SQL raw baseline
       │      │     confirming delta = INR 2,501.90 (exact sum of duplicate orders)
       │      │   - Conducts hypothesis tests & multi-level segmentation
       │      │   - visualize.py generates publication-ready PNG charts
       │      ▼
       │     Produces: narrator/findings.json & visualizations/*.png
       │
       └──► 3. GenAI Insight Narrator Layer (narrator/)
              │   - generate_narrative.py ingests narrator/findings.json
              │   - Synthesizes findings using the Situation-Complication-Resolution (SCR) framework
              │   - Connects to Google Gemini API (with deterministic offline fallback)
              │   - Validates all 5 mandatory metrics via Task 5 numeric accuracy checklist
              ▼
             Produces: Executive Business Report (Source: GEMINI_API / sample_output.txt)
```

---

## Exact Run Order of the Three Layers

Execute the layers strictly in the following sequential order:

### 1. Layer 1: SQL Relational Layer
Build schema, seed raw data, and run 9 analytical reports to establish raw baseline metrics:
```bash
python -c "import sqlite3; conn = sqlite3.connect('mamaearth.db'); conn.cursor().executescript(open('sql/schema.sql').read() + open('sql/seed_data.sql').read() + open('sql/reports.sql').read()); print('Layer 1 (SQL): COMPLETED & VERIFIED')"
```

### 2. Layer 2: Python Data Wrangling & EDA
Clean raw data, perform revenue reconciliation, run hypothesis tests, export verified metrics to `narrator/findings.json`, and render visualizations:
```bash
python analysis/clean_and_eda.py
python analysis/visualize.py
```

### 3. Layer 3: GenAI Insight Narrator
Ingest `narrator/findings.json`, generate executive business narrative via Gemini API (or offline fallback), and run the 5-point numeric accuracy verification:
```bash
python narrator/generate_narrative.py
```

---

## Environment Setup & Installation

### 1. Prerequisites
- Python 3.9+ installed
- SQLite3 CLI or Python built-in `sqlite3`

### 2. Virtual Environment Setup
```bash
# Clone the repository
git clone <your-repo-link>
cd MammaEarth_Project

# Create and activate virtual environment
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Layer 1: SQL Relational Store & Reporting (`sql/`)

The SQL layer constructs the relational database, loads raw data, and executes 9 analytical business queries.

### Run Instructions (SQLite CLI or Python)
To run via Python test runner or SQLite CLI:
```bash
# Option A: Execute using Python
python -c "
import sqlite3
conn = sqlite3.connect('mamaearth.db')
cursor = conn.cursor()
cursor.executescript(open('sql/schema.sql').read())
cursor.executescript(open('sql/seed_data.sql').read())
cursor.executescript(open('sql/reports.sql').read())
print('SQL Layer executed successfully!')
"
```

### Table Definitions (`sql/schema.sql`)
- `customers`: `customer_id` (PK), `name`, `city`, `city_tier`, `signup_date`, `acquisition_source`.
- `products`: `product_id` (PK), `product_name`, `category`, `price`.
- `orders`: `order_id` (PK), `customer_id` (FK), `product_id` (FK), `order_date`, `quantity`, `discount_pct` (Nullable), `payment_method`, `rating` (Nullable), `returned` (Default 0).

### Key SQL Reports Summary (`sql/reports.sql`)
1. **Report (a) Order Totals**: `180` orders, Total Revenue = `INR 99,860.20`, Average Order Value = `INR 554.78`.
2. **Report (b) Rating Coverage**: `180` total orders vs `165` rated orders -> `15` missing ratings.
3. **Report (c) Zero-Order Customers**: Verified via `LEFT JOIN ... HAVING COUNT=0` and `NOT IN` subquery -> `C045 (Vihaan)`.
4. **Report (d) Return Rate by City (>20%)**: Jaipur (`42.1%`), Lucknow (`30.6%`), Bangalore (`24.2%`).
5. **Report (e) Customer Ranking**: Top 5 by spend led by `C043 (Reyansh - INR 12,920.00)`; ranks 3–5 fetched via `OFFSET 2 LIMIT 3`.
6. **Report (f) Revenue by Category**: Haircare (`INR 44,956.10`), Skincare (`INR 27,346.00`), Babycare (`INR 16,805.00`), PersonalCare (`INR 10,753.10`).
7. **Report (g) Pattern Match**: 10 customers whose name starts with 'A'.
8. **Report (h) Acquisition Channels**: 4 distinct sources (`Ad`, `Organic`, `Referral`, `Social`).
9. **Report (i) Loyalty Classification**: `ALTER TABLE` + `UPDATE CASE` -> `28 Gold` (Tier-1), `17 Silver` (Tier-2).

---

## Layer 2: Python Data Wrangling & EDA (`analysis/`)

The Python layer processes raw CSVs independently, cleans data quality defects, reconciles metrics against SQL, performs statistical testing, and generates visualizations.

### Step 1: Execute Cleaning & EDA Script
```bash
python analysis/clean_and_eda.py
```

#### EDA & Cleaning Findings
- **Task 1 (Raw Load)**: `orders.shape` verified as `(180, 9)`.
- **Task 2 (Casing Standardization)**: Standardized 7 raw casing variants into 3 values: `CARD (70)`, `UPI (55)`, `COD (55)`.
- **Task 3 (Deduplication)**: Flagged and removed 5 double-submitted duplicate rows (`O0176`–`O0180`). Clean shape: `(175, 9)`.
- **Task 4 (Imputation)**: Imputed 12 missing `discount_pct` with `0%` and 15 missing `rating` with median `3.0`.
- **Task 5 (Revenue Reconciliation)**:
  - Cleaned Total Revenue = **INR 97,358.30** across 175 orders.
  - Reconciliation Delta = **INR 2,501.90** (Part 1 Raw INR 99,860.20 - Cleaned INR 97,358.30).
  - **Reconciliation Note**: The delta of INR 2,501.90 is 100% attributed to dropping the 5 duplicate orders (`O0176`–`O0180`). Missing value imputation did not alter any order values.
- **Task 6 (Outlier Detection)**: Quantity IQR analysis (`Q1=1.0`, `Q3=2.0`, `IQR=1.0`, `Upper=3.5`). Flagged 2 bulk orders (`O0011`: qty 25, `O0098`: qty 30) with `is_outlier` boolean flag without dropping.
- **Task 7 (COD Hypothesis)**: **CONFIRMED**. COD return rate is **44.4%** (3x Card at 14.7% and 2.3x UPI at 18.9%).
- **Task 8 (Multi-Level Segmentation)**: Identified **COD + Tier-2 Cities** as the single highest-risk segment with a **54.5%** return rate (`12/22` orders).
- **Task 9 (Correlation Matrix)**: All 6 pairwise correlations fell into the `Negligible` band (`|r| < 0.2`). "Discounts reduce returns" hypothesis: **BUSTED** (`r = -0.09`).
- **Task 10 (Time Series)**: Uncorrected data showed January as peak (`INR 29,582.10`). Outlier-corrected series revealed **March 2026** as the **TRUE PEAK MONTH** (**INR 20,318.90**).
- **Export**: Automatically exported verified metrics to `narrator/findings.json`.

### Step 2: Execute Visualization Script
```bash
python analysis/visualize.py
```
Generates two PNGs in `visualizations/`:
1. `visualizations/return_rate_by_payment.png` — Bar chart comparing return rates across payment channels.
2. `visualizations/monthly_revenue_trend.png` — Line chart contrasting raw vs outlier-corrected monthly revenue trends.

---

## Layer 3: GenAI Insight Narrator (`narrator/`)

The GenAI layer synthesizes the verified metrics into an executive **Situation–Complication–Resolution (SCR)** business report using Google's `google-genai` SDK.

### Run Instructions

#### Option A: Running with Gemini API Key (Online Mode)
Set your Google AI Studio API key as an environment variable (do NOT hardcode in source code):

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
python narrator/generate_narrative.py
```

**Linux / macOS:**
```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
python narrator/generate_narrative.py
```

#### Option B: Running without API Key (Offline Fallback Mode)
If `GEMINI_API_KEY` is not set or network access is unavailable, the narrator seamlessly executes Task 4 offline fallback:
```bash
python narrator/generate_narrative.py
```

### Safety & Parameter Specifications
- **API Key Security**: The API key is passed strictly via the `GEMINI_API_KEY` environment variable. It is NEVER hardcoded in code or committed to Git.
- **Model Selection**: Uses `gemini-3.8-flash` / `gemini-3.6-flash` (configurable via `GEMINI_MODEL`).
- **Parameter Locking**:
  - `temperature = 0.0`: Enforces deterministic, reproducible, factual business reporting without creative hallucination.
  - `max_output_tokens = 2048`: Guarantees complete, un-truncated 3-section output.
  - `timeout = 30000ms`: 30-second API timeout handling.
- **Error Handling**: Wrapped in `try/except` returning structured dicts (`status`, `narrative`, `tokens`, `source`).

### Task 5: Numeric Accuracy Checklist
`generate_narrative.py` automatically checks the narrative against the 5 key figures:
1. `97,358.30` (Cleaned Total Revenue)
2. `44.4%` (COD Return Rate)
3. `54.5%` (Highest-Risk COD Tier-2 Segment Return Rate)
4. `2,501.90` (Duplicate Reconciliation Delta)
5. `March 2026` / `INR 20,318.90` (True Peak Month)

---

## End-to-End Pipeline Execution Guide

Run the full pipeline top-to-bottom in sequence:

```bash
# Step 1: SQL Layer Verification (Part 1)
python -c "import sqlite3; conn = sqlite3.connect(':memory:'); conn.cursor().executescript(open('sql/schema.sql').read() + open('sql/seed_data.sql').read() + open('sql/reports.sql').read()); print('Part 1 SQL: PASS')"

# Step 2: Python EDA, Wrangling & Findings Export (Part 2 - Tasks 1-10)
python analysis/clean_and_eda.py

# Step 3: Visualizations (Part 2 - Task 11)
python analysis/visualize.py

# Step 4: GenAI Executive Narrative & Accuracy Check (Part 3)
python narrator/generate_narrative.py
```

---

## Grading Rubric Compliance Checklist

| Part | Task / Component | Target Metric / Result | Status |
| :--- | :--- | :--- | :---: |
| **Part 1** | Schema & Constraints | customers (45), products (16), orders (180) | `PASS` |
| **Part 1** | SQL Reports (a–i) | 9 queries executed with output comments in `sql/reports.sql` | `PASS` |
| **Part 2** | Task 1: Load & Inspect | `orders.shape` = (180, 9) | `PASS` |
| **Part 2** | Task 2: Standardize Casing | CARD: 70, UPI: 55, COD: 55 | `PASS` |
| **Part 2** | Task 3: Deduplication | Dropped 5 rows (`O0176`–`O0180`), Clean shape (175, 9) | `PASS` |
| **Part 2** | Task 4: Imputation | `discount_pct` 0 (12 rows), `rating` median 3.0 (15 rows) | `PASS` |
| **Part 2** | Task 5: Reconciliation | Cleaned Rev = **INR 97,358.30**, Delta = **INR 2,501.90** | `PASS` |
| **Part 2** | Task 6: IQR Outliers | Flagged `O0011` (qty 25) & `O0098` (qty 30) | `PASS` |
| **Part 2** | Task 7: COD Hypothesis | **CONFIRMED** — COD return rate = **44.4%** | `PASS` |
| **Part 2** | Task 8: Segmentation | **COD + Tier-2 Cities** = **54.5%** return rate | `PASS` |
| **Part 2** | Task 9: Correlation | All pairs `Negligible` (`\|r\| < 0.2`), Discount hypothesis **BUSTED** | `PASS` |
| **Part 2** | Task 10: Time Series | Outlier-corrected peak month = **March 2026 (INR 20,318.90)** | `PASS` |
| **Part 2** | Task 11: Visualizations | 2 PNGs created under `visualizations/` | `PASS` |
| **Part 3** | Task 1: findings.json | Exported automatically from Python code | `PASS` |
| **Part 3** | Task 2: SCR Narrative | 3 sections (Situation, Complication, Resolution) via Gemini API | `PASS` |
| **Part 3** | Task 3: Lock Parameters | `temperature=0.0`, token limit, timeout, error handling | `PASS` |
| **Part 3** | Task 4: Offline Fallback | Keyless deterministic generator for zero-spend grading | `PASS` |
| **Part 3** | Task 5: Accuracy Checklist | All 5 key numbers verified in narrative | `PASS` |
| **Part 3** | Task 6: README Setup | Step-by-step reproduction guide | `PASS` |

---
*Mamaearth Returns & Growth Intelligence Pipeline — Built for E&ICT Academy IIT Roorkee & Masai Capstone Submission.*
