-- Smart Bin AI SQL schema for sqlite

CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    bin_id TEXT NOT NULL,
    dish TEXT NOT NULL,
    weight_kg REAL NOT NULL,
    battery_voltage REAL,
    wifi_rssi INTEGER,
    meal TEXT
);

CREATE TABLE IF NOT EXISTS cooked (
    dish TEXT PRIMARY KEY,
    total_cooked_kg REAL NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON readings(timestamp);
