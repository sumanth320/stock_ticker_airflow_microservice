# 📈 Stock Ticker Airflow Microservice

A fully containerized data pipeline that orchestrates stock price fetching using **Apache Airflow**, uses **Redis** as a real-time message broker and cache, and visualizes data through a **Streamlit** dashboard.

## 🏗 System Architecture
The project consists of several interconnected microservices:
* **Airflow (Webserver & Scheduler):** Manages the DAG orchestration and task scheduling.
* **Postgres:** The metadata database for Airflow state and configuration.
* **Redis:** Acts as both the Celery-style broker and the real-time data store for the UI.
* **Ticker Worker:** A custom Python service that consumes tasks and fetches API data.
* **Stock UI:** A Streamlit frontend providing a real-time view of the data in Redis.

## 🚀 Getting Started

### 1. Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.
* A free API Key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key).

### 2. Configuration
Create a `.env` file in the root directory to store your secrets:
```
STOCK_API_KEY=your_api_key_here
AIRFLOW_UID=50000
```

### 3. Deployment

# Initialize the database, create admin user, and set up Airflow Pools
docker-compose up airflow-init

# Start the rest of the microservices in the background
docker-compose up -d


🛠 Usage & Monitoring
Airflow UI: http://localhost:8080 (Default Login: airflow / airflow)

Streamlit Dashboard: http://localhost:8501

Redis Check: docker-compose exec redis redis-cli KEYS "*"


# Stop all services
docker-compose stop

# Shut down and remove containers
docker-compose down

# Total Reset (Wipes Database and Volumes)
docker-compose down -v
