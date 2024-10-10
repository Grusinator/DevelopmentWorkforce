FROM python:3.11-slim

WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt


COPY . /app

ENV PYTHONPATH="/app:${PYTHONPATH}"

CMD ["python", "src/run_job.py"]