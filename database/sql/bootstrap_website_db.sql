CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT,
    name TEXT,
    photo TEXT,
    active INTEGER DEFAULT TRUE NOT NULL,
    admin INTEGER DEFAULT FALSE NOT NULL,
    accountType TEXT,
    UNIQUE (username)
);