file_path = "D:\Study\Code\Complaince-Tool\scoutsuite-report\scoutsuite-results\scoutsuite_results_aws-807344852902.js"
obj = "path"

json_file = ""

with open(obj) as f:
    json_payload = f.readlines()
    json_payload.pop(0)
    json_payload = ''.join(json_payload)
    json_file = json.loads(json_payload)
return json_file

import json

def convert_js_to_json(file_path):
    with open(file_path) as f:
        json_payload = f.readlines()
        json_payload.pop(0)  # Remove the first line if it's a JS variable assignment
        json_payload = ''.join(json_payload).strip().rstrip(';')  # Join and clean up data

    # Convert to JSON
    try:
        json_file = json.loads(json_payload)
        return json_file
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in file - {e}")
        return None

# Example usage
json_data = convert_js_to_json(file_path)

# Save JSON data to a new file
if json_data:
    with open("data.json", "w", encoding="utf-8") as json_out:
        json.dump(json_data, json_out, indent=4)
    print("Conversion successful! JSON saved as data.json")
