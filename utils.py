
from datetime import datetime
import mysql.connector


def print_header(title):
    print("\n" + "=" * 55)
    print(f" {title}")
    print("=" * 55)


def print_table(rows, columns=None):

    rows = [r for r in (rows or []) if r]

    if not rows:
        print("(No records found)")
        return

    if columns is None:
        columns = list(rows[0].keys())

    widths = {c: max(len(str(c)), *(len(str(r.get(c, ""))) for r in rows)) for c in columns}

    header = " | ".join(str(c).ljust(widths[c]) for c in columns)
    print(header)
    print("-" * len(header))
    for r in rows:
        print(" | ".join(str(r.get(c, "")).ljust(widths[c]) for c in columns))


def prompt_date(label="Date (YYYY-MM-DD): "):

    while True:
        value = input(label).strip()
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("  -> Please enter the date as YYYY-MM-DD, e.g. 2026-09-25.")


def prompt_time(label="Time (HH:MM, 24hr): "):

    while True:
        value = input(label).strip()
        if len(value) == 5:
            value += ":00"
        try:
            datetime.strptime(value, "%H:%M:%S")
            return value
        except ValueError:
            print("  -> Please enter the time as HH:MM in 24-hour format, e.g. 14:30.")


def prompt_int(label, allow_blank=False):

    while True:
        value = input(label).strip()
        if allow_blank and value == "":
            return None
        try:
            return int(value)
        except ValueError:
            print("  -> Please enter a whole number.")


def prompt_float(label):
    while True:
        value = input(label).strip()
        try:
            return float(value)
        except ValueError:
            print("  -> Please enter a valid number, e.g. 500 or 499.99.")


def record_exists(connection, table, id_column, record_id):
    cursor = connection.cursor()
    cursor.execute(f"SELECT 1 FROM {table} WHERE {id_column} = %s", (record_id,))
    found = cursor.fetchone() is not None
    cursor.close()
    return found


def run_write(connection, sql, params, success_msg, error_prefix="Could not complete this action"):

    cursor = connection.cursor()
    try:
        cursor.execute(sql, params)
        connection.commit()
        rowcount = cursor.rowcount
        new_id = cursor.lastrowid
        cursor.close()

        if rowcount == 0:
            print("\nNo matching record was found, so nothing was changed.")
            return False

        print(f"\n{success_msg}" + (f" (ID: {new_id})" if new_id else ""))
        return True

    except mysql.connector.Error as e:
        connection.rollback()
        cursor.close()
        print(f"\n{error_prefix}: {e.msg if hasattr(e, 'msg') else e}")
        return False


def pause():
    input("\nPress Enter to continue...")
