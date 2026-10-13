# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

---

## Authentication Endpoints

### POST /auth/login
Login user and receive JWT token.

**Request Body:**
```json
{
  "email": "admin@health.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": 1,
    "username": "admin",
    "email": "admin@health.com",
    "role": "admin"
  }
}
```

### POST /auth/signup
Create new user account.

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "role": "viewer"
}
```

### GET /auth/verify-token
Verify JWT token validity.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "valid": true,
  "user": {
    "user_id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

---

## Dashboard Endpoints

### GET /dashboard/stats
Get dashboard statistics.

**Response:**
```json
{
  "stats": {
    "total_medicines": 17,
    "low_stock_count": 3,
    "pending_predictions": 15,
    "high_risk_predictions": 5,
    "pending_orders": 2,
    "total_inventory_value": 125000.50
  }
}
```

### GET /dashboard/outbreak-map
Get outbreak risk map data.

**Response:**
```json
{
  "locations": [
    {
      "location": "Mumbai",
      "state": "Maharashtra",
      "latitude": 19.0760,
      "longitude": 72.8777,
      "predictions": [...],
      "max_risk_score": 85.5,
      "total_cases": 450
    }
  ]
}
```

### GET /dashboard/inventory-status
Get inventory status overview.

**Response:**
```json
{
  "low_stock": {
    "critical": [...],
    "low": [...],
    "total_count": 5
  }
}
```

---

## Inventory Endpoints

### GET /inventory/medicines
Get all medicines.

**Response:**
```json
{
  "medicines": [
    {
      "medicine_id": 1,
      "medicine_name": "Oseltamivir",
      "disease_name": "Influenza",
      "current_stock": 2500,
      "reorder_level": 500,
      "unit_price": 150.00,
      "supplier_name": "PharmaCorp India",
      "expiry_date": "2025-11-10"
    }
  ],
  "count": 17
}
```

### GET /inventory/medicines/:id
Get specific medicine by ID.

**Response:**
```json
{
  "medicine": {
    "medicine_id": 1,
    "medicine_name": "Oseltamivir",
    ...
  }
}
```

### POST /inventory/medicines
Create new medicine (Admin/Manager only).

**Request Body:**
```json
{
  "medicine_name": "New Medicine",
  "disease_id": 1,
  "current_stock": 1000,
  "reorder_level": 200,
  "unit_price": 100.00,
  "supplier_id": 1,
  "expiry_date": "2025-12-31",
  "batch_number": "BATCH001",
  "storage_location": "Warehouse-A"
}
```

### PUT /inventory/medicines/:id
Update medicine details.

**Request Body:**
```json
{
  "current_stock": 1500,
  "unit_price": 120.00
}
```

### DELETE /inventory/medicines/:id
Delete medicine (Admin only).

### GET /inventory/low-stock
Get medicines with low stock.

**Response:**
```json
{
  "medicines": [...],
  "count": 5
}
```

### GET /inventory/expiring?days=90
Get medicines expiring within specified days.

### PUT /inventory/medicines/:id/stock
Update medicine stock.

**Request Body:**
```json
{
  "quantity": 100,
  "operation": "add"  // "add", "subtract", or "set"
}
```

---

## Predictions Endpoints

### GET /predictions/outbreaks
Get all outbreak predictions.

**Query Parameters:**
- `status` (optional): Filter by status (pending, notified, confirmed)

**Response:**
```json
{
  "predictions": [
    {
      "prediction_id": 1,
      "disease_name": "Dengue",
      "location": "Mumbai",
      "state": "Maharashtra",
      "latitude": 19.0760,
      "longitude": 72.8777,
      "predicted_date": "2024-12-15",
      "probability": 0.85,
      "severity_level": "High",
      "predicted_cases": 450,
      "risk_score": 85.0,
      "status": "pending"
    }
  ],
  "count": 15
}
```

### POST /predictions/run-prediction
Run outbreak prediction pipeline (Admin/Manager only).

**Request Body:**
```json
{
  "months_ahead": 3
}
```

**Response:**
```json
{
  "message": "Predictions generated successfully",
  "count": 50,
  "predictions": [...]
}
```

### POST /predictions/demand-forecast
Forecast medicine demand.

**Request Body:**
```json
{
  "medicine_id": 1,
  "months_ahead": 3,
  "outbreak_prediction": {
    "predicted_cases": 500
  }
}
```

**Response:**
```json
{
  "forecasts": [
    {
      "forecast_date": "2024-12-01",
      "predicted_quantity": 350,
      "lower_bound": 298,
      "upper_bound": 403,
      "confidence": 0.85
    }
  ]
}
```

### GET /predictions/reorder-recommendations
Get medicine reorder recommendations.

**Response:**
```json
{
  "recommendations": [
    {
      "medicine_id": 1,
      "medicine_name": "Oseltamivir",
      "current_stock": 450,
      "predicted_demand": 800,
      "reorder_quantity": 750,
      "urgency": "High",
      "days_until_stockout": 12
    }
  ],
  "count": 5
}
```

### GET /predictions/risk-map
Get outbreak risk map data.

---

## Orders Endpoints

### GET /orders
Get all orders.

**Query Parameters:**
- `status` (optional): Filter by status

**Response:**
```json
{
  "orders": [
    {
      "order_id": 1,
      "medicine_name": "Oseltamivir",
      "supplier_name": "PharmaCorp India",
      "quantity": 1000,
      "order_date": "2024-11-01 10:30:00",
      "expected_delivery": "2024-11-15",
      "status": "pending",
      "total_cost": 150000.00,
      "created_by_name": "admin"
    }
  ],
  "count": 10
}
```

### GET /orders/:id
Get specific order by ID.

### POST /orders/create
Create new order (Admin/Manager only).

**Request Body:**
```json
{
  "medicine_id": 1,
  "supplier_id": 1,
  "quantity": 1000,
  "lead_time_days": 14,
  "notes": "Urgent order for outbreak preparation"
}
```

**Response:**
```json
{
  "message": "Order created successfully",
  "order_id": 15
}
```

### PUT /orders/:id/status
Update order status (Admin/Manager only).

**Request Body:**
```json
{
  "status": "confirmed",
  "notify_email": "manager@health.com"
}
```

**Valid Statuses:**
- `pending`
- `confirmed`
- `shipped`
- `delivered`
- `cancelled`

### GET /orders/suppliers
Get all suppliers.

**Response:**
```json
{
  "suppliers": [
    {
      "supplier_id": 1,
      "supplier_name": "PharmaCorp India",
      "contact_email": "contact@pharmacorp.com",
      "contact_phone": "+91-9876543210",
      "rating": 4.5,
      "avg_delivery_time": 7,
      "reliability_score": 0.95
    }
  ],
  "count": 6
}
```

---

## Reports Endpoints

### GET /reports/inventory?format=pdf
Generate and download inventory report.

**Query Parameters:**
- `format`: `pdf` or `excel`

**Response:** File download (PDF or Excel)

### GET /reports/outbreak-history
Generate and download outbreak history report.

**Response:** File download (PDF)

### GET /reports/orders
Generate and download orders report.

**Response:** File download (Excel)

### POST /reports/generate-all
Generate all reports.

**Response:**
```json
{
  "message": "All reports generated successfully",
  "reports_dir": "C:/path/to/reports"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

### 401 Unauthorized
```json
{
  "error": "Token is missing"
}
```

### 403 Forbidden
```json
{
  "error": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider implementing rate limiting to prevent abuse.

---

## CORS

CORS is enabled for the following origins:
- `http://localhost:3000`
- `http://localhost:3001`
- `http://127.0.0.1:3000`

---

## Data Types

### Disease Object
```json
{
  "disease_id": 1,
  "disease_name": "Influenza",
  "symptoms": "Fever, cough, body ache",
  "severity": "Medium",
  "category": "Viral Infection"
}
```

### Medicine Object
```json
{
  "medicine_id": 1,
  "medicine_name": "Oseltamivir",
  "disease_id": 1,
  "current_stock": 2500,
  "reorder_level": 500,
  "unit_price": 150.00,
  "supplier_id": 1,
  "expiry_date": "2025-11-10",
  "batch_number": "BATCH1001",
  "storage_location": "Warehouse-A"
}
```

### Prediction Object
```json
{
  "prediction_id": 1,
  "disease_id": 1,
  "location": "Mumbai",
  "state": "Maharashtra",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "predicted_date": "2024-12-15",
  "probability": 0.85,
  "severity_level": "High",
  "predicted_cases": 450,
  "risk_score": 85.0,
  "status": "pending"
}
```

### Order Object
```json
{
  "order_id": 1,
  "medicine_id": 1,
  "supplier_id": 1,
  "quantity": 1000,
  "order_date": "2024-11-01 10:30:00",
  "expected_delivery": "2024-11-15",
  "actual_delivery": null,
  "status": "pending",
  "total_cost": 150000.00,
  "created_by": 1,
  "approved_by": null,
  "notes": "Urgent order"
}
```

---

## Testing with cURL

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@health.com","password":"admin123"}'
```

### Get Medicines (with token)
```bash
curl -X GET http://localhost:5000/api/inventory/medicines \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Run Prediction
```bash
curl -X POST http://localhost:5000/api/predictions/run-prediction \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"months_ahead":3}'
```

---

## Postman Collection

Import this collection to test all endpoints:

```json
{
  "info": {
    "name": "Health Inventory API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [],
            "body": {
              "mode": "raw",
              "raw": "{\"email\":\"admin@health.com\",\"password\":\"admin123\"}",
              "options": {
                "raw": {
                  "language": "json"
                }
              }
            },
            "url": {
              "raw": "http://localhost:5000/api/auth/login",
              "protocol": "http",
              "host": ["localhost"],
              "port": "5000",
              "path": ["api", "auth", "login"]
            }
          }
        }
      ]
    }
  ]
}
```

---

**For more information, see the main README.md and SETUP_GUIDE.md files.**
