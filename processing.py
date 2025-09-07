import sqlite3
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait

DB = "./data/gyms.db"
TABLES = ["review", "tip", "business_categories", "business_hours", "business_attributes"]

def drop_orphans(table_name: str) -> None:
    print(f"Dropping {table_name} table data...")
    con: sqlite3.Connection = sqlite3.connect(DB, timeout=30)
    cur: sqlite3.Cursor = con.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")

    cur.execute(f"""
        DELETE FROM {table_name} 
        WHERE business_id NOT IN (SELECT business_id FROM business);
    """)

    con.commit()
    con.close()
    print(f"{table_name} table data has been removed successfully")
    
def drop_user_table() -> None:
    print("Dropping user table data...")
    con: sqlite3.Connection = sqlite3.connect(DB)
    cur: sqlite3.Cursor = con.cursor()
    cur.execute("""
            DELETE FROM user
            WHERE user_id NOT IN (SELECT DISTINCT user_id FROM review)
              AND user_id NOT IN (SELECT DISTINCT user_id FROM tip);
        """)

    con.commit()

    cur.execute("VACUUM;") # shrinking the size of the database after cleansing it, from 6GB -> 6MB.

    con.close()
    print("User table data has been removed successfully")

def drop_rows() -> None:
    print("Dropping rows...")
    con: sqlite3.Connection = sqlite3.connect(DB)
    cur: sqlite3.Cursor = con.cursor()
    cur.execute("""
        DELETE FROM business
        WHERE business_id NOT IN (
            SELECT b.business_id
            FROM business b
            JOIN business_categories bc ON b.business_id = bc.business_id
            WHERE b.state = 'FL'
              AND bc.category = 'Gyms'
        );
    """)
    
    con.commit()
    con.close()

    print("Dropped all non-Florida gyms and cleaned related tables.")

def main() -> int:
    drop_rows()
    [drop_orphans(table) for table in TABLES]
    drop_user_table()
    return 0

if __name__ == "__main__":
    print("exit code:", main())
