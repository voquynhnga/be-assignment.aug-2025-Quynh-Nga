Database Diagram

https://drawsql.app/teams/dut-22/diagrams/be-assignment



B1: Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows

B2: Install dependencies
# Run once
python -m pip install --upgrade pip setuptools wheel

# Run once
pip install --upgrade --force-reinstall --only-binary :all: -r requirements.txt


Start the FastAPI server (for development with auto-reload):

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


B3: Start Docker
docker-compose up

B4: Run database migrations 
# Run once
alembic upgrade head

B5: Open Swagger UI
http://localhost:8000/docs