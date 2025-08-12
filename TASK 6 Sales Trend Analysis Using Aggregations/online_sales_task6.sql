-- TASK 6: Sales Trend Analysis Using Aggregations (SQLite)
-- Dataset CSV: sales_data_sample.csv
-- This script creates a staging table matching the CSV headers, imports the CSV,
-- transforms into a simplified `online_sales` table, and runs required analyses.

-- =====================
-- 0) Safety & display
-- =====================
.timer on
.headers on
.mode column

-- =====================
-- 1) Create staging table and import CSV
-- =====================
DROP TABLE IF EXISTS staging_online_sales;
CREATE TABLE staging_online_sales (
  ORDERNUMBER TEXT,
  QUANTITYORDERED TEXT,
  PRICEEACH TEXT,
  ORDERLINENUMBER TEXT,
  SALES TEXT,
  ORDERDATE TEXT,
  STATUS TEXT,
  QTR_ID TEXT,
  MONTH_ID TEXT,
  YEAR_ID TEXT,
  PRODUCTLINE TEXT,
  MSRP TEXT,
  PRODUCTCODE TEXT,
  CUSTOMERNAME TEXT,
  PHONE TEXT,
  ADDRESSLINE1 TEXT,
  ADDRESSLINE2 TEXT,
  CITY TEXT,
  STATE TEXT,
  POSTALCODE TEXT,
  COUNTRY TEXT,
  TERRITORY TEXT,
  CONTACTLASTNAME TEXT,
  CONTACTFIRSTNAME TEXT,
  DEALSIZE TEXT
);

-- Import CSV into the staging table.
-- For best compatibility, import then remove the header row if present.
.mode csv
.headers off
.import sales_data_sample.csv staging_online_sales

-- Remove header row if it was imported as data
DELETE FROM staging_online_sales WHERE ORDERNUMBER = 'ORDERNUMBER';

-- =====================
-- 2) Create final `online_sales` table with normalized schema
-- =====================
DROP TABLE IF EXISTS online_sales;
CREATE TABLE online_sales (
  order_id INTEGER,          -- maps from ORDERNUMBER
  order_date TEXT,           -- normalized to 'YYYY-MM-01' using YEAR_ID and MONTH_ID for reliable month/year
  amount REAL,               -- maps from SALES
  product_id TEXT            -- maps from PRODUCTCODE
);

-- Populate `online_sales` from staging. We normalize `order_date` to the first day of the
-- month using YEAR_ID and MONTH_ID (more reliable than parsing ORDERDATE which has mixed formats).
INSERT INTO online_sales (order_id, order_date, amount, product_id)
SELECT
  CAST(ORDERNUMBER AS INTEGER) AS order_id,
  printf('%04d-%02d-01', CAST(YEAR_ID AS INTEGER), CAST(MONTH_ID AS INTEGER)) AS order_date,
  CASE WHEN SALES IS NULL OR SALES = '' THEN NULL ELSE CAST(SALES AS REAL) END AS amount,
  PRODUCTCODE AS product_id
FROM staging_online_sales;

-- Helpful indexes for faster aggregation
CREATE INDEX IF NOT EXISTS idx_online_sales_order_date ON online_sales(order_date);
CREATE INDEX IF NOT EXISTS idx_online_sales_product_id ON online_sales(product_id);

-- =====================
-- 3) Analyses
-- =====================
.headers on
.mode column

-- i) Monthly revenue & order volume (group by year & month)
-- Purpose: Track total revenue and number of orders per calendar month.
SELECT
  strftime('%Y', order_date) AS year,
  strftime('%m', order_date) AS month,
  ROUND(SUM(COALESCE(amount, 0)), 2) AS monthly_revenue,
  COUNT(*) AS order_count
FROM online_sales
GROUP BY year, month
ORDER BY year, month;

-- ii) Monthly revenue & order volume for a specific year (example: 2004)
-- Purpose: Focus on a single year's monthly performance for trends and seasonality.
SELECT
  strftime('%Y', order_date) AS year,
  strftime('%m', order_date) AS month,
  ROUND(SUM(COALESCE(amount, 0)), 2) AS monthly_revenue,
  COUNT(*) AS order_count
FROM online_sales
WHERE strftime('%Y', order_date) = '2004'
GROUP BY year, month
ORDER BY month;

-- iii) Top 3 months by sales (across all years)
-- Purpose: Identify the strongest months (year-month) by revenue to inform planning.
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

-- iv) Monthly revenue handling NULLs in amount
-- Purpose: Demonstrate NULL handling in aggregates; compare SUM(amount) vs SUM(COALESCE(amount,0)).
SELECT
  strftime('%Y', order_date) AS year,
  strftime('%m', order_date) AS month,
  ROUND(SUM(amount), 2) AS sum_skipping_nulls,
  ROUND(SUM(COALESCE(amount, 0)), 2) AS sum_treating_nulls_as_zero
FROM online_sales
GROUP BY year, month
ORDER BY year, month;

-- End of Task 6
