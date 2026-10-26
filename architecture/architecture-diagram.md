# Solution Architecture

```mermaid
flowchart LR
    User([User])

    API["API Gateway<br/>GET /upload-url"]
    URLFn["Lambda<br/>Pre-signed URL Generator"]

    Source[("S3<br/>Source Bucket")]
    Queue["SQS<br/>Main Queue"]
    DLQ["SQS<br/>Dead-Letter Queue"]

    Processor["Lambda<br/>Image Processor + Pillow"]

    Destination[("S3<br/>Processed Images")]
    DB[("DynamoDB<br/>Image Metadata")]
    SNS["SNS<br/>Notifications"]
    Email([Email Subscriber])

    CF["CloudFront<br/>OAC + HTTPS"]
    Viewer([Image Viewer])

    SF["Step Functions<br/>Manual Execution"]
    CW["CloudWatch Logs"]

    User -->|"Request upload URL"| API
    API --> URLFn
    URLFn -.->|"Return signed URL"| User
    User -->|"PUT JPG"| Source

    Source -->|"ObjectCreated"| Queue
    Queue -->|"Lambda polling"| Processor

    Processor -->|"Resize + Watermark"| Destination
    Processor -->|"PutItem"| DB
    Processor -->|"Publish"| SNS
    SNS --> Email

    Queue -.->|"Repeated failures"| DLQ

    Destination -->|"Private S3 origin"| CF
    CF --> Viewer

    SF -->|"Direct invocation"| Processor

    Processor -.-> CW
    URLFn -.-> CW
```

## Architecture Notes

- The primary image processing pipeline is event-driven through S3, SQS, and Lambda.
- Step Functions provides a separate manually triggered workflow that invokes the existing image processor.
- CloudFront uses Origin Access Control (OAC) to access the private destination S3 bucket.
- SQS Standard provides at-least-once delivery. Duplicate processing is possible.
