import sys
import os
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

TEST_DB_PATH = "data/test_iot.db"

def get_test_connection():
    conn = sqlite3.connect(TEST_DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn

def setup_test_db():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    conn = get_test_connection()
    with open('schema.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def test_insert_success():
    """Test inserting valid data"""
    setup_test_db()
    conn = get_test_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO sensor_readings (timestamp, sensor_name, value) VALUES (?, ?, ?)",
        ("2024-01-01 10:00:00", "temperature", 25.5)
    )
    conn.commit()
    
    cursor.execute("SELECT * FROM sensor_readings WHERE sensor_name = ?", ("temperature",))
    result = cursor.fetchone()
    
    assert result is not None, "Insert should succeed"
    assert result[2] == "temperature"
    assert result[3] == 25.5
    print("[PASS] test_insert_success")
    
    conn.close()

def test_insert_multiple_sensors():
    """Test inserting multiple sensor data"""
    setup_test_db()
    conn = get_test_connection()
    cursor = conn.cursor()
    
    sensors = [
        ("2024-01-01 10:00:00", "temperature", 25.5),
        ("2024-01-01 10:00:01", "humidity", 60.0),
        ("2024-01-01 10:00:02", "pressure", 1013.25),
    ]
    
    cursor.executemany(
        "INSERT INTO sensor_readings (timestamp, sensor_name, value) VALUES (?, ?, ?)",
        sensors
    )
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM sensor_readings")
    count = cursor.fetchone()[0]
    
    assert count == 3, f"Expected 3 records, got {count}"
    print("[PASS] test_insert_multiple_sensors")
    
    conn.close()

def test_insert_sensor_config():
    """Test inserting sensor config"""
    setup_test_db()
    conn = get_test_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO sensor_configs (sensor_name, min_value, max_value, unit, description) VALUES (?, ?, ?, ?, ?)",
        ("light", 0.0, 1000.0, "lux", "Light sensor")
    )
    conn.commit()
    
    cursor.execute("SELECT * FROM sensor_configs WHERE sensor_name = ?", ("light",))
    result = cursor.fetchone()
    
    assert result is not None, "Insert config should succeed"
    assert result[0] == "light"
    print("[PASS] test_insert_sensor_config")
    
    conn.close()

def test_insert_duplicate_timestamp_sensor():
    """Test inserting duplicate timestamp+sensor_name (should fail)"""
    setup_test_db()
    conn = get_test_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO sensor_readings (timestamp, sensor_name, value) VALUES (?, ?, ?)",
        ("2024-01-01 10:00:00", "temperature", 25.5)
    )
    conn.commit()
    
    try:
        cursor.execute(
            "INSERT INTO sensor_readings (timestamp, sensor_name, value) VALUES (?, ?, ?)",
            ("2024-01-01 10:00:00", "temperature", 30.0)
        )
        conn.commit()
        assert False, "Duplicate insert should fail"
    except sqlite3.IntegrityError as e:
        print(f"[PASS] test_insert_duplicate_timestamp_sensor: {e}")
    
    conn.close()

def test_insert_null_timestamp():
    """Test inserting NULL timestamp (should fail)"""
    setup_test_db()
    conn = get_test_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO sensor_readings (timestamp, sensor_name, value) VALUES (?, ?, ?)",
            (None, "temperature", 25.5)
        )
        conn.commit()
        assert False, "NULL timestamp should fail"
    except sqlite3.IntegrityError as e:
        print(f"[PASS] test_insert_null_timestamp: {e}")
    
    conn.close()

def test_insert_null_sensor_name():
    """Test inserting NULL sensor_name (should fail)"""
    setup_test_db()
    conn = get_test_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO sensor_readings (timestamp, sensor_name, value) VALUES (?, ?, ?)",
            ("2024-01-01 10:00:00", None, 25.5)
        )
        conn.commit()
        assert False, "NULL sensor_name should fail"
    except sqlite3.IntegrityError as e:
        print(f"[PASS] test_insert_null_sensor_name: {e}")
    
    conn.close()

def test_insert_null_value():
    """Test inserting NULL value (should fail)"""
    setup_test_db()
    conn = get_test_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO sensor_readings (timestamp, sensor_name, value) VALUES (?, ?, ?)",
            ("2024-01-01 10:00:00", "temperature", None)
        )
        conn.commit()
        assert False, "NULL value should fail"
    except sqlite3.IntegrityError as e:
        print(f"[PASS] test_insert_null_value: {e}")
    
    conn.close()

def test_insert_invalid_table():
    """Test inserting to non-existent table (should fail)"""
    setup_test_db()
    conn = get_test_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO nonexistent_table (timestamp, sensor_name, value) VALUES (?, ?, ?)",
            ("2024-01-01 10:00:00", "temperature", 25.5)
        )
        conn.commit()
        assert False, "Invalid table should fail"
    except sqlite3.OperationalError as e:
        print(f"[PASS] test_insert_invalid_table: {e}")
    
    conn.close()

def test_insert_duplicate_sensor_config():
    """Test inserting duplicate sensor_name config (should fail)"""
    setup_test_db()
    conn = get_test_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO sensor_configs (sensor_name, min_value, max_value, unit, description) VALUES (?, ?, ?, ?, ?)",
        ("new_sensor", 0.0, 100.0, "unit", "Test sensor")
    )
    conn.commit()
    
    try:
        cursor.execute(
            "INSERT INTO sensor_configs (sensor_name, min_value, max_value, unit, description) VALUES (?, ?, ?, ?, ?)",
            ("new_sensor", 0.0, 200.0, "unit", "Another sensor")
        )
        conn.commit()
        assert False, "Duplicate sensor_name should fail"
    except sqlite3.IntegrityError as e:
        print(f"[PASS] test_insert_duplicate_sensor_config: {e}")
    
    conn.close()

def test_insert_wrong_column_count():
    """Test inserting with wrong number of values (should fail)"""
    setup_test_db()
    conn = get_test_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO sensor_readings (timestamp, sensor_name, value) VALUES (?, ?)",
            ("2024-01-01 10:00:00", "temperature")
        )
        conn.commit()
        assert False, "Wrong column count should fail"
    except sqlite3.OperationalError as e:
        print(f"[PASS] test_insert_wrong_column_count: {e}")
    
    conn.close()

def run_all_tests():
    print("=" * 50)
    print("SQL Tests Started")
    print("=" * 50)
    
    print("\n--- Success Cases ---")
    test_insert_success()
    test_insert_multiple_sensors()
    test_insert_sensor_config()
    
    print("\n--- Failure Cases ---")
    test_insert_duplicate_timestamp_sensor()
    test_insert_null_timestamp()
    test_insert_null_sensor_name()
    test_insert_null_value()
    test_insert_invalid_table()
    test_insert_duplicate_sensor_config()
    test_insert_wrong_column_count()
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    run_all_tests()
