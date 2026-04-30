CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    password_hash TEXT,
    dob DATE,
    auth_provider VARCHAR(50),
    is_verified BOOLEAN,
    status VARCHAR(50),
    failed_attempts INT DEFAULT 0,
    lock_until TIMESTAMP WITH TIME ZONE
);

CREATE TABLE otp_codes (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    phone VARCHAR(20),
    otp VARCHAR(10),
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    token TEXT,
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE user_analytics (
    date DATE PRIMARY KEY,
    new_users INT DEFAULT 0,
    active_users INT DEFAULT 0,
    inactive_users INT DEFAULT 0
);

CREATE TABLE user_daily_activity (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    activity_date DATE
);