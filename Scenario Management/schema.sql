-- Create the scenarios table
CREATE TABLE scenarios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create the attack_vectors table
CREATE TABLE attack_vectors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    scenario_id INT NOT NULL,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
);

-- Create the scenario_schedules table
CREATE TABLE scenario_schedules (
    id SERIAL PRIMARY KEY,
    scenario_id INT NOT NULL,
    schedule_time TIMESTAMP NOT NULL,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
);

-- Create the scenario_runs table to track each run of a scenario
CREATE TABLE scenario_runs (
    id SERIAL PRIMARY KEY,
    scenario_id INT NOT NULL,
    run_time TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
);
