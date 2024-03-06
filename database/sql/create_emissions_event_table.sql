CREATE TABLE EmissionEvent (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    station TEXT NOT NULL,
    measurement TEXT NOT NULL,
    percentage REAL NOT NULL,
    UNIQUE (date, station, measurement)
)