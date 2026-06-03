FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir "fastapi>=0.115.0" "pydantic-settings>=2.6.0" "uvicorn[standard]>=0.32.0"

COPY src ./src

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

