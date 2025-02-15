import json
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    source_bucket = event['myclod121312312']
    source_key = event['s3://myclod121312312/scoutsuite-reports/reports_2025-02-12_14-28-20/scoutsuite_results_aws-807344852902.js']
    target_bucket = event['myclod121312312']
    target_key = event['s3://myclod121312312/scoutsuite_jsonfiles/']

    # Fetch the file from the source S3 bucket
    obj = s3.get_object(Bucket=source_bucket, Key=source_key)
    json_payload = obj['Body'].read().decode('utf-8').splitlines()
    
    # Remove the first line if it's a JS variable assignment
    json_payload.pop(0)
    json_payload = ''.join(json_payload)

    try:
        # Convert to JSON
        json_file = json.loads(json_payload)
        
        # Save JSON data to the target S3 bucket
        s3.put_object(Bucket=target_bucket, Key=target_key, Body=json.dumps(json_file, indent=4).encode('utf-8'))
        return {
            'statusCode': 200,
            'body': json.dumps('Conversion successful! JSON saved in target S3 bucket.')
        }
    except json.JSONDecodeError as e:
        return {
            'statusCode': 400,
            'body': json.dumps(f'Error: Invalid JSON format in file - {e}')
        }