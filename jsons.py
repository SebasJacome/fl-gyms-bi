from typing import List
import dask.dataframe as pd
import sqlite3
import json

BUSINESS_JSON_PATH = "./yelp_json/yelp_academic_dataset_business.json"
REVIEW_JSON_PATH = "./yelp_json/yelp_academic_dataset_review.json"
TIP_JSON_PATH = "./yelp_json/yelp_academic_dataset_tip.json"
USER_JSON_PATH = "./yelp_json/yelp_academic_dataset_user.json"

DB_NAME = "gyms.db"

def transform_json_to_parquet() -> None:
    files : List[str] = [BUSINESS_JSON_PATH, REVIEW_JSON_PATH, TIP_JSON_PATH, USER_JSON_PATH]
    parquet_names : List[str] = ["business", "review", "tip", "user"]
    for file, name in zip(files, parquet_names):
        try:
            df = pd.read_json(file, lines=True, blocksize="64MB")
            df.to_parquet(f"./data/{name}.parquet", engine="pyarrow", compression="snappy")
        except FileNotFoundError:
            print("You are either missing the JSON files or the names are not correct")
            print("Make sure to download the Yelp Dataset JSON files and set the path to the corresponding constants.")
            print("https://business.yelp.com/data/resources/open-dataset/")
            print("Terminating program")
            quit()

def create_db() -> None:
    con: sqlite3.Connection = sqlite3.connect(DB_NAME)
    cur: sqlite3.Cursor = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS business (
            business_id   TEXT PRIMARY KEY,
            name          TEXT,
            address       TEXT,
            city          TEXT,
            state         TEXT,
            postal_code   TEXT,
            latitude      REAL,
            longitude     REAL,
            stars         REAL,
            review_count  INTEGER,
            is_open       INTEGER   -- 0 = closed, 1 = open
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS business_attributes (
            business_id   TEXT,
            attr_key      TEXT,
            attr_value    TEXT,
            FOREIGN KEY(business_id) REFERENCES business(business_id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS business_categories (
            business_id   TEXT,
            category      TEXT,
            FOREIGN KEY(business_id) REFERENCES business(business_id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS business_hours (
            business_id   TEXT,
            day           TEXT,
            open_close    TEXT,
            FOREIGN KEY(business_id) REFERENCES business(business_id)
        );
    """)

    con.close()

def populate_business_table() -> None:
    con: sqlite3.Connection = sqlite3.connect(DB_NAME)
    cur: sqlite3.Cursor = con.cursor()

    with open(BUSINESS_JSON_PATH, "r") as file:
        batch_size: int = 5000
        # omiting types for batches just because
        # these are essentially list[tuples[...]] where ... are the different types within the business.json
        business_batch = []
        attr_batch = []
        cat_batch = []
        hours_batch = []
        
        for line_num, line in enumerate(file, start=1):
            data: Dict[str, Any] = json.loads(line)
            business_batch.append((
                data["business_id"],
                data["name"],
                data["address"],
                data["city"],
                data["state"],
                data["postal_code"],
                data["latitude"],
                data["longitude"],
                data["stars"],
                data["review_count"],
                data["is_open"]
            ))
            
            if data.get("attributes"):
                for k, v in data["attributes"].items():
                    attr_batch.append((data["business_id"], k, str(v)))

            if data.get("categories"):
                for cat in data["categories"].split(", "):
                    cat_batch.append((data["business_id"], cat))

            if data.get("hours"):
                for day, hours in data["hours"].items():
                    hours_batch.append((data["business_id"], day, hours))

            if line_num % batch_size == 0:
                cur.executemany("""
                    INSERT INTO business (
                        business_id, name, address, city, state, postal_code,
                        latitude, longitude, stars, review_count, is_open
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, business_batch)

                cur.executemany("""
                    INSERT INTO business_attributes (business_id, attr_key, attr_value)
                    VALUES (?, ?, ?)
                """, attr_batch)

                cur.executemany("""
                    INSERT INTO business_categories (business_id, category)
                    VALUES (?, ?)
                """, cat_batch)

                cur.executemany("""
                    INSERT INTO business_hours (business_id, day, open_close)
                    VALUES (?, ?, ?)
                """, hours_batch)

                con.commit()
                business_batch, attr_batch, cat_batch, hours_batch = [], [], [], []

        if business_batch:
            cur.executemany("""
                INSERT INTO business (
                    business_id, name, address, city, state, postal_code,
                    latitude, longitude, stars, review_count, is_open
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, business_batch)

        if attr_batch:
            cur.executemany("""
                INSERT INTO business_attributes (business_id, attr_key, attr_value)
                VALUES (?, ?, ?)
            """, attr_batch)

        if cat_batch:
            cur.executemany("""
                INSERT INTO business_categories (business_id, category)
                VALUES (?, ?)
            """, cat_batch)

        if hours_batch:
            cur.executemany("""
                INSERT INTO business_hours (business_id, day, open_close)
                VALUES (?, ?, ?)
            """, hours_batch)

        con.commit()
    con.close()
    print("Successfully populated the table business and related tables")


def transform_json_to_sql() -> None:
    print("Creating database:")
    create_db()
    print("Database created successfully\nPopulating business table")
    populate_business_table()
    print("Business table successfully populated")

    # test ---- delete later
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    print(cur.execute("SELECT * FROM business LIMIT 10").fetchall())

def main() -> int:
    transform_json_to_sql()
    return 0

if __name__ == "__main__":
    print("Generating db files from jsons")
    print("exit code:", main()) 
