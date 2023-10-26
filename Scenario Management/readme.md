# Scenario Management System

Scenario Management System (SMS) is a robust platform designed to create, manage, schedule, and execute cybersecurity training scenarios. It's built using a microservices architecture, with each component dockerized for easy deployment, scaling, and management.

## Architecture

The system consists of three main microservices:

1. **Scenario Builder**:
    - Responsible for creating and managing scenarios.
    - Provides a RESTful API for creating, retrieving, updating, and deleting scenarios.

2. **Scenario Library**:
    - Stores a library of pre-configured scenarios and attack vectors.
    - Provides a RESTful API for listing and retrieving scenarios and attack vectors.

3. **Scenario Scheduler**:
    - Schedules scenarios to run at specified times.
    - Tracks the execution status of each scenario.
    - Provides a RESTful API for scheduling, rescheduling, and cancelling scenario executions.

## Database

A relational database is used to store data for all microservices. It contains tables for scenarios, attack vectors, scenario schedules, and scenario runs.

## Dependencies

- Python 3.8+
- Flask
- SQLAlchemy
- Celery
- Redis
- Gunicorn

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/scenario-management-system.git
cd scenario-management-system
