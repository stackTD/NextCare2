-- NextCare Sample Data
-- This script inserts sample data for testing and demonstration purposes

-- Insert sample users with different roles
INSERT INTO users (username, email, password_hash, first_name, last_name, role) VALUES
-- Password: admin123 (hashed with bcrypt)
('admin', 'admin@nextcare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewstMhV/OQNHNm3.', 'System', 'Administrator', 'admin'),
-- Password: manager123
('manager', 'manager@nextcare.com', '$2b$12$k8Y1THKL1XYASB.V/xnYr.OjgCL7ZMZTrfRFpxr0sKMOGbsEhB5K6', 'Jane', 'Smith', 'manager'),
-- Password: engineer123
('engineer', 'engineer@nextcare.com', '$2b$12$9Xqv5P3A.H6CL8ZDQW9c1eY2gT8FhR4KlM3NvB7pS5UjX0Wq2Ee3I', 'John', 'Doe', 'engineer'),
-- Password: operator123
('operator1', 'operator1@nextcare.com', '$2b$12$7Hs2Q4R5E.A8BL9ZFVA2MoP1FjS6GeH3KiU7YhD9dR5ExB4NjQ8mW', 'Mike', 'Johnson', 'operator'),
('operator2', 'operator2@nextcare.com', '$2b$12$3Tp9W6X1C.M5DK2YGUF7NeL4GiV8JeI9KuB3ZhE5fT7HxC6OjR9pY', 'Sarah', 'Williams', 'operator');

-- Insert parameter definitions
INSERT INTO parameters (parameter_id, name, description, unit, parameter_type, default_min_value, default_max_value, default_alarm_threshold) VALUES
('temperature', 'Temperature', 'Operating temperature measurement', '°C', 'temperature', 10.0, 80.0, 75.0),
('pressure', 'Pressure', 'System pressure measurement', 'PSI', 'pressure', 0.0, 100.0, 90.0),
('vibration', 'Vibration', 'Machine vibration level', 'Hz', 'vibration', 0.0, 20.0, 15.0),
('speed', 'Rotational Speed', 'Motor or shaft rotational speed', 'RPM', 'speed', 0.0, 5000.0, 4500.0),
('power', 'Power Consumption', 'Electrical power consumption', 'kW', 'power', 0.0, 100.0, 85.0),
('humidity', 'Humidity', 'Environmental humidity level', '%', 'humidity', 20.0, 80.0, 75.0),
('flow', 'Flow Rate', 'Fluid flow rate measurement', 'L/min', 'flow', 0.0, 1000.0, 900.0);

-- Insert sample machines
INSERT INTO machines (machine_id, name, description, manufacturer, model, serial_number, location, installation_date, status, last_maintenance, next_maintenance) VALUES
('MACHINE_001', 'Production Line A', 'Main production conveyor system', 'IndustrialCorp', 'PL-2000X', 'SN001234567', 'Floor 1 - Section A', '2023-01-15', 'active', '2023-11-15', '2024-02-15'),
('MACHINE_002', 'Compressor Unit B', 'High-pressure air compressor', 'AirTech Systems', 'AC-500', 'SN002345678', 'Floor 1 - Utility Room', '2023-03-20', 'active', '2023-10-20', '2024-01-20'),
('MACHINE_003', 'CNC Mill C', 'Computer numerical control milling machine', 'PrecisionTools', 'CNC-1500', 'SN003456789', 'Floor 2 - Machining', '2022-11-10', 'active', '2023-11-10', '2024-02-10'),
('MACHINE_004', 'Packaging Unit D', 'Automated packaging system', 'PackMaster', 'PM-800', 'SN004567890', 'Floor 1 - Packaging', '2023-05-05', 'maintenance', '2023-12-01', '2024-03-01'),
('MACHINE_005', 'Cooling Tower E', 'Industrial cooling tower system', 'CoolSystems', 'CT-2500', 'SN005678901', 'Roof Level', '2022-08-30', 'active', '2023-08-30', '2024-02-28');

-- Associate parameters with machines and set specific thresholds
INSERT INTO machine_parameters (machine_id, parameter_id, min_value, max_value, alarm_threshold, warning_threshold, is_monitored) VALUES
-- Production Line A
('MACHINE_001', 'temperature', 15.0, 70.0, 65.0, 60.0, TRUE),
('MACHINE_001', 'vibration', 0.0, 10.0, 8.0, 6.0, TRUE),
('MACHINE_001', 'speed', 100.0, 2000.0, 1800.0, 1600.0, TRUE),
('MACHINE_001', 'power', 5.0, 50.0, 45.0, 40.0, TRUE),

-- Compressor Unit B
('MACHINE_002', 'temperature', 20.0, 85.0, 80.0, 75.0, TRUE),
('MACHINE_002', 'pressure', 20.0, 120.0, 110.0, 100.0, TRUE),
('MACHINE_002', 'vibration', 0.0, 15.0, 12.0, 10.0, TRUE),
('MACHINE_002', 'power', 10.0, 75.0, 70.0, 65.0, TRUE),

-- CNC Mill C
('MACHINE_003', 'temperature', 18.0, 60.0, 55.0, 50.0, TRUE),
('MACHINE_003', 'vibration', 0.0, 8.0, 6.0, 5.0, TRUE),
('MACHINE_003', 'speed', 500.0, 4000.0, 3800.0, 3500.0, TRUE),
('MACHINE_003', 'power', 15.0, 80.0, 75.0, 70.0, TRUE),

-- Packaging Unit D
('MACHINE_004', 'temperature', 10.0, 50.0, 45.0, 40.0, TRUE),
('MACHINE_004', 'speed', 50.0, 1500.0, 1400.0, 1200.0, TRUE),
('MACHINE_004', 'power', 3.0, 30.0, 28.0, 25.0, TRUE),
('MACHINE_004', 'humidity', 30.0, 70.0, 65.0, 60.0, TRUE),

-- Cooling Tower E
('MACHINE_005', 'temperature', 5.0, 40.0, 35.0, 30.0, TRUE),
('MACHINE_005', 'flow', 100.0, 800.0, 750.0, 700.0, TRUE),
('MACHINE_005', 'pressure', 5.0, 50.0, 45.0, 40.0, TRUE),
('MACHINE_005', 'power', 20.0, 100.0, 90.0, 85.0, TRUE),
('MACHINE_005', 'humidity', 40.0, 95.0, 90.0, 85.0, TRUE);

-- Generate sample sensor data for the last 7 days
-- This uses a function to create realistic-looking time series data
DO $$
DECLARE
    machine_rec RECORD;
    param_rec RECORD;
    time_point TIMESTAMP WITH TIME ZONE;
    base_value DECIMAL;
    random_value DECIMAL;
    i INTEGER;
BEGIN
    -- Loop through each machine-parameter combination
    FOR machine_rec IN 
        SELECT DISTINCT machine_id FROM machine_parameters WHERE is_monitored = TRUE
    LOOP
        FOR param_rec IN 
            SELECT parameter_id, min_value, max_value, alarm_threshold 
            FROM machine_parameters 
            WHERE machine_id = machine_rec.machine_id AND is_monitored = TRUE
        LOOP
            -- Generate data points every 15 minutes for the last 7 days
            FOR i IN 0..672 LOOP -- 7 days * 24 hours * 4 (15-min intervals)
                time_point := CURRENT_TIMESTAMP - INTERVAL '7 days' + (i * INTERVAL '15 minutes');
                
                -- Calculate base value (normal operating range)
                base_value := param_rec.min_value + (param_rec.max_value - param_rec.min_value) * 0.3 + 
                             (param_rec.max_value - param_rec.min_value) * 0.4 * random();
                
                -- Add some realistic variation and occasional spikes
                random_value := base_value + (random() - 0.5) * (param_rec.max_value - param_rec.min_value) * 0.1;
                
                -- Occasionally generate values near or above thresholds (5% chance)
                IF random() < 0.05 THEN
                    random_value := param_rec.alarm_threshold * (0.8 + random() * 0.4);
                END IF;
                
                -- Ensure value stays within reasonable bounds
                random_value := GREATEST(param_rec.min_value, LEAST(param_rec.max_value * 1.1, random_value));
                
                INSERT INTO sensor_data (machine_id, parameter_id, value, timestamp, source, quality_score)
                VALUES (
                    machine_rec.machine_id, 
                    param_rec.parameter_id, 
                    ROUND(random_value::NUMERIC, 2),
                    time_point,
                    'mock',
                    0.95 + random() * 0.05 -- Quality score between 0.95 and 1.0
                );
            END LOOP;
        END LOOP;
    END LOOP;
END
$$;

-- Insert sample maintenance logs
INSERT INTO maintenance_logs (machine_id, performed_by, maintenance_type, description, parts_replaced, cost, duration_hours, status, scheduled_date, completed_date, next_maintenance_date) VALUES
((SELECT user_id FROM users WHERE username = 'engineer'), 'MACHINE_001', 'preventive', 'Routine belt replacement and lubrication', 'Conveyor belt, bearings', 450.00, 3.5, 'completed', '2023-11-15', '2023-11-15', '2024-02-15'),
((SELECT user_id FROM users WHERE username = 'engineer'), 'MACHINE_002', 'corrective', 'Pressure valve replacement due to leak', 'Pressure relief valve, gaskets', 280.00, 2.0, 'completed', '2023-10-20', '2023-10-22', '2024-01-20'),
((SELECT user_id FROM users WHERE username = 'manager'), 'MACHINE_003', 'preventive', 'CNC calibration and spindle maintenance', 'Spindle bearings, coolant filter', 1200.00, 6.0, 'completed', '2023-11-10', '2023-11-10', '2024-02-10'),
((SELECT user_id FROM users WHERE username = 'engineer'), 'MACHINE_004', 'emergency', 'Motor failure - complete replacement', 'AC motor, coupling', 2500.00, 8.0, 'in_progress', '2023-12-01', NULL, '2024-03-01'),
((SELECT user_id FROM users WHERE username = 'engineer'), 'MACHINE_005', 'preventive', 'Cooling system cleaning and inspection', 'Water filters, chemical additives', 180.00, 4.0, 'completed', '2023-08-30', '2023-08-30', '2024-02-28');

-- Insert some sample alerts (some active, some resolved)
INSERT INTO alerts (machine_id, parameter_id, message, severity, status, trigger_value, threshold_value, acknowledged_by, acknowledged_at, resolved_at) VALUES
('MACHINE_002', 'pressure', 'Pressure exceeded warning threshold during startup', 'medium', 'resolved', 105.5, 100.0, (SELECT user_id FROM users WHERE username = 'operator1'), '2023-12-01 08:30:00', '2023-12-01 09:15:00'),
('MACHINE_003', 'temperature', 'Temperature spike detected during heavy operation', 'high', 'resolved', 58.2, 55.0, (SELECT user_id FROM users WHERE username = 'engineer'), '2023-11-28 14:20:00', '2023-11-28 15:45:00'),
('MACHINE_001', 'vibration', 'Unusual vibration pattern detected', 'medium', 'active', 6.8, 6.0, NULL, NULL, NULL),
('MACHINE_004', 'power', 'Power consumption anomaly before motor failure', 'critical', 'acknowledged', 32.1, 28.0, (SELECT user_id FROM users WHERE username = 'manager'), '2023-12-01 10:00:00', NULL),
('MACHINE_005', 'flow', 'Flow rate below optimal range', 'low', 'active', 680.5, 700.0, NULL, NULL, NULL);

-- Update system configuration for demo environment
UPDATE system_config SET config_value = 'true' WHERE config_key = 'mock_sensors_enabled';
UPDATE system_config SET config_value = '30' WHERE config_key = 'sensor_reading_interval';

-- Insert additional system configuration for demo
INSERT INTO system_config (config_key, config_value, description, data_type) VALUES
('demo_mode', 'true', 'Enable demo mode with sample data', 'boolean'),
('alert_retention_days', '90', 'Number of days to keep resolved alerts', 'integer'),
('maintenance_reminder_days', '7', 'Days before maintenance to send reminder', 'integer'),
('max_concurrent_alerts', '100', 'Maximum number of active alerts per machine', 'integer'),
('data_backup_enabled', 'true', 'Enable automatic data backup', 'boolean'),
('backup_retention_days', '30', 'Number of days to keep backup files', 'integer');

-- Create some user sessions for active users
INSERT INTO user_sessions (user_id, ip_address, user_agent, expires_at) VALUES
((SELECT user_id FROM users WHERE username = 'admin'), '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', CURRENT_TIMESTAMP + INTERVAL '24 hours'),
((SELECT user_id FROM users WHERE username = 'engineer'), '192.168.1.101', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', CURRENT_TIMESTAMP + INTERVAL '8 hours'),
((SELECT user_id FROM users WHERE username = 'operator1'), '192.168.1.102', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', CURRENT_TIMESTAMP + INTERVAL '4 hours');

-- Display summary of inserted data
\echo 'Sample data insertion completed!'
\echo ''
\echo 'Summary of inserted data:'
SELECT 
    'Users' as data_type, 
    count(*)::text as count 
FROM users
UNION ALL
SELECT 'Machines', count(*)::text FROM machines
UNION ALL
SELECT 'Parameters', count(*)::text FROM parameters
UNION ALL
SELECT 'Machine-Parameter Associations', count(*)::text FROM machine_parameters
UNION ALL
SELECT 'Sensor Data Points', count(*)::text FROM sensor_data
UNION ALL
SELECT 'Maintenance Logs', count(*)::text FROM maintenance_logs
UNION ALL
SELECT 'Alerts', count(*)::text FROM alerts
UNION ALL
SELECT 'Active Alerts', count(*)::text FROM alerts WHERE status = 'active'
UNION ALL
SELECT 'User Sessions', count(*)::text FROM user_sessions;

\echo ''
\echo 'Test login credentials:'
\echo 'Admin: admin / admin123'
\echo 'Manager: manager / manager123'
\echo 'Engineer: engineer / engineer123'
\echo 'Operator: operator1 / operator123'
\echo ''
\echo 'You can now start the NextCare application!'