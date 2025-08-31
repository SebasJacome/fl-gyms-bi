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


def export_all_to_single_parquet() -> None:
    con = sqlite3.connect(DB)

    print("Starting exporting process...")
    df_business = pd.read_sql_query("SELECT * FROM business", con)

    df_categories = pd.read_sql_query("SELECT * FROM business_categories", con)
    df_attributes = pd.read_sql_query("SELECT * FROM business_attributes", con)
    df_hours = pd.read_sql_query("SELECT * FROM business_hours", con)

    df_business = (
        df_business
        .merge(df_categories, on="business_id", how="left")
        .merge(df_attributes, on="business_id", how="left")
        .merge(df_hours, on="business_id", how="left")
    )

    df_users = pd.read_sql_query("SELECT * FROM user", con)

    df_reviews = pd.read_sql_query("SELECT * FROM review", con)

    df_tips = pd.read_sql_query("SELECT * FROM tip", con)

    df_reviews = df_reviews.merge(df_users, on="user_id", how="left")
    df_reviews = df_reviews.merge(df_business, on="business_id", how="left")
    df_tips = df_tips.merge(df_users, on="user_id", how="left")
    df_tips = df_tips.merge(df_business, on="business_id", how="left")
    df_all = pd.concat([df_reviews, df_tips], ignore_index=True, sort=False)

    print(f"Writing to {OUT}...")
    df_all.to_parquet(OUT, engine="pyarrow", index=False, compression="snappy")

    con.close()
    print("Export completed...")


def main() -> int:
    #export_to_parquet()
    export_all_to_single_parquet()
    return 0

if __name__ == "__main__":
    print("exit code:", main())
