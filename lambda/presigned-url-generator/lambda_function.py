import json
import boto3
import os
import uuid

s3 = boto3.client("s3")

BUCKET = "manara-image-source-serverless-image-processing-10-2026"


def lambda_handler(event, context):

    params = event.get("queryStringParameters") or {}

    filename = params.get("filename", "upload.jpg")

    if not filename.lower().endswith(".jpg"):
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Only JPG files are allowed"
            })
        }

    object_key = f"{uuid.uuid4()}-{os.path.basename(filename)}"

    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET,
            "Key": object_key,
            "ContentType": "image/jpeg"
        },
        ExpiresIn=300
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "uploadUrl": url,
            "objectKey": object_key,
            "expiresIn": 300,
            "method": "PUT",
            "contentType": "image/jpeg"
        })
    }