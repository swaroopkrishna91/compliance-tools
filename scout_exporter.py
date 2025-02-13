from flask import Flask, Response
from prometheus_client import Gauge, generate_latest
import json
import boto3
import os

app = Flask(__name__)

# AWS S3 Configuration
BUCKET_NAME = "myclod121312312"
FILE_KEY = "scoutsuite-reports/reports_2025-02-12_14-28-20/scoutsuite_results_aws-807344852902.js"

# Prometheus Metrics
issue_count_gauge = Gauge("scout_suite_issues", "Number of security issues", ["severity"])

def fetch_scoutsuite_data():
    """Fetch JSON data from S3 and process metrics"""
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
    print(BUCKET_NAME,FILE_KEY)
    data = json.loads(obj["Body"].read().decode("utf-8"))

    # Extract issue counts (example based on a common Scout Suite structure)
    critical_issues = sum(1 for issue in data["findings"] if issue["level"] == "danger")
    high_issues = sum(1 for issue in data["findings"] if issue["level"] == "warning")
    # medium_issues = sum(1 for issue in data["findings"] if issue["level"] == "medium")

    # Update Prometheus Metrics
    issue_count_gauge.labels(severity="critical").set(critical_issues)
    issue_count_gauge.labels(severity="high").set(high_issues)
    # issue_count_gauge.labels(severity="medium").set(medium_issues)

@app.route("/metrics")
def metrics():
    fetch_scoutsuite_data()
    return Response(generate_latest(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
