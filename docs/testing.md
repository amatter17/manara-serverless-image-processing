# Testing and Validation

## 1. Automatic Image Processing

Upload a valid JPG to the source S3 bucket.

Expected:
- S3 sends ObjectCreated event to SQS.
- Lambda receives the SQS message.
- Processed image appears in destination S3.
- DynamoDB stores image metadata.
- SNS publishes completion notification.

## 2. Resize and Watermark

Verify:
- Maximum processed dimensions are 800 x 800.
- Aspect ratio is preserved.
- Watermark text is visible.
- Output content type is image/jpeg.

## 3. Dead-Letter Queue

Upload a text file with a .jpg extension.

Expected:
- Pillow raises UnidentifiedImageError.
- Lambda invocation fails.
- SQS retries processing.
- Message eventually moves to the DLQ.

## 4. CloudFront

Open a processed image using the CloudFront distribution domain.

Expected:
- HTTPS access succeeds.
- Image loads through CloudFront.
- Direct unauthenticated S3 access remains blocked.

## 5. Step Functions

Start a manual execution with:

```json
{
  "bucket": "manara-image-source-serverless-image-processing-10-2026",
  "key": "example.jpg"
}
```

Expected: Execution status Succeeded, provided the object exists.

## 6. API Gateway

Request:

GET /upload-url?filename=test.jpg

Expected:
- Temporary pre-signed upload URL.
- HTTP PUT uploads JPG to source S3.
- Automatic pipeline processes the uploaded image.

## 7. SNS

Expected:
- CloudWatch contains "SNS notification published".
- Confirmed email subscriber receives completion message.

## Observed Results

All major integration tests completed successfully during the project implementation.

Duplicate SNS notifications were observed, demonstrating the need for stronger idempotency.
