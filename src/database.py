import sqlite3
import pandas as pd


def get_connection(db_path: str = "data/processed/pharmacy_exchange.db"):
    return sqlite3.connect(db_path)


def save_dataframe(df: pd.DataFrame, table_name: str, db_path: str = "data/processed/pharmacy_exchange.db"):
    conn = get_connection(db_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()


def load_table(table_name: str, db_path: str = "data/processed/pharmacy_exchange.db") -> pd.DataFrame:
    conn = get_connection(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


def create_custom_thresholds_table(db_path: str = "data/processed/pharmacy_exchange.db"):
    conn = get_connection(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS custom_thresholds (
            pharmacy_id TEXT,
            medicine_name TEXT,
            medicine_code TEXT,
            low_stock_threshold INTEGER
        )
    """)
    conn.commit()
    conn.close()


def insert_custom_threshold(pharmacy_id: str, medicine_name: str, medicine_code: str, low_stock_threshold: int,
                            db_path: str = "data/processed/pharmacy_exchange.db"):
    conn = get_connection(db_path)
    conn.execute("""
        INSERT INTO custom_thresholds (pharmacy_id, medicine_name, medicine_code, low_stock_threshold)
        VALUES (?, ?, ?, ?)
    """, (pharmacy_id, medicine_name, medicine_code, low_stock_threshold))
    conn.commit()
    conn.close()


def delete_custom_threshold(pharmacy_id: str, medicine_code: str,
                            db_path: str = "data/processed/pharmacy_exchange.db"):
    conn = get_connection(db_path)
    conn.execute("""
        DELETE FROM custom_thresholds
        WHERE pharmacy_id = ? AND medicine_code = ?
    """, (pharmacy_id, medicine_code))
    conn.commit()
    conn.close()


def load_custom_thresholds(db_path: str = "data/processed/pharmacy_exchange.db") -> pd.DataFrame:
    conn = get_connection(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM custom_thresholds", conn)
    except Exception:
        df = pd.DataFrame(columns=["pharmacy_id", "medicine_name", "medicine_code", "low_stock_threshold"])
    conn.close()
    return df

def create_surplus_thresholds_table(db_path: str = "data/processed/pharmacy_exchange.db"):
    conn = get_connection(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS custom_surplus_thresholds (
            pharmacy_id TEXT,
            medicine_name TEXT,
            medicine_code TEXT,
            surplus_threshold INTEGER,
            expiry_days_threshold INTEGER
        )
    """)
    conn.commit()
    conn.close()


def insert_surplus_threshold(
    pharmacy_id: str,
    medicine_name: str,
    medicine_code: str,
    surplus_threshold: int,
    expiry_days_threshold: int,
    db_path: str = "data/processed/pharmacy_exchange.db"
):
    conn = get_connection(db_path)
    conn.execute("""
        INSERT INTO custom_surplus_thresholds (
            pharmacy_id, medicine_name, medicine_code, surplus_threshold, expiry_days_threshold
        )
        VALUES (?, ?, ?, ?, ?)
    """, (pharmacy_id, medicine_name, medicine_code, surplus_threshold, expiry_days_threshold))
    conn.commit()
    conn.close()


def delete_surplus_threshold(
    pharmacy_id: str,
    medicine_code: str,
    db_path: str = "data/processed/pharmacy_exchange.db"
):
    conn = get_connection(db_path)
    conn.execute("""
        DELETE FROM custom_surplus_thresholds
        WHERE pharmacy_id = ? AND medicine_code = ?
    """, (pharmacy_id, medicine_code))
    conn.commit()
    conn.close()


def load_surplus_thresholds(db_path: str = "data/processed/pharmacy_exchange.db") -> pd.DataFrame:
    conn = get_connection(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM custom_surplus_thresholds", conn)
    except Exception:
        df = pd.DataFrame(columns=[
            "pharmacy_id",
            "medicine_name",
            "medicine_code",
            "surplus_threshold",
            "expiry_days_threshold"
        ])
    conn.close()
    return df