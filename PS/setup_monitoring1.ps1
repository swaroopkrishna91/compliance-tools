# Define the folder and file paths
$FOLDER = "scoutsuite_monitoring"
$EXPORTER_SCRIPT = "$FOLDER\json_exporter.py"
$DOCKERFILE = "$FOLDER\Dockerfile"
$PROMETHEUS_CONFIG = "$FOLDER\prometheus.yml"
$DOCKER_COMPOSE_FILE = "$FOLDER\docker-compose.yml"
$SCOUTSUITE_JSON = "$FOLDER\data.json"

Write-Host "🚀 Setting up Scout Suite Monitoring System..."

# Step 1: Create a directory to store all files
if (!(Test-Path -Path $FOLDER)) {
    New-Item -ItemType Directory -Path $FOLDER | Out-Null
}
Write-Host "✅ Folder '$FOLDER' created."

# Step 2: Ensure the JSON file exists before proceeding
if (!(Test-Path "data.json")) {
    Write-Host "❌ Error: The file 'data.json' was not found in the current directory. Please provide a valid Scout Suite JSON file."
    exit 1
}

# Step 3: Copy the JSON file into the monitoring folder
Copy-Item -Path "data.json" -Destination $SCOUTSUITE_JSON -Force
Write-Host "✅ JSON file copied to '$SCOUTSUITE_JSON'."

# Step 4: Create JSON Exporter Python script
@"
from flask import Flask, Response
import json
import os

app = Flask(__name__)

# Define the JSON file path inside the Docker container
JSON_PATH = "/data/data.json"

# Ensure JSON file exists before starting
if not os.path.exists(JSON_PATH):
    print(f"❌ Error: JSON file '{JSON_PATH}' not found. Make sure it's mounted correctly.")
    exit(1)

def parse_scoutsuite_json():
    try:
        with open(JSON_PATH, "r") as file:
            data = json.load(file)

        # Extract service summary from last run
        services_summary = data.get("last_run", {}).get("summary", {})

        metrics = []
        for service, details in services_summary.items():
            checked_items = details.get("checked_items", 0)
            flagged_items = details.get("flagged_items", 0)
            max_level = details.get("max_level", "warning")

            metrics.append(f'scoutsuite_checked_items{{service="{service}"}} {checked_items}')
            metrics.append(f'scoutsuite_flagged_items{{service="{service}"}} {flagged_items}')
            metrics.append(f'scoutsuite_risk_level{{service="{service}",level="{max_level}"}} 1')

        return "\n".join(metrics) if metrics else "scoutsuite_checked_items{} 0"
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parsing Error: {e}")
        return "scoutsuite_checked_items{} 0"

@app.route("/metrics")
def metrics():
    metric_data = parse_scoutsuite_json()
    return Response(metric_data, mimetype="text/plain")

if __name__ == "__main__":
    print("✅ JSON Exporter is running on http://0.0.0.0:8000/metrics")
    app.run(host="0.0.0.0", port=8000, debug=True)
"@ | Out-File -Encoding utf8 $EXPORTER_SCRIPT

Write-Host "✅ JSON Exporter script created."

# Step 5: Create Dockerfile for JSON Exporter
@"
FROM python:3.9
WORKDIR /app
COPY json_exporter.py /app
COPY data.json /data/data.json
RUN pip install flask
CMD ["python", "json_exporter.py"]
"@ | Out-File -Encoding utf8 $DOCKERFILE

Write-Host "✅ Dockerfile created."

# Step 6: Create Prometheus config file
@"
global:
  scrape_interval: 10s

scrape_configs:
  - job_name: "json_exporter"
    static_configs:
      - targets: ["json-exporter:8000"]
"@ | Out-File -Encoding utf8 $PROMETHEUS_CONFIG

Write-Host "✅ Prometheus config created."

# Step 7: Create Docker Compose file
@"
version: '3.8'

services:
  json-exporter:
    build: .
    container_name: json-exporter
    ports:
      - "8000:8000"
    volumes:
      - ./data.json:/data/data.json

  prometheus:
    image: prom/prometheus
    container_name: prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
    ports:
      - "9090:9090"
    depends_on:
      - json-exporter

  grafana:
    image: grafana/grafana
    container_name: grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
"@ | Out-File -Encoding utf8 $DOCKER_COMPOSE_FILE

Write-Host "✅ Docker Compose file created."

# Step 8: Build and Start the Containers
Set-Location $FOLDER
Write-Host "🚀 Starting Docker containers in '$FOLDER'..."
docker-compose up -d --build

Write-Host "✅ Monitoring system started!"
Write-Host "🌍 Prometheus: http://localhost:9090"
Write-Host "📊 Grafana: http://localhost:3000"
Write-Host "📡 JSON Exporter Metrics: http://localhost:8000/metrics"
