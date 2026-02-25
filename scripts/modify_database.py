import sqlite3

DB_PATH = "data/iot.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL") 
    return conn

# 查
def get_all_readings():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sensor_readings")
        return cursor.fetchall() 

def get_reading_by_sensor(sensor_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sensor_readings WHERE sensor_name = ?", (sensor_name,))
        return cursor.fetchone() 

def get_count():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensor_readings")
        return cursor.fetchone()[0]
    
def show_top_10():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sensor_readings LIMIT 10")
        rows = cursor.fetchall()
        
        print(f"{'ID':<5} {'Timestamp':<25} {'Sensor':<15} {'Value':<10}")
        print("-" * 60)
        
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<25} {row[2]:<15} {row[3]:<10.2f}")

if __name__ == "__main__":
    print("Total readings in database:", get_count())
    show_top_10()