# IoT Sensor Data Processor

A Python application that processes CSV sensor data and stores it in SQLite database.

## Project Structure

```
root/
├── src/
│   ├── db.py         # Database connection and initialization
│   ├── main.py       # Entry point
│   ├── worker.py     # CSV file processor
│   └── config.py     # Configuration
├── scripts/
│   ├── test.py       # SQL test cases
│   └── generate_data.py
├── schema.sql        # Database schema
├── requirements.txt  # Dependencies
└── target_directory/ # Input CSV files
```

## Database Schema

- **sensor_readings**: Stores sensor data (timestamp, sensor_name, value)
- **sensor_configs**: Sensor configuration with min/max values

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Data Generation

```bash
python scripts/generate_data.py [-o OUTPUT_DIR] [-n NUM_FILES] [-r ROWS_PER_FILE] [-s SENSOR_COUNT]
```

Options:
- `-o, --output-dir`: Output directory for generated CSV files (default: ./test-data)
- `-n, --num-files`: Number of CSV files to generate (default: 1000)
- `-r, --rows-per-file`: Number of rows per file (default: 5000)
- `-s, --sensor-count`: Number of unique sensors (default: 4)

### Data Processing

```bash
python src/main.py [-i INPUT_DIR] [-d DB_PATH]
```

Options:
- `-i, --input-dir`: Directory containing CSV files (default: target_directory)
- `-d, --db-path`: Path to SQLite database (default: data/iot.db)

Example:
```bash
python src/main.py -i test-data -d data/my_database.db
```

## Docker Deployment

### Build Image

```bash
docker build -t iot-processor .
```

### Run Container

```bash
docker run -it --rm iot-processor
```

### Quick Demo

```bash
# Build and run in one command
docker build -t iot-processor . && docker run -it --rm iot-processor
```

The container will:
1. Generate test CSV data
2. Process data and store in SQLite
3. Run tests

## Testing

```bash
python scripts/test.py
```

## Tests

**Success Cases:**
- Insert single sensor reading
- Insert multiple sensors
- Insert sensor configuration

**Failure Cases:**
- Duplicate timestamp+sensor_name
- NULL timestamp/sensor_name/value
- Invalid table
- Duplicate sensor config
- Wrong column count

