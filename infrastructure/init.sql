-- Initialize TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create hypertables for time-series data
SELECT create_hypertable('cost_entries', 'date', if_not_exists => TRUE);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_cost_entries_resource_id ON cost_entries(resource_id);
CREATE INDEX IF NOT EXISTS idx_cost_entries_date_resource ON cost_entries(date, resource_id);
CREATE INDEX IF NOT EXISTS idx_cost_entries_service ON cost_entries(service_name);

CREATE INDEX IF NOT EXISTS idx_cloud_resources_provider ON cloud_resources(provider);
CREATE INDEX IF NOT EXISTS idx_cloud_resources_type ON cloud_resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_cloud_resources_region ON cloud_resources(region);

CREATE INDEX IF NOT EXISTS idx_optimization_recs_resource ON optimization_recommendations(resource_id);
CREATE INDEX IF NOT EXISTS idx_optimization_recs_status ON optimization_recommendations(status);
CREATE INDEX IF NOT EXISTS idx_optimization_recs_created ON optimization_recommendations(created_at);

-- Create materialized views for dashboard queries
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_cost_summary AS
SELECT 
    date,
    SUM(cost) as total_cost,
    COUNT(DISTINCT resource_id) as resource_count
FROM cost_entries
GROUP BY date
ORDER BY date;

CREATE MATERIALIZED VIEW IF NOT EXISTS monthly_cost_by_provider AS
SELECT 
    DATE_TRUNC('month', ce.date) as month,
    cr.provider,
    SUM(ce.cost) as total_cost,
    COUNT(DISTINCT ce.resource_id) as resource_count
FROM cost_entries ce
JOIN cloud_resources cr ON ce.resource_id = cr.id
GROUP BY DATE_TRUNC('month', ce.date), cr.provider
ORDER BY month, cr.provider;

-- Create function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_cost_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW daily_cost_summary;
    REFRESH MATERIALIZED VIEW monthly_cost_by_provider;
END;
$$ LANGUAGE plpgsql;

-- Insert some sample data (for development)
INSERT INTO users (id, email, full_name, is_active) 
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'demo@example.com', 'Demo User', true)
ON CONFLICT (email) DO NOTHING;
