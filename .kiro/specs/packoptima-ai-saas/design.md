# Design Document: PackOptima AI SaaS Platform

## Overview

PackOptima AI is an enterprise-grade SaaS platform that optimizes packaging decisions for e-commerce and logistics companies. The system analyzes product dimensions, current packaging choices, and available box inventory to recommend optimal packaging solutions that minimize costs and reduce waste. Built with FastAPI backend and React frontend, the platform provides multi-tenant isolation, real-time optimization calculations, executive dashboards, and cost leakage analysis. The core optimization engine uses deterministic volumetric weight calculations and category-based padding logic to ensure products fit safely while maximizing cost efficiency.

## Architecture

```mermaid
graph TD
    A[React Frontend] -->|REST API| B[FastAPI Backend]
    B -->|SQLAlchemy ORM| C[PostgreSQL Database]
    B --> D[Authentication Service]
    B --> E[Optimization Engine]
    B --> F[Analytics Service]
    D -->|JWT Tokens| A
    E -->|Calculations| G[Cost Leakage Module]
    F -->|Aggregations| H[Dashboard Service]
    C -->|Multi-tenant Data| I[Company Workspace]
```

## Main Algorithm/Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as Auth API
    participant O as Optimization API
    participant E as Engine
    participant DB as Database
    
    U->>F: Login
    F->>A: POST /auth/login
    A->>DB: Verify credentials
    DB-->>A: User data
    A-->>F: JWT token
    
    U->>F: Run optimization
    F->>O: POST /optimize (with JWT)
    O->>DB: Fetch products & boxes
    DB-->>O: Company data
    O->>E: Calculate optimal packaging
    E-->>O: Optimization results
    O->>DB: Log optimization run
    O-->>F: Results with savings
    F-->>U: Display recommendations
```


## Components and Interfaces

### Component 1: Authentication Service

**Purpose**: Manages user authentication, JWT token generation, and company-based access control

**Interface**:
```python
from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str
    company_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class AuthService:
    def register_user(self, user_data: UserCreate) -> Token
    def authenticate_user(self, credentials: UserLogin) -> Token
    def verify_token(self, token: str) -> dict
    def get_current_user(self, token: str) -> User
```

**Responsibilities**:
- Hash passwords using bcrypt
- Generate and validate JWT tokens
- Enforce company-based multi-tenancy
- Provide middleware for protected routes

### Component 2: Product Management Service

**Purpose**: Handles CRUD operations for products with company isolation

**Interface**:
```python
class ProductCreate(BaseModel):
    name: str
    sku: str
    category: str
    length_cm: float
    width_cm: float
    height_cm: float
    weight_kg: float
    current_box_id: int
    monthly_order_volume: int

class ProductUpdate(BaseModel):
    name: str | None
    category: str | None
    length_cm: float | None
    width_cm: float | None
    height_cm: float | None
    weight_kg: float | None
    current_box_id: int | None
    monthly_order_volume: int | None

class ProductService:
    def create_product(self, company_id: int, product: ProductCreate) -> Product
    def get_products(self, company_id: int, skip: int, limit: int) -> list[Product]
    def get_product(self, company_id: int, product_id: int) -> Product
    def update_product(self, company_id: int, product_id: int, updates: ProductUpdate) -> Product
    def delete_product(self, company_id: int, product_id: int) -> bool
```

**Responsibilities**:
- Validate product dimensions and weights
- Ensure SKU uniqueness within company
- Filter all queries by company_id
- Track current packaging choices


### Component 3: Packaging Inventory Service

**Purpose**: Manages available box sizes and tracks usage per company

**Interface**:
```python
class BoxCreate(BaseModel):
    name: str
    length_cm: float
    width_cm: float
    height_cm: float
    cost_per_unit: float

class BoxService:
    def create_box(self, company_id: int, box: BoxCreate) -> Box
    def get_boxes(self, company_id: int) -> list[Box]
    def get_box(self, company_id: int, box_id: int) -> Box
    def update_box(self, company_id: int, box_id: int, updates: BoxCreate) -> Box
    def delete_box(self, company_id: int, box_id: int) -> bool
    def track_usage(self, company_id: int, box_id: int, quantity: int) -> None
```

**Responsibilities**:
- Store company-specific box inventory
- Track box dimensions and costs
- Monitor usage patterns
- Support optimization engine queries

### Component 4: Optimization Engine

**Purpose**: Core algorithm that calculates optimal packaging recommendations

**Interface**:
```python
class OptimizationRequest(BaseModel):
    product_ids: list[int] | None  # None = all products

class OptimizationResult(BaseModel):
    product_id: int
    product_name: str
    current_box_id: int
    current_box_name: str
    current_cost: float
    recommended_box_id: int
    recommended_box_name: str
    recommended_cost: float
    savings: float
    savings_percentage: float
    volumetric_weight_current: float
    volumetric_weight_recommended: float

class OptimizationSummary(BaseModel):
    total_products_analyzed: int
    products_with_savings: int
    total_monthly_savings: float
    total_annual_savings: float
    results: list[OptimizationResult]
    run_id: int
    timestamp: datetime

class OptimizationEngine:
    def optimize_packaging(self, company_id: int, request: OptimizationRequest) -> OptimizationSummary
    def calculate_volumetric_weight(self, length: float, width: float, height: float) -> float
    def find_optimal_box(self, product: Product, boxes: list[Box], padding: float) -> Box | None
    def calculate_savings(self, current_box: Box, optimal_box: Box, monthly_volume: int) -> float
```

**Responsibilities**:
- Calculate volumetric weight: (L × W × H) / 5000
- Apply category-based padding logic
- Find smallest box that fits product + padding
- Never recommend boxes smaller than product dimensions
- Calculate cost savings and ROI


### Component 5: Optimization History Service

**Purpose**: Logs and retrieves historical optimization runs

**Interface**:
```python
class OptimizationRun(BaseModel):
    id: int
    company_id: int
    timestamp: datetime
    products_analyzed: int
    total_monthly_savings: float
    total_annual_savings: float

class OptimizationHistoryService:
    def log_optimization_run(self, company_id: int, summary: OptimizationSummary) -> OptimizationRun
    def get_optimization_history(self, company_id: int, limit: int) -> list[OptimizationRun]
    def get_optimization_details(self, company_id: int, run_id: int) -> OptimizationSummary
```

**Responsibilities**:
- Store each optimization run with timestamp
- Track savings over time
- Enable historical analysis
- Support dashboard queries

### Component 6: Analytics Service

**Purpose**: Aggregates data for executive dashboard and insights

**Interface**:
```python
class DashboardMetrics(BaseModel):
    total_products: int
    total_boxes: int
    total_monthly_savings: float
    total_annual_savings: float
    average_savings_per_product: float
    optimization_runs_count: int
    last_optimization_date: datetime | None

class LeakageInsight(BaseModel):
    category: str
    total_leakage: float
    product_count: int
    percentage_of_total: float

class InefficientProduct(BaseModel):
    product_id: int
    product_name: str
    sku: str
    current_cost: float
    potential_savings: float
    savings_percentage: float

class AnalyticsService:
    def get_dashboard_metrics(self, company_id: int) -> DashboardMetrics
    def get_leakage_insights(self, company_id: int) -> list[LeakageInsight]
    def get_top_inefficient_products(self, company_id: int, limit: int) -> list[InefficientProduct]
    def get_savings_trend(self, company_id: int, months: int) -> list[dict]
```

**Responsibilities**:
- Aggregate savings across all products
- Calculate cost leakage by category
- Identify top inefficient SKUs
- Generate trend data for charts
- Provide Pareto analysis (80/20 rule)


### Component 7: Frontend Router

**Purpose**: Manages navigation and route protection in React application

**Interface**:
```typescript
interface RouteConfig {
  path: string;
  element: React.ComponentType;
  protected: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const routes: RouteConfig[] = [
  { path: '/login', element: LoginPage, protected: false },
  { path: '/register', element: RegisterPage, protected: false },
  { path: '/dashboard', element: DashboardPage, protected: true },
  { path: '/products', element: ProductsPage, protected: true },
  { path: '/boxes', element: BoxesPage, protected: true },
  { path: '/optimize', element: OptimizePage, protected: true },
  { path: '/history', element: HistoryPage, protected: true },
  { path: '/leakage', element: LeakagePage, protected: true }
];
```

**Responsibilities**:
- Define application routes
- Protect authenticated routes
- Handle navigation state
- Redirect unauthorized users

### Component 8: API Client Service

**Purpose**: Centralized HTTP client for backend communication

**Interface**:
```typescript
class ApiClient {
  private baseURL: string;
  private token: string | null;

  setToken(token: string): void;
  clearToken(): void;

  // Auth endpoints
  login(email: string, password: string): Promise<Token>;
  register(userData: UserCreate): Promise<Token>;

  // Product endpoints
  getProducts(skip?: number, limit?: number): Promise<Product[]>;
  createProduct(product: ProductCreate): Promise<Product>;
  updateProduct(id: number, updates: ProductUpdate): Promise<Product>;
  deleteProduct(id: number): Promise<void>;

  // Box endpoints
  getBoxes(): Promise<Box[]>;
  createBox(box: BoxCreate): Promise<Box>;

  // Optimization endpoints
  runOptimization(request: OptimizationRequest): Promise<OptimizationSummary>;
  getOptimizationHistory(limit?: number): Promise<OptimizationRun[]>;

  // Analytics endpoints
  getDashboardMetrics(): Promise<DashboardMetrics>;
  getLeakageInsights(): Promise<LeakageInsight[]>;
  getTopInefficientProducts(limit?: number): Promise<InefficientProduct[]>;
}
```

**Responsibilities**:
- Manage JWT token in headers
- Handle HTTP errors consistently
- Provide typed API methods
- Support environment-based URLs


## Data Models

### Model 1: Company

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class Company(Base):
    __tablename__ = "companies"
    
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, unique=True, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="company")
    products = relationship("Product", back_populates="company")
    boxes = relationship("Box", back_populates="company")
    optimization_runs = relationship("OptimizationRun", back_populates="company")
```

**Validation Rules**:
- Company name must be unique
- Company name must be non-empty
- Created timestamp is auto-generated

### Model 2: User

```python
class User(Base):
    __tablename__ = "users"
    
    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String, unique=True, nullable=False, index=True)
    hashed_password: str = Column(String, nullable=False)
    company_id: int = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="users")
```

**Validation Rules**:
- Email must be unique across all users
- Email must be valid format
- Password must be hashed with bcrypt
- Company_id must reference existing company

### Model 3: Product

```python
class Product(Base):
    __tablename__ = "products"
    
    id: int = Column(Integer, primary_key=True, index=True)
    company_id: int = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name: str = Column(String, nullable=False)
    sku: str = Column(String, nullable=False, index=True)
    category: str = Column(String, nullable=False)
    length_cm: float = Column(Float, nullable=False)
    width_cm: float = Column(Float, nullable=False)
    height_cm: float = Column(Float, nullable=False)
    weight_kg: float = Column(Float, nullable=False)
    current_box_id: int = Column(Integer, ForeignKey("boxes.id"), nullable=True)
    monthly_order_volume: int = Column(Integer, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="products")
    current_box = relationship("Box", foreign_keys=[current_box_id])
```

**Validation Rules**:
- SKU must be unique within company
- All dimensions must be positive numbers
- Weight must be positive
- Monthly order volume must be non-negative integer
- Category must be non-empty


### Model 4: Box

```python
class Box(Base):
    __tablename__ = "boxes"
    
    id: int = Column(Integer, primary_key=True, index=True)
    company_id: int = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name: str = Column(String, nullable=False)
    length_cm: float = Column(Float, nullable=False)
    width_cm: float = Column(Float, nullable=False)
    height_cm: float = Column(Float, nullable=False)
    cost_per_unit: float = Column(Float, nullable=False)
    usage_count: int = Column(Integer, default=0)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="boxes")
```

**Validation Rules**:
- All dimensions must be positive numbers
- Cost per unit must be positive
- Usage count must be non-negative
- Box name must be non-empty

### Model 5: OptimizationRun

```python
class OptimizationRun(Base):
    __tablename__ = "optimization_runs"
    
    id: int = Column(Integer, primary_key=True, index=True)
    company_id: int = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    timestamp: datetime = Column(DateTime, default=datetime.utcnow, index=True)
    products_analyzed: int = Column(Integer, nullable=False)
    total_monthly_savings: float = Column(Float, nullable=False)
    total_annual_savings: float = Column(Float, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="optimization_runs")
    results = relationship("OptimizationResult", back_populates="run")
```

**Validation Rules**:
- Products analyzed must be positive integer
- Savings can be zero or positive
- Timestamp is auto-generated

### Model 6: OptimizationResult

```python
class OptimizationResult(Base):
    __tablename__ = "optimization_results"
    
    id: int = Column(Integer, primary_key=True, index=True)
    run_id: int = Column(Integer, ForeignKey("optimization_runs.id"), nullable=False, index=True)
    product_id: int = Column(Integer, ForeignKey("products.id"), nullable=False)
    current_box_id: int = Column(Integer, ForeignKey("boxes.id"), nullable=False)
    recommended_box_id: int = Column(Integer, ForeignKey("boxes.id"), nullable=False)
    current_cost: float = Column(Float, nullable=False)
    recommended_cost: float = Column(Float, nullable=False)
    savings: float = Column(Float, nullable=False)
    savings_percentage: float = Column(Float, nullable=False)
    volumetric_weight_current: float = Column(Float, nullable=False)
    volumetric_weight_recommended: float = Column(Float, nullable=False)
    
    # Relationships
    run = relationship("OptimizationRun", back_populates="results")
    product = relationship("Product")
    current_box = relationship("Box", foreign_keys=[current_box_id])
    recommended_box = relationship("Box", foreign_keys=[recommended_box_id])
```

**Validation Rules**:
- All costs must be non-negative
- Savings can be zero or positive
- Savings percentage calculated as: (savings / current_cost) * 100
- Volumetric weights must be positive


## Algorithmic Pseudocode

### Main Optimization Algorithm

```python
def optimize_packaging(company_id: int, request: OptimizationRequest) -> OptimizationSummary:
    """
    Main optimization algorithm that finds optimal packaging for products.
    
    Preconditions:
    - company_id is valid and exists in database
    - request.product_ids is None or contains valid product IDs
    - All products belong to the specified company
    
    Postconditions:
    - Returns OptimizationSummary with results for all analyzed products
    - Each result contains valid current and recommended box IDs
    - Savings are accurately calculated based on monthly volumes
    - Optimization run is logged in database
    - No product is recommended a box smaller than its dimensions
    
    Loop Invariants:
    - All processed products have valid optimization results
    - Running totals (savings, product count) remain consistent
    """
    
    # Step 1: Fetch products to optimize
    if request.product_ids is None:
        products = db.query(Product).filter(Product.company_id == company_id).all()
    else:
        products = db.query(Product).filter(
            Product.company_id == company_id,
            Product.id.in_(request.product_ids)
        ).all()
    
    # Step 2: Fetch available boxes for company
    boxes = db.query(Box).filter(Box.company_id == company_id).all()
    
    if not boxes:
        raise ValueError("No boxes available for optimization")
    
    # Step 3: Initialize results tracking
    results = []
    total_monthly_savings = 0.0
    products_with_savings = 0
    
    # Step 4: Process each product
    for product in products:
        # Get category padding (default 2cm per side)
        padding = get_category_padding(product.category)
        
        # Calculate required dimensions with padding
        required_length = product.length_cm + (2 * padding)
        required_width = product.width_cm + (2 * padding)
        required_height = product.height_cm + (2 * padding)
        
        # Find optimal box
        optimal_box = find_optimal_box(
            required_length, required_width, required_height, boxes
        )
        
        if optimal_box is None:
            continue  # Skip if no suitable box found
        
        # Get current box
        current_box = product.current_box
        if current_box is None:
            continue  # Skip if no current box assigned
        
        # Calculate costs
        current_monthly_cost = current_box.cost_per_unit * product.monthly_order_volume
        optimal_monthly_cost = optimal_box.cost_per_unit * product.monthly_order_volume
        monthly_savings = current_monthly_cost - optimal_monthly_cost
        
        # Only include if there are savings
        if monthly_savings > 0:
            products_with_savings += 1
            total_monthly_savings += monthly_savings
            
            # Calculate volumetric weights
            vw_current = calculate_volumetric_weight(
                current_box.length_cm, current_box.width_cm, current_box.height_cm
            )
            vw_optimal = calculate_volumetric_weight(
                optimal_box.length_cm, optimal_box.width_cm, optimal_box.height_cm
            )
            
            # Create result record
            result = OptimizationResult(
                product_id=product.id,
                product_name=product.name,
                current_box_id=current_box.id,
                current_box_name=current_box.name,
                current_cost=current_monthly_cost,
                recommended_box_id=optimal_box.id,
                recommended_box_name=optimal_box.name,
                recommended_cost=optimal_monthly_cost,
                savings=monthly_savings,
                savings_percentage=(monthly_savings / current_monthly_cost) * 100,
                volumetric_weight_current=vw_current,
                volumetric_weight_recommended=vw_optimal
            )
            results.append(result)
    
    # Step 5: Calculate annual savings
    total_annual_savings = total_monthly_savings * 12
    
    # Step 6: Log optimization run
    run = OptimizationRun(
        company_id=company_id,
        timestamp=datetime.utcnow(),
        products_analyzed=len(products),
        total_monthly_savings=total_monthly_savings,
        total_annual_savings=total_annual_savings
    )
    db.add(run)
    db.commit()
    
    # Step 7: Save individual results
    for result in results:
        result.run_id = run.id
        db.add(result)
    db.commit()
    
    # Step 8: Return summary
    return OptimizationSummary(
        total_products_analyzed=len(products),
        products_with_savings=products_with_savings,
        total_monthly_savings=total_monthly_savings,
        total_annual_savings=total_annual_savings,
        results=results,
        run_id=run.id,
        timestamp=run.timestamp
    )
```


### Box Selection Algorithm

```python
def find_optimal_box(
    required_length: float,
    required_width: float,
    required_height: float,
    boxes: list[Box]
) -> Box | None:
    """
    Finds the smallest box that can fit the required dimensions.
    
    Preconditions:
    - required_length, required_width, required_height are positive numbers
    - boxes is a non-empty list of Box objects
    - All boxes have positive dimensions
    
    Postconditions:
    - Returns Box that can fit required dimensions, or None if no box fits
    - If Box returned, all its dimensions >= corresponding required dimensions
    - Returned box has minimum volume among all fitting boxes
    
    Loop Invariants:
    - best_box remains None or is a valid fitting box
    - best_volume is infinity or the volume of best_box
    - All previously checked boxes either don't fit or have volume >= best_volume
    """
    
    best_box = None
    best_volume = float('inf')
    
    for box in boxes:
        # Check if box can fit product (considering all orientations)
        dimensions_product = sorted([required_length, required_width, required_height])
        dimensions_box = sorted([box.length_cm, box.width_cm, box.height_cm])
        
        # Box fits if each sorted dimension is >= corresponding product dimension
        fits = all(
            box_dim >= prod_dim 
            for box_dim, prod_dim in zip(dimensions_box, dimensions_product)
        )
        
        if fits:
            # Calculate box volume
            volume = box.length_cm * box.width_cm * box.height_cm
            
            # Keep track of smallest fitting box
            if volume < best_volume:
                best_box = box
                best_volume = volume
    
    return best_box
```

### Volumetric Weight Calculation

```python
def calculate_volumetric_weight(length_cm: float, width_cm: float, height_cm: float) -> float:
    """
    Calculates volumetric weight using industry standard formula.
    
    Preconditions:
    - length_cm > 0
    - width_cm > 0
    - height_cm > 0
    
    Postconditions:
    - Returns positive float representing volumetric weight in kg
    - Formula: (L × W × H) / 5000
    """
    
    return (length_cm * width_cm * height_cm) / 5000.0
```

### Category Padding Logic

```python
def get_category_padding(category: str) -> float:
    """
    Returns padding in centimeters based on product category.
    
    Preconditions:
    - category is non-empty string
    
    Postconditions:
    - Returns positive float representing padding in cm
    - Default padding is 2.0 cm if category not found
    """
    
    padding_map = {
        "electronics": 3.0,
        "fragile": 4.0,
        "clothing": 1.0,
        "books": 1.5,
        "toys": 2.0,
        "default": 2.0
    }
    
    return padding_map.get(category.lower(), padding_map["default"])
```


### Cost Leakage Analysis Algorithm

```python
def calculate_cost_leakage_by_category(company_id: int) -> list[LeakageInsight]:
    """
    Analyzes cost leakage grouped by product category using Pareto principle.
    
    Preconditions:
    - company_id is valid and exists in database
    - Company has products and optimization history
    
    Postconditions:
    - Returns list of LeakageInsight sorted by total_leakage descending
    - Sum of all percentage_of_total equals 100%
    - Each insight contains valid category data
    
    Loop Invariants:
    - All processed categories have accurate leakage calculations
    - Running total of leakage remains consistent
    """
    
    # Step 1: Get latest optimization run
    latest_run = db.query(OptimizationRun).filter(
        OptimizationRun.company_id == company_id
    ).order_by(OptimizationRun.timestamp.desc()).first()
    
    if not latest_run:
        return []
    
    # Step 2: Get all results with product categories
    results = db.query(
        OptimizationResult, Product.category
    ).join(
        Product, OptimizationResult.product_id == Product.id
    ).filter(
        OptimizationResult.run_id == latest_run.id
    ).all()
    
    # Step 3: Aggregate by category
    category_leakage = {}
    total_leakage = 0.0
    
    for result, category in results:
        monthly_leakage = result.savings
        annual_leakage = monthly_leakage * 12
        
        if category not in category_leakage:
            category_leakage[category] = {
                "total_leakage": 0.0,
                "product_count": 0
            }
        
        category_leakage[category]["total_leakage"] += annual_leakage
        category_leakage[category]["product_count"] += 1
        total_leakage += annual_leakage
    
    # Step 4: Calculate percentages and create insights
    insights = []
    for category, data in category_leakage.items():
        percentage = (data["total_leakage"] / total_leakage * 100) if total_leakage > 0 else 0
        
        insight = LeakageInsight(
            category=category,
            total_leakage=data["total_leakage"],
            product_count=data["product_count"],
            percentage_of_total=percentage
        )
        insights.append(insight)
    
    # Step 5: Sort by leakage descending (Pareto analysis)
    insights.sort(key=lambda x: x.total_leakage, reverse=True)
    
    return insights
```

### Dashboard Metrics Aggregation

```python
def get_dashboard_metrics(company_id: int) -> DashboardMetrics:
    """
    Aggregates key metrics for executive dashboard.
    
    Preconditions:
    - company_id is valid and exists in database
    
    Postconditions:
    - Returns DashboardMetrics with all fields populated
    - All counts are non-negative integers
    - All monetary values are non-negative floats
    """
    
    # Count products
    total_products = db.query(Product).filter(
        Product.company_id == company_id
    ).count()
    
    # Count boxes
    total_boxes = db.query(Box).filter(
        Box.company_id == company_id
    ).count()
    
    # Get latest optimization run
    latest_run = db.query(OptimizationRun).filter(
        OptimizationRun.company_id == company_id
    ).order_by(OptimizationRun.timestamp.desc()).first()
    
    if latest_run:
        total_monthly_savings = latest_run.total_monthly_savings
        total_annual_savings = latest_run.total_annual_savings
        last_optimization_date = latest_run.timestamp
        
        # Calculate average savings per product
        if latest_run.products_analyzed > 0:
            average_savings = total_monthly_savings / latest_run.products_analyzed
        else:
            average_savings = 0.0
    else:
        total_monthly_savings = 0.0
        total_annual_savings = 0.0
        average_savings = 0.0
        last_optimization_date = None
    
    # Count optimization runs
    optimization_runs_count = db.query(OptimizationRun).filter(
        OptimizationRun.company_id == company_id
    ).count()
    
    return DashboardMetrics(
        total_products=total_products,
        total_boxes=total_boxes,
        total_monthly_savings=total_monthly_savings,
        total_annual_savings=total_annual_savings,
        average_savings_per_product=average_savings,
        optimization_runs_count=optimization_runs_count,
        last_optimization_date=last_optimization_date
    )
```


## Key Functions with Formal Specifications

### Function 1: authenticate_user()

```python
def authenticate_user(email: str, password: str) -> Token:
    """Authenticates user and returns JWT token."""
```

**Preconditions:**
- `email` is non-empty string in valid email format
- `password` is non-empty string
- User with email exists in database

**Postconditions:**
- Returns Token object with valid JWT access_token
- Token contains user_id and company_id claims
- Token is signed with SECRET_KEY
- Token expires in 24 hours
- If authentication fails, raises HTTPException with 401 status

**Loop Invariants:** N/A (no loops)

### Function 2: create_product()

```python
def create_product(company_id: int, product: ProductCreate) -> Product:
    """Creates new product for company."""
```

**Preconditions:**
- `company_id` is valid and exists in database
- `product.sku` is unique within company
- All dimensions (length, width, height) are positive floats
- `product.weight_kg` is positive float
- `product.monthly_order_volume` is non-negative integer
- `product.category` is non-empty string

**Postconditions:**
- Returns Product object with generated ID
- Product is persisted in database
- Product.company_id equals input company_id
- Product.created_at is set to current UTC time
- If SKU already exists for company, raises HTTPException with 400 status

**Loop Invariants:** N/A (no loops)

### Function 3: run_optimization()

```python
def run_optimization(company_id: int, request: OptimizationRequest) -> OptimizationSummary:
    """Runs packaging optimization for specified products."""
```

**Preconditions:**
- `company_id` is valid and exists in database
- Company has at least one box in inventory
- If `request.product_ids` is not None, all IDs belong to company
- All products have current_box_id assigned

**Postconditions:**
- Returns OptimizationSummary with results for all analyzed products
- OptimizationRun is created and persisted in database
- All OptimizationResult records are persisted
- No product is recommended a box smaller than its dimensions + padding
- Savings calculations are accurate based on monthly volumes
- If no boxes available, raises HTTPException with 400 status

**Loop Invariants:**
- For product processing loop: All previously processed products have valid results
- Running totals (savings, product count) remain mathematically consistent


### Function 4: get_current_user()

```python
def get_current_user(token: str) -> User:
    """Validates JWT token and returns current user."""
```

**Preconditions:**
- `token` is non-empty string
- Token is properly formatted JWT

**Postconditions:**
- Returns User object if token is valid
- User object includes company relationship
- If token is invalid or expired, raises HTTPException with 401 status
- If user not found, raises HTTPException with 404 status

**Loop Invariants:** N/A (no loops)

### Function 5: find_optimal_box()

```python
def find_optimal_box(
    required_length: float,
    required_width: float, 
    required_height: float,
    boxes: list[Box]
) -> Box | None:
    """Finds smallest box that fits required dimensions."""
```

**Preconditions:**
- All required dimensions are positive floats
- `boxes` is non-empty list
- All boxes have positive dimensions

**Postconditions:**
- Returns Box with minimum volume that fits dimensions, or None
- If Box returned, all dimensions >= required dimensions (considering rotation)
- Box selection considers all possible orientations
- If no box fits, returns None

**Loop Invariants:**
- For box iteration: `best_box` is None or has volume <= all previously checked fitting boxes
- `best_volume` equals volume of `best_box` or infinity if no box found yet

### Function 6: calculate_volumetric_weight()

```python
def calculate_volumetric_weight(length_cm: float, width_cm: float, height_cm: float) -> float:
    """Calculates volumetric weight using formula (L × W × H) / 5000."""
```

**Preconditions:**
- `length_cm` > 0
- `width_cm` > 0
- `height_cm` > 0

**Postconditions:**
- Returns positive float
- Result equals (length_cm × width_cm × height_cm) / 5000
- Precision maintained to 2 decimal places

**Loop Invariants:** N/A (no loops)


## Example Usage

### Example 1: User Registration and Authentication

```python
# Backend API endpoint
@router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create company
    company = Company(name=user_data.company_name)
    db.add(company)
    db.commit()
    
    # Hash password
    hashed_password = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt())
    
    # Create user
    user = User(
        email=user_data.email,
        hashed_password=hashed_password.decode(),
        company_id=company.id
    )
    db.add(user)
    db.commit()
    
    # Generate token
    token = create_access_token({"user_id": user.id, "company_id": company.id})
    return Token(access_token=token, token_type="bearer")

# Frontend usage
const handleRegister = async (email: string, password: string, companyName: string) => {
  const response = await apiClient.register({ email, password, company_name: companyName });
  localStorage.setItem('token', response.access_token);
  navigate('/dashboard');
};
```

### Example 2: Creating Products

```python
# Backend API endpoint
@router.post("/products", response_model=Product)
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check SKU uniqueness
    existing = db.query(Product).filter(
        Product.company_id == current_user.company_id,
        Product.sku == product.sku
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    # Create product
    new_product = Product(
        company_id=current_user.company_id,
        **product.dict()
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

# Frontend usage
const handleCreateProduct = async (productData: ProductCreate) => {
  const product = await apiClient.createProduct(productData);
  setProducts([...products, product]);
  toast.success('Product created successfully');
};
```

### Example 3: Running Optimization

```python
# Backend API endpoint
@router.post("/optimize", response_model=OptimizationSummary)
async def run_optimization(
    request: OptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    engine = OptimizationEngine(db)
    summary = engine.optimize_packaging(current_user.company_id, request)
    return summary

# Frontend usage
const handleOptimize = async () => {
  setLoading(true);
  try {
    const summary = await apiClient.runOptimization({ product_ids: null });
    setOptimizationResults(summary);
    toast.success(`Found ${summary.products_with_savings} products with savings!`);
  } catch (error) {
    toast.error('Optimization failed');
  } finally {
    setLoading(false);
  }
};
```

### Example 4: Dashboard Metrics Display

```typescript
// Frontend component
const DashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  
  useEffect(() => {
    const fetchMetrics = async () => {
      const data = await apiClient.getDashboardMetrics();
      setMetrics(data);
    };
    fetchMetrics();
  }, []);
  
  if (!metrics) return <LoadingSpinner />;
  
  return (
    <div className="dashboard">
      <KPICard 
        title="Annual Savings" 
        value={`$${metrics.total_annual_savings.toLocaleString()}`}
        icon={<DollarIcon />}
      />
      <KPICard 
        title="Total Products" 
        value={metrics.total_products}
        icon={<PackageIcon />}
      />
      <KPICard 
        title="Optimization Runs" 
        value={metrics.optimization_runs_count}
        icon={<ChartIcon />}
      />
      <SavingsTrendChart companyId={user.company_id} />
      <LeakageBreakdownChart companyId={user.company_id} />
    </div>
  );
};
```


### Example 5: Multi-Tenant Data Isolation

```python
# Middleware for automatic company filtering
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# All queries automatically filtered by company_id
@router.get("/products", response_model=list[Product])
async def get_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Automatic company isolation
    products = db.query(Product).filter(
        Product.company_id == current_user.company_id
    ).all()
    return products
```

### Example 6: Cost Leakage Analysis

```python
# Backend endpoint
@router.get("/analytics/leakage", response_model=list[LeakageInsight])
async def get_leakage_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analytics = AnalyticsService(db)
    insights = analytics.calculate_cost_leakage_by_category(current_user.company_id)
    return insights

# Frontend visualization
const LeakagePage: React.FC = () => {
  const [insights, setInsights] = useState<LeakageInsight[]>([]);
  
  useEffect(() => {
    const fetchInsights = async () => {
      const data = await apiClient.getLeakageInsights();
      setInsights(data);
    };
    fetchInsights();
  }, []);
  
  return (
    <div className="leakage-page">
      <h1>Cost Leakage Analysis</h1>
      <ParetoChart data={insights} />
      <table className="leakage-table">
        <thead>
          <tr>
            <th>Category</th>
            <th>Annual Leakage</th>
            <th>Products</th>
            <th>% of Total</th>
          </tr>
        </thead>
        <tbody>
          {insights.map(insight => (
            <tr key={insight.category}>
              <td>{insight.category}</td>
              <td>${insight.total_leakage.toLocaleString()}</td>
              <td>{insight.product_count}</td>
              <td>{insight.percentage_of_total.toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```


## Correctness Properties

### Property 1: Multi-Tenant Isolation
**Universal Quantification:**
```
∀ user₁, user₂ ∈ Users, company₁, company₂ ∈ Companies:
  (user₁.company_id = company₁.id ∧ user₂.company_id = company₂.id ∧ company₁ ≠ company₂)
  ⟹ (accessible_data(user₁) ∩ accessible_data(user₂) = ∅)
```

**Meaning:** Users from different companies can never access each other's data.

**Test Approach:** Property-based test that creates multiple companies and verifies data isolation across all API endpoints.

**Validates: Requirements 3.1, 3.2, 3.4, 3.5, 3.6, 4.8, 4.9, 4.10, 5.5, 5.6, 5.7, 10.2, 13.6**

### Property 2: Optimization Never Reduces Box Size Below Product Dimensions
**Universal Quantification:**
```
∀ product ∈ Products, box ∈ Boxes, padding ∈ ℝ⁺:
  recommended_box(product, padding) = box
  ⟹ (box.length ≥ product.length + 2×padding ∧
      box.width ≥ product.width + 2×padding ∧
      box.height ≥ product.height + 2×padding)
```

**Meaning:** Recommended boxes always accommodate product dimensions plus required padding.

**Test Approach:** Property-based test with random product dimensions and padding values, verifying all recommendations meet size constraints.

**Validates: Requirements 7.7, 8.1, 8.6**

### Property 3: Volumetric Weight Calculation Consistency
**Universal Quantification:**
```
∀ length, width, height ∈ ℝ⁺:
  volumetric_weight(length, width, height) = (length × width × height) / 5000
```

**Meaning:** Volumetric weight calculation always follows the exact formula.

**Test Approach:** Property-based test with random positive dimensions, verifying formula accuracy.

**Validates: Requirements 6.1, 6.2, 6.3**

### Property 4: Savings Calculation Accuracy
**Universal Quantification:**
```
∀ product ∈ Products, current_box, optimal_box ∈ Boxes:
  savings(product, current_box, optimal_box) = 
    (current_box.cost × product.monthly_volume) - (optimal_box.cost × product.monthly_volume)
```

**Meaning:** Savings are always calculated as the difference between current and optimal monthly costs.

**Test Approach:** Property-based test with random costs and volumes, verifying savings formula.

**Validates: Requirements 9.6, 9.7, 9.11**

### Property 5: JWT Token Contains Required Claims
**Universal Quantification:**
```
∀ user ∈ Users, token ∈ Tokens:
  generate_token(user) = token
  ⟹ (decode(token).user_id = user.id ∧ decode(token).company_id = user.company_id)
```

**Meaning:** All JWT tokens contain user_id and company_id claims.

**Test Approach:** Property-based test generating tokens for random users and verifying claim presence.

**Validates: Requirements 1.5, 2.2, 2.6**

### Property 6: Optimization Results Are Deterministic
**Universal Quantification:**
```
∀ company ∈ Companies, products ⊆ Products, boxes ⊆ Boxes:
  (state(products, boxes) unchanged)
  ⟹ (optimize(company, products) = optimize(company, products))
```

**Meaning:** Running optimization twice with same data produces identical results.

**Test Approach:** Property-based test running optimization multiple times and comparing results.

**Validates: Requirements 27.1, 27.2, 27.4**

### Property 7: Box Selection Minimizes Volume
**Universal Quantification:**
```
∀ product ∈ Products, boxes ⊆ Boxes, selected_box ∈ Boxes:
  (find_optimal_box(product, boxes) = selected_box ∧ selected_box ≠ null)
  ⟹ (∀ other_box ∈ boxes: fits(product, other_box) ⟹ volume(selected_box) ≤ volume(other_box))
```

**Meaning:** Selected box has minimum volume among all boxes that fit the product.

**Test Approach:** Property-based test with random box inventories, verifying optimal selection.

**Validates: Requirements 8.2, 8.3, 8.4, 8.7**

### Property 8: Password Hashing Is One-Way
**Universal Quantification:**
```
∀ password ∈ Strings, hashed ∈ Strings:
  hash(password) = hashed
  ⟹ (∃ no efficient function f: f(hashed) = password)
```

**Meaning:** Hashed passwords cannot be reversed to original passwords.

**Test Approach:** Unit test verifying bcrypt hashing and that plain passwords are never stored.

**Validates: Requirement 1.3**

### Property 9: SKU Uniqueness Within Company
**Universal Quantification:**
```
∀ product₁, product₂ ∈ Products, company ∈ Companies:
  (product₁.company_id = company.id ∧ product₂.company_id = company.id ∧ product₁ ≠ product₂)
  ⟹ (product₁.sku ≠ product₂.sku)
```

**Meaning:** No two products within the same company can have the same SKU.

**Test Approach:** Property-based test attempting to create products with duplicate SKUs and verifying rejection.

**Validates: Requirements 4.2, 30.6**

### Property 10: Optimization History Ordering
**Universal Quantification:**
```
∀ runs ∈ OptimizationRuns, company ∈ Companies:
  get_optimization_history(company) = runs
  ⟹ (∀ i, j: i < j ⟹ runs[i].timestamp ≥ runs[j].timestamp)
```

**Meaning:** Optimization history is always returned in descending chronological order.

**Test Approach:** Property-based test creating multiple optimization runs and verifying sort order.

**Validates: Requirement 10.3**

### Property 11: Cost Leakage Percentages Sum to 100
**Universal Quantification:**
```
∀ insights ∈ LeakageInsights, company ∈ Companies:
  get_leakage_insights(company) = insights
  ⟹ (Σ insight.percentage_of_total for insight in insights) = 100
```

**Meaning:** The sum of all category leakage percentages always equals 100%.

**Test Approach:** Property-based test with random optimization data, verifying percentage sum.

**Validates: Requirement 12.7**

### Property 12: Leakage Insights Sorted by Total
**Universal Quantification:**
```
∀ insights ∈ LeakageInsights, company ∈ Companies:
  get_leakage_insights(company) = insights
  ⟹ (∀ i, j: i < j ⟹ insights[i].total_leakage ≥ insights[j].total_leakage)
```

**Meaning:** Cost leakage insights are always sorted by total leakage in descending order (Pareto principle).

**Test Approach:** Property-based test verifying sort order of leakage results.

**Validates: Requirement 12.5**

### Property 13: Transaction Atomicity
**Universal Quantification:**
```
∀ operations ∈ DatabaseOperations:
  (transaction_fails(operations) ⟹ database_state_unchanged) ∧
  (transaction_succeeds(operations) ⟹ all_operations_applied)
```

**Meaning:** Database transactions either fully succeed or fully rollback with no partial changes.

**Test Approach:** Property-based test simulating transaction failures and verifying rollback behavior.

**Validates: Requirements 25.2, 25.4, 25.5**

### Property 14: Top Inefficient Products Ordering
**Universal Quantification:**
```
∀ products ∈ InefficientProducts, company ∈ Companies:
  get_top_inefficient_products(company) = products
  ⟹ (∀ i, j: i < j ⟹ products[i].potential_savings ≥ products[j].potential_savings)
```

**Meaning:** Inefficient products are always sorted by potential savings in descending order.

**Test Approach:** Property-based test verifying sort order of inefficient products.

**Validates: Requirement 13.3**


## Error Handling

### Error Scenario 1: Invalid Authentication

**Condition:** User provides incorrect email or password, or JWT token is expired/invalid

**Response:**
- Return HTTP 401 Unauthorized
- Clear any stored tokens on frontend
- Provide clear error message: "Invalid credentials" or "Session expired"

**Recovery:**
- Redirect user to login page
- Allow user to re-authenticate
- Frontend clears all authentication state

### Error Scenario 2: Duplicate SKU

**Condition:** User attempts to create product with SKU that already exists for their company

**Response:**
- Return HTTP 400 Bad Request
- Error message: "SKU already exists for your company"
- Do not create product in database

**Recovery:**
- Display error message to user
- Keep form data populated
- Allow user to modify SKU and retry

### Error Scenario 3: No Boxes Available

**Condition:** Company attempts to run optimization but has no boxes in inventory

**Response:**
- Return HTTP 400 Bad Request
- Error message: "No boxes available. Please add boxes to your inventory first."
- Do not create optimization run

**Recovery:**
- Display error with link to box management page
- Guide user to add boxes before optimizing
- Prevent optimization button if no boxes exist

### Error Scenario 4: No Suitable Box Found

**Condition:** During optimization, no box in inventory can fit a product (even with padding)

**Response:**
- Skip product in optimization results
- Log warning in application logs
- Continue processing other products

**Recovery:**
- Display list of skipped products to user
- Suggest adding larger boxes to inventory
- Provide product dimensions for reference

### Error Scenario 5: Database Connection Failure

**Condition:** PostgreSQL database is unreachable or connection pool exhausted

**Response:**
- Return HTTP 503 Service Unavailable
- Error message: "Service temporarily unavailable. Please try again."
- Log error with full stack trace

**Recovery:**
- Frontend displays retry button
- Implement exponential backoff for retries
- Backend attempts to reconnect to database
- Health endpoint reports unhealthy status

### Error Scenario 6: Unauthorized Company Access

**Condition:** User attempts to access resources belonging to different company

**Response:**
- Return HTTP 403 Forbidden
- Error message: "Access denied"
- Log security event

**Recovery:**
- Display error message
- Do not reveal existence of resource
- Redirect to user's dashboard

### Error Scenario 7: Invalid Product Dimensions

**Condition:** User provides negative or zero dimensions/weight for product

**Response:**
- Return HTTP 422 Unprocessable Entity
- Error message: "All dimensions and weight must be positive numbers"
- Highlight invalid fields in form

**Recovery:**
- Display validation errors inline
- Keep valid field values
- Allow user to correct and resubmit

### Error Scenario 8: CORS Configuration Error

**Condition:** Frontend deployed on different domain than backend expects

**Response:**
- Browser blocks request with CORS error
- Network tab shows preflight failure

**Recovery:**
- Backend reads ALLOWED_ORIGINS from environment variable
- Support wildcard for development
- Restrict to specific domains in production
- Log CORS rejections for debugging


## Testing Strategy

### Unit Testing Approach

**Backend (Python with pytest):**
- Test each service method in isolation
- Mock database dependencies using pytest fixtures
- Test validation logic for all Pydantic schemas
- Test password hashing and JWT token generation
- Test volumetric weight calculation with known values
- Test box selection algorithm with various scenarios
- Test category padding logic for all categories
- Coverage goal: 90%+ for business logic

**Key Test Cases:**
```python
def test_volumetric_weight_calculation():
    # Test: (10 × 10 × 10) / 5000 = 0.2
    assert calculate_volumetric_weight(10, 10, 10) == 0.2

def test_find_optimal_box_selects_smallest():
    boxes = [
        Box(length=30, width=30, height=30, cost=5),
        Box(length=20, width=20, height=20, cost=3),
        Box(length=40, width=40, height=40, cost=7)
    ]
    optimal = find_optimal_box(15, 15, 15, boxes)
    assert optimal.length == 20  # Smallest fitting box

def test_password_hashing_is_secure():
    password = "test123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) == True
    assert verify_password("wrong", hashed) == False
```

**Frontend (TypeScript with Vitest):**
- Test React components with React Testing Library
- Test API client methods with mocked fetch
- Test authentication context state management
- Test form validation logic
- Test routing and navigation
- Coverage goal: 80%+ for components and utilities

### Property-Based Testing Approach

**Property Test Library:** Hypothesis (Python backend)

**Property Tests to Implement:**

1. **Multi-Tenant Isolation Property:**
```python
from hypothesis import given, strategies as st

@given(
    company1_id=st.integers(min_value=1, max_value=1000),
    company2_id=st.integers(min_value=1, max_value=1000)
)
def test_companies_cannot_access_each_others_data(company1_id, company2_id):
    assume(company1_id != company2_id)
    
    # Create products for both companies
    product1 = create_product(company1_id, sample_product_data())
    product2 = create_product(company2_id, sample_product_data())
    
    # Verify company1 cannot see company2's products
    company1_products = get_products(company1_id)
    assert product2.id not in [p.id for p in company1_products]
    
    # Verify company2 cannot see company1's products
    company2_products = get_products(company2_id)
    assert product1.id not in [p.id for p in company2_products]
```

2. **Box Selection Always Fits Product:**
```python
@given(
    length=st.floats(min_value=1, max_value=100),
    width=st.floats(min_value=1, max_value=100),
    height=st.floats(min_value=1, max_value=100),
    padding=st.floats(min_value=0, max_value=10)
)
def test_selected_box_always_fits_product(length, width, height, padding):
    product = Product(length_cm=length, width_cm=width, height_cm=height)
    boxes = generate_random_boxes(count=10)
    
    optimal_box = find_optimal_box(
        length + 2*padding,
        width + 2*padding,
        height + 2*padding,
        boxes
    )
    
    if optimal_box is not None:
        # Check all orientations
        product_dims = sorted([length + 2*padding, width + 2*padding, height + 2*padding])
        box_dims = sorted([optimal_box.length_cm, optimal_box.width_cm, optimal_box.height_cm])
        
        assert all(box_dim >= prod_dim for box_dim, prod_dim in zip(box_dims, product_dims))
```

3. **Optimization Is Deterministic:**
```python
@given(
    product_count=st.integers(min_value=1, max_value=50),
    box_count=st.integers(min_value=1, max_value=20)
)
def test_optimization_is_deterministic(product_count, box_count):
    company_id = create_test_company()
    products = [create_random_product(company_id) for _ in range(product_count)]
    boxes = [create_random_box(company_id) for _ in range(box_count)]
    
    # Run optimization twice
    result1 = optimize_packaging(company_id, OptimizationRequest(product_ids=None))
    result2 = optimize_packaging(company_id, OptimizationRequest(product_ids=None))
    
    # Results should be identical
    assert result1.total_monthly_savings == result2.total_monthly_savings
    assert len(result1.results) == len(result2.results)
    
    for r1, r2 in zip(result1.results, result2.results):
        assert r1.recommended_box_id == r2.recommended_box_id
        assert r1.savings == r2.savings
```

4. **Savings Calculation Accuracy:**
```python
@given(
    current_cost=st.floats(min_value=0.01, max_value=100),
    optimal_cost=st.floats(min_value=0.01, max_value=100),
    monthly_volume=st.integers(min_value=1, max_value=10000)
)
def test_savings_calculation_is_accurate(current_cost, optimal_cost, monthly_volume):
    expected_savings = (current_cost - optimal_cost) * monthly_volume
    
    current_box = Box(cost_per_unit=current_cost)
    optimal_box = Box(cost_per_unit=optimal_cost)
    product = Product(monthly_order_volume=monthly_volume)
    
    calculated_savings = calculate_savings(product, current_box, optimal_box)
    
    assert abs(calculated_savings - expected_savings) < 0.01  # Allow floating point tolerance
```

### Integration Testing Approach

**API Integration Tests:**
- Test complete user flows: register → login → create product → optimize
- Test authentication middleware on protected endpoints
- Test database transactions and rollbacks
- Test CORS configuration with different origins
- Use test database with fixtures
- Run with pytest-asyncio for async endpoints

**Key Integration Test Scenarios:**
1. Complete optimization workflow from product creation to results
2. Multi-user concurrent access with different companies
3. Optimization history persistence and retrieval
4. Dashboard metrics aggregation accuracy
5. Error handling across API boundaries

**Frontend Integration Tests:**
- Test complete user journeys with Playwright or Cypress
- Test authentication flow with real API calls (mocked backend)
- Test form submissions and error handling
- Test navigation between pages
- Test chart rendering with real data


## Performance Considerations

### Database Query Optimization

**Indexing Strategy:**
- Index on `company_id` for all multi-tenant tables (products, boxes, optimization_runs)
- Index on `email` in users table for login queries
- Index on `sku` in products table for uniqueness checks
- Composite index on `(company_id, timestamp)` for optimization_runs to speed up history queries
- Index on `run_id` in optimization_results for join performance

**Query Optimization:**
- Use `select_related()` and `prefetch_related()` in SQLAlchemy to avoid N+1 queries
- Limit result sets with pagination (default 50 items per page)
- Use database-level aggregations for dashboard metrics instead of application-level calculations
- Implement query result caching for dashboard metrics (5-minute TTL)

### API Response Times

**Target Response Times:**
- Authentication endpoints: < 200ms
- CRUD operations: < 100ms
- Optimization endpoint: < 2s for 100 products
- Dashboard metrics: < 500ms
- Analytics endpoints: < 1s

**Optimization Strategies:**
- Run optimization calculations in background for large product sets (>500 products)
- Implement request timeout of 30 seconds
- Use connection pooling for database (pool size: 20)
- Enable gzip compression for API responses

### Frontend Performance

**Bundle Size Optimization:**
- Code splitting by route (lazy loading)
- Tree shaking to remove unused code
- Target bundle size: < 200KB gzipped for initial load

**Rendering Optimization:**
- Use React.memo for expensive components
- Virtualize large tables (react-window or similar)
- Debounce search inputs (300ms delay)
- Implement optimistic UI updates for better perceived performance

### Scalability Considerations

**Horizontal Scaling:**
- Stateless API design allows multiple backend instances
- JWT tokens enable distributed authentication
- Database connection pooling per instance

**Vertical Scaling:**
- PostgreSQL can handle 10,000+ companies on single instance
- Optimization engine is CPU-bound, benefits from more cores
- Consider read replicas for analytics queries if needed

**Caching Strategy:**
- Cache dashboard metrics in Redis (optional, for high traffic)
- Cache box inventory per company (invalidate on updates)
- Browser caching for static assets (1 year)


## Security Considerations

### Authentication & Authorization

**Password Security:**
- Use bcrypt for password hashing (cost factor: 12)
- Enforce minimum password length: 8 characters
- Never log or display passwords in plain text
- Implement rate limiting on login endpoint (5 attempts per minute per IP)

**JWT Token Security:**
- Sign tokens with HS256 algorithm
- Store SECRET_KEY in environment variable (never in code)
- Set token expiration to 24 hours
- Include user_id and company_id in token claims
- Validate token signature on every protected endpoint
- Frontend stores token in localStorage (consider httpOnly cookies for enhanced security)

**Multi-Tenant Security:**
- Always filter queries by company_id from authenticated user
- Never trust company_id from request body
- Validate user belongs to company before any operation
- Log unauthorized access attempts

### API Security

**CORS Configuration:**
- Whitelist specific frontend origins in production
- Use environment variable ALLOWED_ORIGINS
- Allow credentials for cookie-based auth if implemented
- Restrict allowed methods to: GET, POST, PUT, DELETE, OPTIONS

**Input Validation:**
- Validate all inputs with Pydantic schemas
- Sanitize string inputs to prevent SQL injection (SQLAlchemy ORM provides protection)
- Validate numeric ranges (dimensions > 0, costs > 0)
- Limit string lengths to prevent DoS
- Validate email format with regex

**Rate Limiting:**
- Implement rate limiting middleware
- Limits per endpoint:
  - Login: 5 requests/minute
  - Registration: 3 requests/minute
  - Optimization: 10 requests/minute
  - Other endpoints: 100 requests/minute
- Return HTTP 429 when limit exceeded

### Database Security

**Connection Security:**
- Use SSL/TLS for database connections in production
- Store database credentials in environment variables
- Use connection pooling with max connections limit
- Implement prepared statements (SQLAlchemy default)

**Data Protection:**
- Never store plain text passwords
- Encrypt sensitive data at rest (if applicable)
- Regular database backups (daily)
- Implement soft deletes for audit trail

### Deployment Security

**Environment Variables:**
```bash
# Required environment variables
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=<random-256-bit-key>
ALLOWED_ORIGINS=https://app.packoptima.com,https://www.packoptima.com
ENVIRONMENT=production
```

**HTTPS Enforcement:**
- Redirect all HTTP traffic to HTTPS
- Use HSTS header: `Strict-Transport-Security: max-age=31536000`
- Implement proper SSL certificate management

**Security Headers:**
```python
# FastAPI middleware
app.add_middleware(
    SecurityHeadersMiddleware,
    headers={
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }
)
```

### Threat Mitigation

**SQL Injection:** Prevented by SQLAlchemy ORM parameterized queries
**XSS:** React escapes output by default, validate all inputs
**CSRF:** JWT tokens in headers (not cookies) prevent CSRF
**Brute Force:** Rate limiting on authentication endpoints
**Data Leakage:** Multi-tenant isolation with company_id filtering
**DoS:** Rate limiting, request timeouts, input size limits


## Dependencies

### Backend Dependencies (Python)

**Core Framework:**
- `fastapi==0.104.1` - Modern web framework for building APIs
- `uvicorn[standard]==0.24.0` - ASGI server for running FastAPI
- `python-multipart==0.0.6` - Form data parsing

**Database:**
- `sqlalchemy==2.0.23` - SQL toolkit and ORM
- `psycopg2-binary==2.9.9` - PostgreSQL adapter
- `alembic==1.12.1` - Database migration tool

**Authentication:**
- `python-jose[cryptography]==3.3.0` - JWT token handling
- `passlib[bcrypt]==1.7.4` - Password hashing
- `python-dotenv==1.0.0` - Environment variable management

**Validation:**
- `pydantic==2.5.0` - Data validation using Python type hints
- `email-validator==2.1.0` - Email validation

**CORS & Middleware:**
- `fastapi-cors==0.0.6` - CORS middleware (or use built-in)

**Testing:**
- `pytest==7.4.3` - Testing framework
- `pytest-asyncio==0.21.1` - Async test support
- `hypothesis==6.92.1` - Property-based testing
- `httpx==0.25.2` - HTTP client for testing API endpoints

**Development:**
- `black==23.11.0` - Code formatter
- `flake8==6.1.0` - Linting
- `mypy==1.7.1` - Static type checking

### Frontend Dependencies (TypeScript/React)

**Core Framework:**
- `react==18.2.0` - UI library
- `react-dom==18.2.0` - React DOM rendering
- `react-router-dom==6.20.0` - Client-side routing
- `vite==5.0.0` - Build tool and dev server
- `typescript==5.3.2` - Type safety

**State Management:**
- `react-context` (built-in) - Global state management
- Or `zustand==4.4.7` - Lightweight state management alternative

**HTTP Client:**
- `axios==1.6.2` - HTTP client for API calls

**UI Components:**
- `@headlessui/react==1.7.17` - Unstyled accessible components
- `@heroicons/react==2.0.18` - Icon library
- `tailwindcss==3.3.5` - Utility-first CSS framework

**Charts:**
- `recharts==2.10.3` - Composable charting library
- Or `chart.js==4.4.0` with `react-chartjs-2==5.2.0`

**Forms:**
- `react-hook-form==7.48.2` - Form validation and handling
- `zod==3.22.4` - Schema validation

**Notifications:**
- `react-hot-toast==2.4.1` - Toast notifications

**Testing:**
- `vitest==1.0.4` - Unit testing framework
- `@testing-library/react==14.1.2` - React component testing
- `@testing-library/user-event==14.5.1` - User interaction simulation
- `playwright==1.40.1` - E2E testing (optional)

**Development:**
- `eslint==8.54.0` - Linting
- `prettier==3.1.0` - Code formatting
- `@vitejs/plugin-react==4.2.0` - Vite React plugin

### Infrastructure Dependencies

**Database:**
- PostgreSQL 15+ (managed service on Render/Railway)

**Deployment Platforms:**
- Render.com or Railway.app (both support PostgreSQL + Python + Node.js)
- Docker (optional, for containerization)

**Environment Management:**
- `.env` files for local development
- Platform environment variables for production

**Monitoring (Optional):**
- Sentry for error tracking
- LogRocket for session replay
- Datadog or New Relic for APM

### Development Tools

**Version Control:**
- Git
- GitHub/GitLab for repository hosting

**API Documentation:**
- FastAPI automatic OpenAPI/Swagger docs (built-in)
- Available at `/docs` endpoint

**Database Tools:**
- pgAdmin or DBeaver for database management
- Alembic for migrations

**Code Quality:**
- Pre-commit hooks for linting and formatting
- GitHub Actions for CI/CD (optional)

