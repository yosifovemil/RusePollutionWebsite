CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    email TEXT,
    name TEXT,
    photo TEXT,
    registered INTEGER DEFAULT FALSE NOT NULL,
    UNIQUE (email)
);
