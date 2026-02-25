-- -- schema.sql
-- CREATE TABLE IF NOT EXISTS sensor_readings (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     timestamp TEXT NOT NULL,
--     sensor_name TEXT NOT NULL,
--     value REAL NOT NULL,
--     UNIQUE(timestamp, sensor_name) ON CONFLICT IGNORE
-- );

CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    sensor_name TEXT NOT NULL,
    value REAL NOT NULL,
    UNIQUE(timestamp, sensor_name)
);

CREATE TABLE IF NOT EXISTS sensor_configs (
    sensor_name TEXT PRIMARY KEY,
    min_value REAL NOT NULL,
    max_value REAL NOT NULL,
    unit TEXT,
    description TEXT
);

INSERT OR IGNORE INTO sensor_configs (sensor_name, min_value, max_value, unit, description) VALUES
    ('temperature-sensor', -50.0, 100.0, '°C', 'Temperature sensor'),
    ('humidity-sensor', 0.0, 100.0, '%', 'Humidity sensor'),
    ('pressure-sensor', 800.0, 1200.0, 'hPa', 'Pressure sensor'),
    ('light-sensor', 0.0, 5000.0, 'ppm', 'CO2 sensor');


CREATE INDEX IF NOT EXISTS idx_readings_sensor ON sensor_readings(sensor_name);