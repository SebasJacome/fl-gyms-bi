# Florida Gyms Dataset Documentation

This dataset is a filtered and transformed version of the original Yelp dataset, focused on gyms located in Florida.  
It is split into three main tables stored as **Parquet files**:

- **Business Data** → `business.parquet` → loaded as `df_b`  
- **Review Data** → `review.parquet` → loaded as `db_r`  
- **Tip Data** → `tip.parquet` → loaded as `db_u`

## Index
- [Florida Gyms Dataset Documentation](#florida-gyms-dataset-documentation)
  - [1. Business Table (`df_b`)](#1-business-table-df_b)
    - [working_days Example](#working_days-example)
    - [features Example](#features-example)
  - [2. Review Table (`db_r`)](#2-review-table-db_r)
    - [review Example](#review-example)
  - [3. Tip Table (`db_u`)](#3-tip-table-db_u)
    - [Tip Example](#tip-example)
  - [Entity Relationships](#entity-relationships)
  - [Summary of Changes from Original Yelp Dataset](#summary-of-changes-from-original-yelp-dataset)
  - [Dataset Filtering and Transformation Process](#dataset-filtering-and-transformation-process)
  - [1st Filter: Database to Only Florida Gyms](#1st-filter-database-to-only-florida-gyms)
  - [2nd Filter: Converting and Merging Data for Analysis](#2nd-filter-converting-and-merging-data-for-analysis)

---

## 1. Business Table (`df_b`)

Contains metadata and attributes for each gym location.

| Column         | Type    | Description                                                                                                                                        |
|----------------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| `business_id`  | string  | Unique 22-character identifier for the business.                                                                                                   |
| `name`         | string  | The gym's name.                                                                                                                                    |
| `address`      | string  | Street address of the gym.                                                                                                                         |
| `city`         | string  | City where the gym is located.                                                                                                                     |
| `state`        | string  | Two-character state code (e.g., `"FL"`).                                                                                                           |
| `postal_code`  | string  | Postal ZIP code.                                                                                                                                   |
| `latitude`     | float   | Latitude coordinate of the gym.                                                                                                                    |
| `longitude`    | float   | Longitude coordinate of the gym.                                                                                                                   |
| `stars`        | float   | Average star rating (1.0–5.0, rounded to the nearest half star).                                                                                   |
| `review_count` | int     | Total number of reviews for the gym.                                                                                                               |
| `is_open`      | int     | `1` if the gym is currently open, `0` if permanently closed.                                                                                       |
| `working_days` | object  | Dictionary of opening/closing times per weekday. Values are `datetime.time` objects (stored as arrays of `[open, close]`).                         |
| `features`     | object  | Dictionary of amenity flags. Values can be `true` (available), `false` (not available), or `null` (not specified).                                 |

### `working_days` example
```json
{
  "Monday":   ["06:00", "22:00"],
  "Tuesday":  ["06:00", "22:00"],
  "Wednesday":["06:00", "22:00"],
  "Thursday": ["06:00", "22:00"],
  "Friday":   ["06:00", "20:00"],
  "Saturday": ["08:00", "18:00"],
  "Sunday":   ["09:00", "14:00"]
}
```

### `features` example
```json
{
  "AcceptsInsurance": false,
  "BikeParking": true,
  "BusinessAcceptsBitcoin": null,
  "BusinessAcceptsCreditCards": true,
  "BusinessParking": true,
  "ByAppointmentOnly": false,
  "DogsAllowed": false,
  "GoodForKids": true,
  "WheelchairAccessible": true,
  "WiFi": false
}
```

## 2. Review Table (``db_r``)

Contains detailed customer reviews for each gym.

| Column        | Type   | Description                                            |
| ------------- | ------ | ------------------------------------------------------ |
| `review_id`   | string | Unique 22-character identifier for the review.         |
| `user_id`     | string | Unique 22-character identifier for the authoring user. |
| `business_id` | string | Foreign key linking to `df_b.business_id`.             |
| `stars`       | int    | Star rating given in this review (1–5).                |
| `date`        | string | Review date in `YYYY-MM-DD` format.                    |
| `text`        | string | Full text of the review.                               |
| `useful`      | int    | Number of “useful” votes this review received.         |
| `funny`       | int    | Number of “funny” votes this review received.          |
| `cool`        | int    | Number of “cool” votes this review received.           |

### `review` example
```json
{
  "review_id": "xyz456",
  "user_id": "user789",
  "business_id": "abc123",
  "stars": 5,
  "date": "2024-05-12",
  "text": "Amazing gym! Super clean and modern equipment.",
  "useful": 3,
  "funny": 0,
  "cool": 1
}
``` 

## 3. Tip Table (`db_u`)
Contains short tips left by users. Tips are quick comments or suggestions and are shorter than reviews.

| **Column**         | **Type** | **Description**                                    |
| ------------------ | -------- | -------------------------------------------------- |
| `tip_id`           | `int`    | Unique integer identifier for the tip.             |
| `text`             | `string` | The content of the tip.                            |
| `date`             | `string` | Date the tip was posted (`YYYY-MM-DD`).            |
| `compliment_count` | `int`    | Number of compliments this tip received.           |
| `business_id`      | `string` | Foreign key linking to `df_b.business_id`.         |
| `user_id`          | `string` | Foreign key linking to the user who wrote the tip. |

### `Tip` example
```json
{
  "tip_id": 101,
  "text": "Try their Saturday morning yoga class!",
  "date": "2024-05-10",
  "compliment_count": 5,
  "business_id": "abc123",
  "user_id": "user789"
}
```

## Entity Relationships
| **From**           | **To**             | **Relationship**               |
| ------------------ | ------------------ | ------------------------------ |
| `df_b.business_id` | `db_r.business_id` | One gym can have many reviews. |
| `df_b.business_id` | `db_u.business_id` | One gym can have many tips.    |

### Summary of Changes from Original Yelp Dataset
| **Original Field**                          | **Modified Field** | **Description**                                      |
| ------------------------------------------- | ------------------ | ---------------------------------------------------- |
| `attributes`                                | `features`         | Simplified into a clean Boolean/nullable dictionary. |
| `hours`                                     | `working_days`     | Converted to structured opening/closing times.       |
| `categories`, `checkins`, `photos`, `users` | **Removed**        | Not needed for gym analysis.                         |

## Dataset Filtering and Transformation Process

The original Yelp dataset is provided as four large JSON files (`business`, `review`, `tip`, and `user`).  
To make the data easier to query and process, these files were first **transformed into a structured SQLite database**.

The script begins by creating a database schema that organizes the data into normalized tables:
- **Business information** is split across multiple tables for core details, attributes, categories, and operating hours.
- **Reviews**, **users**, and **tips** each have their own dedicated tables, with foreign key relationships linking them back to the businesses.

Once the schema is in place, each JSON file is processed line-by-line to handle its massive size efficiently.  
Data is inserted into the database using batch operations, which greatly improve performance.  
For example, the `business` JSON populates the main business table as well as related tables for attributes, categories, and hours.  
Similarly, the `review`, `tip`, and `user` files populate their respective tables with detailed information about customer feedback, tips, and user metadata.

To speed up the process, all four population functions run **in parallel** using multiple processes.  
This allows the system to handle the large amount of data more efficiently and reduce overall processing time.

The final result is a fully populated SQLite database (`gyms.db`) containing a clean, relational version of the Yelp dataset.  
This database serves as the foundation for subsequent filtering steps, such as isolating Florida businesses and focusing specifically on gym-related categories, which are later exported as optimized `.parquet` files for analysis and visualization.

## 1st Filter: Database to Only Florida Gyms

After creating the full SQLite database with all Yelp data, the next step is to **filter the dataset** so that it only contains information relevant to **gyms located in Florida**.  

The filtering process includes the following operations:

1. **Remove Non-Florida Gyms**  
   The script checks the `business` table and keeps only businesses:
   - Located in Florida (`state = 'FL'`).
   - Categorized specifically as `"Gyms"` in the `business_categories` table.
   All other businesses are deleted.

2. **Clean Related Tables**  
   Once irrelevant businesses are removed, orphaned records in related tables are also cleaned.  
   This ensures there are no rows referring to businesses that no longer exist in the filtered dataset.
   - Tables cleaned:  
     `review`, `tip`, `business_categories`, `business_hours`, `business_attributes`

3. **Remove Unused Users**  
   The `user` table is then cleaned to keep only users who have either:
   - Written at least one review, or  
   - Posted at least one tip  
   for the remaining Florida gyms.

4. **Database Optimization**  
   After deletion, the `VACUUM` command is executed to shrink the database size from **several gigabytes (≈6GB)** to just a few megabytes.  
   This makes the database much lighter and faster for further processing.

The result is a **clean, focused SQLite database** containing only gyms located in Florida and all directly related data, ready for export and analysis.

---

## 2nd Filter: Converting and Merging Data for Analysis

Once the filtered SQLite database (`gyms.db`) is ready, the next step is to **export, clean, and merge** the data into optimized `.parquet` files for analysis and visualization.

The process begins by exporting each table from the database into individual Parquet files.  
Exporting to Parquet provides faster read/write performance and better storage efficiency through compression.

Two key merge operations are then performed:

1. **Merging Business Hours**  
   - The `business_hours` table contains one row per day with opening and closing times stored as strings.  
   - These times are converted into Python `datetime.time` objects and grouped by `business_id`.  
   - A new column called `working_days` is created, where each row contains a dictionary mapping days of the week to their respective opening and closing times.

2. **Merging Business Attributes**  
   - The `business_attributes` table contains various key-value pairs about each business (e.g., Wi-Fi availability, parking options).  
   - Values stored as strings like `"True"`, `"False"`, `"None"`, or nested structures are cleaned and normalized into proper boolean values.  
   - Features are grouped by `business_id` and stored in a single column called `features`.

The final result is a master file named `business.parquet`, which combines:
- Core business details  
- Cleaned working schedules (`working_days`)  
- Normalized features (`features`)
