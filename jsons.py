import sys
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait
import sqlite3
import json

BATCH_SIZE = 5000

BUSINESS_JSON_PATH = "./yelp_json/yelp_academic_dataset_business.json"
REVIEW_JSON_PATH = "./yelp_json/yelp_academic_dataset_review.json"
TIP_JSON_PATH = "./yelp_json/yelp_academic_dataset_tip.json"
USER_JSON_PATH = "./yelp_json/yelp_academic_dataset_user.json"

DB_NAME = "./data/gyms.db"

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
            is_open       INTEGER
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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS review (
            review_id    TEXT PRIMARY KEY,
            user_id      TEXT NOT NULL,
            business_id  TEXT NOT NULL,
            stars        INTEGER NOT NULL,
            date         TEXT NOT NULL,
            text         TEXT,
            useful       INTEGER DEFAULT 0,
            funny        INTEGER DEFAULT 0,
            cool         INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES user(user_id),
            FOREIGN KEY(business_id) REFERENCES business(business_id)
        );    
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user (
            user_id          TEXT PRIMARY KEY,
            name             TEXT,
            review_count     INTEGER,
            yelping_since    TEXT,
            useful           INTEGER DEFAULT 0,
            funny            INTEGER DEFAULT 0,
            cool             INTEGER DEFAULT 0,
            fans             INTEGER DEFAULT 0,
            average_stars    REAL DEFAULT 0.0,
            compliment_hot       INTEGER DEFAULT 0,
            compliment_more      INTEGER DEFAULT 0,
            compliment_profile   INTEGER DEFAULT 0,
            compliment_cute      INTEGER DEFAULT 0,
            compliment_list      INTEGER DEFAULT 0,
            compliment_note      INTEGER DEFAULT 0,
            compliment_plain     INTEGER DEFAULT 0,
            compliment_cool      INTEGER DEFAULT 0,
            compliment_funny     INTEGER DEFAULT 0,
            compliment_writer    INTEGER DEFAULT 0,
            compliment_photos    INTEGER DEFAULT 0
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tip (
            tip_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            text             TEXT NOT NULL,
            date             TEXT NOT NULL,
            compliment_count INTEGER DEFAULT 0,
            business_id      TEXT NOT NULL,
            user_id          TEXT NOT NULL,
            FOREIGN KEY(business_id) REFERENCES business(business_id),
            FOREIGN KEY(user_id) REFERENCES user(user_id)
        );
    """)

    con.close()

def populate_business_table() -> None:
    con: sqlite3.Connection = sqlite3.connect(DB_NAME, timeout=30)
    cur: sqlite3.Cursor = con.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    print("Starting to populate business table")
    with open(BUSINESS_JSON_PATH, "r") as file:
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

            if line_num % BATCH_SIZE == 0:
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

def populate_review_table() -> None:
    con: sqlite3.Connection = sqlite3.connect(DB_NAME, timeout=30)
    cur: sqlite3.Cursor = con.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    print("Starting to populate review table")
    with open(REVIEW_JSON_PATH, "r", encoding="utf-8") as file:
        review_batch = []

        for line_num, line in enumerate(file, start=1):
            data: Dict[str, Any] = json.loads(line)

            review_batch.append((
                data["review_id"],
                data["user_id"],
                data["business_id"],
                float(data["stars"]),
                data["date"],
                data.get("text", ""),
                int(data.get("useful", 0)),
                int(data.get("funny", 0)),
                int(data.get("cool", 0))
            ))

            if line_num % BATCH_SIZE == 0:
                cur.executemany("""
                    INSERT INTO review (
                        review_id, user_id, business_id, stars, date, text, useful, funny, cool
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, review_batch)

                con.commit()
                review_batch = []

        if review_batch:
            cur.executemany("""
                INSERT INTO review (
                    review_id, user_id, business_id, stars, date, text, useful, funny, cool
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, review_batch)

            con.commit()

    con.close()
    print("Successfully populated the review table")



def populate_tip_table() -> None:
    con: sqlite3.Connection = sqlite3.connect(DB_NAME, timeout=30)
    cur: sqlite3.Cursor = con.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    print("Starting to populate tip table")
    with open(TIP_JSON_PATH, "r", encoding="utf-8") as file:        
        tip_batch = []

        for line_num, line in enumerate(file, start=1):
            data: Dict[str, Any] = json.loads(line)

            tip_batch.append((
                data["user_id"],
                data["business_id"],
                data.get("text", ""),
                data["date"],
                int(data.get("compliment_count", 0))
            ))

            if line_num % BATCH_SIZE == 0:
                cur.executemany("""
                    INSERT INTO tip (user_id, business_id, text, date, compliment_count)
                    VALUES (?, ?, ?, ?, ?)
                """, tip_batch)

                con.commit()
                tip_batch = []

        if tip_batch:
            cur.executemany("""
                INSERT INTO tip (user_id, business_id, text, date, compliment_count)
                VALUES (?, ?, ?, ?, ?)
            """, tip_batch)

            con.commit()

    con.close()
    print("Successfully populated the tip table")

def populate_user_table() -> None:
    con: sqlite3.Connection = sqlite3.connect(DB_NAME, timeout=30)
    cur: sqlite3.Cursor = con.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    print("Starting to populate user table")
    with open(USER_JSON_PATH, "r") as file:
        user_batch = []
        elite_batch = []

        for line_num, line in enumerate(file, start=1):
            data: Dict[str, Any] = json.loads(line)

            user_batch.append((
                data["user_id"],
                data.get("name", ""),
                int(data.get("review_count", 0)),
                data.get("yelping_since", ""),
                int(data.get("useful", 0)),
                int(data.get("funny", 0)),
                int(data.get("cool", 0)),
                int(data.get("fans", 0)),
                float(data.get("average_stars", 0.0)),
                int(data.get("compliment_hot", 0)),
                int(data.get("compliment_more", 0)),
                int(data.get("compliment_profile", 0)),
                int(data.get("compliment_cute", 0)),
                int(data.get("compliment_list", 0)),
                int(data.get("compliment_note", 0)),
                int(data.get("compliment_plain", 0)),
                int(data.get("compliment_cool", 0)),
                int(data.get("compliment_funny", 0)),
                int(data.get("compliment_writer", 0)),
                int(data.get("compliment_photos", 0))
            ))

            if line_num % BATCH_SIZE == 0:
                cur.executemany("""
                    INSERT INTO user (
                        user_id, name, review_count, yelping_since, useful, funny, cool,
                        fans, average_stars, compliment_hot, compliment_more, compliment_profile,
                        compliment_cute, compliment_list, compliment_note, compliment_plain,
                        compliment_cool, compliment_funny, compliment_writer, compliment_photos
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, user_batch)

                con.commit()
                user_batch = []

        if user_batch:
            cur.executemany("""
                INSERT INTO user (
                    user_id, name, review_count, yelping_since, useful, funny, cool,
                    fans, average_stars, compliment_hot, compliment_more, compliment_profile,
                    compliment_cute, compliment_list, compliment_note, compliment_plain,
                    compliment_cool, compliment_funny, compliment_writer, compliment_photos
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, user_batch)

            con.commit()

    con.close()
    print("Successfully populated the user table")


def transform_json_to_sql() -> None:
    print("Creating database:")
    create_db()
    print("Database created successfully\nPopulating tables")
    with ProcessPoolExecutor() as e:
        futures = [
            e.submit(populate_business_table),
            e.submit(populate_review_table),
            e.submit(populate_tip_table),
            e.submit(populate_user_table)
        ]
        
        dones, _ = wait(futures)

        for done in dones:
            try:
                done.result()
            except FileNotFoundError:
                print("Some file(s) from the Yelp Database was(were) not found")
                print("Make sure to download and store them with the specified format")
                print("./yelp_json/{here the json files}")
                print("https://business.yelp.com/data/resources/open-dataset/")
                sys.exit(1)

def main() -> int:
    transform_json_to_sql()
    return 0

if __name__ == "__main__":
    print("Generating db files from jsons")
    print("exit code:", main()) 
