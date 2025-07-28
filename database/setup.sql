-- NextCare Database Setup Script
-- This script performs initial database setup and configuration

-- Create the database (run this as postgres superuser)
-- Note: This should be run separately before running the main schema
-- CREATE DATABASE nextcare;
-- CREATE USER nextcare_user WITH PASSWORD 'your_secure_password';
-- GRANT ALL PRIVILEGES ON DATABASE nextcare TO nextcare_user;

-- Connect to the nextcare database and run the following:

-- Ensure we're using the correct database
\c nextcare

-- Set timezone for consistent timestamps
SET timezone = 'UTC';

-- Create a function to check if the database is properly initialized
CREATE OR REPLACE FUNCTION check_database_initialization()
RETURNS TABLE(
    table_name TEXT,
    row_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.table_name::TEXT,
        CASE 
            WHEN t.table_name IN ('users', 'parameters', 'machines') THEN
                (SELECT count(*) FROM information_schema.tables WHERE table_name = t.table_name)
            ELSE 0
        END as row_count
    FROM information_schema.tables t
    WHERE t.table_schema = 'public'
    AND t.table_type = 'BASE TABLE'
    ORDER BY t.table_name;
END;
$$ LANGUAGE plpgsql;

-- Create a function to generate database statistics
CREATE OR REPLACE FUNCTION get_database_stats()
RETURNS TABLE(
    stat_name TEXT,
    stat_value TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'Total Tables'::TEXT, count(*)::TEXT
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    
    UNION ALL
    
    SELECT 'Total Users'::TEXT, count(*)::TEXT
    FROM users
    
    UNION ALL
    
    SELECT 'Total Machines'::TEXT, count(*)::TEXT
    FROM machines
    
    UNION ALL
    
    SELECT 'Total Parameters'::TEXT, count(*)::TEXT
    FROM parameters
    
    UNION ALL
    
    SELECT 'Total Sensor Records'::TEXT, count(*)::TEXT
    FROM sensor_data
    
    UNION ALL
    
    SELECT 'Active Alerts'::TEXT, count(*)::TEXT
    FROM alerts
    WHERE status = 'active'
    
    UNION ALL
    
    SELECT 'Database Size'::TEXT, pg_size_pretty(pg_database_size(current_database()))
    
    UNION ALL
    
    SELECT 'Current Time'::TEXT, CURRENT_TIMESTAMP::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Create a maintenance function to optimize database performance
CREATE OR REPLACE FUNCTION perform_maintenance()
RETURNS TEXT AS $$
DECLARE
    result_text TEXT := '';
BEGIN
    -- Update table statistics
    ANALYZE;
    result_text := result_text || 'Table statistics updated. ';
    
    -- Reindex all tables for optimal performance
    REINDEX DATABASE nextcare;
    result_text := result_text || 'Database reindexed. ';
    
    -- Clean up old sensor data (older than configured retention period)
    PERFORM cleanup_old_sensor_data(
        (SELECT config_value::INTEGER FROM system_config WHERE config_key = 'max_sensor_data_age_days')
    );
    result_text := result_text || 'Old sensor data cleaned up. ';
    
    RETURN result_text || 'Maintenance completed successfully.';
END;
$$ LANGUAGE plpgsql;

-- Create function to reset demo data
CREATE OR REPLACE FUNCTION reset_demo_data()
RETURNS TEXT AS $$
BEGIN
    -- Disable triggers temporarily
    SET session_replication_role = replica;
    
    -- Clear existing data (in dependency order)
    DELETE FROM user_sessions;
    DELETE FROM maintenance_logs;
    DELETE FROM alerts;
    DELETE FROM sensor_data;
    DELETE FROM machine_parameters;
    DELETE FROM machines;
    DELETE FROM parameters;
    DELETE FROM users WHERE username != 'admin';
    
    -- Re-enable triggers
    SET session_replication_role = DEFAULT;
    
    RETURN 'Demo data reset completed. You can now run sample_data.sql to reload demo data.';
END;
$$ LANGUAGE plpgsql;

-- Create function to backup critical configuration
CREATE OR REPLACE FUNCTION backup_configuration()
RETURNS TABLE(
    backup_type TEXT,
    backup_data TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'users'::TEXT, 
           json_agg(row_to_json(u))::TEXT
    FROM (SELECT username, email, first_name, last_name, role, is_active 
          FROM users ORDER BY username) u
    
    UNION ALL
    
    SELECT 'system_config'::TEXT,
           json_agg(row_to_json(sc))::TEXT
    FROM (SELECT config_key, config_value, description, data_type 
          FROM system_config ORDER BY config_key) sc
    
    UNION ALL
    
    SELECT 'parameters'::TEXT,
           json_agg(row_to_json(p))::TEXT
    FROM (SELECT * FROM parameters ORDER BY parameter_id) p
    
    UNION ALL
    
    SELECT 'machines'::TEXT,
           json_agg(row_to_json(m))::TEXT
    FROM (SELECT machine_id, name, description, manufacturer, model, 
                 location, status 
          FROM machines ORDER BY machine_id) m;
END;
$$ LANGUAGE plpgsql;

-- Create initial admin user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin') THEN
        INSERT INTO users (username, email, password_hash, first_name, last_name, role)
        VALUES ('admin', 'admin@nextcare.com', 
                '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewstMhV/OQNHNm3.', -- admin123
                'System', 'Administrator', 'admin');
    END IF;
END
$$;

-- Grant necessary permissions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO nextcare_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nextcare_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nextcare_user;

-- Create helpful aliases/shortcuts
CREATE OR REPLACE VIEW system_status AS
SELECT 
    (SELECT count(*) FROM machines WHERE status = 'active') as active_machines,
    (SELECT count(*) FROM alerts WHERE status = 'active') as active_alerts,
    (SELECT count(*) FROM users WHERE is_active = true) as active_users,
    (SELECT count(*) FROM sensor_data WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '1 hour') as recent_readings,
    CURRENT_TIMESTAMP as checked_at;

-- Display initialization status
\echo 'NextCare Database Setup Complete!'
\echo ''
\echo 'Run the following to check your setup:'
\echo 'SELECT * FROM check_database_initialization();'
\echo 'SELECT * FROM get_database_stats();'
\echo 'SELECT * FROM system_status;'
\echo ''
\echo 'Useful maintenance commands:'
\echo 'SELECT perform_maintenance();'
\echo 'SELECT reset_demo_data();'
\echo ''