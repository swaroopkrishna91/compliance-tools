import boto3
import json

# AWS S3 Configuration
BUCKET_NAME = "myclod121312312"
FILE_KEY = "scoutsuite-reports/reports_2025-02-12_14-28-20/scoutsuite_results_aws-807344852902.js"

def fetch_scoutsuite_data():
    """Fetch JSON file from S3 and return data"""
    s3 = boto3.client("s3")

    try:
        print("Connecting to S3...")
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
        obj = s3.download_file(Bucket=BUCKET_NAME, Key=FILE_KEY, LOCAL_FILE_PATH='*')

        print("File found. Downloading...")
        # file_content = obj["Body"].read().decode("utf-8").strip()
        with open(obj) as f:
            json_payload = f.readlines()
            json_payload.pop(0)
            json_payload = ''.join(json_payload)
            json_file = json.loads(json_payload)
            return json_file

        if not file_content:
            print("Error: File is empty.")
            return None

        print("Parsing JSON data...")
        data = json.loads(file_content)

        print("Data successfully loaded!")
        return data

    except json.JSONDecodeError:
        print("Error: File is not valid JSON.")
        return None
    except s3.exceptions.NoSuchKey:
        print("Error: File not found in S3.")
        return None
    except Exception as e:
        print("Unexpected error:", str(e))
        return None

# Run the function and print output
data = fetch_scoutsuite_data()
if data:
    print(json.dumps(data, indent=2))
