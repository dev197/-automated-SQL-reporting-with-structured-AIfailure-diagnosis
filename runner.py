"""
SelfHealSQL: Query Runner
Executes each daily business query, saves successful results to CSV,
and logs structured failure details for the AI diagnostic agent (Step 5/6).

Before running:
    pip install pyodbc

Folder expectations:
    project/
      runner.py                <- this file
      01_daily_sales.sql
      02_top_products.sql
      03_sales_by_city.sql
      04_failed_transactions.sql
      05_top_segment.sql
      reports/                 <- created automatically
      logs/                    <- created automatically
"""

import os
import json
import csv
import traceback
from datetime import datetime

import pyodbc

# ---------------------------------------------------------------------------
# 1. CONNECTION SETTINGS — same as seed_data.py
# ---------------------------------------------------------------------------
SERVER = "localhost\\SQLEXPRESS"
DATABASE = "SelfHealSQL_DB"
CONN_STR = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)

# ---------------------------------------------------------------------------
# 2. WHICH QUERIES TO RUN — friendly name -> filename
# ---------------------------------------------------------------------------
QUERIES = {
    "daily_sales": "01_daily_sales.sql",
    "top_products": "02_top-selling_product.sql",
    "sales_by_city": "03_sales_by_city.sql",
    "failed_transactions": "04_failed_transactions.sql",
    "top_segment": "05_top_segment.sql",
}

REPORTS_DIR = "reports"
LOGS_DIR = "logs"


def get_connection():
    return pyodbc.connect(CONN_STR)


def read_query_file(filepath):
    """Reads a .sql file and strips out commented-out lines (e.g. '--select * ...')."""
    with open(filepath, "r") as f:
        lines = f.readlines()
    # Drop full-line comments so leftover debug lines (like SELECT * from Orders) don't run
    clean_lines = [line for line in lines if not line.strip().startswith("--")]
    return "\n".join(clean_lines).strip()


def run_query(cursor, sql_text):
    """Runs a query and returns (columns, rows). Raises on failure."""
    cursor.execute(sql_text)
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return columns, rows


def save_success(query_name, columns, rows, run_date):
    """Saves successful query results to a timestamped CSV in reports/."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filename = f"{REPORTS_DIR}/{query_name}_{run_date}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow(list(row))
    print(f"  [OK] {query_name} -> {filename} ({len(rows)} rows)")


def capture_failure(cursor, query_name, sql_text, error, run_date):
    """
    Builds a structured failure record for the AI diagnostic agent (built in Step 6).
    Includes the error, the query, and — where possible — a sample of recent data
    from the table the query touches, so the agent has real context to work with.
    """
    os.makedirs(LOGS_DIR, exist_ok=True)

    failure_record = {
        "query_name": query_name,
        "timestamp": datetime.now().isoformat(),
        "error_message": str(error),
        "error_type": type(error).__name__,
        "sql_text": sql_text,
        "traceback": traceback.format_exc(),
    }

    filename = f"{LOGS_DIR}/failure_{query_name}_{run_date}.json"
    with open(filename, "w") as f:
        json.dump(failure_record, f, indent=2)

    print(f"  [FAILED] {query_name} -> logged to {filename}")
    print(f"           Error: {error}")


def main():
    run_date = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    print(f"SelfHealSQL runner starting: {run_date}\n")

    conn = get_connection()
    summary = {"success": [], "failed": []}

    for query_name, filename in QUERIES.items():
        print(f"Running: {query_name} ({filename})")
        cursor = conn.cursor()
        try:
            sql_text = read_query_file(filename)
            columns, rows = run_query(cursor, sql_text)
            save_success(query_name, columns, rows, run_date)
            summary["success"].append(query_name)
        except Exception as e:
            capture_failure(cursor, query_name, sql_text if "sql_text" in locals() else "", e, run_date)
            summary["failed"].append(query_name)
        finally:
            cursor.close()

    conn.close()

    print("\n--- Run Summary ---")
    print(f"Succeeded: {summary['success']}")
    print(f"Failed:    {summary['failed']}")

    if summary["failed"]:
        print("\nSome queries failed. Check the logs/ folder for details.")
        print("(This is where the AI diagnostic agent will plug in next.)")


if __name__ == "__main__":
    main()