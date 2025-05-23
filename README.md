[![CI Pipeline Status](https://github.com/YehiaSobeh/Weather-Monitoring-App/actions/workflows/main.yaml/badge.svg)](https://github.com/YehiaSobeh/Weather-Monitoring-App/actions/workflows/main.yaml)

# Weather Monitoring App

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-D83C3A?style=flat&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814D?style=flat&logo=celery&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-1C1C1C?style=flat&logo=poetry&logoColor=white)
![pytest](https://img.shields.io/badge/Pytest-302C2F?style=flat&logo=pytest&logoColor=white)

This repository contains the weather monitoring and alert system using Python. This system will
fetch weather data from a public API, process it asynchronously, and provide various endpoints
for weather information and alerts.

## Table of Contents

1. [Setup Instructions](#setup-instructions)
    - [Requirements](#requirements)
    - [Poetry](#docker)

2. [API Documentation](#api-documentation)
    - [Alert Router](#alert-router)
    - [Weather Router](#weather-router)
3. [Architecture Overview](#architecture-overview)
    - [Database](#database)
    - [Redis](#redis)
    - [Rate Limiter](#rate-limiter)
    - [Celery](#celery)
    - [Celery Tasks](#celery-tasks)

4. [Design Decisions and Trade-offs](#design-decisions-and-trade-offs)

5. [Tests](#tests)
## Setup Instructions

### Requirements

- Python 3.9 or higher
- poetry

## Poetry (Recommended)

- Clone this branch to your local machine

```bash
git clone git@github.com:YehiaSobeh/Weather-Monitoring-App.git
```

- make sure you are in the `Weather Alert System` directory

- Create a `.env` file in the backend/app directory to store environment variables following the `.env.example`

```bash
make all
```

The application will be available at [localhost:8000](http://localhost:8000/)


## API Documentation

### Alert Service

#### 1. Subscribe to Alerts

- **Endpoint**: `POST /alert/subscribe`
- **Summary**: Subscribe to Alerts
- **Description**: Allows a user to subscribe to alerts by providing subscription details.
- **Request Body**: `SubscriptionRequest`
- **Response**: `SubscriptionRequest`
- **Dependencies**:
  - `db`: Database session (dependency)
  
| Parameter      | Type               | Description                           |
|----------------|--------------------|---------------------------------------|
| `subscription` | `SubscriptionRequest` | Subscription details (request body)  |
| `db`           | `Session`          | Database session (dependency)        |


### Weather Service

#### 1. Get Current Weather

- **Endpoint**: `GET /weather/current/{city}`
- **Summary**: Get Current Weather
- **Description**: Fetches the current weather for a given city.
- **Request Parameters**: `city` (Path parameter)
- **Response**: `dict[str, Any]`
- **Dependencies**:
  - `db`: Database session (dependency)
  - `r`: Redis cache session (dependency)
  - `rate_limit`: Rate limiter (dependency)

| Parameter      | Type       | Description                           |
|----------------|------------|---------------------------------------|
| `city`         | `str`      | The name of the city                 |
| `db`           | `Session`  | Database session (dependency)        |
| `r`            | `Redis`    | Redis cache session (dependency)     |
| `rate_limit`   | `Limiter`  | Rate limiter (dependency)            |



## Architecture Overview

- For an overview of the system architecture, please refer to [System Architecture Diagram](https://www.mermaidchart.com/raw/f66a25ac-01d5-4795-9f8d-c655e8b78998?theme=light&version=v0.1&format=svg).

### Database

- The system uses a Relational Database (SQLite) to store user data, alerts, weather data, etc.

- created indexes on key columns in the database to optimize query performance, especially for frequently accessed data 

- For the full database schema, refer to [Database Schema](https://dbdiagram.io/d/67b355f0263d6cf9a072e3dc).

- use `Alembic` For  database migrations

### Redis

- `Caches`: Redis is used to cache weather data to reduce load on the backend and speed up responses for frequently requested weather data.

- `Message Broker`: Redis is used as a message broker for Celery, handling the asynchronous execution of tasks like `sending emails` and `updating weather data`.

- `Rate Limiter`: Redis is used to implement rate limiting

### Rate Limiter

- The rate limiter tracks the number of requests to an endpoint using Redis. weather endpoint has a rate limit defined by a count and window time (60 requests per minute)

- If the request count exceeds the allowed limit, the system responds with an HTTP 429 status code and a message to inform the user to try again later.

### Celery

- task Queue: Celery is used for handling background tasks asynchronously. It executes tasks such as s`ending subscription emails`, `weather alert emails`, and `updating weather data for cities`.

- Scheduled Tasks: Some tasks are scheduled using Celery Beat to run periodically (updating weather data for all subscribed cities every 15 minutes).

### Celery Tasks

- `send_subscription_email`

  - Sends a welcome email to a user upon successful subscription to weather alerts.

- `send_weather_alert_email`

  - Sends a weather alert email to a user if their subscribed conditions (temperature threshold) are met.

- `update_weather_data`

  - Updates the weather data for a specific city and checks if any alert conditions are triggered based on the new data.

- `update_all_weather_data`

  - Updates weather data for all subscribed cities. This task queries the list of cities from the database and triggers the update_weather_data task for each city.

- `check_and_trigger_alerts`

  - Checks all active subscriptions and compares the latest weather data against the user's alert conditions. If conditions are met, an alert is created and a notification email is sent.

### Design Decisions and Trade-offs

- I used redis for multiple purposes: rate limiting, caching weather data, and as a message broker for Celery.

  - `Trade-off`:
        - `cons`: If Redis fails, it could impact the rate limiting, caching, and background processing systems
        - `pros`:  provides low-latency access to data, making it ideal for caching and real-time operations.

- Rate Limiting Implementation Decision:
  - i choosed  `Redis` over `SlowAPI` because

    - `Trade-off`:
      - `cons`: Redis is ideal for counting requests quickly and supports features like automatic expiration
      - `pros`:
        - added complexity of managing Redis configurations
          - I was unsure about `SlowAPI` its scalability and whether it could handle high traffic efficiently in the long term.

- Background Task Execution:
  - i choosed celery over FastAPI’s built-in background task because the  application has multiple background tasks (such as sending emails, fetching weather updates, and triggering alerts), I preferred `Celery`. It allows task execution in a separate worker process, supports distributed task execution, and provides features like retries, `scheduling`, and monitoring.

    - pros:
      - uns tasks in separate worker processes, allowing horizontal scaling across multiple servers.
      - Celery supports periodic tasks via Celery Beat, making it ideal for scheduled jobs like cron jobs.

    - cons:
      - increases complexity.
      - consume more memory and CPU.


## Tests

* **Backend**: Validates subscription schema, CRUD workflows, rate-limiter logic, API client resilience, and Celery task helpers.

  ```bash
  poetry run python3 -m backend/app/tests/
  ```

* **Frontend**: Tests dashboard rendering, subscription form flow, alert list UI, and error/loading states.

  ```bash
  poetry run python3 -m frontend/tests/
  ```

* **Load Testing**: Simulates concurrent `/weather/current/{city}` requests to benchmark rate limiting, caching, and task throughput via Locust.

  ```bash
  poetry run locust --host http://localhost:8000
  ```

* **Coverage**: Runs all backend tests with a coverage threshold.

  ```bash
  poetry run python3 -m coverage run -m pytest app/tests/ \
  && poetry run python3 -m coverage report --fail-under=60 -m

  ```