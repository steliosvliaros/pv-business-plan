-- Projects table: Main PV projects
CREATE TABLE IF NOT EXISTS projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL UNIQUE,
    location VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    project_type VARCHAR(50),  -- residential, commercial, utility-scale
    status VARCHAR(50) DEFAULT 'planning',  -- planning, approved, construction, operational
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System specifications
CREATE TABLE IF NOT EXISTS system_specs (
    spec_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id) ON DELETE CASCADE,
    system_capacity_kw DECIMAL(10, 2) NOT NULL,
    module_type VARCHAR(100),
    module_efficiency DECIMAL(5, 2),
    inverter_type VARCHAR(100),
    tilt_angle DECIMAL(5, 2),
    azimuth DECIMAL(5, 2),
    estimated_annual_production_kwh DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial assumptions
CREATE TABLE IF NOT EXISTS financial_assumptions (
    assumption_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id) ON DELETE CASCADE,
    total_capex DECIMAL(15, 2) NOT NULL,  -- Capital expenditure
    module_cost_per_watt DECIMAL(8, 4),
    inverter_cost DECIMAL(12, 2),
    bos_cost DECIMAL(12, 2),  -- Balance of system
    installation_cost DECIMAL(12, 2),
    opex_annual DECIMAL(12, 2),  -- Operating expenses
    electricity_rate_kwh DECIMAL(8, 4),
    escalation_rate DECIMAL(5, 4),  -- Annual rate increase
    discount_rate DECIMAL(5, 4),
    project_lifetime_years INTEGER DEFAULT 25,
    incentives_total DECIMAL(12, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial results (calculated)
CREATE TABLE IF NOT EXISTS financial_results (
    result_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id) ON DELETE CASCADE,
    npv DECIMAL(15, 2),  -- Net Present Value
    irr DECIMAL(8, 4),   -- Internal Rate of Return
    payback_period_years DECIMAL(5, 2),
    lcoe DECIMAL(8, 4),  -- Levelized Cost of Energy
    roi_percentage DECIMAL(8, 4),
    annual_savings_year1 DECIMAL(12, 2),
    total_lifetime_savings DECIMAL(15, 2),
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Energy production (monthly or annual records)
CREATE TABLE IF NOT EXISTS energy_production (
    production_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    energy_produced_kwh DECIMAL(12, 2) NOT NULL,
    irradiance_avg DECIMAL(8, 2),  -- kWh/m²/day
    performance_ratio DECIMAL(5, 4),  -- Actual vs expected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scenarios for sensitivity analysis
CREATE TABLE IF NOT EXISTS scenarios (
    scenario_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id) ON DELETE CASCADE,
    scenario_name VARCHAR(100) NOT NULL,
    parameter_changed VARCHAR(100),  -- e.g., 'electricity_rate', 'capex'
    parameter_value_original DECIMAL(15, 4),
    parameter_value_modified DECIMAL(15, 4),
    npv_result DECIMAL(15, 2),
    irr_result DECIMAL(8, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_location ON projects(location);
CREATE INDEX idx_energy_production_project_period ON energy_production(project_id, period_start);
CREATE INDEX idx_scenarios_project ON scenarios(project_id);

-- Sample data
INSERT INTO projects (project_name, location, latitude, longitude, project_type, status) VALUES
    ('Downtown Solar Array', 'Phoenix, AZ', 33.4484, -112.0740, 'commercial', 'planning'),
    ('Residential Rooftop', 'San Diego, CA', 32.7157, -117.1611, 'residential', 'approved');

INSERT INTO system_specs (project_id, system_capacity_kw, module_type, module_efficiency, tilt_angle, azimuth, estimated_annual_production_kwh) VALUES
    (1, 500.0, 'Monocrystalline 400W', 20.5, 25.0, 180.0, 875000),
    (2, 8.0, 'Monocrystalline 400W', 20.5, 25.0, 180.0, 14000);
