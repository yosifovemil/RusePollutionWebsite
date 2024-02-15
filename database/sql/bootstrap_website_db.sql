CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    email TEXT,
    name TEXT,
    photo TEXT,
    registered INTEGER DEFAULT FALSE NOT NULL,
    admin INTEGER DEFAULT FALSE NOT NULL,
    UNIQUE (email)
);

CREATE TABLE TempUsers (
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT,
    UNIQUE (username)
)