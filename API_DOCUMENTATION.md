# PackOptima AI - API Documentation

## Base URL
```
Development: http://localhost:8000
Production: https://api.packoptima.ai
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "company_name": "Acme Corp"
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

---

### Products

#### List Products
```http
GET /products?skip=0&limit=100
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Laptop",
    "sku": "LAP-001",
    "category": "electronics",
    "length_cm": 35.0,
    "width_cm": 25.0,
    "height_cm": 3.0,
    "weight_kg": 2.5,
    "current_box_cost": 5.50,
    "company_id": 1,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

#### Create Product
```http
POST /products
```

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Laptop",
  "sku": "LAP-001",
  "category": "electronics",
  "length_cm": 35.0,
  "width_cm": 25.0,
  "height_cm": 3.0,
  "weight_kg": 2.5,
  "current_box_cost": 5.50
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "Laptop",
  "sku": "LAP-001",
  "category": "electronics",
  "length_cm": 35.0,
  "width_cm": 25.0,
  "height_cm": 3.0,
  "weight_kg": 2.5,
  "current_box_cost": 5.50,
  "company_id": 1,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Get Product
```http
GET /products/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Laptop",
  "sku": "LAP-001",
  "category": "electronics",
  "length_cm": 35.0,
  "width_cm": 25.0,
  "height_cm": 3.0,
  "weight_kg": 2.5,
  "current_box_cost": 5.50,
  "company_id": 1,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Update Product
```http
PUT /products/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Gaming Laptop",
  "sku": "LAP-001",
  "category": "electronics",
  "length_cm": 35.0,
  "width_cm": 25.0,
  "height_cm": 3.0,
  "weight_kg": 2.5,
  "current_box_cost": 5.50
}
```

**Response:** `200 OK`

#### Delete Product
```http
DELETE /products/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `204 No Content`

---

### Boxes

#### List Boxes
```http
GET /boxes
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Small Box",
    "length_cm": 30.0,
    "width_cm": 20.0,
    "height_cm": 15.0,
    "cost": 2.50,
    "company_id": 1,
    "usage_count": 45,
    "created_at": "2024-01-10T08:00:00Z"
  }
]
```

#### Create Box
```http
POST /boxes
```

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Small Box",
  "length_cm": 30.0,
  "width_cm": 20.0,
  "height_cm": 15.0,
  "cost": 2.50
}
```

**Response:** `201 Created`

#### Update Box
```http
PUT /boxes/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Small Box Updated",
  "length_cm": 30.0,
  "width_cm": 20.0,
  "height_cm": 15.0,
  "cost": 2.75
}
```

**Response:** `200 OK`

#### Delete Box
```http
DELETE /boxes/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `204 No Content`

---

### Optimization

#### Run Optimization
```http
POST /optimize
```

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "product_ids": [1, 2, 3]
}
```

**Response:** `200 OK`
```json
{
  "run_id": 1,
  "total_products": 3,
  "optimized_products": 3,
  "total_savings": 12.50,
  "results": [
    {
      "product_id": 1,
      "product_name": "Laptop",
      "current_box": "Large Box",
      "current_cost": 5.50,
      "recommended_box": "Medium Box",
      "recommended_cost": 3.50,
      "savings": 2.00
    }
  ]
}
```

---

### Analytics

#### Get Dashboard Metrics
```http
GET /analytics/dashboard
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "total_products": 150,
  "total_boxes": 12,
  "total_savings": 1250.75,
  "optimization_runs": 45,
  "avg_savings_per_run": 27.79
}
```

#### Get Leakage Insights
```http
GET /analytics/leakage
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
  {
    "product_name": "Laptop",
    "sku": "LAP-001",
    "current_box": "Large Box",
    "recommended_box": "Medium Box",
    "wasted_space_percent": 35.5,
    "potential_savings": 2.00
  }
]
```

#### Get Top Inefficient Products
```http
GET /analytics/inefficient?limit=10
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
  {
    "product_name": "Small Widget",
    "sku": "WID-001",
    "current_cost": 5.00,
    "optimal_cost": 2.00,
    "savings_potential": 3.00
  }
]
```

#### Get Savings Trends
```http
GET /analytics/trends?days=30
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
  {
    "date": "2024-01-15",
    "savings": 125.50
  },
  {
    "date": "2024-01-16",
    "savings": 98.25
  }
]
```

---

### History

#### Get Optimization History
```http
GET /history?skip=0&limit=50
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "company_id": 1,
    "total_savings": 125.50,
    "products_optimized": 25,
    "created_at": "2024-01-15T14:30:00Z"
  }
]
```

#### Get Optimization Details
```http
GET /history/{run_id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "company_id": 1,
  "total_savings": 125.50,
  "products_optimized": 25,
  "created_at": "2024-01-15T14:30:00Z",
  "results": [
    {
      "product_name": "Laptop",
      "current_box": "Large Box",
      "recommended_box": "Medium Box",
      "savings": 2.00
    }
  ]
}
```

---

### Health Check

#### Check API Health
```http
GET /health
```

**Response:** `200 OK`
```json
{
  "status": "healthy"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

- **Rate**: 60 requests per minute per IP address
- **Header**: `X-RateLimit-Remaining` shows remaining requests
- **Response**: 429 status code when limit exceeded

## Pagination

List endpoints support pagination with query parameters:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100, max: 1000)

Example:
```http
GET /products?skip=20&limit=10
```

## Categories

Valid product categories:
- `general`
- `electronics`
- `fragile`
- `clothing`
- `books`
- `toys`

## Timestamps

All timestamps are in ISO 8601 format (UTC):
```
2024-01-15T14:30:00Z
```

## Interactive Documentation

Visit these URLs when the API is running:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
