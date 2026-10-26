# Cost Optimization

## Architecture Decisions

- AWS Lambda replaces continuously running servers.
- SQS provides managed asynchronous buffering.
- DynamoDB On-Demand avoids fixed provisioned throughput.
- S3 SSE-S3 avoids additional customer-managed KMS key charges.
- No NAT Gateway, EC2, ALB, RDS, or custom domain required.
- CloudFront provides caching for processed images.

## Cost Monitoring

An AWS Budget was configured with:

- Monthly budget: USD 8.
- Notification threshold: 85%.

AWS Budgets provide notifications but do not automatically stop resources.

## Recommendations

- Use small images during testing.
- Limit repeated API requests.
- Set CloudWatch Logs retention to 7 days.
- Monitor CloudFront usage and request volume.
- Delete unused resources after the evaluation period.

AWS credits do not guarantee that all service usage is free.
