FROM python:3.11-slim

WORKDIR /app

COPY src /app/src
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src

CMD ["python", "src/run_job.py"]