FROM python:3.12-slim

WORKDIR /app

COPY ../sudokulib /app/sudokulib
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY tests/ ./tests/
COPY pytest.ini .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
