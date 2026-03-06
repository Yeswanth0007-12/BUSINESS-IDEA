# PackOptima Warehouse Integration Guide

## Overview

This guide provides step-by-step instructions for integrating PackOptima's packaging optimization API into your warehouse management system (WMS). The integration enables real-time packaging optimization, webhook notifications, and comprehensive cost analysis.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Webhook Configuration](#webhook-configuration)
5. [Code Examples](#code-examples)
6. [Error Handling](#error-handling)
7. [Rate Limits](#rate-limits)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Active PackOptima account with API access
- HTTPS-enabled webhook endpoint (for event notifications)
- Product catalog configured in PackOptima
- Box inventory configured in PackOptima

### Integration Steps

1. Generate API key from PackOptima dashboard
2. Configure webhook endpoint (optional)
3. Implement API calls in your WMS
4. Test integration in staging environment
5. Deploy to production

---

## Authentication

### API Key Generation

1. Log in to PackOptima dashboard
2. Navigate to **Settings** → **API Keys**
3. Click **Create New API Key**
4. Provide a descriptive name (e.g., "Production WMS")
5. **Copy the API key immediately** (it's only shown once)
6. Store the key securely (environment variable or secrets manager)

### Using API Keys

Include the API key in the `Authorization` header of all requests:

```
Authorization: Bearer YOUR_API_KEY
```

**Security Best Practices:**
- Never commit API keys to version control
- Rotate keys periodically (every 90 days recommended)
- Use different keys for staging and production
- Revoke compromised keys immediately

---

## API Endpoints

### Base URL

```
Production: https://api.packoptima.ai
Staging: https://staging-api.packoptima.ai
```

### 1. Optimize Package

**Endpoint:** `POST /api/v1/warehouse/optimize-package`

**Description:** Optimize packaging for a warehouse order with multiple items.

**Request Headers:**
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Request Body:**
```json
{
  "order_id": "WH-12345",
  "items": [
    {
      "sku": "PROD-123",
      "quantity": 2,
      "dimensions": {
        "length_cm": 30.0,
        "width_cm": 20.0,
        "height_cm": 10.0
      },
      "weight_kg": 2.5
    },
    {
      "sku": "PROD-456",
      "quantity": 1
    }
  ],
  "shipping_address": {
    "country": "US",
    "postal_code": "12345"
  },
  "courier_rate": 2.5
}
```

**Field Descriptions:**
- `order_id` (required): Your internal order identifier
- `items` (required): Array of items to pack
  - `sku` (required): Product SKU (must exist in your catalog)
  - `quantity` (required): Number of items
  - `dimensions` (optional): Override catalog dimensions
  - `weight_kg` (optional): Override catalog weight
- `shipping_address` (optional): For future shipping rate calculation
- `courier_rate` (optional): Shipping cost per kg (default: 2.5)

**Response (200 OK):**
```json
{
  "optimization_id": "opt-789",
  "order_id": "WH-12345",
  "status": "success",
  "boxes_required": [
    {
      "box_id": 5,
      "box_name": "Medium Box",
      "dimensions": {
        "length_cm": 40.0,
        "width_cm": 30.0,
        "height_cm": 20.0
      },
      "items": ["PROD-123", "PROD-123", "PROD-456"],
      "total_weight_kg": 6.5,
      "space_utilization": 75.5,
      "box_cost": 5.00,
      "shipping_cost": 16.25,
      "total_cost": 21.25
    }
  ],
  "total_boxes": 1,
  "total_cost": 21.25,
  "estimated_shipping_cost": 16.25,
  "unpacked_items": null
}
```

**Response Fields:**
- `optimization_id`: Unique identifier for this optimization
- `status`: `success`, `partial` (some items unpacked), or `failed`
- `boxes_required`: Array of boxes needed
- `total_boxes`: Number of boxes required
- `total_cost`: Total packaging + shipping cost
- `unpacked_items`: Array of SKUs that couldn't be packed (if any)

**Performance:** Target response time < 500ms at p95

---

### 2. Register Webhook

**Endpoint:** `POST /api/v1/warehouse/webhooks`

**Description:** Register a webhook to receive event notifications.

**Request Body:**
```json
{
  "url": "https://warehouse.example.com/webhooks/packoptima",
  "events": ["optimization.completed", "optimization.failed"],
  "secret": "your_webhook_secret_min_16_chars"
}
```

**Supported Events:**
- `optimization.completed`: Optimization succeeded
- `optimization.failed`: Optimization failed

**Response (201 Created):**
```json
{
  "id": 1,
  "company_id": 123,
  "url": "https://warehouse.example.com/webhooks/packoptima",
  "events": ["optimization.completed", "optimization.failed"],
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 3. List Webhooks

**Endpoint:** `GET /api/v1/warehouse/webhooks`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "company_id": 123,
    "url": "https://warehouse.example.com/webhooks/packoptima",
    "events": ["optimization.completed"],
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### 4. Delete Webhook

**Endpoint:** `DELETE /api/v1/warehouse/webhooks/{webhook_id}`

**Response:** `204 No Content`

---

## Webhook Configuration

### Webhook Payload

When an event occurs, PackOptima sends a POST request to your webhook URL:

**Headers:**
```
Content-Type: application/json
X-PackOptima-Signature: sha256=abc123...
X-PackOptima-Event: optimization.completed
```

**Payload:**
```json
{
  "event": "optimization.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "optimization_id": "opt-789",
    "order_id": "WH-12345",
    "status": "completed",
    "total_boxes": 1,
    "total_cost": 21.25
  }
}
```

### Signature Verification

**Why verify signatures?**
- Ensures webhook came from PackOptima
- Prevents replay attacks
- Protects against man-in-the-middle attacks

**Verification Steps:**

1. Extract signature from `X-PackOptima-Signature` header
2. Compute HMAC-SHA256 of payload using your webhook secret
3. Compare computed signature with received signature (constant-time comparison)

**Example (Python):**
```python
import hmac
import hashlib

def verify_webhook_signature(payload_body, signature_header, secret):
    """Verify webhook signature."""
    # Extract signature (format: "sha256=abc123...")
    expected_signature = signature_header.split('=')[1]
    
    # Compute HMAC-SHA256
    computed_signature = hmac.new(
        secret.encode('utf-8'),
        payload_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison
    return hmac.compare_digest(computed_signature, expected_signature)
```

### Retry Logic

- Failed deliveries are retried up to 3 times
- Exponential backoff: 1s, 2s, 4s
- Webhook deactivated after 10 consecutive failures
- Monitor webhook status in dashboard

---

## Code Examples

### Python

```python
import requests
import hmac
import hashlib
from flask import Flask, request, jsonify

# Configuration
API_KEY = "your_api_key_here"
API_BASE_URL = "https://api.packoptima.ai"
WEBHOOK_SECRET = "your_webhook_secret"

app = Flask(__name__)

# 1. Optimize Package
def optimize_package(order_id, items):
    """Call PackOptima optimization API."""
    url = f"{API_BASE_URL}/api/v1/warehouse/optimize-package"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "order_id": order_id,
        "items": items,
        "courier_rate": 2.5
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# Example usage
if __name__ == "__main__":
    result = optimize_package(
        order_id="WH-12345",
        items=[
            {
                "sku": "PROD-123",
                "quantity": 2
            },
            {
                "sku": "PROD-456",
                "quantity": 1
            }
        ]
    )
    print(f"Optimization ID: {result['optimization_id']}")
    print(f"Total boxes: {result['total_boxes']}")
    print(f"Total cost: ${result['total_cost']:.2f}")

# 2. Webhook Endpoint
@app.route('/webhooks/packoptima', methods=['POST'])
def handle_webhook():
    """Handle PackOptima webhook."""
    # Get signature from header
    signature = request.headers.get('X-PackOptima-Signature')
    if not signature:
        return jsonify({"error": "Missing signature"}), 401
    
    # Verify signature
    payload_body = request.get_data(as_text=True)
    if not verify_webhook_signature(payload_body, signature, WEBHOOK_SECRET):
        return jsonify({"error": "Invalid signature"}), 401
    
    # Process event
    event_data = request.json
    event_type = event_data['event']
    
    if event_type == 'optimization.completed':
        # Handle successful optimization
        order_id = event_data['data']['order_id']
        print(f"Optimization completed for order {order_id}")
        # Update your WMS here
    
    elif event_type == 'optimization.failed':
        # Handle failed optimization
        order_id = event_data['data']['order_id']
        print(f"Optimization failed for order {order_id}")
        # Alert operations team
    
    return jsonify({"status": "received"}), 200

def verify_webhook_signature(payload_body, signature_header, secret):
    """Verify webhook signature."""
    expected_signature = signature_header.split('=')[1]
    computed_signature = hmac.new(
        secret.encode('utf-8'),
        payload_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_signature, expected_signature)
```

---

### JavaScript (Node.js)

```javascript
const axios = require('axios');
const crypto = require('crypto');
const express = require('express');

// Configuration
const API_KEY = 'your_api_key_here';
const API_BASE_URL = 'https://api.packoptima.ai';
const WEBHOOK_SECRET = 'your_webhook_secret';

const app = express();
app.use(express.json());

// 1. Optimize Package
async function optimizePackage(orderId, items) {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/warehouse/optimize-package`,
      {
        order_id: orderId,
        items: items,
        courier_rate: 2.5
      },
      {
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('Optimization failed:', error.response?.data || error.message);
    throw error;
  }
}

// Example usage
(async () => {
  const result = await optimizePackage('WH-12345', [
    { sku: 'PROD-123', quantity: 2 },
    { sku: 'PROD-456', quantity: 1 }
  ]);
  console.log(`Optimization ID: ${result.optimization_id}`);
  console.log(`Total boxes: ${result.total_boxes}`);
  console.log(`Total cost: $${result.total_cost.toFixed(2)}`);
})();

// 2. Webhook Endpoint
app.post('/webhooks/packoptima', (req, res) => {
  // Get signature from header
  const signature = req.headers['x-packoptima-signature'];
  if (!signature) {
    return res.status(401).json({ error: 'Missing signature' });
  }
  
  // Verify signature
  const payloadBody = JSON.stringify(req.body);
  if (!verifyWebhookSignature(payloadBody, signature, WEBHOOK_SECRET)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  // Process event
  const { event, data } = req.body;
  
  if (event === 'optimization.completed') {
    console.log(`Optimization completed for order ${data.order_id}`);
    // Update your WMS here
  } else if (event === 'optimization.failed') {
    console.log(`Optimization failed for order ${data.order_id}`);
    // Alert operations team
  }
  
  res.json({ status: 'received' });
});

function verifyWebhookSignature(payloadBody, signatureHeader, secret) {
  const expectedSignature = signatureHeader.split('=')[1];
  const computedSignature = crypto
    .createHmac('sha256', secret)
    .update(payloadBody)
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(expectedSignature),
    Buffer.from(computedSignature)
  );
}

app.listen(3000, () => {
  console.log('Webhook server listening on port 3000');
});
```

---

### cURL

```bash
# 1. Optimize Package
curl -X POST https://api.packoptima.ai/api/v1/warehouse/optimize-package \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "WH-12345",
    "items": [
      {
        "sku": "PROD-123",
        "quantity": 2
      },
      {
        "sku": "PROD-456",
        "quantity": 1
      }
    ],
    "courier_rate": 2.5
  }'

# 2. Register Webhook
curl -X POST https://api.packoptima.ai/api/v1/warehouse/webhooks \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://warehouse.example.com/webhooks/packoptima",
    "events": ["optimization.completed", "optimization.failed"],
    "secret": "your_webhook_secret_min_16_chars"
  }'

# 3. List Webhooks
curl -X GET https://api.packoptima.ai/api/v1/warehouse/webhooks \
  -H "Authorization: Bearer YOUR_API_KEY"

# 4. Delete Webhook
curl -X DELETE https://api.packoptima.ai/api/v1/warehouse/webhooks/1 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Check request payload |
| 401 | Unauthorized | Verify API key |
| 404 | Not Found | Check SKU exists in catalog |
| 429 | Too Many Requests | Implement backoff, check rate limits |
| 500 | Server Error | Retry with exponential backoff |
| 503 | Service Unavailable | System maintenance, retry later |

### Error Response Format

```json
{
  "detail": "Product SKU 'INVALID-SKU' not found in catalog",
  "error_code": "PRODUCT_NOT_FOUND",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Errors

**1. Invalid API Key**
```json
{
  "detail": "Invalid or inactive API key"
}
```
**Solution:** Verify API key is correct and active

**2. Product Not Found**
```json
{
  "detail": "Product SKU 'PROD-999' not found in catalog"
}
```
**Solution:** Ensure product exists in PackOptima catalog

**3. Rate Limit Exceeded**
```json
{
  "detail": "Rate limit exceeded. Retry after 60 seconds"
}
```
**Solution:** Implement exponential backoff, upgrade tier if needed

**4. No Suitable Box**
```json
{
  "status": "partial",
  "unpacked_items": ["PROD-LARGE"]
}
```
**Solution:** Add larger boxes to inventory or split order

---

## Rate Limits

### Tier Limits

| Tier | Requests/Minute | Recommended For |
|------|-----------------|-----------------|
| Standard | 100 | Small warehouses (< 1000 orders/day) |
| Premium | 500 | Medium warehouses (1000-5000 orders/day) |
| Enterprise | 2000 | Large warehouses (> 5000 orders/day) |

### Rate Limit Headers

Response includes rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

### Handling Rate Limits

```python
import time

def call_api_with_retry(func, max_retries=3):
    """Call API with exponential backoff on rate limit."""
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited
                retry_after = int(e.response.headers.get('Retry-After', 60))
                if attempt < max_retries - 1:
                    time.sleep(retry_after)
                    continue
            raise
```

---

## Best Practices

### 1. Caching

Cache optimization results for identical orders:

```python
import hashlib
import json

def get_cache_key(order_items):
    """Generate cache key from order items."""
    items_str = json.dumps(order_items, sort_keys=True)
    return hashlib.md5(items_str.encode()).hexdigest()

# Check cache before API call
cache_key = get_cache_key(items)
if cache_key in cache:
    return cache[cache_key]

# Call API and cache result
result = optimize_package(order_id, items)
cache[cache_key] = result
```

### 2. Batch Processing

For bulk orders, use asynchronous processing:

```python
import asyncio
import aiohttp

async def optimize_batch(orders):
    """Optimize multiple orders concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            optimize_package_async(session, order)
            for order in orders
        ]
        return await asyncio.gather(*tasks)
```

### 3. Error Monitoring

Track API errors and performance:

```python
import logging
from datetime import datetime

def log_api_call(order_id, response_time, status_code):
    """Log API call metrics."""
    logging.info(f"API Call: order={order_id}, "
                f"time={response_time}ms, status={status_code}")
    
    # Alert if response time > 1000ms
    if response_time > 1000:
        alert_ops_team(f"Slow API response: {response_time}ms")
```

### 4. Graceful Degradation

Handle API failures gracefully:

```python
def get_packaging_recommendation(order_id, items):
    """Get packaging with fallback."""
    try:
        # Try PackOptima API
        return optimize_package(order_id, items)
    except Exception as e:
        logging.error(f"PackOptima API failed: {e}")
        # Fallback to default packaging logic
        return use_default_packaging(items)
```

---

## Troubleshooting

### Issue: Slow Response Times

**Symptoms:** API calls taking > 1 second

**Possible Causes:**
1. Large number of items (> 50)
2. Complex product dimensions
3. Network latency

**Solutions:**
- Split large orders into smaller batches
- Use asynchronous endpoint for large orders
- Check network connectivity
- Contact support if persistent

### Issue: Unpacked Items

**Symptoms:** `unpacked_items` array not empty

**Possible Causes:**
1. No box large enough for item
2. Weight exceeds all box limits
3. Fragile item constraints

**Solutions:**
- Add larger boxes to inventory
- Add boxes with higher weight limits
- Check product dimensions are correct
- Review fragile/stackable settings

### Issue: Webhook Not Receiving Events

**Symptoms:** No webhook calls received

**Possible Causes:**
1. Webhook URL not accessible
2. Firewall blocking requests
3. Invalid SSL certificate
4. Webhook deactivated due to failures

**Solutions:**
- Verify webhook URL is publicly accessible
- Check firewall allows PackOptima IPs
- Ensure valid SSL certificate
- Check webhook status in dashboard
- Review webhook delivery logs

### Issue: Authentication Failures

**Symptoms:** 401 Unauthorized errors

**Possible Causes:**
1. Invalid API key
2. API key deactivated
3. Wrong authorization header format

**Solutions:**
- Verify API key is correct
- Check API key is active in dashboard
- Ensure header format: `Authorization: Bearer YOUR_KEY`
- Generate new API key if compromised

---

## Support

### Documentation
- API Reference: https://docs.packoptima.ai/api
- OpenAPI Spec: https://api.packoptima.ai/docs

### Contact
- Email: support@packoptima.ai
- Phone: +1 (555) 123-4567
- Support Portal: https://support.packoptima.ai

### SLA
- Standard: 24-hour response time
- Premium: 4-hour response time
- Enterprise: 1-hour response time + dedicated support engineer

---

## Changelog

### Version 2.0.0 (2024-01-15)
- Added warehouse integration API
- Added webhook support
- Added API key authentication
- Added rate limiting by tier

### Version 1.0.0 (2023-12-01)
- Initial release
- Basic optimization API
- JWT authentication

---

## License

© 2024 PackOptima. All rights reserved.
