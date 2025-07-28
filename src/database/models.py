"""
Database schema and table creation scripts
"""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'manager', 'engineer')),
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
"""

CREATE_MACHINES_TABLE = """
CREATE TABLE IF NOT EXISTS machines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    location VARCHAR(100),
    machine_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE
);
"""

CREATE_PARAMETERS_TABLE = """
CREATE TABLE IF NOT EXISTS parameters (
    id SERIAL PRIMARY KEY,
    machine_id INTEGER REFERENCES machines(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    register_address VARCHAR(10) NOT NULL,
    unit VARCHAR(20),
    min_value FLOAT,
    max_value FLOAT,
    alarm_low FLOAT,
    alarm_high FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
"""

CREATE_SENSOR_DATA_TABLE = """
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    parameter_id INTEGER REFERENCES parameters(id) ON DELETE CASCADE,
    value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quality BOOLEAN DEFAULT TRUE
);
"""

CREATE_USER_MACHINE_ACCESS_TABLE = """
CREATE TABLE IF NOT EXISTS user_machine_access (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    machine_id INTEGER REFERENCES machines(id) ON DELETE CASCADE,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, machine_id)
);
"""

CREATE_ALARMS_TABLE = """
CREATE TABLE IF NOT EXISTS alarms (
    id SERIAL PRIMARY KEY,
    parameter_id INTEGER REFERENCES parameters(id) ON DELETE CASCADE,
    alarm_type VARCHAR(20) NOT NULL CHECK (alarm_type IN ('high', 'low', 'communication')),
    value FLOAT,
    message TEXT,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by INTEGER REFERENCES users(id),
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Indexes for performance
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_sensor_data_parameter_id ON sensor_data(parameter_id);",
    "CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_parameters_machine_id ON parameters(machine_id);",
    "CREATE INDEX IF NOT EXISTS idx_user_machine_access_user_id ON user_machine_access(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_alarms_parameter_id ON alarms(parameter_id);",
    "CREATE INDEX IF NOT EXISTS idx_alarms_acknowledged ON alarms(acknowledged);",
]

# Initial data for testing
INSERT_DEFAULT_USERS = """
INSERT INTO users (username, password_hash, role, full_name, email) VALUES
    ('admin', '$2b$12$LzjXF7M9wuYcRST8.mTPi.NhH8.bP7/FhhgQdJ2FjsiAAQW7HcpJ2', 'admin', 'System Administrator', 'admin@nextcare.com'),
    ('manager1', '$2b$12$LzjXF7M9wuYcRST8.mTPi.NhH8.bP7/FhhgQdJ2FjsiAAQW7HcpJ2', 'manager', 'Plant Manager', 'manager@nextcare.com'),
    ('engineer1', '$2b$12$LzjXF7M9wuYcRST8.mTPi.NhH8.bP7/FhhgQdJ2FjsiAAQW7HcpJ2', 'engineer', 'Maintenance Engineer', 'engineer@nextcare.com')
ON CONFLICT (username) DO NOTHING;
"""

INSERT_SAMPLE_MACHINES = """
INSERT INTO machines (name, description, location, machine_type, created_by) VALUES
    ('Pump #1', 'Main water circulation pump', 'Building A - Floor 1', 'Centrifugal Pump', 1),
    ('Motor #1', 'Production line drive motor', 'Building B - Floor 2', 'AC Motor', 1),
    ('Compressor #1', 'Air compression unit', 'Building A - Basement', 'Screw Compressor', 1)
ON CONFLICT DO NOTHING;
"""

INSERT_SAMPLE_PARAMETERS = """
INSERT INTO parameters (machine_id, name, register_address, unit, min_value, max_value, alarm_low, alarm_high) VALUES
    (1, 'Temperature', 'D20', '°C', 0, 100, 5, 85),
    (1, 'Pressure', 'D21', 'bar', 0, 10, 0.5, 8.5),
    (1, 'Vibration', 'D22', 'mm/s', 0, 50, 0, 25),
    (2, 'Temperature', 'D20', '°C', 0, 120, 10, 100),
    (2, 'Current', 'D24', 'A', 0, 100, 5, 85),
    (2, 'Speed', 'D23', 'RPM', 0, 3000, 100, 2800),
    (3, 'Temperature', 'D20', '°C', 0, 80, 5, 70),
    (3, 'Pressure', 'D21', 'bar', 0, 15, 1, 12),
    (3, 'Vibration', 'D22', 'mm/s', 0, 30, 0, 20)
ON CONFLICT DO NOTHING;
"""

ALL_TABLES = [
    CREATE_USERS_TABLE,
    CREATE_MACHINES_TABLE,
    CREATE_PARAMETERS_TABLE,
    CREATE_SENSOR_DATA_TABLE,
    CREATE_USER_MACHINE_ACCESS_TABLE,
    CREATE_ALARMS_TABLE
]

ALL_INDEXES = CREATE_INDEXES

INITIAL_DATA = [
    INSERT_DEFAULT_USERS,
    # INSERT_SAMPLE_MACHINES,
    # INSERT_SAMPLE_PARAMETERS
]