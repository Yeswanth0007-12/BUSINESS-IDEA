# Implementation Plan: Production Logistics Upgrade

## Overview

This implementation plan breaks down the comprehensive upgrade of PackOptima into 11 phases with detailed, actionable tasks. Each phase builds upon previous work to systematically transform the system from a prototype into a production-ready enterprise logistics platform.

The implementation covers enhanced data models, advanced packing algorithms, shipping cost optimization, multi-product order processing, asynchronous queue systems, bulk operations, advanced analytics, warehouse integration APIs, comprehensive testing, and production deployment.

## Tasks

### Phase 1: Enhanced Data Models

- [x] 1.1 Create database migration for enhanced product and box models
  - Create Alembic migration script `004_enhanced_data_models.py`
  - Add `fragile` BOOLEAN column to products table with default FALSE
  - Add `stackable` BOOLEAN column to products table with default TRUE
  - Add `max_weight_kg` FLOAT column to boxes table with default 30.0
  - Add `material_type` VARCHAR(50) column to boxes table with default 'cardboard'
  - Include both upgrade and downgrade methods
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 1.2 Update Product model with new fields
  - Add `fragile: bool = False` field to Product model in `backend/app/models/product.py`
  - Add `stackable: bool = True` field to Product model
  - Update model docstring to document new fields
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 1.3 Update Box model with new fields
  - Add `max_weight_kg: float = 30.0` field to Box model in `backend/app/models/box.py`
  - Add `material_type: str = "cardboard"` field to Box model
  - Update model docstring to document new fields
  - _Requirements: 2.1, 2.2, 2.3_


- [x] 1.4 Update Product schema with new fields
  - Add `fragile: bool = False` field to ProductCreate schema in `backend/app/schemas/product.py`
  - Add `stackable: bool = True` field to ProductCreate schema
  - Add same fields to ProductUpdate and ProductResponse schemas
  - Make fields optional in ProductUpdate schema
  - _Requirements: 1.3, 1.4_

- [x] 1.5 Update Box schema with new fields
  - Add `max_weight_kg: float = 30.0` field to BoxCreate schema in `backend/app/schemas/box.py`
  - Add `material_type: str = "cardboard"` field to BoxCreate schema
  - Add validation for material_type to accept only: cardboard, plastic, wood
  - Add same fields to BoxUpdate and BoxResponse schemas
  - Make fields optional in BoxUpdate schema
  - _Requirements: 2.3, 2.4_

- [x] 1.6 Run database migration and verify backward compatibility
  - Execute migration: `alembic upgrade head`
  - Verify existing products have fragile=FALSE and stackable=TRUE
  - Verify existing boxes have max_weight_kg=30.0 and material_type='cardboard'
  - Test existing API endpoints still work without new fields
  - Test creating products/boxes with new fields
  - _Requirements: 1.5, 2.5, 41.1, 41.2, 41.3_

### Phase 2: Advanced Packing Engine

- [x] 2.1 Implement 6-orientation testing algorithm
  - Create `test_all_orientations()` method in OptimizationEngine class
  - Generate all 6 possible orientations: (L,W,H), (L,H,W), (W,L,H), (W,H,L), (H,L,W), (H,W,L)
  - For each orientation, add padding and check if fits in box dimensions
  - Calculate space utilization as (product_volume / box_volume) × 100
  - Return best orientation with highest utilization and the utilization percentage
  - Return None if no orientation fits
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 2.2 Write property test for 6-orientation testing
  - **Property 1: Orientation Testing Completeness**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
  - Test that if orientation is returned, it fits in box with padding
  - Test that space_utilization is between 0 and 100
  - Use property-based testing with random product and box dimensions

- [x] 2.3 Implement weight constraint validation
  - Create `validate_weight_constraint()` method in OptimizationEngine
  - Check if product.weight_kg ≤ box.max_weight_kg
  - Return boolean result
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 2.4 Write unit tests for weight constraint validation
  - Test product weight exactly at box limit (edge case)
  - Test product weight exceeds box limit
  - Test product weight well below box limit
  - _Requirements: 4.1, 4.2, 4.3_


- [x] 2.5 Refactor find_optimal_box to use 6-orientation testing
  - Replace current dimension sorting with call to test_all_orientations()
  - Add weight constraint validation before testing orientations
  - Filter boxes by weight constraint first
  - For each suitable box, test all orientations
  - Select box with lowest cost (primary) and best utilization (secondary)
  - Return box, orientation, space_utilization, unused_volume, and reason
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 2.6 Update OptimizationResult schema with new fields
  - Add `orientation: Tuple[float, float, float]` field to OptimizationResult schema
  - Add `space_utilization: float` field
  - Add `unused_volume: float` field
  - Update response examples in schema
  - _Requirements: 5.3, 5.4_

- [ ] 2.7 Write integration tests for enhanced box selection
  - Test box selection with multiple orientations
  - Test weight constraint filtering
  - Test cost-based selection when multiple boxes fit
  - Test utilization-based tiebreaker
  - Test no suitable box scenario
  - _Requirements: 3.5, 4.3, 5.1, 5.2, 5.5_

- [x] 2.8 Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

### Phase 3: Shipping Cost Calculator

- [x] 3.1 Implement volumetric weight calculation
  - Create `calculate_volumetric_weight()` method in OptimizationEngine
  - Use formula: (length_cm × width_cm × height_cm) / 5000
  - Round result to 2 decimal places
  - Add validation that result > 0 when dimensions are positive
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 3.2 Implement billable weight calculation
  - Create `calculate_billable_weight()` method in OptimizationEngine
  - Return max(actual_weight_kg, volumetric_weight_kg)
  - Add validation that result ≥ both input weights
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 3.3 Implement shipping cost calculation
  - Create `calculate_shipping_cost()` method in OptimizationEngine
  - Calculate volumetric weight using box dimensions
  - Calculate billable weight from actual and volumetric weights
  - Multiply billable weight by courier_rate (default 2.5)
  - Round result to 2 decimal places
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 3.4 Write property test for shipping cost calculation
  - **Property 5: Shipping Cost Accuracy**
  - **Validates: Requirements 6.1, 7.1, 8.1, 8.5**
  - Test that shipping_cost = billable_weight × courier_rate
  - Test that billable_weight = max(actual_weight, volumetric_weight)
  - Use property-based testing with random dimensions and weights


- [x] 3.5 Update optimization engine to include shipping costs
  - Add courier_rate parameter to optimize_packaging() method (default 2.5)
  - Calculate shipping cost for both current and recommended boxes
  - Calculate total cost as box_cost + shipping_cost
  - Update savings calculation to include shipping cost differences
  - _Requirements: 8.4, 8.5_

- [x] 3.6 Update OptimizationResult schema with shipping fields
  - Add `shipping_cost_current: float` field to OptimizationResult
  - Add `shipping_cost_recommended: float` field
  - Add `total_cost_current: float` field (box + shipping)
  - Add `total_cost_recommended: float` field (box + shipping)
  - Add `volumetric_weight_current: float` field
  - Add `volumetric_weight_recommended: float` field
  - Add `billable_weight_current: float` field
  - Add `billable_weight_recommended: float` field
  - _Requirements: 8.4, 8.5_

- [x] 3.7 Update optimization API endpoint to accept courier_rate
  - Add optional `courier_rate: float = 2.5` to OptimizationRequest schema
  - Pass courier_rate to optimization engine
  - Update API documentation with courier_rate parameter
  - _Requirements: 8.3_

- [ ] 3.8 Write integration tests for shipping cost optimization
  - Test optimization with default courier rate
  - Test optimization with custom courier rate
  - Test that total cost includes both box and shipping costs
  - Test volumetric weight exceeds actual weight scenario
  - Test actual weight exceeds volumetric weight scenario
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 3.9 Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

### Phase 4: Multi-Product Order Packing

- [x] 4.1 Create database models for orders
  - Create Order model in `backend/app/models/order.py`
  - Fields: id, company_id, order_number, customer_name, status, created_at, completed_at
  - Add unique constraint on (company_id, order_number)
  - Create OrderItem model linking orders to products with quantity
  - Create OrderPackingResult model storing packing results per box
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 4.2 Create database migration for order tables
  - Create Alembic migration script `005_multi_product_orders.py`
  - Create orders table with all fields and constraints
  - Create order_items table with foreign keys to orders and products
  - Create order_packing_results table with packing details
  - Add indexes on company_id, order_number, and status
  - _Requirements: 9.1, 9.2, 9.3_

- [x] 4.3 Create order schemas
  - Create OrderCreate, OrderUpdate, OrderResponse schemas in `backend/app/schemas/order.py`
  - Create OrderItemCreate schema with product_id and quantity
  - Create OrderPackingResultResponse schema
  - Add validation for quantity > 0
  - Add validation for status enum values
  - _Requirements: 9.1, 9.4_


- [x] 4.4 Implement bin packing algorithm (First Fit Decreasing)
  - Create `pack_multi_product_order()` method in OptimizationEngine
  - Expand order items to individual products based on quantity
  - Sort products by volume in descending order
  - Implement First Fit Decreasing: try existing boxes first, then new box
  - Track remaining space and current weight per box
  - Return list of boxes used, total boxes, total cost, success flag, unpacked items
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 4.5 Implement space tracking for multi-product packing
  - Create `can_fit_in_box()` method to check if item fits in current box state
  - Check weight constraint: new_weight ≤ box.max_weight_kg
  - Check fragile constraint: don't stack fragile items
  - Check stackability constraint: don't stack non-stackable items
  - Check volume constraint: item_volume ≤ remaining_space
  - Return boolean result
  - _Requirements: 11.1, 11.2, 11.3, 12.1, 12.2, 12.3_

- [x] 4.6 Implement fragile item handling
  - In can_fit_in_box(), check if item is fragile
  - If item is fragile and box has items, return false
  - If box has fragile items and adding new item, return false
  - Create helper method `has_fragile_items()` to check box state
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [x] 4.7 Implement stackability constraints
  - In can_fit_in_box(), check if item is stackable
  - If item is not stackable and box has items, return false
  - If box has non-stackable items and adding new item, return false
  - _Requirements: 12.1, 12.2, 12.3, 12.4_

- [ ] 4.8 Write property test for bin packing algorithm
  - **Property 4: Bin Packing Completeness**
  - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**
  - Test that all items are either packed or in unpacked_items
  - Test that success=true implies unpacked_items is empty
  - Test that success=false implies unpacked_items is not empty

- [ ] 4.9 Write property test for fragile item safety
  - **Property 7: Fragile Item Safety**
  - **Validates: Requirements 11.1, 11.2, 11.3**
  - Test that boxes with fragile items contain only one product
  - Use property-based testing with random orders containing fragile items

- [ ] 4.10 Write unit tests for multi-product packing
  - Test packing order with all items fitting
  - Test packing order with some items not fitting
  - Test fragile items packed separately
  - Test non-stackable items packed separately
  - Test weight constraint prevents overpacking
  - Test volume sorting (largest first)
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 11.1, 11.2, 11.3, 12.1, 12.2, 12.3_

- [x] 4.11 Create order service layer
  - Create `backend/app/services/order_service.py`
  - Implement create_order() method
  - Implement get_order() method with company_id filtering
  - Implement list_orders() method with pagination
  - Implement optimize_order_packing() method calling bin packing algorithm
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_


- [x] 4.12 Create order API endpoints
  - Create `backend/app/api/orders.py` router
  - POST /api/v1/orders - Create new order
  - GET /api/v1/orders/{order_id} - Get order details
  - GET /api/v1/orders - List orders with pagination
  - POST /api/v1/orders/{order_id}/optimize - Optimize order packing
  - Add company_id filtering for multi-tenant isolation
  - Add authentication requirements
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 4.13 Register order router in main application
  - Import orders router in `backend/app/main.py`
  - Add `app.include_router(orders.router)` to mount endpoints
  - _Requirements: 9.1_

- [ ] 4.14 Write integration tests for order API
  - Test creating order with multiple items
  - Test optimizing order packing
  - Test retrieving order details
  - Test listing orders with pagination
  - Test multi-tenant isolation (can't access other company's orders)
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 4.15 Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

### Phase 5: Queue System Architecture

- [x] 5.1 Install Redis and Celery dependencies
  - Add `redis==5.0.1` to requirements.txt
  - Add `celery==5.3.4` to requirements.txt
  - Add `flower==2.0.1` to requirements.txt (Celery monitoring)
  - Run `pip install -r requirements.txt`
  - _Requirements: 13.1, 13.2_

- [x] 5.2 Configure Redis connection
  - Add REDIS_URL to environment variables in `.env`
  - Add CELERY_BROKER_URL to environment variables
  - Add CELERY_RESULT_BACKEND to environment variables
  - Update `backend/app/core/config.py` to load Redis settings
  - _Requirements: 13.1, 35.2_

- [x] 5.3 Create Celery application configuration
  - Create `backend/app/core/celery_app.py`
  - Initialize Celery with Redis broker and result backend
  - Configure task serialization (JSON)
  - Configure result expiration (24 hours)
  - Configure task routing and priorities
  - _Requirements: 13.2, 13.3_

- [x] 5.4 Create optimization task status model
  - Create OptimizationTask model in `backend/app/models/optimization_task.py`
  - Fields: id (UUID), company_id, task_type, status, progress, created_at, started_at, completed_at, result_id, error_message, metadata
  - Add status enum: pending, processing, completed, failed
  - Add indexes on (company_id, status) and created_at
  - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [x] 5.5 Create database migration for task tracking
  - Create Alembic migration script `006_optimization_tasks.py`
  - Create optimization_tasks table with UUID primary key
  - Add foreign key to optimization_runs table
  - Add indexes for efficient querying
  - _Requirements: 14.1, 14.2, 14.3_


- [x] 5.6 Create task status schemas
  - Create TaskStatusResponse schema in `backend/app/schemas/task.py`
  - Include task_id, status, progress, created_at, completed_at, result_id, error_message
  - Create TaskSubmitResponse schema with task_id
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 5.7 Implement Celery task for optimization
  - Create `backend/app/tasks/optimization_tasks.py`
  - Implement `optimize_packaging_task()` as Celery task
  - Update task status to "processing" at start
  - Call OptimizationEngine.optimize_packaging()
  - Store result in database and link to task
  - Update task status to "completed" on success
  - Update task status to "failed" with error message on failure
  - Update progress at key milestones (0%, 25%, 75%, 100%)
  - _Requirements: 13.3, 13.4, 14.1, 14.2, 14.3, 14.4, 15.1, 15.2_

- [x] 5.8 Create async optimization API endpoint
  - Add POST /api/v1/optimize/async endpoint in optimization router
  - Create task record with status "pending"
  - Queue Celery task with task_id
  - Return HTTP 202 Accepted with task_id
  - _Requirements: 13.3, 13.4, 13.5_

- [x] 5.9 Create task status API endpoint
  - Add GET /api/v1/tasks/{task_id} endpoint
  - Query task status from database
  - If completed, include result_id and link to results
  - If failed, include error_message
  - Return HTTP 404 if task not found
  - _Requirements: 14.5, 15.4, 15.5_

- [x] 5.10 Create task result retrieval endpoint
  - Add GET /api/v1/tasks/{task_id}/result endpoint
  - Check task status is "completed"
  - Retrieve optimization result from database using result_id
  - Return full optimization summary
  - Return HTTP 404 if task not found or not completed
  - _Requirements: 15.1, 15.2, 15.3, 15.4_

- [ ] 5.11 Write integration tests for queue system
  - Test submitting async optimization task
  - Test querying task status
  - Test retrieving task results
  - Test task not found scenario
  - Test task failure handling
  - _Requirements: 13.3, 13.4, 13.5, 14.1, 14.2, 14.3, 14.4, 14.5, 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 5.12 Create Celery worker startup script
  - Create `backend/start_worker.sh` script
  - Command: `celery -A app.core.celery_app worker --loglevel=info`
  - Make script executable
  - Document worker startup in README
  - _Requirements: 13.2_

- [x] 5.13 Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

### Phase 6: Bulk Order Processing

- [x] 6.1 Create bulk upload models
  - Create BulkUpload model in `backend/app/models/bulk_upload.py`
  - Fields: id, company_id, filename, total_orders, processed_orders, failed_orders, status, created_at, completed_at
  - Create BulkUploadOrder model linking uploads to individual orders
  - Fields: id, upload_id, row_number, order_data (JSON), status, task_id, error_message
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 18.1, 18.2, 18.3, 18.4_


- [x] 6.2 Create database migration for bulk uploads
  - Create Alembic migration script `007_bulk_uploads.py`
  - Create bulk_uploads table with status tracking
  - Create bulk_upload_orders table with order details and task links
  - Add indexes on upload_id and status
  - _Requirements: 17.1, 17.2, 17.3_

- [x] 6.3 Create bulk upload schemas
  - Create BulkUploadResponse schema in `backend/app/schemas/bulk_upload.py`
  - Create BulkUploadSummary schema with counts and task_ids
  - Create BulkUploadOrderResponse schema for failed order details
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 18.5_

- [x] 6.4 Implement CSV parsing and validation
  - Create `parse_bulk_upload_csv()` function in bulk upload service
  - Validate CSV has required headers: order_number, customer_name, product_sku, quantity
  - Parse CSV rows and validate data types
  - Group rows by order_number to create complete orders
  - Return list of order dictionaries
  - Raise validation error if CSV is malformed
  - _Requirements: 16.1, 16.2, 16.3, 16.4_

- [x] 6.5 Implement bulk upload processing algorithm
  - Create `process_bulk_upload()` method in bulk upload service
  - Parse and validate CSV file
  - Create bulk_upload record with total_orders count
  - For each order: validate SKUs exist, create order record, queue optimization task
  - Track successful and failed orders
  - Create bulk_upload_order records for each order
  - Update bulk_upload with processed_orders and failed_orders counts
  - Return summary with task_ids
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 17.1, 17.2, 17.3, 17.4, 17.5, 18.1, 18.2, 18.3_

- [x] 6.6 Create bulk upload service layer
  - Create `backend/app/services/bulk_upload_service.py`
  - Implement parse_bulk_upload_csv() method
  - Implement process_bulk_upload() method
  - Implement get_bulk_upload_status() method
  - Implement get_failed_orders() method
  - _Requirements: 16.1, 16.2, 16.3, 17.1, 18.5_

- [x] 6.7 Create bulk upload API endpoints
  - Create `backend/app/api/bulk_upload.py` router
  - POST /api/v1/bulk-upload - Upload CSV file (multipart/form-data)
  - GET /api/v1/bulk-upload/{upload_id} - Get upload status
  - GET /api/v1/bulk-upload/{upload_id}/failed - Get failed orders
  - Add file size validation (max 10 MB)
  - Add row count validation (max 10,000 rows)
  - Add company_id filtering for multi-tenant isolation
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 17.1, 17.2, 17.3, 17.4, 17.5, 18.5_

- [x] 6.8 Register bulk upload router in main application
  - Import bulk_upload router in `backend/app/main.py`
  - Add `app.include_router(bulk_upload.router)` to mount endpoints
  - _Requirements: 16.1_

- [ ] 6.9 Write unit tests for CSV parsing
  - Test valid CSV with multiple orders
  - Test CSV with missing required columns
  - Test CSV with invalid data types
  - Test CSV grouping by order_number
  - Test empty CSV file
  - _Requirements: 16.1, 16.2, 16.3, 16.4_


- [ ] 6.10 Write property test for bulk upload accounting
  - **Property 10: Bulk Upload Accounting**
  - **Validates: Requirements 17.1, 17.2, 17.3, 18.1, 18.2**
  - Test that total_orders = processed_orders + failed_orders
  - Test that counts are non-negative
  - Use property-based testing with random CSV data

- [ ] 6.11 Write integration tests for bulk upload
  - Test uploading valid CSV file
  - Test uploading CSV with some invalid orders
  - Test retrieving upload status
  - Test retrieving failed orders
  - Test file size limit enforcement
  - Test row count limit enforcement
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 17.1, 17.2, 17.3, 17.4, 17.5, 18.1, 18.2, 18.3, 18.4, 18.5_

- [x] 6.12 Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

### Phase 7: Advanced Analytics

- [x] 7.1 Create analytics data models
  - Create AnalyticsSnapshot model in `backend/app/models/analytics_snapshot.py`
  - Fields: id, company_id, snapshot_date, total_products, total_boxes, total_optimizations, avg_space_utilization, total_monthly_savings, total_annual_savings
  - Create BoxUsageMetrics model with usage tracking per box
  - Create ShippingCostMetrics model with shipping cost analysis
  - Add unique constraint on (company_id, snapshot_date) for snapshots
  - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5_

- [x] 7.2 Create database migration for analytics tables
  - Create Alembic migration script `008_analytics_tables.py`
  - Create analytics_snapshots table
  - Create box_usage_metrics table
  - Create shipping_cost_metrics table
  - Add indexes on company_id and date fields
  - _Requirements: 23.1, 23.2, 23.3_

- [x] 7.3 Implement space utilization analytics
  - Create `calculate_space_utilization_metrics()` method in analytics service
  - Query optimization results for date range
  - Calculate average, min, max space utilization
  - Calculate waste percentage as 100 - avg_utilization
  - Return metrics dictionary
  - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_

- [ ] 7.4 Write property test for analytics consistency
  - **Property 8: Analytics Consistency**
  - **Validates: Requirements 19.1, 19.2, 19.3, 19.4**
  - Test that waste_percentage = 100 - avg_utilization
  - Test that avg_utilization is between 0 and 100
  - Use property-based testing with random optimization results

- [x] 7.5 Implement box usage frequency analysis
  - Create `analyze_box_usage_frequency()` method in analytics service
  - Query optimization results for date range
  - Count usage per box_id
  - Calculate total cost per box (usage_count × cost_per_unit)
  - Calculate percentage of total usage
  - Sort by usage_count descending
  - Return list of box usage data
  - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5_

- [x] 7.6 Implement shipping cost analytics
  - Create `calculate_shipping_cost_metrics()` method in analytics service
  - Query optimization results for date range
  - Calculate total shipping costs
  - Calculate average billable weight
  - Calculate percentage where volumetric weight > actual weight
  - Calculate average shipping cost per order
  - Return shipping metrics dictionary
  - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5_


- [x] 7.7 Implement time-series trend analysis
  - Create `calculate_savings_trend()` method in analytics service
  - For each month in specified range, query optimization runs
  - Calculate total savings, optimization count, average savings per optimization
  - Return list of monthly trend data in chronological order
  - Support querying up to 12 months of data
  - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5_

- [x] 7.8 Implement daily snapshot generation
  - Create `generate_daily_snapshot()` method in analytics service
  - Count total products, boxes, optimizations for company
  - Calculate average space utilization from recent optimizations
  - Calculate total monthly and annual savings
  - Create or update analytics_snapshot record for today
  - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5_

- [x] 7.9 Create analytics service layer
  - Create `backend/app/services/analytics_service_v2.py` (to avoid conflict with existing)
  - Implement all analytics calculation methods
  - Add company_id filtering for multi-tenant isolation
  - Add date range validation
  - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 20.1, 20.2, 20.3, 20.4, 20.5, 21.1, 21.2, 21.3, 21.4, 21.5, 22.1, 22.2, 22.3, 22.4, 22.5_

- [ ] 7.10 Write unit tests for analytics calculations
  - Test space utilization with empty results
  - Test space utilization with multiple results
  - Test box usage frequency calculation
  - Test shipping cost metrics calculation
  - Test trend analysis for multiple months
  - Test daily snapshot generation
  - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 20.1, 20.2, 20.3, 20.4, 20.5, 21.1, 21.2, 21.3, 21.4, 21.5, 22.1, 22.2, 22.3, 22.4, 22.5, 23.1, 23.2, 23.3, 23.4, 23.5_

- [x] 7.11 Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

### Phase 8: Enhanced Dashboard APIs

- [x] 8.1 Create analytics summary API endpoint
  - Add GET /api/v1/analytics/summary endpoint
  - Accept optional period parameter (days, default 30)
  - Return total products, boxes, optimizations
  - Return total monthly and annual savings
  - Return average space utilization and waste percentage
  - Target response time: < 200ms at p95
  - _Requirements: 24.1, 24.2, 24.3, 24.4, 24.5_

- [x] 8.2 Create box usage API endpoint
  - Add GET /api/v1/analytics/box-usage endpoint
  - Accept optional start_date and end_date parameters
  - Return box usage frequency data sorted by usage_count
  - Include box_id, box_name, usage_count, total_cost, percentage, avg_utilization
  - Target response time: < 200ms at p95
  - _Requirements: 25.1, 25.2, 25.3, 25.4, 25.5_

- [x] 8.3 Create shipping cost API endpoint
  - Add GET /api/v1/analytics/shipping-cost endpoint
  - Accept optional period parameter (days, default 30)
  - Return total shipments, total cost, average cost per order
  - Return average billable weight and volumetric weight percentage
  - Target response time: < 200ms at p95
  - _Requirements: 26.1, 26.2, 26.3, 26.4, 26.5_

- [x] 8.4 Create trends API endpoint
  - Add GET /api/v1/analytics/trends endpoint
  - Accept months parameter (1-12, default 6)
  - Return monthly trend data in chronological order
  - Include month, total_savings, optimization_count, avg_savings_per_optimization
  - Target response time: < 200ms at p95
  - _Requirements: 27.1, 27.2, 27.3, 27.4, 27.5_


- [x] 8.5 Update analytics router with new endpoints
  - Update `backend/app/api/analytics.py` with new endpoints
  - Add company_id filtering for all endpoints
  - Add authentication requirements
  - Add response schemas for all endpoints
  - Update API documentation
  - _Requirements: 24.1, 25.1, 26.1, 27.1_

- [ ] 8.6 Write integration tests for analytics APIs
  - Test summary endpoint with default and custom periods
  - Test box usage endpoint with date range filtering
  - Test shipping cost endpoint
  - Test trends endpoint with different month ranges
  - Test multi-tenant isolation
  - Test response time performance
  - _Requirements: 24.1, 24.2, 24.3, 24.4, 24.5, 25.1, 25.2, 25.3, 25.4, 25.5, 26.1, 26.2, 26.3, 26.4, 26.5, 27.1, 27.2, 27.3, 27.4, 27.5_

- [x] 8.7 Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

### Phase 9: Warehouse Integration API

- [x] 9.1 Create API key model
  - Create ApiKey model in `backend/app/models/api_key.py`
  - Fields: id, company_id, key_hash, name, created_at, last_used_at, is_active
  - Store SHA-256 hash of API key, not plaintext
  - _Requirements: 29.1, 29.2, 29.3_

- [x] 9.2 Create webhook models
  - Create Webhook model in `backend/app/models/webhook.py`
  - Fields: id, company_id, url, events (JSON), secret, is_active, created_at
  - Create WebhookDelivery model for tracking deliveries
  - Fields: id, webhook_id, event, payload (JSON), status, response_code, response_body, created_at, delivered_at
  - _Requirements: 31.1, 31.2, 31.3, 31.4, 31.5, 32.1, 32.2, 32.3, 32.4_

- [x] 9.3 Create database migration for warehouse integration
  - Create Alembic migration script `009_warehouse_integration.py`
  - Create api_keys table with key_hash column
  - Create webhooks table with URL and events
  - Create webhook_deliveries table with delivery tracking
  - Add indexes on company_id, webhook_id, and created_at
  - _Requirements: 29.1, 31.1, 32.1_

- [x] 9.4 Create warehouse integration schemas
  - Create WarehouseOptimizationRequest schema in `backend/app/schemas/warehouse.py`
  - Include order_id, items (SKU, quantity, dimensions, weight), shipping_address
  - Create WarehouseOptimizationResponse schema
  - Include optimization_id, boxes_required, total_boxes, total_cost, estimated_shipping_cost
  - Create WebhookCreate, WebhookResponse schemas
  - Create WebhookPayload schema for event notifications
  - _Requirements: 28.1, 28.2, 28.3, 28.4, 31.1, 31.2, 31.3_

- [x] 9.5 Implement API key authentication
  - Create `authenticate_api_key()` function in auth service
  - Hash provided API key using SHA-256
  - Query database for matching key_hash and company_id
  - Use constant-time comparison to prevent timing attacks
  - Update last_used_at timestamp on successful authentication
  - Return 401 Unauthorized if key invalid or inactive
  - _Requirements: 29.1, 29.2, 29.3, 29.4, 29.5_

- [x] 9.6 Implement API key generation
  - Create `generate_api_key()` function in auth service
  - Generate random 32-byte key using secrets module
  - Encode as base64 string
  - Hash with SHA-256 before storing
  - Return plaintext key to user (only shown once)
  - _Requirements: 29.1, 29.2_


- [x] 9.7 Implement rate limiting for warehouse API
  - Create rate limiter using Redis
  - Track request count per API key per minute
  - Standard tier: 100 requests/minute
  - Premium tier: 500 requests/minute
  - Return 429 Too Many Requests when limit exceeded
  - Include Retry-After header in response
  - _Requirements: 30.1, 30.2, 30.3, 30.4, 30.5_

- [x] 9.8 Create warehouse optimization endpoint
  - Add POST /api/v1/warehouse/optimize-package endpoint
  - Accept WarehouseOptimizationRequest with order details
  - Validate all SKUs exist in company's product catalog
  - Call multi-product packing algorithm
  - Calculate shipping costs for each box
  - Return WarehouseOptimizationResponse with boxes and costs
  - Target response time: < 500ms at p95
  - _Requirements: 28.1, 28.2, 28.3, 28.4, 28.5_

- [x] 9.9 Implement webhook registration endpoint
  - Add POST /api/v1/warehouse/webhooks endpoint
  - Accept webhook URL, event types, and secret
  - Validate URL is HTTPS endpoint
  - Validate event types are supported
  - Store webhook configuration with is_active=true
  - Return webhook ID and configuration
  - _Requirements: 31.1, 31.2, 31.3, 31.4, 31.5_

- [x] 9.10 Implement webhook signature generation
  - Create `generate_webhook_signature()` function
  - Use HMAC-SHA256 with webhook secret
  - Include timestamp in payload to prevent replay attacks
  - Return signature as hex string
  - _Requirements: 33.1, 33.2, 33.3, 33.4_

- [x] 9.11 Implement webhook delivery system
  - Create `deliver_webhook()` function in webhook service
  - Generate HMAC-SHA256 signature for payload
  - Send HTTP POST to webhook URL with signature header
  - Record delivery attempt in webhook_deliveries table
  - Retry up to 3 times with exponential backoff on failure
  - Mark webhook as inactive after repeated failures
  - _Requirements: 32.1, 32.2, 32.3, 32.4, 32.5_

- [x] 9.12 Implement webhook event triggers
  - Trigger "optimization.completed" event when optimization succeeds
  - Trigger "optimization.failed" event when optimization fails
  - Include optimization_id, order_id, status, and result in payload
  - Call deliver_webhook() for all active webhooks subscribed to event
  - _Requirements: 31.3, 32.1, 32.2_

- [x] 9.13 Create warehouse integration service layer
  - Create `backend/app/services/warehouse_service.py`
  - Implement optimize_package() method
  - Implement webhook registration and management methods
  - Implement webhook delivery with retry logic
  - _Requirements: 28.1, 31.1, 32.1_

- [x] 9.14 Create warehouse API router
  - Create `backend/app/api/warehouse.py` router
  - Add optimize-package endpoint
  - Add webhook registration endpoints
  - Add API key authentication dependency
  - Add rate limiting middleware
  - _Requirements: 28.1, 29.1, 30.1, 31.1_

- [x] 9.15 Register warehouse router in main application
  - Import warehouse router in `backend/app/main.py`
  - Add `app.include_router(warehouse.router)` to mount endpoints
  - _Requirements: 28.1_


- [x] 9.16 Write unit tests for API key authentication
  - Test valid API key authentication
  - Test invalid API key rejection
  - Test inactive API key rejection
  - Test constant-time comparison
  - Test last_used_at timestamp update
  - _Requirements: 29.1, 29.2, 29.3, 29.4, 29.5_

- [x] 9.17 Write unit tests for webhook signature
  - Test signature generation
  - Test signature verification
  - Test timestamp validation
  - Test replay attack prevention
  - _Requirements: 33.1, 33.2, 33.3, 33.4_

- [ ]* 9.18 Write integration tests for warehouse API
  - Test warehouse optimization endpoint
  - Test API key authentication
  - Test rate limiting enforcement
  - Test webhook registration
  - Test webhook delivery
  - Test webhook retry logic
  - Test webhook signature validation
  - _Requirements: 28.1, 28.2, 28.3, 28.4, 28.5, 29.1, 29.2, 29.3, 29.4, 29.5, 30.1, 30.2, 30.3, 30.4, 30.5, 31.1, 31.2, 31.3, 31.4, 31.5, 32.1, 32.2, 32.3, 32.4, 32.5, 33.1, 33.2, 33.3, 33.4_

- [x] 9.19 Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

### Phase 10: Testing & Validation

- [x] 10.1 Set up property-based testing framework
  - Install `hypothesis==6.92.0` for property-based testing
  - Create test configuration in `backend/tests/conftest.py`
  - Configure Hypothesis settings (max examples, deadline)
  - _Requirements: 43.1, 43.2, 43.3, 43.4, 43.5_

- [x] 10.2 Create comprehensive unit test suite
  - Ensure all algorithms have unit tests
  - Test edge cases: zero dimensions, maximum values, boundary conditions
  - Test error handling: invalid inputs, missing data, constraint violations
  - Target: > 85% code coverage
  - _Requirements: 43.1, 43.2, 43.3, 43.4, 43.5_

- [ ]* 10.3 Write property tests for correctness properties
  - **Property 1: Orientation Testing Completeness** (if not already done in 2.2)
  - **Property 2: Weight Constraint Enforcement**
  - **Property 3: Cost Optimality**
  - **Property 6: Space Utilization Bounds**
  - **Property 9: Queue Task Uniqueness**
  - Test all universal quantification properties from design
  - _Requirements: 43.1, 43.2, 43.3, 43.4, 43.5_

- [x] 10.4 Create integration test suite
  - Test complete optimization workflows end-to-end
  - Test multi-product order processing
  - Test bulk upload processing
  - Test queue system integration
  - Test webhook delivery
  - Test multi-tenant isolation
  - _Requirements: 43.1, 43.2, 43.3, 43.4, 43.5_

- [x] 10.5 Create performance benchmark tests
  - Test single product optimization < 100ms
  - Test multi-product order (10 items) < 500ms
  - Test bulk upload (100 orders) < 30 seconds
  - Test analytics queries < 200ms
  - Test warehouse API < 500ms at p95
  - _Requirements: 43.1, 43.2, 43.3, 43.4, 43.5_

- [x] 10.6 Create load testing scripts
  - Create locust or k6 load test scripts
  - Scenario 1: 100 concurrent users, 10 requests each
  - Scenario 2: 10 concurrent bulk uploads, 500 orders each
  - Scenario 3: 50 concurrent dashboard loads
  - Measure response times, error rates, throughput
  - _Requirements: 43.1, 43.2, 43.3, 43.4, 43.5_


- [x] 10.7 Run load tests and validate performance
  - Execute all load testing scenarios
  - Verify p95 response times meet targets
  - Verify no memory leaks during sustained load
  - Verify error rate < 0.1%
  - Document performance results
  - _Requirements: 43.1, 43.2, 43.3, 43.4, 43.5_

- [x] 10.8 Perform security validation
  - Run security scanner (bandit, safety) on codebase
  - Verify zero critical vulnerabilities
  - Test multi-tenant isolation (can't access other company data)
  - Test input validation on all endpoints
  - Test API key encryption at rest
  - Test webhook secret encryption at rest
  - Verify TLS 1.2+ for all external communications
  - _Requirements: 44.1, 44.2, 44.3, 44.4, 44.5_

- [x] 10.9 Create smoke test suite
  - Test all critical endpoints respond
  - Test database connectivity
  - Test Redis connectivity
  - Test Celery worker health
  - Create script for post-deployment verification
  - _Requirements: 38.1, 38.2, 38.3, 38.4, 38.5, 45.5_

- [x] 10.10 Write end-to-end workflow tests
  - Test complete user journey: create products → create boxes → optimize → view results
  - Test complete order journey: create order → optimize packing → view results
  - Test complete bulk upload journey: upload CSV → track progress → view results
  - Test complete warehouse integration: authenticate → optimize → receive webhook
  - _Requirements: 43.1, 43.2, 43.3, 43.4, 43.5_

- [x] 10.11 Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

### Phase 11: Documentation & Deployment

- [x] 11.1 Generate OpenAPI/Swagger documentation
  - Ensure all endpoints have docstrings
  - Ensure all schemas have descriptions and examples
  - Verify /docs endpoint displays complete API documentation
  - Add authentication requirements to documentation
  - Add error codes and responses to documentation
  - _Requirements: 39.1, 39.2, 39.3, 39.4, 39.5_

- [x] 11.2 Create warehouse integration guide
  - Document API key generation and authentication
  - Document webhook registration and configuration
  - Document rate limiting details and tier limits
  - Provide code examples in Python, JavaScript, and cURL
  - Document error codes and troubleshooting steps
  - Create step-by-step integration tutorial
  - _Requirements: 40.1, 40.2, 40.3, 40.4, 40.5_

- [x] 11.3 Create deployment guide
  - Document environment variable configuration
  - Document database migration process
  - Document Redis setup and configuration
  - Document Celery worker deployment
  - Document rolling update procedure
  - Document rollback procedure
  - _Requirements: 35.1, 35.2, 35.3, 35.4, 35.5, 42.1, 42.2, 42.3, 42.4, 42.5, 45.1, 45.2, 45.3, 45.4_

- [x] 11.4 Create monitoring and alerting setup guide
  - Document Prometheus metrics configuration
  - Document Sentry error tracking setup
  - Document alerting rules and thresholds
  - Document health check endpoints
  - Document log aggregation setup
  - _Requirements: 36.1, 36.2, 36.3, 36.4, 36.5, 37.1, 37.2, 37.3, 37.4, 37.5, 38.1, 38.2, 38.3, 38.4, 38.5_


- [x] 11.5 Set up monitoring infrastructure
  - Install and configure Prometheus for metrics collection
  - Install and configure Grafana for metrics visualization
  - Create dashboards for API performance, queue metrics, database metrics
  - Configure Sentry for error tracking
  - Set up log aggregation (ELK stack or similar)
  - _Requirements: 36.1, 36.2, 36.3, 36.4, 36.5, 37.1, 37.2, 37.3, 37.4, 37.5_

- [x] 11.6 Configure alerting rules
  - Alert on API p95 > 1 second
  - Alert on queue depth > 1000 tasks
  - Alert on error rate > 5%
  - Alert on database connections > 80% of pool
  - Alert on Celery worker down
  - Alert on Redis memory > 80%
  - _Requirements: 36.1, 36.2, 36.3, 36.4, 36.5_

- [x] 11.7 Create database migration deployment script
  - Create `deploy_migrations.sh` script
  - Backup database before migration
  - Run `alembic upgrade head`
  - Verify migration success
  - Rollback on failure
  - _Requirements: 34.1, 34.2, 34.3, 34.4, 34.5, 45.1_

- [x] 11.8 Create API server deployment script
  - Create `deploy_api.sh` script
  - Build Docker image or prepare deployment package
  - Deploy to servers with rolling update
  - Verify health checks pass
  - Rollback on failure
  - _Requirements: 45.2, 45.4_

- [x] 11.9 Create Celery worker deployment script
  - Create `deploy_workers.sh` script
  - Deploy worker processes to servers
  - Verify workers connect to Redis
  - Verify workers can process tasks
  - _Requirements: 45.3_

- [x] 11.10 Create environment configuration templates
  - Create `.env.example` with all required variables
  - Create `.env.production.example` with production settings
  - Create `.env.staging.example` with staging settings
  - Document each environment variable
  - _Requirements: 35.1, 35.2, 35.3, 35.4, 35.5_

- [x] 11.11 Update main README with upgrade information
  - Document new features and capabilities
  - Document breaking changes (if any)
  - Document migration path from previous version
  - Document new environment variables
  - Document new dependencies (Redis, Celery)
  - Link to integration guide and deployment guide
  - _Requirements: 41.1, 41.2, 41.3, 41.4, 41.5_

- [x] 11.12 Create rollback procedures documentation
  - Document database migration rollback steps
  - Document feature flag configuration for disabling new features
  - Document fallback to synchronous processing
  - Document data preservation guarantees
  - _Requirements: 42.1, 42.2, 42.3, 42.4, 42.5_

- [x] 11.13 Perform staging deployment
  - Deploy to staging environment
  - Run smoke tests
  - Run integration tests against staging
  - Verify monitoring and alerting working
  - Test rollback procedure
  - _Requirements: 45.1, 45.2, 45.3, 45.4, 45.5_

- [x] 11.14 Perform production deployment
  - Schedule maintenance window (if needed)
  - Backup production database
  - Deploy database migrations
  - Deploy API servers with rolling update
  - Deploy Celery workers
  - Run smoke tests
  - Monitor error rates and performance
  - Verify zero downtime achieved
  - _Requirements: 45.1, 45.2, 45.3, 45.4, 45.5_


- [x] 11.15 Post-deployment validation
  - Monitor system for 24 hours
  - Verify all metrics within normal ranges
  - Verify no increase in error rates
  - Verify performance targets met
  - Collect user feedback
  - Document any issues and resolutions
  - _Requirements: 43.1, 43.2, 43.3, 43.4, 43.5, 44.1, 44.2, 44.3, 44.4, 44.5_

- [x] 11.16 Final checkpoint - Production validation complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at the end of each phase
- Property tests validate universal correctness properties from the design
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows
- All database migrations include both upgrade and downgrade methods
- Multi-tenant isolation (company_id filtering) is enforced throughout
- Backward compatibility is maintained for existing API endpoints
- Performance targets are validated through load testing
- Security validation ensures production-ready quality

## Implementation Timeline

- Phase 1: Enhanced Data Models (1-2 days)
- Phase 2: Advanced Packing Engine (3-4 days)
- Phase 3: Shipping Cost Calculator (2-3 days)
- Phase 4: Multi-Product Order Packing (4-5 days)
- Phase 5: Queue System Architecture (3-4 days)
- Phase 6: Bulk Order Processing (3-4 days)
- Phase 7: Advanced Analytics (3-4 days)
- Phase 8: Enhanced Dashboard APIs (2-3 days)
- Phase 9: Warehouse Integration API (4-5 days)
- Phase 10: Testing & Validation (5-7 days)
- Phase 11: Documentation & Deployment (3-4 days)

Total Estimated Timeline: 33-45 days (6-9 weeks)

## Dependencies

- Phase 2 depends on Phase 1 (enhanced data models)
- Phase 3 depends on Phase 2 (advanced packing engine)
- Phase 4 depends on Phases 2 and 3 (packing and shipping)
- Phase 6 depends on Phases 4 and 5 (orders and queue system)
- Phase 7 depends on Phases 2, 3, and 4 (optimization results)
- Phase 8 depends on Phase 7 (analytics calculations)
- Phase 9 depends on Phases 4 and 5 (orders and async processing)
- Phase 10 depends on all previous phases (comprehensive testing)
- Phase 11 depends on Phase 10 (validated system ready for deployment)

## Parallel Development Opportunities

- Phases 2 and 5 can be developed in parallel (packing engine and queue system)
- Phases 7 and 9 can be developed in parallel (analytics and warehouse API)
- Phase 8 can start as soon as Phase 7 is complete
- Testing (Phase 10) can begin incrementally as each phase completes
