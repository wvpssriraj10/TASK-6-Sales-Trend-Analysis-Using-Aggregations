# TASK 6: Sales Trend Analysis Using Aggregations

## 📊 Project Overview

This project implements a comprehensive sales trend analysis using SQL aggregations on an online sales dataset. The solution demonstrates advanced SQL querying techniques, data aggregation, and NULL handling in SQLite.

## 🎯 Objectives

1. Create a SQLite-compatible SQL script for sales data analysis
2. Load and transform CSV data into a normalized database schema
3. Execute complex aggregation queries for business insights
4. Generate visual reports of query results
5. Handle NULL values appropriately in aggregations
6. Answer technical interview questions about SQL aggregations

## 📁 Project Structure

```
TASK 6 Sales Trend Analysis Using Aggregations/
├── sales_data_sample.csv           # Original dataset (533KB, 2,823 records)
├── online_sales.db                 # SQLite database with processed data
├── online_sales_task6.sql          # Main SQL script with all queries
├── complete_task6.py               # Automated solution script
├── render_results.py               # Result visualization script
├── interview_answers.md            # Technical interview Q&A
├── monthly_revenue.png             # Monthly revenue visualization
├── monthly_revenue_2004.png        # 2004-specific analysis
├── top3_months.png                 # Top 3 performing months
├── monthly_nulls.png               # NULL handling demonstration
└── README.md                       # This documentation
```

## 🗄️ Database Schema

### Original CSV Columns
- `ORDERNUMBER`, `QUANTITYORDERED`, `PRICEEACH`, `ORDERLINENUMBER`
- `SALES`, `ORDERDATE`, `STATUS`, `QTR_ID`, `MONTH_ID`, `YEAR_ID`
- `PRODUCTLINE`, `MSRP`, `PRODUCTCODE`, `CUSTOMERNAME`
- `PHONE`, `ADDRESSLINE1`, `ADDRESSLINE2`, `CITY`, `STATE`
- `POSTALCODE`, `COUNTRY`, `TERRITORY`, `CONTACTLASTNAME`
- `CONTACTFIRSTNAME`, `DEALSIZE`

### Normalized Schema (`online_sales` table)
```sql
CREATE TABLE online_sales (
    order_id INTEGER,          -- Maps from ORDERNUMBER
    order_date TEXT,           -- Normalized to 'YYYY-MM-01' format
    amount REAL,               -- Maps from SALES
    product_id TEXT            -- Maps from PRODUCTCODE
);
```

## 🔍 SQL Queries Implemented

### 1. Monthly Revenue & Order Volume (All Years)
```sql
SELECT
    strftime('%Y', order_date) AS year,
    strftime('%m', order_date) AS month,
    ROUND(SUM(COALESCE(amount, 0)), 2) AS monthly_revenue,
    COUNT(*) AS order_count
FROM online_sales
GROUP BY year, month
ORDER BY year, month;
```
**Purpose**: Track total revenue and order volume per calendar month across all years.

### 2. Monthly Revenue & Order Volume (2004 Specific)
```sql
SELECT
    strftime('%Y', order_date) AS year,
    strftime('%m', order_date) AS month,
    ROUND(SUM(COALESCE(amount, 0)), 2) AS monthly_revenue,
    COUNT(*) AS order_count
FROM online_sales
WHERE strftime('%Y', order_date) = '2004'
GROUP BY year, month
ORDER BY month;
```
**Purpose**: Analyze 2004 monthly performance for trends and seasonality.

### 3. Top 3 Months by Sales
```sql
WITH monthly AS (
    SELECT
        strftime('%Y', order_date) AS year,
        strftime('%m', order_date) AS month,
        SUM(COALESCE(amount, 0)) AS monthly_revenue
    FROM online_sales
    GROUP BY year, month
)
SELECT year, month, ROUND(monthly_revenue, 2) AS monthly_revenue
FROM monthly
ORDER BY monthly_revenue DESC, year, month
LIMIT 3;
```
**Purpose**: Identify strongest months by revenue for business planning.

### 4. Monthly Revenue with NULL Handling
```sql
SELECT
    strftime('%Y', order_date) AS year,
    strftime('%m', order_date) AS month,
    ROUND(SUM(amount), 2) AS sum_skipping_nulls,
    ROUND(SUM(COALESCE(amount, 0)), 2) AS sum_treating_nulls_as_zero,
    COUNT(*) AS total_orders,
    COUNT(amount) AS orders_with_amount
FROM online_sales
GROUP BY year, month
ORDER BY year, month;
```
**Purpose**: Demonstrate different approaches to handling NULL values in aggregations.

## 🚀 How to Run

### Prerequisites
```bash
pip install pandas matplotlib sqlite3
```

### Option 1: Run Complete Automated Solution
```bash
python complete_task6.py
```
This will:
- Create and populate the SQLite database
- Execute all queries
- Generate screenshot images
- Create interview answers document

### Option 2: Run SQL Script Manually
```bash
# Using SQLite command line
sqlite3 online_sales.db < online_sales_task6.sql

# Or using PowerShell
Get-Content online_sales_task6.sql | sqlite3 online_sales.db
```

### Option 3: Generate Screenshots Only
```bash
python render_results.py
```

## 📈 Key Insights from Analysis

- **Dataset Size**: 2,823 sales records across multiple years
- **Peak Performance**: Top 3 months identified by revenue analysis
- **Data Quality**: Proper NULL handling ensures accurate aggregations
- **Time Series**: Monthly trends reveal seasonal patterns

## 🎓 Technical Interview Questions Covered

1. **How do you group data by month/year?**
   - Use `strftime('%Y', date)` and `strftime('%m', date)` in SQLite
   - GROUP BY year, month for time-based aggregations

2. **Difference between COUNT(*) and COUNT(DISTINCT col)?**
   - `COUNT(*)`: All rows including duplicates and NULLs
   - `COUNT(DISTINCT col)`: Unique non-NULL values only

3. **How do you calculate monthly revenue?**
   - `SUM(amount)` with `GROUP BY month/year`
   - Use `COALESCE()` for NULL handling

4. **What are aggregate functions in SQL?**
   - Functions that operate on multiple rows: SUM, COUNT, AVG, MIN, MAX
   - Return single result per group

5. **How to handle NULLs in aggregates?**
   - `SUM(amount)`: Ignores NULLs
   - `SUM(COALESCE(amount, 0))`: Treats NULLs as 0
   - `COUNT(amount)` vs `COUNT(*)` behavior

6. **Role of ORDER BY and GROUP BY?**
   - `GROUP BY`: Groups rows for aggregation
   - `ORDER BY`: Sorts final results
   - Execution order: GROUP BY first, then ORDER BY

7. **How to get top 3 months by sales?**
   - Use `ORDER BY revenue DESC LIMIT 3`
   - Can combine with CTEs for complex rankings

## 🛠️ Technologies Used

- **SQLite**: Database engine for data storage and querying
- **Python**: Automation and data processing
- **Pandas**: Data manipulation and CSV handling
- **Matplotlib**: Chart generation and table visualization
- **SQL**: Advanced querying with aggregations and window functions

## 📊 Generated Outputs

- **Database**: `online_sales.db` with 2,823 processed records
- **Visualizations**: 4 PNG files showing query results as formatted tables
- **Documentation**: Complete interview Q&A and technical explanations

## 🔧 Features

- ✅ Automatic CSV encoding detection and handling
- ✅ Robust data transformation and validation
- ✅ Professional table visualizations
- ✅ Comprehensive error handling
- ✅ SQLite-optimized queries using `strftime()`
- ✅ NULL value handling demonstrations
- ✅ Indexed database for performance

## 📝 Notes

- Uses SQLite-specific functions (`strftime()`) instead of standard SQL `EXTRACT()`
- Handles various CSV encodings automatically (UTF-8, Latin-1, CP1252)
- Normalizes dates to first day of month for consistent grouping
- Includes performance indexes for faster query execution

## 👨‍💻 Author

Created as part of ELEVATE LABS technical assessment - demonstrating advanced SQL aggregation techniques and data analysis capabilities.
