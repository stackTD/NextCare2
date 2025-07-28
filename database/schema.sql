-- NextCare Database Schema
-- This file creates the complete database structure for the NextCare application

-- Enable UUID extension for generating unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types for better data integrity
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'engineer', 'operator');
CREATE TYPE machine_status AS ENUM ('active', 'inactive', 'maintenance', 'error');
CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE alert_status AS ENUM ('active', 'acknowledged', 'resolved');
CREATE TYPE parameter_type AS ENUM ('temperature', 'pressure', 'vibration', 'speed', 'power', 'humidity', 'flow');

-- Users table for authentication and authorization
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role user_role NOT NULL DEFAULT 'operator',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Parameters table defining measurable properties
CREATE TABLE parameters (
    parameter_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    unit VARCHAR(20),
    parameter_type parameter_type NOT NULL,
    default_min_value DECIMAL(10,3),
    default_max_value DECIMAL(10,3),
    default_alarm_threshold DECIMAL(10,3),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Machines table for equipment registry
CREATE TABLE machines (
    machine_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    location VARCHAR(100),
    installation_date DATE,
    status machine_status NOT NULL DEFAULT 'active',
    last_maintenance DATE,
    next_maintenance DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Junction table for machine-parameter relationships with specific thresholds
CREATE TABLE machine_parameters (
    machine_id VARCHAR(50) REFERENCES machines(machine_id) ON DELETE CASCADE,
    parameter_id VARCHAR(50) REFERENCES parameters(parameter_id) ON DELETE CASCADE,
    min_value DECIMAL(10,3),
    max_value DECIMAL(10,3),
    alarm_threshold DECIMAL(10,3),
    warning_threshold DECIMAL(10,3),
    is_monitored BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (machine_id, parameter_id)
);

-- Sensor data table for time-series measurements
CREATE TABLE sensor_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    machine_id VARCHAR(50) NOT NULL REFERENCES machines(machine_id) ON DELETE CASCADE,
    parameter_id VARCHAR(50) NOT NULL REFERENCES parameters(parameter_id) ON DELETE CASCADE,
    value DECIMAL(10,3) NOT NULL,
    quality_score DECIMAL(3,2) DEFAULT 1.0, -- Data quality indicator (0.0 to 1.0)
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'sensor' -- 'sensor', 'manual', 'calculated', 'mock'
);

-- Create indexes for efficient time-series queries
CREATE INDEX idx_sensor_data_machine_time ON sensor_data(machine_id, timestamp DESC);
CREATE INDEX idx_sensor_data_parameter_time ON sensor_data(parameter_id, timestamp DESC);
CREATE INDEX idx_sensor_data_timestamp ON sensor_data(timestamp DESC);
CREATE INDEX idx_sensor_data_machine_parameter ON sensor_data(machine_id, parameter_id);

-- Alerts table for system notifications
CREATE TABLE alerts (
    alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    machine_id VARCHAR(50) NOT NULL REFERENCES machines(machine_id) ON DELETE CASCADE,
    parameter_id VARCHAR(50) REFERENCES parameters(parameter_id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    severity alert_severity NOT NULL,
    status alert_status NOT NULL DEFAULT 'active',
    trigger_value DECIMAL(10,3),
    threshold_value DECIMAL(10,3),
    acknowledged_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for alert queries
CREATE INDEX idx_alerts_machine ON alerts(machine_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);

-- Maintenance logs table for tracking maintenance activities
CREATE TABLE maintenance_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    machine_id VARCHAR(50) NOT NULL REFERENCES machines(machine_id) ON DELETE CASCADE,
    performed_by UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    maintenance_type VARCHAR(50) NOT NULL, -- 'preventive', 'corrective', 'emergency'
    description TEXT NOT NULL,
    parts_replaced TEXT,
    cost DECIMAL(10,2),
    duration_hours DECIMAL(5,2),
    status VARCHAR(20) NOT NULL DEFAULT 'completed', -- 'scheduled', 'in_progress', 'completed', 'cancelled'
    scheduled_date DATE,
    completed_date DATE,
    next_maintenance_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for maintenance logs
CREATE INDEX idx_maintenance_machine ON maintenance_logs(machine_id);
CREATE INDEX idx_maintenance_user ON maintenance_logs(performed_by);
CREATE INDEX idx_maintenance_date ON maintenance_logs(completed_date DESC);

-- User sessions table for web session management
CREATE TABLE user_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Create index for session lookups
CREATE INDEX idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active, expires_at);

-- System configuration table for application settings
CREATE TABLE system_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT NOT NULL,
    description TEXT,
    data_type VARCHAR(20) NOT NULL DEFAULT 'string', -- 'string', 'integer', 'float', 'boolean', 'json'
    is_sensitive BOOLEAN NOT NULL DEFAULT FALSE,
    updated_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply the trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_machines_updated_at BEFORE UPDATE ON machines
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maintenance_logs_updated_at BEFORE UPDATE ON maintenance_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for commonly used queries
-- Active machines with their latest sensor readings
CREATE VIEW active_machines_status AS
SELECT 
    m.machine_id,
    m.name,
    m.location,
    m.status,
    COUNT(DISTINCT mp.parameter_id) as monitored_parameters,
    MAX(sd.timestamp) as last_reading
FROM machines m
LEFT JOIN machine_parameters mp ON m.machine_id = mp.machine_id AND mp.is_monitored = TRUE
LEFT JOIN sensor_data sd ON m.machine_id = sd.machine_id
WHERE m.status = 'active'
GROUP BY m.machine_id, m.name, m.location, m.status;

-- Active alerts summary
CREATE VIEW active_alerts_summary AS
SELECT 
    a.machine_id,
    m.name as machine_name,
    COUNT(*) as alert_count,
    MAX(CASE WHEN a.severity = 'critical' THEN 1 ELSE 0 END) as has_critical,
    MAX(CASE WHEN a.severity = 'high' THEN 1 ELSE 0 END) as has_high,
    MIN(a.created_at) as oldest_alert,
    MAX(a.created_at) as newest_alert
FROM alerts a
JOIN machines m ON a.machine_id = m.machine_id
WHERE a.status = 'active'
GROUP BY a.machine_id, m.name;

-- Latest sensor readings for each machine-parameter combination
CREATE VIEW latest_sensor_readings AS
SELECT DISTINCT ON (sd.machine_id, sd.parameter_id)
    sd.machine_id,
    sd.parameter_id,
    sd.value,
    sd.timestamp,
    sd.quality_score,
    m.name as machine_name,
    p.name as parameter_name,
    p.unit,
    mp.alarm_threshold,
    mp.warning_threshold,
    CASE 
        WHEN sd.value > mp.alarm_threshold THEN 'alarm'
        WHEN sd.value > mp.warning_threshold THEN 'warning'
        ELSE 'normal'
    END as status
FROM sensor_data sd
JOIN machines m ON sd.machine_id = m.machine_id
JOIN parameters p ON sd.parameter_id = p.parameter_id
JOIN machine_parameters mp ON sd.machine_id = mp.machine_id AND sd.parameter_id = mp.parameter_id
WHERE mp.is_monitored = TRUE
ORDER BY sd.machine_id, sd.parameter_id, sd.timestamp DESC;

-- Create function for automatic alert generation
CREATE OR REPLACE FUNCTION check_and_create_alerts()
RETURNS TRIGGER AS $$
DECLARE
    machine_param RECORD;
    alert_message TEXT;
    alert_sev alert_severity;
BEGIN
    -- Get machine parameter configuration
    SELECT mp.alarm_threshold, mp.warning_threshold, p.name as param_name, p.unit
    INTO machine_param
    FROM machine_parameters mp
    JOIN parameters p ON mp.parameter_id = p.parameter_id
    WHERE mp.machine_id = NEW.machine_id 
    AND mp.parameter_id = NEW.parameter_id
    AND mp.is_monitored = TRUE;

    -- Check if we found the configuration
    IF machine_param IS NULL THEN
        RETURN NEW;
    END IF;

    -- Check for alarm condition
    IF NEW.value > machine_param.alarm_threshold THEN
        alert_sev := 'high';
        alert_message := format('Parameter %s exceeded alarm threshold: %.3f %s (threshold: %.3f %s)',
            machine_param.param_name, NEW.value, machine_param.unit, 
            machine_param.alarm_threshold, machine_param.unit);
        
        -- Insert alert if not already exists for this condition
        INSERT INTO alerts (machine_id, parameter_id, message, severity, trigger_value, threshold_value)
        SELECT NEW.machine_id, NEW.parameter_id, alert_message, alert_sev, NEW.value, machine_param.alarm_threshold
        WHERE NOT EXISTS (
            SELECT 1 FROM alerts 
            WHERE machine_id = NEW.machine_id 
            AND parameter_id = NEW.parameter_id 
            AND status = 'active'
            AND trigger_value > machine_param.alarm_threshold
        );
        
    ELSIF NEW.value > machine_param.warning_threshold THEN
        alert_sev := 'medium';
        alert_message := format('Parameter %s exceeded warning threshold: %.3f %s (threshold: %.3f %s)',
            machine_param.param_name, NEW.value, machine_param.unit, 
            machine_param.warning_threshold, machine_param.unit);
        
        -- Insert warning alert if not already exists
        INSERT INTO alerts (machine_id, parameter_id, message, severity, trigger_value, threshold_value)
        SELECT NEW.machine_id, NEW.parameter_id, alert_message, alert_sev, NEW.value, machine_param.warning_threshold
        WHERE NOT EXISTS (
            SELECT 1 FROM alerts 
            WHERE machine_id = NEW.machine_id 
            AND parameter_id = NEW.parameter_id 
            AND status = 'active'
            AND trigger_value > machine_param.warning_threshold
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic alert generation
CREATE TRIGGER sensor_data_alert_trigger
    AFTER INSERT ON sensor_data
    FOR EACH ROW
    EXECUTE FUNCTION check_and_create_alerts();

-- Create function to clean up old sensor data (for maintenance)
CREATE OR REPLACE FUNCTION cleanup_old_sensor_data(days_to_keep INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sensor_data 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions to nextcare_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nextcare_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nextcare_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO nextcare_user;

-- Insert default system configuration
INSERT INTO system_config (config_key, config_value, description, data_type) VALUES
('app_name', 'NextCare', 'Application name', 'string'),
('app_version', '1.0.0', 'Application version', 'string'),
('max_sensor_data_age_days', '365', 'Maximum age of sensor data to keep', 'integer'),
('alert_email_enabled', 'true', 'Enable email alerts', 'boolean'),
('mock_sensors_enabled', 'false', 'Enable mock sensor data generation', 'boolean'),
('sensor_reading_interval', '60', 'Sensor reading interval in seconds', 'integer'),
('dashboard_refresh_interval', '30', 'Dashboard auto-refresh interval in seconds', 'integer');

COMMIT;