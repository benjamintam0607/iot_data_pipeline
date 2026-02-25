import csv
import sqlite3
from datetime import datetime
from db import get_connection

def validate_timestamp(ts_str):
    try:
        # 尝试解析 ISO8601，Python 3.7+ fromisoformat 支持大部分格式
        # 为了兼容时区，简单处理：替换 Z 为 +00:00
        ts_str = ts_str.replace('Z', '+00:00')
        datetime.fromisoformat(ts_str)
        return ts_str
    except Exception:
        return None

def validate_value(val_str):
    try:
        return float(val_str)
    except (ValueError, TypeError):
        return None

def process_file(file_path, db_path=None):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    valid_count = 0
    invalid_count = 0
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ts = validate_timestamp(row.get('timestamp', ''))
                val = validate_value(row.get('value', ''))
                sensor = row.get('sensorName', '').strip()
                
                if ts and val is not None and sensor:
                    try:
                        cursor.execute(
                            "INSERT OR IGNORE INTO sensor_readings (timestamp, sensor_name, value) VALUES (?, ?, ?)",
                            (ts, sensor, val)
                        )
                        valid_count += 1
                    except Exception:
                        invalid_count += 1
                else:
                    invalid_count += 1
        conn.commit()
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    finally:
        conn.close()
    
    return file_path, valid_count, invalid_count