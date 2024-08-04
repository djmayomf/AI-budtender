-- User table with medical card details
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    password_hash TEXT NOT NULL,
    id_image BLOB,
    medical_card_number TEXT,
    medical_card_expiration DATE,
    address TEXT
);
