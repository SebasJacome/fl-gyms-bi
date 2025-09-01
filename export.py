import sqlite3
import pandas as pd

TABLES = ["review", "user", "tip", "business", "business_categories", "business_attributes", "business_hours"]
DB = "./data/gyms.db"
OUT = "./data/yelp.parquet"
CHUNKSIZE = 100_000

def export_to_parquet() -> None:
    con = sqlite3.connect(DB)
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", con)["name"].tolist()
    for table in TABLES:
        print(f"Exporting {table}...")
        out_file = f"./data/{table}.parquet"
        pd.read_sql_query(f"SELECT * FROM {table}", con).to_parquet(
            out_file, engine="pyarrow", index=False, compression="snappy"
        )
        
    con.close()
    print("Export complete...")

def main() -> int:
    export_to_parquet()
    return 0

if __name__ == "__main__":
    print("exit code:", main())
