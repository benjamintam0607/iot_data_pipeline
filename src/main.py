import os
import glob
import argparse
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db
from worker import process_file

DEFAULT_TARGET_DIR = "target_directory"
DEFAULT_DB_PATH = "data/iot.db"

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="IoT Sensor Data Processor")
    parser.add_argument("--target_directory", "-i", default=DEFAULT_TARGET_DIR,
                        help="Directory containing CSV files (default: target_directory)")
    parser.add_argument("--db-path", "-d", default=DEFAULT_DB_PATH,
                        help="Path to SQLite database (default: database/iot.db)")
    return parser.parse_args()

def main():
    args = parse_args()
    
    target_dir = args.target_directory
    db_path = args.db_path
    
    os.environ["DB_PATH"] = db_path
    
    print(f"Target Directory: {target_dir}")
    print(f"Database Path: {db_path}")
    print("Initializing Database...")
    init_db(db_path)
    
    files = glob.glob(os.path.join(target_dir, "*.csv"))
    print(f"Found {len(files)} files to process.")
    
    total_valid = 0
    total_invalid = 0
    
    max_workers = os.cpu_count() or 4
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(process_file, f, db_path): f for f in files}
        for future in as_completed(future_to_file):
            try:
                path, valid, invalid = future.result()
                total_valid += valid
                total_invalid += invalid
                print(f"Processed: {path} | Valid: {valid} | Invalid: {invalid}")
            except Exception as exc:
                print(f"File generated an exception: {exc}")

    print(f"Done. Total Valid: {total_valid}, Total Invalid: {total_invalid}")

if __name__ == "__main__":
    main()
