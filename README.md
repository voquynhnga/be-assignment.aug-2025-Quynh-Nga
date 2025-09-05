# 📌 Database Diagram

You can view the database schema here:
👉 [Database Diagram](https://drawsql.app/teams/dut-22/diagrams/be-assignment)

# Set up 
## 1. Create & Activate Virtual Environment

```bash
python -m venv venv
```

Windows (PowerShell):
```bash
.\venv\Scripts\Activate.ps1
```

Linux / macOS:
```bash
source venv/bin/activate
```


## 2. Install Dependencies (run once)

Upgrade pip and essential tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

Install project dependencies:

```bash
pip install --upgrade --force-reinstall --only-binary :all: -r requirements.txt
```

## 3. Start Docker

```bash
docker-compose up
```

## 4. Run Database Migrations & Seed Data

Run migrations:

```bash
alembic upgrade head
```

Seed initial data:

```bash
python seed.py
```

## 5. Start FastAPI Server (Development Mode)

With auto-reload enabled:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 6. Open API Documentation

Once the server is running, visit:

👉 [Localhost](http://localhost:8000/docs)