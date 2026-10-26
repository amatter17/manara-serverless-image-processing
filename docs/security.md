# Security Design

## Implemented Controls

- Private S3 source and destination buckets.
- S3 Block Public Access enabled.
- CloudFront Origin Access Control (OAC).
- HTTPS for CloudFront delivery.
- IAM execution roles for Lambda.
- Resource-scoped IAM permissions.
- Temporary pre-signed upload URLs.

## Security Limitations

The API Gateway endpoint currently has no authentication.

A caller who can access the endpoint can request temporary upload URLs.

The system validates the .jpg filename extension at the API level, but does not enforce file size limits or inspect file content before upload.

The processor detects invalid image content during Pillow decoding.

## Production Recommendations

- Add API authorization using JWT or another appropriate identity mechanism.
- Configure API throttling.
- Limit uploaded object size.
- Validate image content and MIME type.
- Add stronger idempotency.
- Avoid uploading sensitive personal images to public demo links.
- Rotate or revoke exposed temporary credentials if applicable.
