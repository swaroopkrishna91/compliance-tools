FROM python:3.9
WORKDIR /app
COPY scout_exporter.py .
RUN pip install flask prometheus_client boto3
CMD ["python", "scout_exporter.py"]
