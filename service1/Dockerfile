# Dockerfile for Service1
FROM python:3.9-slim

WORKDIR /app

# Install necessary system utilities: procps for ps, coreutils for uptime
RUN apt-get update && apt-get install -y procps coreutils && rm -rf /var/lib/apt/lists/*
RUN pip install requests

COPY service1.py /app/

CMD ["python", "service1.py"]