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