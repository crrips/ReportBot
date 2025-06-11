# 📊 Report Bot

This is a report bot that provides control for reports and records.

## 🚀 Launch

Firstly, create an .env file in the main directory and set the following values, replacing the placeholders with your actual values:
```
TOKEN = "your_token"

ADMIN_ID = 123456789

DB_NAME = "report_db"
DB_USER = "user"
DB_PASSWORD = "password"
DB_HOST = "db"
DB_PORT = 5432
DB_SCHEMA = "schema"
```

To start the bot using Docker and docker-compose, run:
```
docker-compose up --build
```

## 🛠️ Development

* Bot: Aiogram
* Database: PostgreSQL
* Containerization: Docker
* Excel: pandas and openpyxl
