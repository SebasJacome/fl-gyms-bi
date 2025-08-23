from typing import List
import dask.dataframe as pd

BUSINESS_JSON_PATH = "./yelp_json/yelp_academic_dataset_business.json"
REVIEW_JSON_PATH = "./yelp_json/yelp_academic_dataset_review.json"
TIP_JSON_PATH = "./yelp_json/yelp_academic_dataset_tip.json"
USER_JSON_PATH = "./yelp_json/yelp_academic_dataset_user.json"

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

def main() -> int:
    transform_json_to_parquet()
    return 0

if __name__ == "__main__":
    print("Generating parquet files from jsons")
    print("exit code:", main()) 
