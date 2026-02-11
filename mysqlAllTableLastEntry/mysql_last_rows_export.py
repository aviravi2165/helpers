import mysql.connector
import csv
from mysql.connector import Error

# ---- DB CONFIG ----
DB_CONFIG = {
    "host": "192.168.1.4",
    "user": "root",
    "password": "Passw00rd@9",
    "database": "ievoin_process"
}

OUTPUT_FILE = "latest_rows_all_tables.csv"


def get_tables(cursor):
    cursor.execute("SHOW TABLES")
    return [row[0] for row in cursor.fetchall()]


def get_last_row(cursor, table_name):
    try:
        # Detect Primary Key
        cursor.execute(f"SHOW KEYS FROM `{table_name}` WHERE Key_name = 'PRIMARY'")
        pk = cursor.fetchone()

        if pk:
            pk_column = pk[4]
            cursor.execute(f"""
                SELECT * FROM `{table_name}`
                ORDER BY `{pk_column}` DESC
                LIMIT 1
            """)
        else:
            # Fallback if no PK exists
            cursor.execute(f"SELECT * FROM `{table_name}`")
            rows = cursor.fetchall()
            if not rows:
                return None, []
            return rows[-1], [i[0] for i in cursor.description]

        return cursor.fetchone(), [i[0] for i in cursor.description]

    except Exception as e:
        return f"Error: {str(e)}", []


def main():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)

        if conn.is_connected():
            print("Connected to MySQL")

            cursor = conn.cursor()
            tables = get_tables(cursor)

            with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["TableName", "Data"])

                for table in tables:
                    print(f"Processing {table}")

                    row, columns = get_last_row(cursor, table)

                    if isinstance(row, str):
                        writer.writerow([table, row])
                        continue

                    if not row:
                        writer.writerow([table, "No Data"])
                        continue

                    # Concatenate fields
                    combined = " | ".join(
                        f"{col}={val}" for col, val in zip(columns, row)
                    )

                    writer.writerow([table, combined])

            print(f"\nCSV Generated: {OUTPUT_FILE}")

    except Error as e:
        print("DB Error:", e)

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Connection closed")


if __name__ == "__main__":
    main()
