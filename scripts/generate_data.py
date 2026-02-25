#!/usr/bin/env python3
"""
Mock Data Generator for IoT Sensor Data Ingestion Test.

This script generates CSV files with various data scenarios:
- Valid records
- Invalid timestamps
- Invalid numeric values
- Duplicate records (within file and across files)
- Edge cases (empty fields, special characters)

Usage:
    python scripts/generate_data.py [--output-dir ./test-data] [--num-files 10]
"""
import csv
import os
import random
import string
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

DEFAULT_OUTPUT_DIR = "./target_directory"
DEFAULT_NUM_FILES = 1000
DEFAULT_ROWS_PER_FILE = 500
DEFAULT_SENSOR_COUNT = 4

SENSOR_NAMES = [
    "temperature-sensor", "humidity-sensor", "pressure-sensor",
    "light-sensor",
]

def parse_args():
    parser = argparse.ArgumentParser(description="IoT Sensor Mock Data Generator")
    parser.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT_DIR,
                        help="Output directory for generated CSV files")
    parser.add_argument("--num-files", "-n", type=int, default=DEFAULT_NUM_FILES,
                        help="Number of CSV files to generate")
    parser.add_argument("--rows-per-file", "-r", type=int, default=DEFAULT_ROWS_PER_FILE,
                        help="Number of rows per file")
    parser.add_argument("--sensor-count", "-s", type=int, default=DEFAULT_SENSOR_COUNT,
                        help="Number of unique sensors")
    return parser.parse_args()

DATA_CONFIG = {
    "output_dir": DEFAULT_OUTPUT_DIR,
    "num_files": DEFAULT_NUM_FILES,
    "rows_per_file": DEFAULT_ROWS_PER_FILE,
    "sensor_count": DEFAULT_SENSOR_COUNT,
    "dirty_ratio": 0.05,
    "duplicate_ratio": 0.02,
    "start_date": datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc),
    "time_range_days": 30,
}

# =============================================================================
# Data Generation Helpers
# =============================================================================

def generate_sensor_name(sensor_id: int) -> str:
    """Generate a sensor name with ID suffix."""
    base_name = random.choice(SENSOR_NAMES)
    return f"{base_name}-{sensor_id:04d}"

def generate_valid_timestamp(base_time: datetime, time_range_days: int) -> str:
    """Generate a valid ISO8601 timestamp with timezone."""
    random_seconds = random.randint(0, time_range_days * 24 * 3600)
    timestamp = base_time + timedelta(seconds=random_seconds)
    # ISO8601 format with timezone
    return timestamp.isoformat()

def generate_valid_value() -> str:
    """Generate a valid numeric value."""
    # Mix of integers and decimals
    if random.random() > 0.5:
        return str(random.uniform(-1000, 1000))
    else:
        return str(random.randint(-1000, 1000))
    
def generate_dirty_timestamp() -> str:
    """Generate various invalid timestamp formats."""
    dirty_types = [
        "not-a-date",                              # Plain text
        "2024/01/01 12:00:00",                     # Wrong separator
        "01-01-2024T12:00:00Z",                    # Wrong date order
        "2024-13-45T99:99:99Z",                    # Invalid date/time values
        "1704067200",                              # Unix timestamp (not ISO8601)
        "2024-01-01",                              # Missing time
        "2024-01-01T12:00:00",                     # Missing timezone
        "",                                        # Empty string
        "2024-01-01T12:00:00+99:99",               # Invalid timezone offset
    ]
    return random.choice(dirty_types)


def generate_dirty_value() -> str:
    """Generate various invalid numeric values."""
    dirty_types = [
        "ABC",                                     # Text
        "true",                                    # Boolean string
        "null",                                    # Null string
        "N/A",                                     # Not available
        "-",                                       # Dash
        "12.34.56",                                # Multiple decimals
        "1,234.56",                                # Comma separator
        "$100",                                    # Currency symbol
        "",                                        # Empty string
        "NaN",                                     # Not a Number
        "Infinity",                                # Infinity
    ]
    return random.choice(dirty_types)

# =============================================================================
# Record Generation
# =============================================================================

def generate_valid_record(sensor_pool: List[str]) -> Dict[str, str]:
    """Generate a single valid record."""
    return {
        "timestamp": generate_valid_timestamp(
            DATA_CONFIG["start_date"],
            DATA_CONFIG["time_range_days"]
        ),
        "sensorName": random.choice(sensor_pool),
        "value": generate_valid_value()
    }


def generate_dirty_record(sensor_pool: List[str]) -> Dict[str, str]:
    """Generate a single dirty record (invalid timestamp or value)."""
    record = generate_valid_record(sensor_pool)
    
    # Randomly corrupt timestamp or value
    if random.random() > 0.5:
        record["timestamp"] = generate_dirty_timestamp()
    else:
        record["value"] = generate_dirty_value()
    
    return record

# =============================================================================
# File Generation
# =============================================================================

def generate_sensor_pool(sensor_count: int) -> List[str]:
    """Generate a pool of unique sensor names."""
    return [generate_sensor_name(i) for i in range(sensor_count)]


def write_csv_file(
    filepath: Path,
    records: List[Dict[str, str]],
    fieldnames: List[str]
) -> None:
    """Write records to a CSV file."""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def generate_file(
    file_id: int,
    sensor_pool: List[str],
    shared_records: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """
    Generate a single CSV file with mixed valid, dirty, and duplicate records.
    Returns generated records for cross-file duplication.
    """
    rows = DATA_CONFIG["rows_per_file"]
    dirty_count = int(rows * DATA_CONFIG["dirty_ratio"])
    duplicate_count = int(rows * DATA_CONFIG["duplicate_ratio"])
    valid_count = rows - dirty_count - duplicate_count
    
    records = []
    
    # 1. Generate valid records
    for _ in range(valid_count):
        records.append(generate_valid_record(sensor_pool))
    
    # 2. Generate dirty records
    for _ in range(dirty_count):
        records.append(generate_dirty_record(sensor_pool))
    
    # 3. Generate duplicate records (within this file)
    if records and duplicate_count > 0:
        # Pick some existing records to duplicate
        source_records = records[:min(100, len(records))]
        for _ in range(duplicate_count):
            records.append(random.choice(source_records).copy())
    
    # 4. Add cross-file duplicates (from shared pool)
    if shared_records:
        cross_file_dup_count = min(10, len(shared_records))
        for _ in range(cross_file_dup_count):
            records.append(random.choice(shared_records).copy())
    
    # Shuffle to make it realistic
    random.shuffle(records)
    
    # Write to file
    fieldnames = ["timestamp", "sensorName", "value"]
    filepath = Path(DATA_CONFIG["output_dir"]) / f"file-{file_id:04d}.csv"
    write_csv_file(filepath, records, fieldnames)
    
    # Return some records for cross-file duplication
    return records

# =============================================================================
# Main Execution
# =============================================================================

def setup_output_directory() -> Path:
    """Create output directory if it doesn't exist."""
    output_path = Path(DATA_CONFIG["output_dir"])
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Output directory: {output_path.absolute()}")
    return output_path


def cleanup_existing_files(output_dir: Path) -> None:
    """Remove existing CSV files in output directory."""
    existing_files = list(output_dir.glob("*.csv"))
    if existing_files:
        print(f"[WARNING] Cleaning up {len(existing_files)} existing CSV files...")
        for f in existing_files:
            f.unlink()


def main() -> None:
    """Main entry point for data generation."""
    args = parse_args()
    
    DATA_CONFIG["output_dir"] = args.output_dir
    DATA_CONFIG["num_files"] = args.num_files
    DATA_CONFIG["rows_per_file"] = args.rows_per_file
    DATA_CONFIG["sensor_count"] = args.sensor_count
    
    print("=" * 60)
    print("IoT Sensor Mock Data Generator")
    print("=" * 60)
    
    output_dir = setup_output_directory()
    cleanup_existing_files(output_dir)
    
    # Generate sensor pool
    sensor_pool = generate_sensor_pool(DATA_CONFIG["sensor_count"])
    print(f"[OK] Generated {len(sensor_pool)} unique sensor names")
    
    # Generate files
    shared_records: List[Dict[str, str]] = []
    total_records = 0
    total_dirty = 0
    total_duplicates = 0
    
    print(f"\nGenerating {DATA_CONFIG['num_files']} CSV files...")
    
    for i in range(1, DATA_CONFIG["num_files"] + 1):
        file_records = generate_file(i, sensor_pool, shared_records)
        total_records += len(file_records)
        print(total_records)
        
        # Estimate dirty and duplicate counts
        rows = DATA_CONFIG["rows_per_file"]
        total_dirty += int(rows * DATA_CONFIG["dirty_ratio"])
        total_duplicates += int(rows * DATA_CONFIG["duplicate_ratio"])
        
        # Build shared pool for cross-file duplicates
        if i <= 5:  # First 5 files contribute to shared pool
            shared_records.extend(file_records[:50])
        
        # Progress indicator
        if i % 5 == 0 or i == DATA_CONFIG["num_files"]:
            print(f"  Generated {i}/{DATA_CONFIG['num_files']} files...")
    
    print("\n" + "=" * 60)
    print("Generation Summary")
    print("=" * 60)
    print(f"Output Directory: {output_dir.absolute()}")
    print(f"Total Files: {DATA_CONFIG['num_files']}")
    print(f"Approx. Total Records: {total_records:,}")
    print(f"Approx. Dirty Records: {total_dirty:,} ({DATA_CONFIG['dirty_ratio']*100:.1f}%)")
    print(f"Approx. Duplicate Records: {total_duplicates:,} ({DATA_CONFIG['duplicate_ratio']*100:.1f}%)")
    print(f"Unique Sensors: {len(sensor_pool)}")
    print("=" * 60)
    print("[OK] Mock data generation completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()