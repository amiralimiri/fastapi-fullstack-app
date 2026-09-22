import json
import os
import boto3
from botocore.exceptions import ClientError
from image_utils import _get_s3_client  
from config import settings     


def apply_bucket_policy(json_file_path: str, bucket_name: str | None = None) -> None:
    # 1. Fallback to default bucket from settings if not specified
    target_bucket = bucket_name or getattr(settings, "s3_bucket_name", None)
    if not target_bucket:
        print("[ERROR] Bucket name was not provided and not found in settings.")
        return

    # 2. Check if the JSON policy file exists
    if not os.path.exists(json_file_path):
        print(f"[ERROR] File not found at path: {json_file_path}")
        return

    # 3. Read and parse the JSON file
    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            policy_data = json.load(file)
            # Convert JSON dict to string required by S3 API
            policy_string = json.dumps(policy_data)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON syntax in file: {e}")
        return
    except Exception as e:
        print(f"[ERROR] Failed to read file: {e}")
        return

    # 4. Get S3 client and apply the bucket policy
    try:
        s3_client = boto3.client(
                "s3",
                endpoint_url=settings.s3_endpoint_url,
                aws_access_key_id=(
                    settings.s3_access_key_id.get_secret_value()
                    if settings.s3_access_key_id
                    else None
                ),
                aws_secret_access_key=(
                    settings.s3_secret_access_key.get_secret_value()
                    if settings.s3_secret_access_key
                    else None
                ),
            )
        s3_client.put_bucket_policy(
            Bucket=target_bucket,
            Policy=policy_string
        )
        print(f"[SUCCESS] Policy applied successfully to bucket '{target_bucket}'.")

    except ClientError as e:
        print(f"[ERROR] S3 API Error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")


# --- Usage Example ---
if __name__ == "__main__":
    POLICY_FILE_PATH = r"E:\new_world\projects\fastapi-fullstack-app\bucket_policy\aws_bucket_policy.json"
    BUCKET_NAME = settings.s3_bucket_name
    
    # Pass bucket_name explicitly or leave it None if configured in settings
    apply_bucket_policy(
        json_file_path=POLICY_FILE_PATH,
        bucket_name=BUCKET_NAME
    )