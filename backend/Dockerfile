FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir hatch

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY . .

CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"
