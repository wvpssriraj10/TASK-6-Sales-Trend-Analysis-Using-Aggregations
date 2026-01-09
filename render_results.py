import os
import sqlite3

import pandas as pd
import matplotlib.pyplot as plt


def save_table_as_image(df: pd.DataFrame, out_path: str, title: str | None = None) -> None:
    fig, ax = plt.subplots(figsize=(max(6, len(df.columns) * 1.2), max(2.5, 0.4 * (len(df) + 1))))
    ax.axis('off')
    if title:
        ax.set_title(title, fontsize=12, pad=12)
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns.tolist(),
        loc='center',
        cellLoc='center',
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.2)

    plt.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'online_sales.db')

    conn = sqlite3.connect(db_path)

    queries: dict[str, tuple[str, str]] = {
        'monthly_revenue': (
            """
            SELECT
              strftime('%Y', order_date) AS year,
              strftime('%m', order_date) AS month,
              ROUND(SUM(COALESCE(amount, 0)), 2) AS monthly_revenue,
              COUNT(*) AS order_count
            FROM online_sales
            GROUP BY year, month
            ORDER BY year, month;
            """,
            'Monthly revenue & order volume (all years)'
        ),
        'monthly_revenue_2004': (
            """
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
            'Monthly revenue & order volume (2004)'
        ),
        'top3_months': (
            """
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
            """,
            'Top 3 months by sales'
        ),
        'monthly_nulls': (
            """
            SELECT
              strftime('%Y', order_date) AS year,
              strftime('%m', order_date) AS month,
              ROUND(SUM(amount), 2) AS sum_skipping_nulls,
              ROUND(SUM(COALESCE(amount, 0)), 2) AS sum_treating_nulls_as_zero
            FROM online_sales
            GROUP BY year, month
            ORDER BY year, month;
            """,
            'Monthly revenue with NULL handling'
        ),
    }

    for key, (sql, title) in queries.items():
        df = pd.read_sql_query(sql, conn)
        out_path = os.path.join(base_dir, f"{key}.png")
        save_table_as_image(df, out_path, title=title)
        print(f"Saved {out_path}")

    conn.close()


if __name__ == '__main__':
    main()
