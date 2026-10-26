import json
import boto3
import io
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import PurePosixPath
from urllib.parse import unquote_plus

from PIL import Image, ImageDraw, ImageOps


s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


SOURCE_BUCKET = "manara-image-source-serverless-image-processing-10-2026"

DESTINATION_BUCKET = "manara-image-processed-serverless-image-processing-10-2026"

TABLE_NAME = "manara-image-metadata"
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:223663280345:manara-image-processing-notifications"

MAX_IMAGE_SIZE = (800, 800)


def process_image(bucket_name, object_key):

    if bucket_name != SOURCE_BUCKET:
        raise ValueError("Unexpected source bucket")

    logger.info("Downloading image: %s", object_key)

    response = s3.get_object(
        Bucket=bucket_name,
        Key=object_key
    )

    image_bytes = response["Body"].read()

    image = Image.open(io.BytesIO(image_bytes))

    image = ImageOps.exif_transpose(image)

    image = image.convert("RGB")

    original_width, original_height = image.size

    image.thumbnail(MAX_IMAGE_SIZE)

    processed_width, processed_height = image.size

    draw = ImageDraw.Draw(image)

    draw.text(
        (20, 20),
        "Manara AWS Project",
        fill="white",
        stroke_width=2,
        stroke_fill="black"
    )

    output_buffer = io.BytesIO()

    image.save(
        output_buffer,
        format="JPEG",
        quality=85
    )

    output_buffer.seek(0)

    # Unique identifier based on source object key
    image_id = hashlib.sha256(
        object_key.encode("utf-8")
    ).hexdigest()[:16]

    filename = PurePosixPath(object_key).stem

    output_key = f"processed/{image_id}-{filename}.jpg"

    s3.put_object(
        Bucket=DESTINATION_BUCKET,
        Key=output_key,
        Body=output_buffer.getvalue(),
        ContentType="image/jpeg"
    )

    logger.info(
        "Image uploaded successfully: %s",
        output_key
    )
    

    # Save metadata to DynamoDB
    table = dynamodb.Table(TABLE_NAME)

    table.put_item(
        Item={
            "imageId": image_id,
            "sourceBucket": bucket_name,
            "sourceKey": object_key,
            "processedBucket": DESTINATION_BUCKET,
            "processedKey": output_key,
            "originalWidth": original_width,
            "originalHeight": original_height,
            "processedWidth": processed_width,
            "processedHeight": processed_height,
            "status": "COMPLETED",
            "processedAt": datetime.now(
                timezone.utc
            ).isoformat()
        }
    )

    logger.info(
        "Metadata saved to DynamoDB: %s",
        image_id
    )
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="Manara Image Processing Completed",
        Message=json.dumps({
            "imageId": image_id,
            "status": "COMPLETED",
            "sourceKey": object_key,
            "processedKey": output_key,
            "processedBucket": DESTINATION_BUCKET,
            "processedAt": datetime.now(
                timezone.utc
            ).isoformat()
        }, indent=2)
    )

    logger.info(
        "SNS notification published: %s",
        image_id
    )


def lambda_handler(event, context):

    logger.info(
        "Received event: %s",
        json.dumps(event)
    )

    # Direct invocation from Step Functions
    if "bucket" in event and "key" in event:

        process_image(
            event["bucket"],
            event["key"]
        )

        return {
            "statusCode": 200,
            "message": "Image processed via Step Functions"
        }

    # SQS event processing
    for record in event.get("Records", []):

        message_body = json.loads(record["body"])

        if message_body.get("Event") == "s3:TestEvent":
            logger.info("Ignoring S3 test event")
            continue

        for s3_record in message_body.get("Records", []):

            bucket_name = s3_record["s3"]["bucket"]["name"]

            object_key = unquote_plus(
                s3_record["s3"]["object"]["key"]
            )

            process_image(
                bucket_name,
                object_key
            )

    return {
        "statusCode": 200,
        "body": "Image processing and metadata completed"
    }