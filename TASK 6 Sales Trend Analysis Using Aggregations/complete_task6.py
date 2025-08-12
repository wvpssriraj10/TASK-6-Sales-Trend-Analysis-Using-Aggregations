#!/usr/bin/env python3
"""
TASK 6: Sales Trend Analysis Using Aggregations
Complete solution with data import, SQL queries, and screenshot generation
"""

import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def save_table_as_image(df: pd.DataFrame, out_path: str, title: str = None) -> None:
    """Save DataFrame as a formatted table image"""
    if df.empty:
        print(f"Warning: DataFrame is empty for {title}")
        return
        
    fig, ax = plt.subplots(figsize=(max(8, len(df.columns) * 1.5), max(3, 0.5 * (len(df) + 2))))
    ax.axis('off')
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Create table
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns.tolist(),
        loc='center',
        cellLoc='center',
    )
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    # Header styling
    for i in range(len(df.columns)):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(df) + 1):
        for j in range(len(df.columns)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')
    
    plt.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"✓ Saved: {out_path}")

def create_database_and_import_data():
    """Create database and import CSV data"""
    base_dir = Path(__file__).parent
    csv_path = base_dir.parent / "sales_data_sample.csv"
    db_path = base_dir / "online_sales.db"
    
    # Remove existing database
    if db_path.exists():
        db_path.unlink()
    
    print("📊 Creating database and importing data...")
    
    # Read CSV file with proper encoding handling
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        df = None
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                print(f"✓ Loaded CSV with {len(df)} rows and {len(df.columns)} columns using {encoding} encoding")
                print(f"✓ Columns: {list(df.columns)}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise Exception("Could not read CSV with any supported encoding")
            
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return None
    
    # Create SQLite connection
    conn = sqlite3.connect(db_path)
    
    # Create online_sales table with proper schema
    conn.execute("""
        DROP TABLE IF EXISTS online_sales;
    """)
    
    conn.execute("""
        CREATE TABLE online_sales (
            order_id INTEGER,
            order_date TEXT,
            amount REAL,
            product_id TEXT
        );
    """)
    
    # Transform and insert data
    # Map from CSV columns to our schema
    transformed_data = []
    for _, row in df.iterrows():
        try:
            order_id = int(row['ORDERNUMBER']) if pd.notna(row['ORDERNUMBER']) else None
            # Use YEAR_ID and MONTH_ID for reliable date formatting
            year = int(row['YEAR_ID']) if pd.notna(row['YEAR_ID']) else 2003
            month = int(row['MONTH_ID']) if pd.notna(row['MONTH_ID']) else 1
            order_date = f"{year:04d}-{month:02d}-01"
            amount = float(row['SALES']) if pd.notna(row['SALES']) else None
            product_id = str(row['PRODUCTCODE']) if pd.notna(row['PRODUCTCODE']) else None
            
            transformed_data.append((order_id, order_date, amount, product_id))
        except Exception as e:
            print(f"Warning: Skipping row due to error: {e}")
            continue
    
    # Insert data
    conn.executemany("""
        INSERT INTO online_sales (order_id, order_date, amount, product_id)
        VALUES (?, ?, ?, ?)
    """, transformed_data)
    
    conn.commit()
    
    # Verify data import
    count = conn.execute("SELECT COUNT(*) FROM online_sales").fetchone()[0]
    print(f"✓ Imported {count} records into online_sales table")
    
    return conn

def run_queries_and_generate_screenshots(conn):
    """Execute SQL queries and generate screenshot images"""
    base_dir = Path(__file__).parent
    
    queries = {
        'monthly_revenue': {
            'sql': """
                SELECT
                    strftime('%Y', order_date) AS year,
                    strftime('%m', order_date) AS month,
                    ROUND(SUM(COALESCE(amount, 0)), 2) AS monthly_revenue,
                    COUNT(*) AS order_count
                FROM online_sales
                GROUP BY year, month
                ORDER BY year, month;
            """,
            'title': 'Monthly Revenue & Order Volume (All Years)',
            'purpose': 'Track total revenue and number of orders per calendar month across all years'
        },
        
        'monthly_revenue_2004': {
            'sql': """
                SELECT
                    strftime('%Y', order_date) AS year,
                    strftime('%m', order_date) AS month,
                    ROUND(SUM(COALESCE(amount, 0)), 2) AS monthly_revenue,
                    COUNT(*) AS order_count
                FROM online_sales
                WHERE strftime('%Y', order_date) = '2004'
                GROUP BY year, month
                ORDER BY month;
            """,
            'title': 'Monthly Revenue & Order Volume (2004)',
            'purpose': 'Focus on 2004 monthly performance to analyze trends and seasonality'
        },
        
        'top3_months': {
            'sql': """
                WITH monthly AS (
                    SELECT
                        strftime('%Y', order_date) AS year,
                        strftime('%m', order_date) AS month,
                        SUM(COALESCE(amount, 0)) AS monthly_revenue
                    FROM online_sales
                    GROUP BY year, month
                )
                SELECT 
                    year, 
                    month, 
                    ROUND(monthly_revenue, 2) AS monthly_revenue
                FROM monthly
                ORDER BY monthly_revenue DESC, year, month
                LIMIT 3;
            """,
            'title': 'Top 3 Months by Sales',
            'purpose': 'Identify the strongest months by revenue to inform business planning'
        },
        
        'monthly_nulls': {
            'sql': """
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
            """,
            'title': 'Monthly Revenue with NULL Handling',
            'purpose': 'Demonstrate different approaches to handling NULL values in aggregations'
        }
    }
    
    print("\n📈 Executing queries and generating screenshots...")
    
    for key, query_info in queries.items():
        try:
            df = pd.read_sql_query(query_info['sql'], conn)
            if not df.empty:
                out_path = base_dir / f"{key}.png"
                save_table_as_image(df, str(out_path), query_info['title'])
                
                # Print query results to console
                print(f"\n{query_info['title']}:")
                print(f"Purpose: {query_info['purpose']}")
                print(df.to_string(index=False))
                print("-" * 50)
            else:
                print(f"⚠️  No data returned for query: {key}")
        except Exception as e:
            print(f"❌ Error executing query {key}: {e}")

def generate_interview_answers():
    """Generate answers to interview questions"""
    answers = """
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
"""
    
    answers_path = Path(__file__).parent / "interview_answers.md"
    with open(answers_path, 'w') as f:
        f.write(answers)
    print(f"✓ Saved interview answers to: {answers_path}")

def main():
    """Main execution function"""
    print("🚀 Starting TASK 6: Sales Trend Analysis Using Aggregations")
    print("=" * 60)
    
    # Step 1: Create database and import data
    conn = create_database_and_import_data()
    if not conn:
        print("❌ Failed to create database. Exiting.")
        return
    
    # Step 2: Run queries and generate screenshots
    run_queries_and_generate_screenshots(conn)
    
    # Step 3: Generate interview answers
    generate_interview_answers()
    
    # Step 4: Close connection
    conn.close()
    
    print("\n✅ TASK 6 completed successfully!")
    print("Generated files:")
    print("- online_sales.db (SQLite database)")
    print("- monthly_revenue.png")
    print("- monthly_revenue_2004.png") 
    print("- top3_months.png")
    print("- monthly_nulls.png")
    print("- interview_answers.md")

if __name__ == "__main__":
    main()
