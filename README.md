# PackOptima AI - Packaging Optimization SaaS Platform

Enterprise-grade AI-powered packaging optimization platform that helps businesses reduce shipping costs and improve efficiency.

## 🚀 Version 2.0 - Production Logistics Upgrade

PackOptima v2.0 introduces comprehensive enterprise features for production logistics operations:

### New in v2.0

- **🎯 Advanced Packing Engine**: 6-orientation testing with weight constraints and space utilization optimization
- **📦 Multi-Product Orders**: Bin packing algorithm for optimizing multiple products into minimum boxes
- **🚚 Shipping Cost Optimization**: Volumetric weight calculation and billable weight determination
- **⚡ Asynchronous Processing**: Redis + Celery queue system for handling large workloads
- **📊 Bulk Upload**: Process hundreds of orders via CSV upload
- **🔗 Warehouse Integration API**: RESTful API with webhooks for seamless WMS integration
- **📈 Advanced Analytics**: Time-series trends, box usage frequency, and shipping cost analysis
- **🔐 API Key Authentication**: Secure warehouse integration with rate limiting by tier
- **🔔 Webhook System**: Real-time event notifications with HMAC-SHA256 signatures
- **📉 Enhanced Dashboard**: Comprehensive analytics with space utilization and cost metrics

### Breaking Changes from v1.x

- Redis is now required for queue system
- New environment variables required (see [Migration Guide](#migration-from-v1x))
- Database schema changes (automatic via migrations)

## Features

### Core Features
- **Smart Optimization**: AI-powered algorithms to find the optimal box for each product
- **Multi-Tenant**: Secure company-based isolation for enterprise use
- **Analytics Dashboard**: Real-time insights into savings and efficiency
- **Leakage Analysis**: Identify packaging inefficiencies with Pareto charts
- **Product Management**: Complete CRUD operations for products and boxes
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Dark Theme**: Modern, WCAG AA compliant dark theme UI

### Enterprise Features (v2.0)
- **Asynchronous Task Queue**: Handle thousands of concurrent optimization requests
- **Bulk Order Processing**: Upload and process CSV files with up to 10,000 orders
- **Warehouse Integration**: RESTful API with API key authentication
- **Webhook Notifications**: Real-time event delivery with retry logic
- **Advanced Analytics**: Box usage frequency, shipping cost analysis, time-series trends
- **Rate Limiting**: Tiered rate limits (Standard: 100/min, Premium: 500/min, Enterprise: 2000/min)
- **Fragile & Stackability**: Respect product handling constraints in packing
- **Shipping Cost Calculator**: Volumetric weight and billable weight calculation

## Technology Stack

### Backend
- FastAPI 0.104.1
- PostgreSQL with SQLAlchemy ORM
- Redis 6+ (message broker and cache)
- Celery 5.3.4 (distributed task queue)
- JWT Authentication with bcrypt
- Alembic for database migrations
- Python 3.9+

### Frontend
- React 18.3.1 with TypeScript
- Vite 6.0.5
- Tailwind CSS 3.4.17
- React Router DOM 7.13.1
- Recharts for data visualization
- Axios for HTTP requests

### Infrastructure
- Prometheus (metrics collection)
- Grafana (metrics visualization)
- Sentry (error tracking)
- Nginx (load balancing)
- Supervisor/Systemd (process management)

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- Redis 6 or higher (new in v2.0)

### Quick Start (Development)

1. **Clone the repository**
```bash
git clone https://github.com/your-org/packoptima-ai-saas.git
cd packoptima-ai-saas
```

2. **Set up PostgreSQL database**
```bash
createdb packoptima_dev
```

3. **Install and start Redis**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis
```

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Update the `.env` file with your database credentials, Redis URL, and secret keys.

6. Run database migrations:
```bash
alembic upgrade head
```

7. Start the API server:
```bash
uvicorn app.main:app --reload
```

8. Start Celery worker (in a new terminal):
```bash
cd backend
source venv/bin/activate
celery -A app.core.celery_app worker --loglevel=info
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file:
```bash
cp .env.example .env
```

4. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Project Structure

```
packoptima-ai-saas/
├── backend/
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core configuration
│   │   ├── middleware/       # Custom middleware
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── main.py           # Application entry point
│   ├── tests/                # Unit tests
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── contexts/         # React contexts
│   │   ├── layout/           # Layout components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API client
│   │   └── main.tsx          # Application entry point
│   └── package.json          # Node dependencies
└── README.md
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs` - Interactive API documentation
- **ReDoc**: `http://localhost:8000/redoc` - Alternative API documentation
- **Warehouse Integration Guide**: See `docs/WAREHOUSE_INTEGRATION_GUIDE.md`
- **Deployment Guide**: See `docs/DEPLOYMENT_GUIDE.md`
- **Monitoring Setup**: See `docs/MONITORING_SETUP_GUIDE.md`

## Migration from v1.x

### Step 1: Install Redis

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis
```

### Step 2: Update Environment Variables

Add the following to your `.env` file:

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Feature Flags
ENABLE_QUEUE_SYSTEM=true
ENABLE_BULK_UPLOAD=true
ENABLE_WEBHOOKS=true
ENABLE_WAREHOUSE_API=true

# Optimization Defaults
DEFAULT_COURIER_RATE=2.5
MAX_BULK_UPLOAD_SIZE_MB=10
MAX_BULK_UPLOAD_ROWS=10000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_STANDARD_RPM=100
RATE_LIMIT_PREMIUM_RPM=500
RATE_LIMIT_ENTERPRISE_RPM=2000

# Celery Worker Configuration
CELERY_WORKER_CONCURRENCY=4
CELERY_WORKER_MAX_TASKS_PER_CHILD=1000
```

### Step 3: Run Database Migrations

```bash
cd backend
alembic upgrade head
```

This will add:
- `fragile` and `stackable` fields to products
- `max_weight_kg` and `material_type` fields to boxes
- New tables for orders, tasks, bulk uploads, webhooks, and analytics

### Step 4: Start Celery Worker

```bash
cd backend
source venv/bin/activate
celery -A app.core.celery_app worker --loglevel=info
```

### Step 5: Verify Migration

Run smoke tests to verify everything works:

```bash
cd backend
python smoke_tests/test_smoke.py
```

### Backward Compatibility

All existing API endpoints remain unchanged. New fields have default values:
- Products: `fragile=false`, `stackable=true`
- Boxes: `max_weight_kg=30.0`, `material_type="cardboard"`

You can continue using v1.x endpoints while gradually adopting v2.0 features.

## Key Endpoints

### Authentication
- `POST /auth/register` - Register new user and company
- `POST /auth/login` - Login and get JWT token

### Products
- `GET /products` - List all products
- `POST /products` - Create new product (now supports `fragile` and `stackable`)
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product

### Boxes
- `GET /boxes` - List all boxes
- `POST /boxes` - Create new box (now supports `max_weight_kg` and `material_type`)
- `PUT /boxes/{id}` - Update box
- `DELETE /boxes/{id}` - Delete box

### Optimization
- `POST /optimize` - Run packaging optimization (synchronous)
- `POST /optimize/async` - Queue optimization task (asynchronous)

### Orders (New in v2.0)
- `POST /orders` - Create multi-product order
- `GET /orders/{id}` - Get order details
- `GET /orders` - List orders with pagination
- `POST /orders/{id}/optimize` - Optimize order packing

### Tasks (New in v2.0)
- `GET /tasks/{task_id}` - Get task status
- `GET /tasks/{task_id}/result` - Get task results

### Bulk Upload (New in v2.0)
- `POST /bulk-upload` - Upload CSV file with orders
- `GET /bulk-upload/{upload_id}` - Get upload status
- `GET /bulk-upload/{upload_id}/failed` - Get failed orders

### Warehouse Integration (New in v2.0)
- `POST /api/v1/warehouse/optimize-package` - Optimize package (API key auth)
- `POST /api/v1/warehouse/webhooks` - Register webhook
- `GET /api/v1/warehouse/webhooks` - List webhooks
- `POST /api/v1/warehouse/api-keys` - Create API key
- `GET /api/v1/warehouse/api-keys` - List API keys

### Analytics
- `GET /analytics/dashboard` - Get dashboard metrics
- `GET /analytics/summary` - Get analytics summary (new in v2.0)
- `GET /analytics/box-usage` - Get box usage frequency (new in v2.0)
- `GET /analytics/shipping-cost` - Get shipping cost analytics (new in v2.0)
- `GET /analytics/trends` - Get time-series trends (new in v2.0)
- `GET /analytics/leakage` - Get leakage insights

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Build
```bash
cd frontend
npm run build
```

## Deployment

### Production Deployment

See the comprehensive [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) for detailed instructions.

**Quick Overview:**

1. **Database Migration**
```bash
./scripts/deploy_migrations.sh production
```

2. **API Server Deployment**
```bash
./scripts/deploy_api.sh production
```

3. **Celery Worker Deployment**
```bash
./scripts/deploy_workers.sh production
```

4. **Monitoring Setup**

See [Monitoring Setup Guide](docs/MONITORING_SETUP_GUIDE.md) for:
- Prometheus metrics collection
- Grafana dashboards
- Sentry error tracking
- Log aggregation
- Alerting rules

### Docker Deployment (Coming Soon)

Docker Compose configuration for easy deployment is in development.

### Rollback Procedures

If deployment fails, use rollback scripts:

```bash
# Rollback database migration
./scripts/deploy_migrations.sh production --rollback

# Rollback API deployment
./scripts/deploy_api.sh production --rollback

# Rollback worker deployment
./scripts/deploy_workers.sh production --rollback
```

## Environment Variables

### Backend (.env)

**Required Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/packoptima_db

# Redis (new in v2.0)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Security
API_SECRET_KEY=your-api-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Optional Variables:**
```bash
# Feature Flags
ENABLE_QUEUE_SYSTEM=true
ENABLE_BULK_UPLOAD=true
ENABLE_WEBHOOKS=true
ENABLE_WAREHOUSE_API=true

# Optimization
DEFAULT_COURIER_RATE=2.5
MAX_BULK_UPLOAD_SIZE_MB=10
MAX_BULK_UPLOAD_ROWS=10000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_STANDARD_RPM=100
RATE_LIMIT_PREMIUM_RPM=500
RATE_LIMIT_ENTERPRISE_RPM=2000

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

See `.env.example`, `.env.production.example`, and `.env.staging.example` for complete configuration templates.

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- API key authentication for warehouse integration (new in v2.0)
- Rate limiting by subscription tier (new in v2.0)
- CORS protection
- Security headers (HSTS, X-Frame-Options, CSP, etc.)
- Multi-tenant data isolation with company_id filtering
- HMAC-SHA256 webhook signatures (new in v2.0)
- Constant-time comparison for API keys (new in v2.0)
- Input validation with Pydantic schemas
- SQL injection protection via SQLAlchemy ORM
- TLS 1.2+ for all external communications

## Performance

- Optimized database queries with proper indexing
- Efficient pagination for large datasets
- Asynchronous task processing with Celery (new in v2.0)
- Redis caching for frequently accessed data (new in v2.0)
- Connection pooling for database and Redis
- Lazy loading for frontend components
- Response time targets:
  - Single product optimization: < 100ms
  - Multi-product order (10 items): < 500ms
  - Warehouse API: < 500ms at p95
  - Analytics queries: < 200ms at p95
  - Bulk upload (100 orders): < 30 seconds

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Documentation

- **[Warehouse Integration Guide](docs/WAREHOUSE_INTEGRATION_GUIDE.md)** - Complete guide for integrating with warehouse management systems
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment procedures and rollback strategies
- **[Monitoring Setup Guide](docs/MONITORING_SETUP_GUIDE.md)** - Prometheus, Grafana, Sentry, and alerting configuration
- **[API Documentation](http://localhost:8000/docs)** - Interactive Swagger UI (when server is running)

## Architecture

### System Components

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Nginx     │────▶│  API Servers │────▶│ PostgreSQL  │
│Load Balancer│     │  (FastAPI)   │     │  Database   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ├────────────▶ ┌─────────────┐
                           │              │    Redis    │
                           │              │ (Cache/Queue)│
                           │              └─────────────┘
                           │                     │
                           ▼                     ▼
                    ┌──────────────┐     ┌─────────────┐
                    │   Celery     │────▶│  Monitoring │
                    │   Workers    │     │(Prometheus) │
                    └──────────────┘     └─────────────┘
```

### Data Flow

1. **Synchronous Requests**: Client → Nginx → API Server → Database → Response
2. **Asynchronous Requests**: Client → API Server → Redis Queue → Celery Worker → Database
3. **Webhook Delivery**: Event → Webhook Service → External System (with retry logic)
4. **Bulk Upload**: CSV Upload → Parse → Queue Tasks → Process → Store Results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

Proprietary - All rights reserved

## Support

For support, email support@packoptima.ai or open an issue in the repository.

## Acknowledgments

- FastAPI for the excellent web framework
- React team for the amazing frontend library
- Tailwind CSS for the utility-first CSS framework
