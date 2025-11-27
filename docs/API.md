#  API Documentation

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)
- [Client Libraries](#client-libraries)

---

## Overview

The Kairs API provides a RESTful interface for processing heartbeat events and detecting service outages. This is an optional production feature that extends the CLI functionality.

**Base URL**: `http://localhost:8000` (default)

**API Version**: 1.0.0

**Content Type**: `application/json`

---

## Quick Start

### Starting the API Server

```bash
# Basic startup
python -m app.main --api --port 8000

# With custom configuration
export API_PORT=8080
export API_WORKERS=4
export LOG_LEVEL=DEBUG
python -m app.main --api

# Using Docker
docker-compose up -d api
```

### Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Authentication

### API Key (Optional but Recommended)

Set the `API_KEY` environment variable to enable authentication:

```bash
export API_KEY=your-secret-key-here
python -m app.main --api
```

Include the API key in request headers:

```bash
curl -H "X-API-Key: your-secret-key-here" \
     http://localhost:8000/health
```

**Security Best Practices**:
- Use strong, random API keys (32+ characters)
- Rotate keys regularly
- Never commit keys to version control
- Use environment variables or secrets management

---

## Endpoints

### Root Endpoint

```
GET /
```

Returns API information and available endpoints.

**Response**:
```json
{
  "name": "Kairs API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "monitor": "/monitor",
    "docs": "/docs"
  }
}
```

---

### Health Check

```
GET /health
```

Check if the API server is healthy and responsive.

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Use Cases**:
- Load balancer health checks
- Kubernetes liveness/readiness probes
- Monitoring systems
- CI/CD pipelines

**Example**:
```bash
curl http://localhost:8000/health
```

---

### Monitor Heartbeats

```
POST /monitor
```

Upload heartbeat events and receive alert analysis.

**Request**:

- **Method**: POST
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file` (required): JSON file with heartbeat events
  - `interval` (optional, default: 60): Expected interval in seconds
  - `allowed_misses` (optional, default: 3): Threshold for alerts
  - `tolerance` (optional, default: 0): Tolerance window in seconds

**Request Example**:
```bash
curl -X POST http://localhost:8000/monitor \
  -F "file=@events.json" \
  -F "interval=60" \
  -F "allowed_misses=3" \
  -F "tolerance=0"
```

**Response**: `200 OK`
```json
{
  "alerts": [
    {
      "service": "email",
      "alert_at": "2025-08-04T10:05:00+00:00",
      "missed_count": 3,
      "last_seen": "2025-08-04T10:01:00+00:00"
    }
  ],
  "validation": {
    "total_events": 29,
    "valid_events": 26,
    "invalid_events": 3,
    "errors": [
      "Event 5: Missing timestamp field",
      "Event 12: Invalid timestamp format",
      "Event 18: Missing service field"
    ],
    "skipped_reasons": {
      "missing_timestamp": 1,
      "invalid_timestamp_format": 1,
      "missing_service": 1
    }
  },
  "services_monitored": ["email", "sms", "push"],
  "monitoring_duration_ms": 15.3,
  "timestamp": "2025-11-27T18:00:00+00:00"
}
```

**Input File Format**:
```json
[
  {
    "service": "email",
    "timestamp": "2025-08-04T10:00:00Z"
  },
  {
    "service": "email",
    "timestamp": "2025-08-04T10:01:00Z"
  }
]
```

---

### Error Responses

#### 400 Bad Request

Invalid input or malformed JSON.

```json
{
  "detail": "Invalid JSON file"
}
```

#### 413 Payload Too Large

File size exceeds limit (default: 10MB).

```json
{
  "detail": "File too large. Maximum size: 10MB"
}
```

#### 500 Internal Server Error

Unexpected server error.

```json
{
  "detail": "Internal server error"
}
```

---

## Error Handling

### Validation Errors

The API gracefully handles malformed events:

```json
{
  "validation": {
    "total_events": 10,
    "valid_events": 7,
    "invalid_events": 3,
    "errors": [
      "Event 2: missing_timestamp - Field required",
      "Event 5: invalid_timestamp_format - Invalid datetime format",
      "Event 8: empty_service - Service name cannot be empty"
    ],
    "skipped_reasons": {
      "missing_timestamp": 1,
      "invalid_timestamp_format": 1,
      "empty_service": 1
    }
  }
}
```

**Validation Categories**:
- `missing_service`: Service field not present
- `missing_timestamp`: Timestamp field not present
- `empty_service`: Service field is null/empty
- `empty_timestamp`: Timestamp field is null/empty
- `invalid_timestamp_format`: Timestamp cannot be parsed
- `invalid_service_format`: Service name has invalid characters
- `validation_error`: Other validation errors

---

## Rate Limiting

Currently, the API does not implement rate limiting. For production deployments, consider:

- **Nginx rate limiting**: `limit_req_zone`
- **API Gateway**: AWS API Gateway, Kong, etc.
- **Application-level**: middleware with Redis

Example Nginx configuration:
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    location /monitor {
        limit_req zone=api burst=20;
        proxy_pass http://localhost:8000;
    }
}
```

---

## Examples

### Python Client

```python
import requests

# Upload events
with open('events.json', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/monitor',
        files={'file': f},
        data={
            'interval': 60,
            'allowed_misses': 3,
            'tolerance': 0
        }
    )

result = response.json()
print(f"Alerts: {len(result['alerts'])}")
for alert in result['alerts']:
    print(f"  - {alert['service']} at {alert['alert_at']}")
```

### JavaScript/TypeScript Client

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('interval', '60');
formData.append('allowed_misses', '3');

const response = await fetch('http://localhost:8000/monitor', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(`Found ${result.alerts.length} alerts`);
```

### cURL Examples

```bash
# Basic upload
curl -X POST http://localhost:8000/monitor \
  -F "file=@events.json" \
  -F "interval=60" \
  -F "allowed_misses=3"

# With authentication
curl -X POST http://localhost:8000/monitor \
  -H "X-API-Key: your-secret-key" \
  -F "file=@events.json"

# Health check
curl http://localhost:8000/health

# Pretty-print JSON response
curl -s http://localhost:8000/monitor \
  -F "file=@events.json" | jq .
```

---

## Client Libraries

### Official Clients

Currently, no official client libraries are available. The API follows RESTful conventions and can be used with any HTTP client.

### Community Clients

If you've created a client library, please submit a PR to add it here!

---

## OpenAPI Specification

The full OpenAPI 3.0 specification is available at:
- **JSON**: http://localhost:8000/openapi.json
- **Interactive**: http://localhost:8000/docs

### Download OpenAPI Spec

```bash
curl http://localhost:8000/openapi.json > openapi.json
```

### Generate Client from OpenAPI

```bash
# Install OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./python-client

# Generate TypeScript client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o ./ts-client
```

---

## Production Deployment

### Docker Deployment

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    image: kairos:latest
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - API_WORKERS=4
      - API_KEY=${API_KEY}
      - LOG_LEVEL=INFO
      - CORS_ORIGINS=https://yourdomain.com
    restart: unless-stopped
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kairos-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kairos
  template:
    metadata:
      labels:
        app: kairos
    spec:
      containers:
      - name: api
        image: kairos:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: API_WORKERS
          value: "4"
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: api-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

### Environment Variables

See [Configuration Guide](../README.md#configuration) for all available environment variables.

---

## Monitoring and Observability

### Prometheus Metrics (Future Feature)

```
GET /metrics
```

Planned metrics:
- `kairos_requests_total`: Total API requests
- `kairos_alerts_total`: Total alerts generated
- `kairos_events_processed`: Events processed
- `kairos_processing_duration_seconds`: Processing time
- `kairos_validation_errors_total`: Validation errors

### Logging

Structured JSON logs in production:

```json
{
  "timestamp": "2025-11-27T18:00:00Z",
  "level": "INFO",
  "service": "kairos",
  "message": "Alert detection complete",
  "alerts": 7,
  "duration_ms": 15.3,
  "events": 29
}
```

Enable with:
```bash
export JSON_LOGS=true
python -m app.main --api
```

---

## CORS Configuration

Configure allowed origins for cross-origin requests:

```bash
# Development (allow all)
export CORS_ORIGINS=*

# Production (specific domains)
export CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## Performance

### Throughput

- **Small files** (<100 events): ~50-100 requests/second
- **Medium files** (100-1000 events): ~20-50 requests/second
- **Large files** (1000+ events): ~5-20 requests/second

*Benchmarked on: 4-core CPU, 8GB RAM*

### Optimization Tips

1. **Horizontal scaling**: Run multiple API workers
2. **Caching**: Enable Redis for repeated queries
3. **Database**: Store results for historical analysis
4. **Load balancing**: Distribute across multiple instances

---

## Support

-  Email: kagrawalk510@gmail.com
-  LinkedIn: [Krishna Agrawal](https://www.linkedin.com/in/agrawal-krishna-aa11a61ba/)
-  GitHub: [@krishnaak114](https://github.com/krishnaak114)
-  Documentation: [Full Docs](../README.md)

---

**Author**: Krishna Agrawal  
**Version**: 1.0.0  
**Last Updated**: November 27, 2025
