import sqlite3
import pandas as pd
from datetime import *

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

def merge_business_hours() -> None:
    df_business = pd.read_parquet("./data/business.parquet")
    df_business_h = pd.read_parquet("./data/business_hours.parquet")
    
    elements = []
    for key, value in zip(df_business_h["day"], df_business_h["open_close"]):
        open_hour, close_hour = value.split("-")
        dt_open = datetime.strptime(open_hour, "%H:%M")
        dt_close = datetime.strptime(close_hour, "%H:%M")
        elements.append({key: tuple((dt_open.time(), dt_close.time()))})
    
    s = pd.Series(elements)
    
    df_b = pd.concat([df_business_h['business_id'], s], axis=1)
    df_b = df_b.rename(columns = {0: "working_days"})
    
    df_b["working_days"] = df_b["working_days"].apply(lambda x: dict(x))
    
    df_b = (
        df_b.groupby("business_id", sort=False, as_index=False)
            .agg({"working_days": lambda lst: {k: v for d in lst for k, v in d.items()}})
    )
    
    df_merged = pd.merge(df_business, df_b, on="business_id", how="left")
    
    df_merged.to_parquet("./data/business_hours_merge.parquet")
    print("Successful merge: business_hours -> business")

def merge_business_attr() -> None:
    df_business_a = pd.read_parquet("./data/business_attributes.parquet")
    df_business_m = pd.read_parquet("./data/business_hours_merge.parquet")
    
    df_business_a = df_business_a[df_business_a["attr_key"] != "RestaurantsPriceRange2"]
    df_business_a = df_business_a.reset_index(drop=True)
    
    elements = []
    for key, value in zip(df_business_a['attr_key'], df_business_a['attr_value']):
        if value != "True" and value != "False":
            if "{" and "}" in value:
                if value.count(":") == value.count("False") and value.count(":"):
                    value = "False"
                else:
                    value = "True"
            elif value == "None":
                value = "False"
            elif value == "u'free'":
                value = "True"
            elif value == "u'no'":
                value = "False"
        if value == "True":
            value = True
        elif value == "False":
            value = False
        elements.append({key: value})
    
    s = pd.Series(elements)    
    df_b = pd.concat([df_business_a['business_id'], s], axis=1)
    df_b = df_b.rename(columns={0: "features"})
    
    df_b["features"] = df_b["features"].apply(lambda x: dict(x))
    
    df_b = (
        df_b.groupby("business_id", sort=False, as_index=False)
            .agg({"features": lambda lst: {k: v for d in lst for k, v in d.items()}})
    )
    
    df_merged = pd.merge(df_business_m, df_b, on="business_id", how="left")
    
    df_merged.to_parquet("./data/business_merge.parquet")
    print("Successful merge: business_attributes -> business")

def main() -> int:
    export_to_parquet()
    merge_business_hours()
    merge_business_attr()
    return 0

if __name__ == "__main__":
    print("exit code:", main())
