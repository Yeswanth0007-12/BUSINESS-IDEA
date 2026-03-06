# Design Document: Production Logistics Upgrade

## Overview

This design document outlines the comprehensive upgrade of PackOptima from a prototype packaging optimization tool to a production-ready enterprise logistics platform. The upgrade encompasses 11 phases that systematically enhance data models, introduce advanced packing algorithms, implement shipping cost optimization, enable multi-product order processing, add asynchronous queue systems, support bulk operations, provide advanced analytics, create warehouse integration APIs, and ensure production-grade quality through testing and documentation.

The current system provides basic single-product box optimization using cost-based selection with category-specific padding. The upgraded system will handle complex multi-product orders, optimize for both packaging and shipping costs, process bulk operations asynchronously, provide comprehensive analytics, and integrate seamlessly with warehouse management systems while maintaining backward compatibility with existing functionality.

## Architecture

### Current System Architecture

```mermaid
graph TD
    A[FastAPI Backend] --> B[PostgreSQL Database]
    A --> C[Authentication JWT]
    D[React Frontend] --> A
    B --> E[Product Model]
    B --> F[Box Model]
    B --> G[User Model]
    A --> H[Optimization Engine]
    H --> I[Simple Cost Selection]
```

### Target Production Architecture

```mermaid
graph TD
    A[FastAPI Backend] --> B[PostgreSQL Database]
    A --> C[Redis Cache/Queue]
    A --> D[Celery Workers]
    D --> E[Advanced Packing Engine]
    E --> F[6-Orientation Testing]
    E --> G[Shipping Cost Calculator]
    E --> H[Multi-Product Bin Packing]
    A --> I[Analytics Service]
    I --> J[Time-Series Metrics]
    A --> K[Warehouse Integration API]
    K --> L[Webhook System]
    M[React Frontend] --> A
    N[External Warehouse Systems] --> K
```


## System Components Overview

```mermaid
graph LR
    A[API Gateway] --> B[Rate Limiter]
    B --> C[Authentication]
    C --> D[Business Logic Layer]
    D --> E[Data Access Layer]
    D --> F[Queue Manager]
    F --> G[Celery Workers]
    G --> H[Packing Engine]
    G --> I[Analytics Processor]
    E --> J[PostgreSQL]
    F --> K[Redis]
    D --> L[Export Service]
    D --> M[Webhook Service]
```

## Phase 1: Enhanced Data Models

### Product Model Extensions

**Current Schema:**
```python
class Product:
    id: int
    company_id: int
    name: str
    sku: str
    category: str
    length_cm: float
    width_cm: float
    height_cm: float
    weight_kg: float
    current_box_id: int (nullable)
    monthly_order_volume: int
    created_at: datetime
```

**Enhanced Schema:**
```python
class Product:
    # Existing fields (unchanged)
    id: int
    company_id: int
    name: str
    sku: str
    category: str
    length_cm: float
    width_cm: float
    height_cm: float
    weight_kg: float
    current_box_id: int (nullable)
    monthly_order_volume: int
    created_at: datetime
    
    # New fields
    fragile: bool = False
    stackable: bool = True
```


### Box Model Extensions

**Current Schema:**
```python
class Box:
    id: int
    company_id: int
    name: str
    length_cm: float
    width_cm: float
    height_cm: float
    cost_per_unit: float
    usage_count: int
    created_at: datetime
```

**Enhanced Schema:**
```python
class Box:
    # Existing fields (unchanged)
    id: int
    company_id: int
    name: str
    length_cm: float
    width_cm: float
    height_cm: float
    cost_per_unit: float
    usage_count: int
    created_at: datetime
    
    # New fields
    max_weight_kg: float = 30.0
    material_type: str = "cardboard"  # cardboard, plastic, wood
```

### Migration Strategy

**Backward Compatibility:**
- All new fields have default values
- Existing API endpoints continue to work
- Optional fields in request schemas
- Database migration adds columns with defaults

**Migration Script:**
```sql
-- Add new columns to products table
ALTER TABLE products 
ADD COLUMN fragile BOOLEAN DEFAULT FALSE,
ADD COLUMN stackable BOOLEAN DEFAULT TRUE;

-- Add new columns to boxes table
ALTER TABLE boxes
ADD COLUMN max_weight_kg FLOAT DEFAULT 30.0,
ADD COLUMN material_type VARCHAR(50) DEFAULT 'cardboard';
```


## Phase 2: Advanced Packing Engine

### 6-Orientation Testing Algorithm

**Purpose:** Test all possible orientations of a product to find the best fit in a box.

**Algorithm:**
```python
ALGORITHM test_all_orientations(product_dims, box_dims, padding)
INPUT: 
  product_dims = (length, width, height) in cm
  box_dims = (box_length, box_width, box_height) in cm
  padding = padding requirement in cm
OUTPUT: 
  best_orientation = (L, W, H) or None
  space_utilization = percentage (0-100)

PRECONDITIONS:
  - All dimensions > 0
  - padding >= 0
  - box_dims are valid box dimensions

POSTCONDITIONS:
  - If fit found: best_orientation is valid and fits in box
  - space_utilization is accurate percentage
  - Returns None if no orientation fits

BEGIN
  orientations ← [
    (length, width, height),
    (length, height, width),
    (width, length, height),
    (width, height, length),
    (height, length, width),
    (height, width, length)
  ]
  
  best_fit ← None
  best_utilization ← 0
  
  FOR each orientation IN orientations DO
    ASSERT orientation has 3 dimensions
    
    // Add padding to each dimension
    required_L ← orientation[0] + (2 × padding)
    required_W ← orientation[1] + (2 × padding)
    required_H ← orientation[2] + (2 × padding)
    
    // Check if fits in box
    IF required_L ≤ box_dims[0] AND 
       required_W ≤ box_dims[1] AND 
       required_H ≤ box_dims[2] THEN
      
      // Calculate space utilization
      product_volume ← orientation[0] × orientation[1] × orientation[2]
      box_volume ← box_dims[0] × box_dims[1] × box_dims[2]
      utilization ← (product_volume / box_volume) × 100
      
      // Keep best utilization
      IF utilization > best_utilization THEN
        best_fit ← orientation
        best_utilization ← utilization
      END IF
    END IF
  END FOR
  
  ASSERT best_utilization ≥ 0 AND best_utilization ≤ 100
  
  RETURN (best_fit, best_utilization)
END
```

**Loop Invariants:**
- All previously tested orientations have been evaluated for fit
- best_utilization represents the highest utilization found so far
- best_fit is None or a valid orientation that fits in the box


### Weight Constraint Validation

**Algorithm:**
```python
ALGORITHM validate_weight_constraint(product_weight, box_max_weight)
INPUT:
  product_weight = weight in kg
  box_max_weight = maximum box capacity in kg
OUTPUT:
  is_valid = boolean

PRECONDITIONS:
  - product_weight ≥ 0
  - box_max_weight > 0

POSTCONDITIONS:
  - Returns true if and only if product_weight ≤ box_max_weight
  - No side effects

BEGIN
  RETURN product_weight ≤ box_max_weight
END
```

### Enhanced Box Selection

**Algorithm:**
```python
ALGORITHM find_optimal_box_advanced(product, boxes, padding)
INPUT:
  product = Product object with dimensions, weight, fragile, stackable
  boxes = List of Box objects
  padding = padding requirement in cm
OUTPUT:
  result = {
    box: Box object or None,
    orientation: (L, W, H) or None,
    space_utilization: float (0-100),
    unused_volume: float in cm³,
    reason: string
  }

PRECONDITIONS:
  - product has valid dimensions and weight
  - boxes is non-empty list
  - padding ≥ 0

POSTCONDITIONS:
  - If box found: result.box fits product in result.orientation
  - space_utilization is accurate
  - unused_volume = box_volume - product_volume

BEGIN
  suitable_boxes ← []
  
  // Filter boxes by weight constraint
  FOR each box IN boxes DO
    IF validate_weight_constraint(product.weight_kg, box.max_weight_kg) THEN
      
      // Test all orientations
      (orientation, utilization) ← test_all_orientations(
        (product.length_cm, product.width_cm, product.height_cm),
        (box.length_cm, box.width_cm, box.height_cm),
        padding
      )
      
      IF orientation IS NOT None THEN
        box_volume ← box.length_cm × box.width_cm × box.height_cm
        product_volume ← orientation[0] × orientation[1] × orientation[2]
        unused_volume ← box_volume - product_volume
        
        suitable_boxes.add({
          box: box,
          orientation: orientation,
          utilization: utilization,
          unused_volume: unused_volume
        })
      END IF
    END IF
  END FOR
  
  IF suitable_boxes IS EMPTY THEN
    RETURN {
      box: None,
      orientation: None,
      space_utilization: 0,
      unused_volume: 0,
      reason: "No suitable box found"
    }
  END IF
  
  // Select box with minimum cost (primary) and best utilization (secondary)
  optimal ← suitable_boxes[0]
  FOR each candidate IN suitable_boxes DO
    IF candidate.box.cost_per_unit < optimal.box.cost_per_unit THEN
      optimal ← candidate
    ELSE IF candidate.box.cost_per_unit = optimal.box.cost_per_unit AND
            candidate.utilization > optimal.utilization THEN
      optimal ← candidate
    END IF
  END FOR
  
  RETURN {
    box: optimal.box,
    orientation: optimal.orientation,
    space_utilization: optimal.utilization,
    unused_volume: optimal.unused_volume,
    reason: "Success"
  }
END
```


## Phase 3: Shipping Cost Calculator

### Volumetric Weight Calculation

**Formula:** Volumetric Weight = (L × W × H) / 5000

**Algorithm:**
```python
ALGORITHM calculate_volumetric_weight(length_cm, width_cm, height_cm)
INPUT:
  length_cm, width_cm, height_cm = dimensions in centimeters
OUTPUT:
  volumetric_weight_kg = weight in kilograms

PRECONDITIONS:
  - All dimensions > 0

POSTCONDITIONS:
  - volumetric_weight_kg > 0
  - Result is accurate to 2 decimal places

BEGIN
  VOLUMETRIC_DIVISOR ← 5000
  volume_cm3 ← length_cm × width_cm × height_cm
  volumetric_weight_kg ← volume_cm3 / VOLUMETRIC_DIVISOR
  RETURN round(volumetric_weight_kg, 2)
END
```

### Billable Weight Calculation

**Algorithm:**
```python
ALGORITHM calculate_billable_weight(actual_weight_kg, volumetric_weight_kg)
INPUT:
  actual_weight_kg = physical weight in kg
  volumetric_weight_kg = calculated volumetric weight in kg
OUTPUT:
  billable_weight_kg = weight used for shipping cost

PRECONDITIONS:
  - actual_weight_kg ≥ 0
  - volumetric_weight_kg ≥ 0

POSTCONDITIONS:
  - billable_weight_kg ≥ actual_weight_kg
  - billable_weight_kg ≥ volumetric_weight_kg

BEGIN
  RETURN max(actual_weight_kg, volumetric_weight_kg)
END
```

### Shipping Cost Calculation

**Algorithm:**
```python
ALGORITHM calculate_shipping_cost(box, product, courier_rate)
INPUT:
  box = Box object with dimensions
  product = Product object with weight
  courier_rate = cost per kg (default 2.5)
OUTPUT:
  shipping_cost = total shipping cost

PRECONDITIONS:
  - box has valid dimensions
  - product.weight_kg ≥ 0
  - courier_rate > 0

POSTCONDITIONS:
  - shipping_cost ≥ 0
  - shipping_cost = billable_weight × courier_rate

BEGIN
  volumetric_weight ← calculate_volumetric_weight(
    box.length_cm,
    box.width_cm,
    box.height_cm
  )
  
  billable_weight ← calculate_billable_weight(
    product.weight_kg,
    volumetric_weight
  )
  
  shipping_cost ← billable_weight × courier_rate
  
  RETURN round(shipping_cost, 2)
END
```

### Total Cost Optimization

**Algorithm:**
```python
ALGORITHM calculate_total_cost(box, product, courier_rate, monthly_volume)
INPUT:
  box = Box object
  product = Product object
  courier_rate = shipping rate per kg
  monthly_volume = number of orders per month
OUTPUT:
  total_cost = packaging + shipping cost per month

PRECONDITIONS:
  - box and product are valid
  - courier_rate > 0
  - monthly_volume > 0

POSTCONDITIONS:
  - total_cost = (box_cost + shipping_cost) × monthly_volume

BEGIN
  shipping_cost ← calculate_shipping_cost(box, product, courier_rate)
  cost_per_order ← box.cost_per_unit + shipping_cost
  total_cost ← cost_per_order × monthly_volume
  
  RETURN round(total_cost, 2)
END
```


## Phase 4: Multi-Product Order Packing

### Order Data Model

**Schema:**
```python
class Order:
    id: int
    company_id: int
    order_number: str
    customer_name: str
    status: str  # pending, processing, completed, failed
    created_at: datetime
    completed_at: datetime (nullable)
    
class OrderItem:
    id: int
    order_id: int
    product_id: int
    quantity: int
    
class OrderPackingResult:
    id: int
    order_id: int
    box_id: int
    box_number: int  # 1, 2, 3... for multiple boxes
    total_weight_kg: float
    space_utilization: float
    items_packed: List[int]  # product IDs in this box
```

### Bin Packing Algorithm (First Fit Decreasing)

**Algorithm:**
```python
ALGORITHM pack_multi_product_order(order_items, products, boxes, padding)
INPUT:
  order_items = List of (product_id, quantity) tuples
  products = Map of product_id → Product object
  boxes = List of available Box objects
  padding = padding requirement in cm
OUTPUT:
  packing_result = {
    boxes_used: List of {box, items, weight, utilization},
    total_boxes: int,
    total_cost: float,
    success: boolean,
    unpacked_items: List of product_ids
  }

PRECONDITIONS:
  - order_items is non-empty
  - All product_ids exist in products map
  - boxes is non-empty
  - padding ≥ 0

POSTCONDITIONS:
  - All items either packed or in unpacked_items
  - total_boxes = length of boxes_used
  - total_cost = sum of all box costs

BEGIN
  // Step 1: Expand order items to individual products
  items_to_pack ← []
  FOR each (product_id, quantity) IN order_items DO
    FOR i FROM 1 TO quantity DO
      items_to_pack.add(products[product_id])
    END FOR
  END FOR
  
  // Step 2: Sort items by volume (largest first)
  SORT items_to_pack BY (length × width × height) DESCENDING
  
  // Step 3: Initialize packing state
  packed_boxes ← []
  unpacked_items ← []
  
  // Step 4: Pack items using First Fit Decreasing
  FOR each item IN items_to_pack DO
    ASSERT item has valid dimensions and weight
    
    packed ← false
    
    // Try to fit in existing boxes
    FOR each box_state IN packed_boxes DO
      IF can_fit_in_box(item, box_state, padding) THEN
        add_item_to_box(item, box_state)
        packed ← true
        BREAK
      END IF
    END FOR
    
    // If not packed, try new box
    IF NOT packed THEN
      new_box ← find_optimal_box_advanced(item, boxes, padding)
      
      IF new_box.box IS NOT None THEN
        box_state ← {
          box: new_box.box,
          items: [item],
          remaining_space: new_box.unused_volume,
          current_weight: item.weight_kg,
          utilization: new_box.space_utilization
        }
        packed_boxes.add(box_state)
        packed ← true
      END IF
    END IF
    
    IF NOT packed THEN
      unpacked_items.add(item.id)
    END IF
  END FOR
  
  // Step 5: Calculate totals
  total_cost ← 0
  FOR each box_state IN packed_boxes DO
    total_cost ← total_cost + box_state.box.cost_per_unit
  END FOR
  
  RETURN {
    boxes_used: packed_boxes,
    total_boxes: length(packed_boxes),
    total_cost: total_cost,
    success: length(unpacked_items) = 0,
    unpacked_items: unpacked_items
  }
END
```

**Loop Invariants:**
- All items before current index are either packed or in unpacked_items
- packed_boxes contains valid box states with no weight/dimension violations
- total_cost accurately reflects sum of box costs


### Space Tracking Algorithm

**Algorithm:**
```python
ALGORITHM can_fit_in_box(item, box_state, padding)
INPUT:
  item = Product to add
  box_state = Current box state with items and remaining space
  padding = padding requirement
OUTPUT:
  can_fit = boolean

PRECONDITIONS:
  - item has valid dimensions and weight
  - box_state is valid with current items
  - padding ≥ 0

POSTCONDITIONS:
  - Returns true if and only if item fits with all constraints
  - No modifications to box_state

BEGIN
  // Check weight constraint
  new_weight ← box_state.current_weight + item.weight_kg
  IF new_weight > box_state.box.max_weight_kg THEN
    RETURN false
  END IF
  
  // Check if fragile items can be stacked
  IF item.fragile OR has_fragile_items(box_state.items) THEN
    IF length(box_state.items) > 0 THEN
      RETURN false  // Don't stack fragile items
    END IF
  END IF
  
  // Check if items are stackable
  IF NOT item.stackable THEN
    IF length(box_state.items) > 0 THEN
      RETURN false  // Don't stack non-stackable items
    END IF
  END IF
  
  // Simplified volume check (conservative estimate)
  item_volume ← item.length_cm × item.width_cm × item.height_cm
  IF item_volume > box_state.remaining_space THEN
    RETURN false
  END IF
  
  RETURN true
END
```


## Phase 5: Queue System Architecture

### Technology Stack

- **Queue Broker:** Redis (in-memory data store)
- **Task Queue:** Celery (distributed task queue)
- **Result Backend:** Redis (stores task results)

### Queue System Components

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Redis
    participant Celery
    participant Worker
    participant DB
    
    Client->>API: POST /optimize (async)
    API->>Redis: Enqueue task
    API-->>Client: 202 Accepted {task_id}
    Redis->>Celery: Task available
    Celery->>Worker: Assign task
    Worker->>DB: Fetch data
    Worker->>Worker: Run optimization
    Worker->>DB: Store results
    Worker->>Redis: Update status
    Client->>API: GET /tasks/{task_id}
    API->>Redis: Check status
    API-->>Client: Status + Results
```

### Task Status Model

**Schema:**
```python
class OptimizationTask:
    id: str  # UUID
    company_id: int
    task_type: str  # single, bulk, order
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    created_at: datetime
    started_at: datetime (nullable)
    completed_at: datetime (nullable)
    result_id: int (nullable)  # Links to OptimizationRun
    error_message: str (nullable)
    metadata: dict  # Additional task info
```

### Celery Task Implementation

**Algorithm:**
```python
ALGORITHM celery_optimize_task(task_id, company_id, request_data)
INPUT:
  task_id = unique task identifier
  company_id = company ID for isolation
  request_data = optimization request parameters
OUTPUT:
  result = optimization result or error

PRECONDITIONS:
  - task_id is unique and valid
  - company_id exists
  - request_data is valid JSON

POSTCONDITIONS:
  - Task status updated to completed or failed
  - Results stored in database if successful
  - Error message stored if failed

BEGIN
  TRY
    // Update status to processing
    update_task_status(task_id, "processing", progress=0)
    
    // Get database session
    db ← get_database_session()
    
    // Initialize optimization engine
    engine ← OptimizationEngine(db)
    
    // Update progress
    update_task_status(task_id, "processing", progress=25)
    
    // Run optimization
    result ← engine.optimize_packaging(company_id, request_data)
    
    // Update progress
    update_task_status(task_id, "processing", progress=75)
    
    // Store result
    store_optimization_result(task_id, result)
    
    // Update status to completed
    update_task_status(task_id, "completed", progress=100)
    
    RETURN result
    
  CATCH error
    // Log error
    log_error(task_id, error)
    
    // Update status to failed
    update_task_status(task_id, "failed", error_message=error.message)
    
    RAISE error
  FINALLY
    // Close database session
    close_database_session(db)
  END TRY
END
```


## Phase 6: Bulk Order Processing

### CSV Upload Data Model

**Schema:**
```python
class BulkUpload:
    id: int
    company_id: int
    filename: str
    total_orders: int
    processed_orders: int
    failed_orders: int
    status: str  # uploading, processing, completed, failed
    created_at: datetime
    completed_at: datetime (nullable)
    
class BulkUploadOrder:
    id: int
    upload_id: int
    row_number: int
    order_data: dict  # JSON with order details
    status: str  # pending, processing, completed, failed
    task_id: str (nullable)  # Celery task ID
    error_message: str (nullable)
```

### CSV Format Specification

**Required Columns:**
- order_number (string)
- customer_name (string)
- product_sku (string)
- quantity (integer)

**Example CSV:**
```csv
order_number,customer_name,product_sku,quantity
ORD-001,Acme Corp,PROD-123,2
ORD-001,Acme Corp,PROD-456,1
ORD-002,Beta Inc,PROD-789,3
```

### Bulk Processing Algorithm

**Algorithm:**
```python
ALGORITHM process_bulk_upload(upload_id, csv_file, company_id)
INPUT:
  upload_id = unique upload identifier
  csv_file = uploaded CSV file
  company_id = company ID for isolation
OUTPUT:
  summary = {
    total_orders: int,
    successful: int,
    failed: int,
    task_ids: List[str]
  }

PRECONDITIONS:
  - upload_id is unique
  - csv_file is valid CSV format
  - company_id exists

POSTCONDITIONS:
  - All orders queued for processing
  - Upload status updated
  - Task IDs returned for tracking

BEGIN
  // Step 1: Parse CSV file
  rows ← parse_csv(csv_file)
  
  IF rows IS EMPTY THEN
    RAISE Error("CSV file is empty")
  END IF
  
  // Step 2: Validate headers
  required_headers ← ["order_number", "customer_name", "product_sku", "quantity"]
  IF NOT has_required_headers(rows[0], required_headers) THEN
    RAISE Error("Missing required columns")
  END IF
  
  // Step 3: Group rows by order_number
  orders ← group_by_order_number(rows)
  
  // Step 4: Update upload record
  update_upload(upload_id, total_orders=length(orders), status="processing")
  
  // Step 5: Queue each order for processing
  task_ids ← []
  processed ← 0
  failed ← 0
  
  FOR each order IN orders DO
    TRY
      // Validate order data
      validate_order_data(order, company_id)
      
      // Create order record
      order_record ← create_order_record(order, company_id)
      
      // Queue optimization task
      task_id ← queue_order_optimization(order_record.id, company_id)
      task_ids.add(task_id)
      
      // Create bulk upload order record
      create_bulk_upload_order(
        upload_id=upload_id,
        order_data=order,
        task_id=task_id,
        status="pending"
      )
      
      processed ← processed + 1
      
    CATCH error
      // Log failed order
      create_bulk_upload_order(
        upload_id=upload_id,
        order_data=order,
        status="failed",
        error_message=error.message
      )
      
      failed ← failed + 1
    END TRY
  END FOR
  
  // Step 6: Update upload status
  update_upload(
    upload_id,
    processed_orders=processed,
    failed_orders=failed,
    status="completed"
  )
  
  RETURN {
    total_orders: length(orders),
    successful: processed,
    failed: failed,
    task_ids: task_ids
  }
END
```

**Loop Invariants:**
- processed + failed ≤ total orders
- All processed orders have valid task_ids
- All failed orders have error messages


## Phase 7: Advanced Analytics

### Analytics Data Models

**Schema:**
```python
class AnalyticsSnapshot:
    id: int
    company_id: int
    snapshot_date: date
    total_products: int
    total_boxes: int
    total_optimizations: int
    avg_space_utilization: float
    total_monthly_savings: float
    total_annual_savings: float
    
class BoxUsageMetrics:
    id: int
    company_id: int
    box_id: int
    period_start: date
    period_end: date
    usage_count: int
    total_cost: float
    avg_utilization: float
    
class ShippingCostMetrics:
    id: int
    company_id: int
    period_start: date
    period_end: date
    total_shipments: int
    total_shipping_cost: float
    avg_billable_weight: float
    volumetric_weight_percentage: float
```

### Space Utilization Calculation

**Algorithm:**
```python
ALGORITHM calculate_space_utilization_metrics(company_id, start_date, end_date)
INPUT:
  company_id = company identifier
  start_date = analysis period start
  end_date = analysis period end
OUTPUT:
  metrics = {
    avg_utilization: float,
    min_utilization: float,
    max_utilization: float,
    waste_percentage: float
  }

PRECONDITIONS:
  - company_id exists
  - start_date ≤ end_date

POSTCONDITIONS:
  - All percentages are 0-100
  - waste_percentage = 100 - avg_utilization

BEGIN
  // Fetch optimization results in date range
  results ← query_optimization_results(company_id, start_date, end_date)
  
  IF results IS EMPTY THEN
    RETURN {
      avg_utilization: 0,
      min_utilization: 0,
      max_utilization: 0,
      waste_percentage: 100
    }
  END IF
  
  // Calculate statistics
  utilizations ← []
  FOR each result IN results DO
    product_volume ← calculate_product_volume(result.product)
    box_volume ← calculate_box_volume(result.recommended_box)
    utilization ← (product_volume / box_volume) × 100
    utilizations.add(utilization)
  END FOR
  
  avg_utilization ← mean(utilizations)
  min_utilization ← min(utilizations)
  max_utilization ← max(utilizations)
  waste_percentage ← 100 - avg_utilization
  
  RETURN {
    avg_utilization: round(avg_utilization, 2),
    min_utilization: round(min_utilization, 2),
    max_utilization: round(max_utilization, 2),
    waste_percentage: round(waste_percentage, 2)
  }
END
```


### Box Usage Frequency Analysis

**Algorithm:**
```python
ALGORITHM analyze_box_usage_frequency(company_id, start_date, end_date)
INPUT:
  company_id = company identifier
  start_date = analysis period start
  end_date = analysis period end
OUTPUT:
  usage_data = List of {
    box_id: int,
    box_name: str,
    usage_count: int,
    total_cost: float,
    percentage: float
  }

PRECONDITIONS:
  - company_id exists
  - start_date ≤ end_date

POSTCONDITIONS:
  - Sum of percentages = 100
  - Results sorted by usage_count descending

BEGIN
  // Query optimization results
  results ← query_optimization_results(company_id, start_date, end_date)
  
  // Count box usage
  box_usage ← {}  // Map: box_id → count
  box_info ← {}   // Map: box_id → box details
  
  FOR each result IN results DO
    box_id ← result.recommended_box_id
    
    IF box_id NOT IN box_usage THEN
      box_usage[box_id] ← 0
      box_info[box_id] ← fetch_box_details(box_id)
    END IF
    
    box_usage[box_id] ← box_usage[box_id] + 1
  END FOR
  
  // Calculate totals and percentages
  total_usage ← sum(box_usage.values())
  usage_data ← []
  
  FOR each (box_id, count) IN box_usage DO
    box ← box_info[box_id]
    percentage ← (count / total_usage) × 100
    total_cost ← count × box.cost_per_unit
    
    usage_data.add({
      box_id: box_id,
      box_name: box.name,
      usage_count: count,
      total_cost: total_cost,
      percentage: round(percentage, 2)
    })
  END FOR
  
  // Sort by usage count descending
  SORT usage_data BY usage_count DESCENDING
  
  RETURN usage_data
END
```

### Time-Series Trend Analysis

**Algorithm:**
```python
ALGORITHM calculate_savings_trend(company_id, months)
INPUT:
  company_id = company identifier
  months = number of months to analyze
OUTPUT:
  trend_data = List of {
    month: str,
    total_savings: float,
    optimization_count: int,
    avg_savings_per_optimization: float
  }

PRECONDITIONS:
  - company_id exists
  - months > 0

POSTCONDITIONS:
  - Results ordered chronologically
  - Length of trend_data ≤ months

BEGIN
  trend_data ← []
  current_date ← today()
  
  FOR i FROM 0 TO months - 1 DO
    month_start ← first_day_of_month(current_date - i months)
    month_end ← last_day_of_month(current_date - i months)
    
    // Query optimizations for this month
    runs ← query_optimization_runs(company_id, month_start, month_end)
    
    IF runs IS NOT EMPTY THEN
      total_savings ← sum(run.total_monthly_savings FOR run IN runs)
      count ← length(runs)
      avg_savings ← total_savings / count
      
      trend_data.add({
        month: format_month(month_start),
        total_savings: round(total_savings, 2),
        optimization_count: count,
        avg_savings_per_optimization: round(avg_savings, 2)
      })
    END IF
  END FOR
  
  // Reverse to chronological order
  REVERSE trend_data
  
  RETURN trend_data
END
```


## Phase 8: Enhanced Dashboard APIs

### API Endpoints

**GET /api/v1/analytics/summary**

Returns comprehensive analytics summary for the company.

**Request:**
```python
GET /api/v1/analytics/summary?period=30
Authorization: Bearer {token}
```

**Response:**
```python
{
  "total_products": 150,
  "total_boxes": 20,
  "total_optimizations": 45,
  "total_monthly_savings": 2500.00,
  "total_annual_savings": 30000.00,
  "avg_space_utilization": 68.5,
  "waste_percentage": 31.5,
  "period_days": 30
}
```

**GET /api/v1/analytics/box-usage**

Returns box usage frequency and cost analysis.

**Request:**
```python
GET /api/v1/analytics/box-usage?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

**Response:**
```python
{
  "boxes": [
    {
      "box_id": 5,
      "box_name": "Medium Box",
      "usage_count": 120,
      "total_cost": 600.00,
      "percentage": 45.5,
      "avg_utilization": 72.3
    },
    {
      "box_id": 3,
      "box_name": "Small Box",
      "usage_count": 85,
      "total_cost": 340.00,
      "percentage": 32.2,
      "avg_utilization": 81.5
    }
  ],
  "total_usage": 264,
  "total_cost": 1320.00
}
```

**GET /api/v1/analytics/shipping-cost**

Returns shipping cost analysis with volumetric weight breakdown.

**Request:**
```python
GET /api/v1/analytics/shipping-cost?period=30
Authorization: Bearer {token}
```

**Response:**
```python
{
  "total_shipments": 264,
  "total_shipping_cost": 3960.00,
  "avg_shipping_cost_per_order": 15.00,
  "avg_billable_weight": 6.0,
  "volumetric_weight_percentage": 65.5,
  "actual_weight_percentage": 34.5
}
```

**GET /api/v1/analytics/trends**

Returns time-series trend data for savings and optimizations.

**Request:**
```python
GET /api/v1/analytics/trends?months=6
Authorization: Bearer {token}
```

**Response:**
```python
{
  "trends": [
    {
      "month": "2024-01",
      "total_savings": 2500.00,
      "optimization_count": 45,
      "avg_savings_per_optimization": 55.56
    },
    {
      "month": "2024-02",
      "total_savings": 2800.00,
      "optimization_count": 52,
      "avg_savings_per_optimization": 53.85
    }
  ]
}
```


## Phase 9: Warehouse Integration API

### Standardized Integration Endpoints

**POST /api/v1/warehouse/optimize-package**

Synchronous optimization endpoint for warehouse systems.

**Request:**
```python
POST /api/v1/warehouse/optimize-package
Authorization: Bearer {api_key}
Content-Type: application/json

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
    }
  ],
  "shipping_address": {
    "country": "US",
    "postal_code": "12345"
  }
}
```

**Response:**
```python
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
      "items": ["PROD-123", "PROD-123"],
      "total_weight_kg": 5.0,
      "space_utilization": 75.5,
      "box_cost": 5.00,
      "shipping_cost": 12.50,
      "total_cost": 17.50
    }
  ],
  "total_boxes": 1,
  "total_cost": 17.50,
  "estimated_shipping_cost": 12.50
}
```

### Webhook System

**Webhook Registration:**
```python
POST /api/v1/warehouse/webhooks
Authorization: Bearer {api_key}

{
  "url": "https://warehouse.example.com/webhooks/packoptima",
  "events": ["optimization.completed", "optimization.failed"],
  "secret": "webhook_secret_key"
}
```

**Webhook Payload:**
```python
POST https://warehouse.example.com/webhooks/packoptima
X-PackOptima-Signature: sha256=...
Content-Type: application/json

{
  "event": "optimization.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "optimization_id": "opt-789",
    "order_id": "WH-12345",
    "status": "completed",
    "result": { /* optimization result */ }
  }
}
```

### Authentication & Rate Limiting

**API Key Authentication:**
```python
ALGORITHM authenticate_api_key(api_key, company_id)
INPUT:
  api_key = provided API key
  company_id = claimed company ID
OUTPUT:
  is_valid = boolean

PRECONDITIONS:
  - api_key is non-empty string
  - company_id is valid integer

POSTCONDITIONS:
  - Returns true if and only if api_key is valid for company_id
  - No side effects

BEGIN
  stored_key ← fetch_api_key(company_id)
  
  IF stored_key IS None THEN
    RETURN false
  END IF
  
  // Constant-time comparison to prevent timing attacks
  RETURN constant_time_compare(api_key, stored_key)
END
```

**Rate Limiting:**
- Standard tier: 100 requests/minute
- Premium tier: 500 requests/minute
- Enterprise tier: 2000 requests/minute


## Phase 10: Testing & Validation

### Testing Strategy

**Unit Testing Coverage:**
- All algorithms (orientation testing, bin packing, cost calculation)
- Data model validations
- Service layer methods
- API endpoint handlers

**Integration Testing:**
- End-to-end optimization workflows
- Queue system integration
- Database transactions
- Webhook delivery

**Property-Based Testing:**
- Packing algorithm correctness
- Cost calculation accuracy
- Space utilization bounds

**Performance Benchmarks:**
- Single product optimization: < 100ms
- Multi-product order (10 items): < 500ms
- Bulk upload (100 orders): < 30 seconds
- Analytics queries: < 200ms

### Test Cases

**Test Case 1: 6-Orientation Testing**
```python
TEST test_all_orientations_finds_best_fit
  GIVEN product with dimensions (30, 20, 10)
  AND box with dimensions (35, 25, 15)
  AND padding of 2 cm
  
  WHEN test_all_orientations is called
  
  THEN orientation is found
  AND space_utilization > 0
  AND all dimensions fit with padding
END TEST
```

**Test Case 2: Weight Constraint Validation**
```python
TEST test_weight_constraint_rejection
  GIVEN product with weight 25 kg
  AND box with max_weight 20 kg
  
  WHEN find_optimal_box_advanced is called
  
  THEN box is rejected
  AND reason includes "weight constraint"
END TEST
```

**Test Case 3: Multi-Product Bin Packing**
```python
TEST test_multi_product_packing_optimization
  GIVEN order with 5 different products
  AND 10 available boxes
  
  WHEN pack_multi_product_order is called
  
  THEN all items are packed
  AND total_boxes is minimized
  AND no weight constraints violated
  AND fragile items not stacked
END TEST
```

**Test Case 4: Shipping Cost Calculation**
```python
TEST test_volumetric_weight_exceeds_actual
  GIVEN product with actual weight 2 kg
  AND box with dimensions (50, 40, 30) cm
  AND volumetric weight = 12 kg
  
  WHEN calculate_shipping_cost is called
  
  THEN billable_weight = 12 kg
  AND shipping_cost = 12 × courier_rate
END TEST
```

**Test Case 5: Bulk Upload Processing**
```python
TEST test_bulk_upload_with_mixed_results
  GIVEN CSV with 10 orders
  AND 2 orders have invalid SKUs
  
  WHEN process_bulk_upload is called
  
  THEN 8 orders queued successfully
  AND 2 orders marked as failed
  AND error messages recorded
  AND upload status = "completed"
END TEST
```


### Load Testing Scenarios

**Scenario 1: Concurrent Optimizations**
- 100 concurrent users
- Each submitting 10 optimization requests
- Target: 95th percentile < 1 second

**Scenario 2: Bulk Upload Stress Test**
- 10 concurrent bulk uploads
- Each with 500 orders
- Target: All complete within 5 minutes

**Scenario 3: Analytics Query Performance**
- 50 concurrent dashboard loads
- Each fetching all analytics endpoints
- Target: All queries < 500ms


## Phase 11: Documentation & Deployment

### API Documentation

**OpenAPI/Swagger Specification:**
- Complete endpoint documentation
- Request/response schemas
- Authentication requirements
- Error codes and messages
- Example requests and responses

**Integration Guide:**
- Authentication setup
- Webhook configuration
- Rate limiting details
- Best practices
- Code examples (Python, JavaScript, cURL)

### Deployment Architecture

```mermaid
graph TD
    A[Load Balancer] --> B[API Server 1]
    A --> C[API Server 2]
    A --> D[API Server 3]
    B --> E[PostgreSQL Primary]
    C --> E
    D --> E
    E --> F[PostgreSQL Replica]
    B --> G[Redis Cluster]
    C --> G
    D --> G
    H[Celery Worker 1] --> E
    I[Celery Worker 2] --> E
    J[Celery Worker 3] --> E
    H --> G
    I --> G
    J --> G
```

### Migration Scripts

**Database Migration:**
```sql
-- Phase 1: Enhanced Data Models
ALTER TABLE products 
ADD COLUMN fragile BOOLEAN DEFAULT FALSE,
ADD COLUMN stackable BOOLEAN DEFAULT TRUE;

ALTER TABLE boxes
ADD COLUMN max_weight_kg FLOAT DEFAULT 30.0,
ADD COLUMN material_type VARCHAR(50) DEFAULT 'cardboard';

-- Phase 4: Multi-Product Orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    order_number VARCHAR(100) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    UNIQUE(company_id, order_number)
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0)
);

CREATE TABLE order_packing_results (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    box_id INTEGER NOT NULL REFERENCES boxes(id),
    box_number INTEGER NOT NULL,
    total_weight_kg FLOAT NOT NULL,
    space_utilization FLOAT NOT NULL,
    items_packed JSONB NOT NULL
);

-- Phase 5: Queue System
CREATE TABLE optimization_tasks (
    id UUID PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    task_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result_id INTEGER REFERENCES optimization_runs(id),
    error_message TEXT,
    metadata JSONB
);

CREATE INDEX idx_tasks_company_status ON optimization_tasks(company_id, status);
CREATE INDEX idx_tasks_created_at ON optimization_tasks(created_at);

-- Phase 6: Bulk Upload
CREATE TABLE bulk_uploads (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    filename VARCHAR(255) NOT NULL,
    total_orders INTEGER NOT NULL,
    processed_orders INTEGER DEFAULT 0,
    failed_orders INTEGER DEFAULT 0,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE bulk_upload_orders (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER NOT NULL REFERENCES bulk_uploads(id) ON DELETE CASCADE,
    row_number INTEGER NOT NULL,
    order_data JSONB NOT NULL,
    status VARCHAR(50) NOT NULL,
    task_id UUID REFERENCES optimization_tasks(id),
    error_message TEXT
);

-- Phase 7: Analytics
CREATE TABLE analytics_snapshots (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    snapshot_date DATE NOT NULL,
    total_products INTEGER NOT NULL,
    total_boxes INTEGER NOT NULL,
    total_optimizations INTEGER NOT NULL,
    avg_space_utilization FLOAT NOT NULL,
    total_monthly_savings FLOAT NOT NULL,
    total_annual_savings FLOAT NOT NULL,
    UNIQUE(company_id, snapshot_date)
);

CREATE TABLE box_usage_metrics (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    box_id INTEGER NOT NULL REFERENCES boxes(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    usage_count INTEGER NOT NULL,
    total_cost FLOAT NOT NULL,
    avg_utilization FLOAT NOT NULL
);

CREATE TABLE shipping_cost_metrics (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_shipments INTEGER NOT NULL,
    total_shipping_cost FLOAT NOT NULL,
    avg_billable_weight FLOAT NOT NULL,
    volumetric_weight_percentage FLOAT NOT NULL
);

-- Phase 9: Warehouse Integration
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE webhooks (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    url VARCHAR(500) NOT NULL,
    events JSONB NOT NULL,
    secret VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE webhook_deliveries (
    id SERIAL PRIMARY KEY,
    webhook_id INTEGER NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
    event VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(50) NOT NULL,
    response_code INTEGER,
    response_body TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    delivered_at TIMESTAMP
);

CREATE INDEX idx_webhook_deliveries_webhook ON webhook_deliveries(webhook_id);
CREATE INDEX idx_webhook_deliveries_created ON webhook_deliveries(created_at);
```


### Environment Configuration

**Required Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/packoptima

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# API Configuration
API_SECRET_KEY=your-secret-key-here
API_RATE_LIMIT=100  # requests per minute

# Shipping
DEFAULT_COURIER_RATE=2.5  # per kg
VOLUMETRIC_DIVISOR=5000

# Feature Flags
ENABLE_QUEUE_SYSTEM=true
ENABLE_BULK_UPLOAD=true
ENABLE_WEBHOOKS=true
```

### Monitoring Setup

**Metrics to Track:**
- API response times (p50, p95, p99)
- Queue depth and processing rate
- Database connection pool usage
- Redis memory usage
- Celery worker health
- Error rates by endpoint
- Optimization success/failure rates

**Alerting Rules:**
- API p95 > 1 second
- Queue depth > 1000 tasks
- Error rate > 5%
- Database connections > 80% of pool
- Celery worker down

### Deployment Checklist

**Pre-Deployment:**
- [ ] Run all unit tests
- [ ] Run integration tests
- [ ] Run load tests
- [ ] Review database migration scripts
- [ ] Backup production database
- [ ] Update API documentation
- [ ] Configure monitoring alerts

**Deployment Steps:**
1. Deploy database migrations
2. Deploy Redis configuration
3. Deploy API servers (rolling update)
4. Deploy Celery workers
5. Verify health checks
6. Run smoke tests
7. Monitor error rates

**Post-Deployment:**
- [ ] Verify all endpoints responding
- [ ] Check queue system processing
- [ ] Validate analytics data
- [ ] Test webhook delivery
- [ ] Monitor performance metrics
- [ ] Review error logs


## Correctness Properties

### Universal Quantification Properties

**Property 1: Orientation Testing Completeness**
```
∀ product, box, padding:
  IF test_all_orientations(product, box, padding) returns orientation
  THEN orientation fits in box with padding
  AND space_utilization ∈ [0, 100]
```

**Property 2: Weight Constraint Enforcement**
```
∀ product, box:
  IF find_optimal_box_advanced returns box
  THEN product.weight_kg ≤ box.max_weight_kg
```

**Property 3: Cost Optimality**
```
∀ product, boxes:
  IF find_optimal_box_advanced returns box_optimal
  THEN ∀ box_alternative ∈ boxes:
    IF box_alternative fits product
    THEN box_optimal.cost_per_unit ≤ box_alternative.cost_per_unit
```

**Property 4: Bin Packing Completeness**
```
∀ order, products, boxes:
  IF pack_multi_product_order returns result
  THEN (result.success = true ⟹ result.unpacked_items = [])
  AND (result.success = false ⟹ result.unpacked_items ≠ [])
```

**Property 5: Shipping Cost Accuracy**
```
∀ box, product, courier_rate:
  LET shipping_cost = calculate_shipping_cost(box, product, courier_rate)
  LET volumetric_weight = (box.L × box.W × box.H) / 5000
  LET billable_weight = max(product.weight_kg, volumetric_weight)
  THEN shipping_cost = billable_weight × courier_rate
```

**Property 6: Space Utilization Bounds**
```
∀ product, box:
  IF product fits in box
  THEN space_utilization = (product_volume / box_volume) × 100
  AND space_utilization ∈ (0, 100]
```

**Property 7: Fragile Item Safety**
```
∀ order, packing_result:
  IF order contains fragile items
  THEN ∀ box_state ∈ packing_result.boxes_used:
    (has_fragile_item(box_state.items) ⟹ |box_state.items| = 1)
```

**Property 8: Analytics Consistency**
```
∀ company, period:
  LET metrics = calculate_space_utilization_metrics(company, period)
  THEN metrics.waste_percentage = 100 - metrics.avg_utilization
  AND metrics.avg_utilization ∈ [0, 100]
```

**Property 9: Queue Task Uniqueness**
```
∀ task_id:
  task_id is unique across all optimization tasks
  AND task_id is immutable once created
```

**Property 10: Bulk Upload Accounting**
```
∀ upload:
  upload.total_orders = upload.processed_orders + upload.failed_orders
  AND upload.processed_orders ≥ 0
  AND upload.failed_orders ≥ 0
```


## Error Handling

### Error Scenarios and Responses

**Scenario 1: No Suitable Box Found**
- **Condition:** Product dimensions exceed all available boxes
- **Response:** Return 200 with empty recommendation and reason
- **Recovery:** Suggest adding larger boxes or modifying product dimensions

**Scenario 2: Weight Constraint Violation**
- **Condition:** Product weight exceeds all box weight limits
- **Response:** Return 200 with error reason "Weight constraint violated"
- **Recovery:** Suggest adding boxes with higher weight capacity

**Scenario 3: Queue System Failure**
- **Condition:** Redis connection lost or Celery worker unavailable
- **Response:** Return 503 Service Unavailable
- **Recovery:** Retry with exponential backoff, fallback to synchronous processing

**Scenario 4: Bulk Upload Invalid CSV**
- **Condition:** CSV missing required columns or malformed
- **Response:** Return 400 Bad Request with validation errors
- **Recovery:** Provide detailed error message with expected format

**Scenario 5: Webhook Delivery Failure**
- **Condition:** Webhook endpoint unreachable or returns error
- **Response:** Retry up to 3 times with exponential backoff
- **Recovery:** Log failure, mark webhook as inactive after repeated failures

**Scenario 6: Database Connection Pool Exhausted**
- **Condition:** All database connections in use
- **Response:** Return 503 Service Unavailable
- **Recovery:** Queue request for retry, scale up connection pool

**Scenario 7: Invalid API Key**
- **Condition:** API key not found or inactive
- **Response:** Return 401 Unauthorized
- **Recovery:** Provide clear error message to regenerate API key

**Scenario 8: Rate Limit Exceeded**
- **Condition:** Request count exceeds tier limit
- **Response:** Return 429 Too Many Requests with Retry-After header
- **Recovery:** Client should implement exponential backoff


## Performance Considerations

### Optimization Targets

**Response Time Targets:**
- Single product optimization: < 100ms (p95)
- Multi-product order (10 items): < 500ms (p95)
- Bulk upload submission: < 2 seconds (p95)
- Analytics queries: < 200ms (p95)
- Webhook delivery: < 1 second (p95)

**Throughput Targets:**
- API requests: 1000 req/sec per server
- Queue processing: 100 tasks/sec per worker
- Bulk uploads: 10 concurrent uploads
- Database queries: < 50ms average

### Optimization Strategies

**Database Optimization:**
- Index on company_id for all multi-tenant tables
- Index on created_at for time-series queries
- Composite index on (company_id, status) for task queries
- Connection pooling with 20 connections per server
- Read replicas for analytics queries

**Caching Strategy:**
- Cache box catalog per company (TTL: 1 hour)
- Cache product catalog per company (TTL: 30 minutes)
- Cache analytics snapshots (TTL: 5 minutes)
- Redis for session storage and rate limiting

**Queue Optimization:**
- Celery worker pool: 4 workers per server
- Task prefetch: 2 tasks per worker
- Result expiration: 24 hours
- Priority queues: high (API), normal (bulk), low (analytics)

**Algorithm Optimization:**
- Early termination in orientation testing when perfect fit found
- Memoization of box volume calculations
- Batch database queries for multi-product orders
- Lazy loading of product relationships


## Security Considerations

### Authentication & Authorization

**API Key Management:**
- SHA-256 hashing for stored keys
- Constant-time comparison to prevent timing attacks
- Key rotation support
- Automatic key expiration after 90 days of inactivity
- Audit log of key usage

**JWT Token Security:**
- RS256 algorithm for signing
- 1-hour token expiration
- Refresh token rotation
- Token revocation support
- Secure HTTP-only cookies for web clients

**Multi-Tenant Isolation:**
- All queries filtered by company_id
- Row-level security in database
- API key scoped to single company
- No cross-company data access

### Input Validation

**Request Validation:**
- Pydantic schemas for all API inputs
- Dimension bounds: 0.1 cm to 500 cm
- Weight bounds: 0.01 kg to 1000 kg
- Quantity bounds: 1 to 10,000
- String length limits on all text fields

**CSV Upload Validation:**
- File size limit: 10 MB
- Row limit: 10,000 rows
- Column validation against schema
- SKU format validation
- Sanitization of all string inputs

### Data Protection

**Sensitive Data:**
- API keys encrypted at rest
- Webhook secrets encrypted at rest
- Database connection strings in environment variables
- No PII in logs or error messages

**Rate Limiting:**
- Per-company rate limits
- Per-API-key rate limits
- Distributed rate limiting via Redis
- Automatic blocking after repeated violations

### Webhook Security

**Signature Verification:**
- HMAC-SHA256 signature on all webhook payloads
- Timestamp validation (max 5 minutes old)
- Replay attack prevention
- TLS 1.2+ required for webhook endpoints


## Dependencies

### Core Dependencies

**Backend Framework:**
- FastAPI 0.104+ (async web framework)
- Uvicorn 0.24+ (ASGI server)
- Pydantic 2.5+ (data validation)

**Database:**
- PostgreSQL 14+ (primary database)
- SQLAlchemy 2.0+ (ORM)
- Alembic 1.12+ (migrations)
- psycopg2-binary 2.9+ (PostgreSQL driver)

**Queue System:**
- Redis 7.0+ (message broker and cache)
- Celery 5.3+ (distributed task queue)
- redis-py 5.0+ (Redis client)

**Authentication:**
- python-jose 3.3+ (JWT handling)
- passlib 1.7+ (password hashing)
- bcrypt 4.0+ (hashing algorithm)

**Testing:**
- pytest 7.4+ (test framework)
- pytest-asyncio 0.21+ (async test support)
- httpx 0.25+ (async HTTP client for testing)
- faker 20.0+ (test data generation)

**Monitoring:**
- prometheus-client 0.19+ (metrics)
- sentry-sdk 1.38+ (error tracking)

### Infrastructure Dependencies

**Required Services:**
- PostgreSQL database server
- Redis server
- Celery worker processes
- Load balancer (nginx or similar)

**Optional Services:**
- PostgreSQL read replica (for analytics)
- Redis Sentinel (for high availability)
- Prometheus (for metrics collection)
- Grafana (for metrics visualization)

### External APIs

**Shipping Carriers (Future Integration):**
- FedEx API (rate calculation)
- UPS API (rate calculation)
- USPS API (rate calculation)
- DHL API (rate calculation)

### Development Dependencies

**Code Quality:**
- black (code formatting)
- flake8 (linting)
- mypy (type checking)
- isort (import sorting)

**Documentation:**
- mkdocs (documentation site)
- swagger-ui (API documentation)


## Implementation Sequence

### Phase Dependencies

```mermaid
graph TD
    P1[Phase 1: Enhanced Data Models] --> P2[Phase 2: Advanced Packing Engine]
    P2 --> P3[Phase 3: Shipping Cost Calculator]
    P3 --> P4[Phase 4: Multi-Product Order Packing]
    P1 --> P5[Phase 5: Queue System]
    P4 --> P6[Phase 6: Bulk Order Processing]
    P5 --> P6
    P2 --> P7[Phase 7: Advanced Analytics]
    P3 --> P7
    P4 --> P7
    P7 --> P8[Phase 8: Enhanced Dashboard APIs]
    P4 --> P9[Phase 9: Warehouse Integration API]
    P5 --> P9
    P1 --> P10[Phase 10: Testing & Validation]
    P2 --> P10
    P3 --> P10
    P4 --> P10
    P5 --> P10
    P6 --> P10
    P7 --> P10
    P8 --> P10
    P9 --> P10
    P10 --> P11[Phase 11: Documentation & Deployment]
```

### Recommended Implementation Order

1. **Phase 1** (1-2 days): Enhanced Data Models
   - Low risk, foundational changes
   - Enables all subsequent phases

2. **Phase 2** (3-4 days): Advanced Packing Engine
   - Core algorithm improvements
   - High value, moderate complexity

3. **Phase 3** (2-3 days): Shipping Cost Calculator
   - Builds on Phase 2
   - Straightforward implementation

4. **Phase 5** (3-4 days): Queue System
   - Can be implemented in parallel with Phase 4
   - Required for Phase 6

5. **Phase 4** (4-5 days): Multi-Product Order Packing
   - Complex bin packing algorithm
   - Depends on Phases 2 and 3

6. **Phase 7** (3-4 days): Advanced Analytics
   - Can start after Phase 2-4 complete
   - Provides business value early

7. **Phase 8** (2-3 days): Enhanced Dashboard APIs
   - Exposes Phase 7 analytics
   - Quick win for user experience

8. **Phase 6** (3-4 days): Bulk Order Processing
   - Depends on Phases 4 and 5
   - High business value

9. **Phase 9** (4-5 days): Warehouse Integration API
   - External integration layer
   - Can be developed in parallel with Phase 6

10. **Phase 10** (5-7 days): Testing & Validation
    - Comprehensive testing of all phases
    - Performance benchmarking

11. **Phase 11** (3-4 days): Documentation & Deployment
    - Final preparation for production
    - Deployment and monitoring setup

**Total Estimated Timeline:** 33-45 days (6-9 weeks)

### Parallel Development Opportunities

- Phases 2 and 5 can be developed in parallel
- Phases 7 and 9 can be developed in parallel
- Phase 8 can start as soon as Phase 7 is complete
- Testing (Phase 10) can begin incrementally as each phase completes


## Backward Compatibility

### Compatibility Guarantees

**Existing API Endpoints:**
- All current endpoints remain functional
- Response formats unchanged for existing fields
- New fields added as optional extensions
- Deprecated endpoints marked but not removed

**Database Schema:**
- All new columns have default values
- No breaking changes to existing columns
- Foreign key relationships preserved
- Indexes maintained for existing queries

**UI Compatibility:**
- Existing UI components continue to work
- No modifications required to current pages
- New features accessible via new routes
- Graceful degradation for missing features

### Migration Path

**For Existing Users:**
1. Database migration runs automatically
2. New fields populated with defaults
3. Existing data remains unchanged
4. New features opt-in via configuration

**For API Clients:**
1. Existing API calls work without changes
2. New endpoints available at /api/v1/*
3. Versioned API ensures compatibility
4. Deprecation notices with 6-month timeline

### Rollback Strategy

**Database Rollback:**
- Migration scripts include down() methods
- Backup before migration required
- New columns can be dropped safely
- No data loss on rollback

**Application Rollback:**
- Feature flags for new functionality
- Can disable queue system if issues arise
- Fallback to synchronous processing
- Monitoring alerts for degraded performance


## Success Metrics

### Technical Metrics

**Performance:**
- API response time p95 < 500ms
- Queue processing rate > 100 tasks/sec
- Database query time p95 < 50ms
- System uptime > 99.9%

**Quality:**
- Test coverage > 85%
- Zero critical security vulnerabilities
- Error rate < 0.1%
- Successful deployment with zero downtime

### Business Metrics

**Adoption:**
- 80% of users try new multi-product optimization
- 50% of users upload bulk orders within first month
- 30% of users integrate via warehouse API

**Value Delivery:**
- Average savings increase by 25%
- Processing time reduced by 60%
- User satisfaction score > 4.5/5
- API integration time < 2 hours

### Operational Metrics

**Scalability:**
- Handle 10x current load without degradation
- Queue depth stays below 100 tasks
- Database connections < 70% of pool
- Redis memory usage < 80%

**Reliability:**
- Zero data loss incidents
- Mean time to recovery < 15 minutes
- Successful webhook delivery rate > 99%
- Backup and restore tested monthly

## Conclusion

This design document provides a comprehensive blueprint for upgrading PackOptima from a prototype to a production-ready enterprise logistics optimization platform. The 11-phase approach ensures systematic enhancement of capabilities while maintaining backward compatibility and production-grade quality.

The design emphasizes:
- **Correctness:** Formal specifications and property-based testing
- **Performance:** Sub-second response times and high throughput
- **Scalability:** Queue-based architecture and horizontal scaling
- **Security:** Multi-tenant isolation and comprehensive authentication
- **Reliability:** Error handling, monitoring, and rollback strategies

Implementation following this design will result in a robust, scalable platform capable of handling complex multi-product orders, bulk processing, and seamless warehouse integration while providing advanced analytics and maintaining the simplicity of the current system.
