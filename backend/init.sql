CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user'
);

INSERT INTO users (name, role) VALUES
    ('Rayane', 'admin'),
    ('Alice', 'user'),
    ('Bob', 'user'),
    ('Charlie', 'user');
