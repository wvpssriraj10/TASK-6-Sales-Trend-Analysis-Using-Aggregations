
# Interview Questions and Answers

## 1. How do you group data by month/year?
Use `strftime()` function in SQLite:
- `strftime('%Y', order_date)` extracts year
- `strftime('%m', order_date)` extracts month
- GROUP BY year, month groups records by these time periods

## 2. Difference between COUNT(*) and COUNT(DISTINCT col)?
- `COUNT(*)`: Counts all rows including duplicates and NULLs
- `COUNT(DISTINCT col)`: Counts unique non-NULL values in the column
- Example: If you have orders [1,1,2,NULL], COUNT(*) = 4, COUNT(DISTINCT col) = 2

## 3. How do you calculate monthly revenue?
```sql
SELECT 
    strftime('%Y-%m', order_date) as month,
    SUM(amount) as monthly_revenue
FROM online_sales 
GROUP BY month;
```
Use SUM() aggregate function with GROUP BY month/year.

## 4. What are aggregate functions in SQL?
Functions that perform calculations on multiple rows and return a single result:
- `SUM()`: Total of numeric values
- `COUNT()`: Number of rows
- `AVG()`: Average value
- `MIN()/MAX()`: Minimum/Maximum values
- `GROUP_CONCAT()`: Concatenate values

## 5. How to handle NULLs in aggregates?
- `SUM(amount)`: Ignores NULL values
- `SUM(COALESCE(amount, 0))`: Treats NULLs as 0
- `COUNT(amount)`: Counts non-NULL values only
- `COUNT(*)`: Counts all rows including NULLs

## 6. What's the role of ORDER BY and GROUP BY?
- `GROUP BY`: Groups rows with same values into summary rows
- `ORDER BY`: Sorts the final result set
- ORDER BY comes after GROUP BY in query execution order
- You can order by grouped columns or aggregate results

## 7. How to get the top 3 months by sales?
```sql
SELECT month, SUM(amount) as revenue
FROM online_sales
GROUP BY month
ORDER BY revenue DESC
LIMIT 3;
```
Use ORDER BY with DESC and LIMIT to get top results.
