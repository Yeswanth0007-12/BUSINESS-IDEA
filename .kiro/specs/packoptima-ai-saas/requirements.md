# Requirements Document: PackOptima AI SaaS Platform

## Introduction

PackOptima AI is an enterprise-grade SaaS platform designed to optimize packaging decisions for e-commerce and logistics companies. The system analyzes product dimensions, current packaging choices, and available box inventory to recommend optimal packaging solutions that minimize costs and reduce waste. The platform provides multi-tenant isolation, real-time optimization calculations, executive dashboards, and cost leakage analysis to help companies make data-driven packaging decisions.

## Glossary

- **System**: The PackOptima AI SaaS platform (backend and frontend combined)
- **Backend**: The FastAPI server handling business logic and data persistence
- **Frontend**: The React web application providing user interface
- **User**: An authenticated person with access to the platform
- **Company**: A tenant organization with isolated data workspace
- **Product**: An item that requires packaging, with dimensions and attributes
- **Box**: A packaging container with dimensions and cost
- **Optimization_Engine**: The core algorithm that calculates optimal packaging recommendations
- **Optimization_Run**: A logged execution of the optimization algorithm with results
- **Authentication_Service**: The component managing user login and JWT tokens
- **Dashboard**: The executive view displaying key metrics and analytics
- **Cost_Leakage**: The difference between current packaging costs and optimal packaging costs
- **Volumetric_Weight**: Calculated weight based on package dimensions using formula (L × W × H) / 5000
- **SKU**: Stock Keeping Unit, a unique identifier for a product within a company
- **JWT**: JSON Web Token used for authentication
- **Padding**: Additional space added around product dimensions for safe packaging
- **Multi_Tenant**: Architecture pattern ensuring data isolation between companies

## Requirements

### Requirement 1: User Registration and Company Creation

**User Story:** As a new user, I want to register with my email and create a company account, so that I can start using the platform with isolated data.

#### Acceptance Criteria

1. WHEN a user submits registration with email, password, and company name, THE System SHALL create a new company record
2. WHEN a user submits registration with email, password, and company name, THE System SHALL create a new user record associated with the company
3. WHEN a user submits registration with a password, THE System SHALL hash the password using bcrypt before storage
4. WHEN a user submits registration with an email that already exists, THE System SHALL return an error and prevent duplicate registration
5. WHEN registration is successful, THE System SHALL generate a JWT token containing user_id and company_id claims
6. WHEN registration is successful, THE System SHALL return the JWT token to the Frontend
7. THE System SHALL enforce that company names are non-empty strings
8. THE System SHALL enforce that email addresses are in valid format

### Requirement 2: User Authentication

**User Story:** As a registered user, I want to log in with my credentials, so that I can access my company's data securely.

#### Acceptance Criteria

1. WHEN a user submits login credentials with valid email and password, THE Authentication_Service SHALL verify the credentials against stored data
2. WHEN a user submits valid login credentials, THE Authentication_Service SHALL generate a JWT token with 24-hour expiration
3. WHEN a user submits valid login credentials, THE System SHALL return the JWT token to the Frontend
4. WHEN a user submits invalid email or password, THE System SHALL return HTTP 401 error with message "Invalid credentials"
5. WHEN a user submits login request, THE System SHALL apply rate limiting of 5 attempts per minute per IP address
6. THE JWT token SHALL contain user_id and company_id claims
7. THE JWT token SHALL be signed with HS256 algorithm using SECRET_KEY from environment
8. WHEN a JWT token expires, THE System SHALL reject requests with HTTP 401 error

### Requirement 3: Multi-Tenant Data Isolation

**User Story:** As a company administrator, I want my company's data to be completely isolated from other companies, so that our sensitive business information remains private.

#### Acceptance Criteria

1. WHEN a user makes any data request, THE System SHALL filter all queries by the company_id from the authenticated user's JWT token
2. WHEN a user attempts to access a resource belonging to a different company, THE System SHALL return HTTP 403 Forbidden error
3. THE System SHALL never trust company_id values from request bodies or query parameters
4. WHEN querying products, THE Backend SHALL automatically filter by company_id
5. WHEN querying boxes, THE Backend SHALL automatically filter by company_id
6. WHEN querying optimization runs, THE Backend SHALL automatically filter by company_id
7. THE System SHALL log all unauthorized access attempts for security monitoring

### Requirement 4: Product Management

**User Story:** As a logistics manager, I want to create and manage products with their dimensions and packaging details, so that I can track what needs to be optimized.

#### Acceptance Criteria

1. WHEN a user creates a product with name, SKU, category, dimensions, weight, current box, and monthly volume, THE System SHALL persist the product to the database
2. WHEN a user creates a product, THE System SHALL validate that the SKU is unique within the company
3. WHEN a user creates a product with duplicate SKU, THE System SHALL return HTTP 400 error with message "SKU already exists"
4. WHEN a user creates a product, THE System SHALL validate that length_cm, width_cm, height_cm are positive numbers
5. WHEN a user creates a product, THE System SHALL validate that weight_kg is a positive number
6. WHEN a user creates a product, THE System SHALL validate that monthly_order_volume is a non-negative integer
7. WHEN a user creates a product, THE System SHALL validate that category is a non-empty string
8. WHEN a user retrieves products, THE System SHALL return only products belonging to their company
9. WHEN a user updates a product, THE System SHALL apply changes only if the product belongs to their company
10. WHEN a user deletes a product, THE System SHALL remove it only if the product belongs to their company
11. THE System SHALL support pagination for product listings with default limit of 50 items

### Requirement 5: Packaging Inventory Management

**User Story:** As a warehouse manager, I want to maintain an inventory of available box sizes with their costs, so that the system can recommend from our actual packaging options.

#### Acceptance Criteria

1. WHEN a user creates a box with name, dimensions, and cost, THE System SHALL persist the box to the database
2. WHEN a user creates a box, THE System SHALL validate that length_cm, width_cm, height_cm are positive numbers
3. WHEN a user creates a box, THE System SHALL validate that cost_per_unit is a positive number
4. WHEN a user creates a box, THE System SHALL associate it with the user's company
5. WHEN a user retrieves boxes, THE System SHALL return only boxes belonging to their company
6. WHEN a user updates a box, THE System SHALL apply changes only if the box belongs to their company
7. WHEN a user deletes a box, THE System SHALL remove it only if the box belongs to their company
8. THE System SHALL initialize usage_count to zero when a box is created
9. WHEN a box is used in optimization, THE System SHALL track usage by incrementing usage_count

### Requirement 6: Volumetric Weight Calculation

**User Story:** As a shipping analyst, I want the system to calculate volumetric weight accurately, so that I can understand the dimensional impact of packaging choices.

#### Acceptance Criteria

1. WHEN calculating volumetric weight for any box or product, THE Optimization_Engine SHALL use the formula (length_cm × width_cm × height_cm) / 5000
2. WHEN provided with dimensions, THE System SHALL return a positive float value for volumetric weight
3. THE System SHALL maintain precision to 2 decimal places for volumetric weight calculations
4. WHEN dimensions are provided, THE System SHALL validate that all dimensions are positive numbers before calculation

### Requirement 7: Category-Based Padding Logic

**User Story:** As a packaging engineer, I want different product categories to have appropriate padding, so that fragile items get more protection than durable items.

#### Acceptance Criteria

1. WHEN a product has category "electronics", THE Optimization_Engine SHALL apply 3.0 cm padding per side
2. WHEN a product has category "fragile", THE Optimization_Engine SHALL apply 4.0 cm padding per side
3. WHEN a product has category "clothing", THE Optimization_Engine SHALL apply 1.0 cm padding per side
4. WHEN a product has category "books", THE Optimization_Engine SHALL apply 1.5 cm padding per side
5. WHEN a product has category "toys", THE Optimization_Engine SHALL apply 2.0 cm padding per side
6. WHEN a product has an unrecognized category, THE Optimization_Engine SHALL apply 2.0 cm default padding per side
7. THE System SHALL apply padding to all three dimensions (length, width, height) by adding 2 × padding to each dimension

### Requirement 8: Optimal Box Selection

**User Story:** As a cost analyst, I want the system to find the smallest box that fits each product, so that we minimize packaging material and shipping costs.

#### Acceptance Criteria

1. WHEN finding an optimal box for a product, THE Optimization_Engine SHALL calculate required dimensions as product dimensions plus padding
2. WHEN evaluating if a box fits, THE Optimization_Engine SHALL consider all possible orientations of the product
3. WHEN evaluating if a box fits, THE Optimization_Engine SHALL sort both product and box dimensions and compare them element-wise
4. WHEN multiple boxes fit a product, THE Optimization_Engine SHALL select the box with minimum volume
5. WHEN no box in inventory can fit a product, THE Optimization_Engine SHALL return null for that product
6. THE Optimization_Engine SHALL never recommend a box where any dimension is smaller than the corresponding product dimension plus padding
7. WHEN calculating box volume, THE System SHALL use the formula length_cm × width_cm × height_cm

### Requirement 9: Packaging Optimization Execution

**User Story:** As an operations manager, I want to run optimization across all or selected products, so that I can identify cost-saving opportunities.

#### Acceptance Criteria

1. WHEN a user initiates optimization without specifying products, THE System SHALL analyze all products belonging to their company
2. WHEN a user initiates optimization with specific product IDs, THE System SHALL analyze only those products
3. WHEN optimization runs, THE System SHALL fetch all boxes belonging to the company
4. WHEN a company has no boxes in inventory, THE System SHALL return HTTP 400 error with message "No boxes available"
5. WHEN optimization processes a product, THE System SHALL calculate the optimal box using category padding and box selection algorithm
6. WHEN optimization finds a cheaper box option, THE System SHALL calculate monthly savings as (current_cost - optimal_cost) × monthly_volume
7. WHEN optimization finds a cheaper box option, THE System SHALL calculate savings_percentage as (savings / current_cost) × 100
8. WHEN optimization completes, THE System SHALL create an OptimizationRun record with timestamp and summary statistics
9. WHEN optimization completes, THE System SHALL create OptimizationResult records for each product with savings
10. WHEN optimization completes, THE System SHALL return a summary including total products analyzed, products with savings, monthly savings, and annual savings
11. THE System SHALL calculate annual savings as monthly savings × 12
12. THE System SHALL complete optimization within 2 seconds for 100 products

### Requirement 10: Optimization History Tracking

**User Story:** As a financial analyst, I want to view historical optimization runs, so that I can track savings trends over time.

#### Acceptance Criteria

1. WHEN an optimization run completes, THE System SHALL log the run with company_id, timestamp, products_analyzed, and total savings
2. WHEN a user requests optimization history, THE System SHALL return runs belonging only to their company
3. WHEN a user requests optimization history, THE System SHALL sort runs by timestamp in descending order
4. WHEN a user requests optimization history, THE System SHALL support limiting the number of results returned
5. WHEN a user requests details for a specific optimization run, THE System SHALL return the complete results including all product recommendations
6. THE System SHALL persist optimization results indefinitely for historical analysis
7. THE System SHALL index optimization_runs by company_id and timestamp for query performance

### Requirement 11: Executive Dashboard Metrics

**User Story:** As an executive, I want to see key metrics at a glance, so that I can understand the overall impact of packaging optimization.

#### Acceptance Criteria

1. WHEN a user views the dashboard, THE System SHALL display the total count of products for their company
2. WHEN a user views the dashboard, THE System SHALL display the total count of boxes for their company
3. WHEN a user views the dashboard, THE System SHALL display the total monthly savings from the latest optimization run
4. WHEN a user views the dashboard, THE System SHALL display the total annual savings from the latest optimization run
5. WHEN a user views the dashboard, THE System SHALL display the average savings per product from the latest optimization run
6. WHEN a user views the dashboard, THE System SHALL display the total count of optimization runs for their company
7. WHEN a user views the dashboard, THE System SHALL display the timestamp of the last optimization run
8. WHEN no optimization has been run, THE System SHALL display zero for all savings metrics and null for last optimization date
9. THE System SHALL calculate average savings per product as total_monthly_savings / products_analyzed
10. THE System SHALL return dashboard metrics within 500 milliseconds

### Requirement 12: Cost Leakage Analysis

**User Story:** As a supply chain director, I want to see cost leakage broken down by product category, so that I can prioritize optimization efforts on the highest-impact areas.

#### Acceptance Criteria

1. WHEN a user views cost leakage analysis, THE System SHALL aggregate savings by product category from the latest optimization run
2. WHEN calculating leakage for a category, THE System SHALL sum annual savings for all products in that category
3. WHEN calculating leakage for a category, THE System SHALL count the number of products in that category
4. WHEN calculating leakage for a category, THE System SHALL calculate percentage of total leakage
5. WHEN displaying leakage insights, THE System SHALL sort categories by total leakage in descending order
6. WHEN displaying leakage insights, THE System SHALL show category name, total annual leakage, product count, and percentage
7. THE System SHALL ensure that the sum of all category percentages equals 100%
8. WHEN no optimization has been run, THE System SHALL return an empty list of leakage insights

### Requirement 13: Top Inefficient Products Identification

**User Story:** As a procurement manager, I want to identify the most inefficient products, so that I can focus on the items with the greatest savings potential.

#### Acceptance Criteria

1. WHEN a user requests top inefficient products, THE System SHALL return products with the highest potential savings from the latest optimization run
2. WHEN displaying inefficient products, THE System SHALL show product_id, product_name, SKU, current_cost, potential_savings, and savings_percentage
3. WHEN displaying inefficient products, THE System SHALL sort by potential_savings in descending order
4. WHEN a user requests top inefficient products, THE System SHALL support limiting the number of results (default 10)
5. THE System SHALL calculate potential_savings as monthly savings for each product
6. THE System SHALL return only products belonging to the user's company

### Requirement 14: Protected Route Access

**User Story:** As a security-conscious user, I want all sensitive pages to require authentication, so that unauthorized users cannot access company data.

#### Acceptance Criteria

1. WHEN a user accesses the dashboard page without authentication, THE Frontend SHALL redirect to the login page
2. WHEN a user accesses the products page without authentication, THE Frontend SHALL redirect to the login page
3. WHEN a user accesses the boxes page without authentication, THE Frontend SHALL redirect to the login page
4. WHEN a user accesses the optimize page without authentication, THE Frontend SHALL redirect to the login page
5. WHEN a user accesses the history page without authentication, THE Frontend SHALL redirect to the login page
6. WHEN a user accesses the leakage page without authentication, THE Frontend SHALL redirect to the login page
7. WHEN a user is authenticated, THE Frontend SHALL allow access to all protected routes
8. WHEN a user logs out, THE Frontend SHALL clear the JWT token and redirect to the login page

### Requirement 15: API Client Token Management

**User Story:** As a frontend developer, I want the API client to automatically include authentication tokens, so that all requests are properly authenticated.

#### Acceptance Criteria

1. WHEN a user logs in successfully, THE Frontend SHALL store the JWT token in localStorage
2. WHEN the API client makes any request to a protected endpoint, THE Frontend SHALL include the JWT token in the Authorization header
3. WHEN the API client receives HTTP 401 error, THE Frontend SHALL clear the stored token and redirect to login
4. WHEN a user logs out, THE Frontend SHALL remove the JWT token from localStorage
5. THE Frontend SHALL format the Authorization header as "Bearer {token}"
6. WHEN the API client is initialized, THE Frontend SHALL read the token from localStorage if present

### Requirement 16: Form Validation and Error Handling

**User Story:** As a user entering data, I want immediate feedback on validation errors, so that I can correct mistakes before submission.

#### Acceptance Criteria

1. WHEN a user submits a product form with negative dimensions, THE Frontend SHALL display an error message "All dimensions must be positive numbers"
2. WHEN a user submits a product form with negative weight, THE Frontend SHALL display an error message "Weight must be a positive number"
3. WHEN a user submits a product form with empty SKU, THE Frontend SHALL display an error message "SKU is required"
4. WHEN a user submits a product form with empty category, THE Frontend SHALL display an error message "Category is required"
5. WHEN the Backend returns a validation error, THE Frontend SHALL display the error message inline with the relevant form field
6. WHEN a user corrects a validation error, THE Frontend SHALL clear the error message for that field
7. WHEN a form submission succeeds, THE Frontend SHALL display a success notification
8. WHEN a form submission fails, THE Frontend SHALL keep the form data populated for correction

### Requirement 17: Optimization Results Display

**User Story:** As a user who ran optimization, I want to see detailed results for each product, so that I can understand the recommendations and savings.

#### Acceptance Criteria

1. WHEN optimization completes successfully, THE Frontend SHALL display the total number of products analyzed
2. WHEN optimization completes successfully, THE Frontend SHALL display the number of products with savings opportunities
3. WHEN optimization completes successfully, THE Frontend SHALL display the total monthly savings amount
4. WHEN optimization completes successfully, THE Frontend SHALL display the total annual savings amount
5. WHEN optimization completes successfully, THE Frontend SHALL display a table of results with product name, current box, recommended box, and savings
6. WHEN displaying optimization results, THE Frontend SHALL show savings_percentage for each product
7. WHEN displaying optimization results, THE Frontend SHALL show volumetric weights for current and recommended boxes
8. WHEN optimization finds no savings opportunities, THE Frontend SHALL display a message "No savings opportunities found"
9. WHEN optimization is running, THE Frontend SHALL display a loading indicator

### Requirement 18: CORS Configuration

**User Story:** As a system administrator, I want the backend to accept requests only from authorized frontend domains, so that unauthorized websites cannot access the API.

#### Acceptance Criteria

1. THE Backend SHALL read allowed origins from the ALLOWED_ORIGINS environment variable
2. WHEN a request comes from an origin in ALLOWED_ORIGINS, THE Backend SHALL include appropriate CORS headers in the response
3. WHEN a request comes from an origin not in ALLOWED_ORIGINS, THE Backend SHALL reject the request
4. THE Backend SHALL allow HTTP methods: GET, POST, PUT, DELETE, OPTIONS
5. THE Backend SHALL allow credentials in CORS requests
6. WHERE the environment is development, THE Backend SHALL allow wildcard origin for testing
7. WHERE the environment is production, THE Backend SHALL restrict origins to specific domains only

### Requirement 19: Database Connection Management

**User Story:** As a system administrator, I want the backend to manage database connections efficiently, so that the system remains stable under load.

#### Acceptance Criteria

1. THE Backend SHALL read database connection URL from DATABASE_URL environment variable
2. THE Backend SHALL use connection pooling with a maximum of 20 connections
3. WHEN a database query fails, THE Backend SHALL log the error with full stack trace
4. WHEN the database is unreachable, THE Backend SHALL return HTTP 503 error with message "Service temporarily unavailable"
5. THE Backend SHALL use SSL/TLS for database connections in production environment
6. THE Backend SHALL implement prepared statements for all queries to prevent SQL injection
7. WHEN connection pool is exhausted, THE Backend SHALL queue requests with timeout of 30 seconds

### Requirement 20: Security Headers and Rate Limiting

**User Story:** As a security engineer, I want the API to implement security best practices, so that the platform is protected against common attacks.

#### Acceptance Criteria

1. THE Backend SHALL include X-Content-Type-Options: nosniff header in all responses
2. THE Backend SHALL include X-Frame-Options: DENY header in all responses
3. THE Backend SHALL include X-XSS-Protection: 1; mode=block header in all responses
4. WHERE the environment is production, THE Backend SHALL include Strict-Transport-Security header with max-age=31536000
5. THE Backend SHALL enforce rate limit of 5 requests per minute on the login endpoint
6. THE Backend SHALL enforce rate limit of 3 requests per minute on the registration endpoint
7. THE Backend SHALL enforce rate limit of 10 requests per minute on the optimization endpoint
8. THE Backend SHALL enforce rate limit of 100 requests per minute on other endpoints
9. WHEN rate limit is exceeded, THE Backend SHALL return HTTP 429 error
10. THE Backend SHALL never log or display passwords in plain text

### Requirement 21: Health Check Endpoint

**User Story:** As a DevOps engineer, I want a health check endpoint, so that I can monitor the service status and configure load balancer health checks.

#### Acceptance Criteria

1. THE Backend SHALL provide a health check endpoint at /health
2. WHEN the database connection is healthy, THE health endpoint SHALL return HTTP 200 with status "healthy"
3. WHEN the database connection fails, THE health endpoint SHALL return HTTP 503 with status "unhealthy"
4. THE health endpoint SHALL not require authentication
5. THE health endpoint SHALL respond within 100 milliseconds

### Requirement 22: API Documentation

**User Story:** As a developer integrating with the API, I want comprehensive API documentation, so that I can understand all available endpoints and their parameters.

#### Acceptance Criteria

1. THE Backend SHALL provide interactive API documentation at /docs endpoint
2. THE documentation SHALL include all endpoint paths, methods, parameters, and response schemas
3. THE documentation SHALL include example requests and responses
4. THE documentation SHALL be automatically generated from FastAPI route definitions
5. THE documentation SHALL allow testing endpoints directly from the browser interface

### Requirement 23: Responsive UI Design

**User Story:** As a user accessing the platform from different devices, I want the interface to work well on desktop, tablet, and mobile, so that I can use it anywhere.

#### Acceptance Criteria

1. WHEN viewed on desktop (>1024px width), THE Frontend SHALL display the full sidebar navigation
2. WHEN viewed on tablet (768px-1024px width), THE Frontend SHALL display a collapsible sidebar
3. WHEN viewed on mobile (<768px width), THE Frontend SHALL display a hamburger menu for navigation
4. WHEN displaying tables on mobile, THE Frontend SHALL make them horizontally scrollable
5. WHEN displaying charts on mobile, THE Frontend SHALL scale them to fit the screen width
6. THE Frontend SHALL use responsive typography that scales appropriately for each screen size

### Requirement 24: Professional Dark Theme

**User Story:** As a user working long hours, I want a professional dark theme, so that the interface is comfortable for extended use.

#### Acceptance Criteria

1. THE Frontend SHALL use a dark background color scheme throughout the application
2. THE Frontend SHALL use high-contrast text colors for readability
3. THE Frontend SHALL use consistent color palette for primary, secondary, and accent colors
4. THE Frontend SHALL use subtle shadows and borders to define component boundaries
5. THE Frontend SHALL ensure all charts and visualizations work well with the dark theme
6. THE Frontend SHALL maintain WCAG AA contrast ratios for accessibility

### Requirement 25: Data Persistence and Transactions

**User Story:** As a system administrator, I want all data operations to be transactional, so that data integrity is maintained even during failures.

#### Acceptance Criteria

1. WHEN creating a user and company during registration, THE Backend SHALL use a database transaction
2. WHEN a transaction fails, THE Backend SHALL rollback all changes
3. WHEN saving optimization results, THE Backend SHALL use a transaction to ensure all results are saved together
4. WHEN updating related records, THE Backend SHALL use transactions to maintain referential integrity
5. THE Backend SHALL commit transactions only after all operations succeed
6. WHEN a database constraint is violated, THE Backend SHALL rollback the transaction and return an appropriate error

### Requirement 26: Environment Configuration

**User Story:** As a DevOps engineer, I want all environment-specific settings to be configurable via environment variables, so that I can deploy to different environments without code changes.

#### Acceptance Criteria

1. THE Backend SHALL read SECRET_KEY from environment variable for JWT signing
2. THE Backend SHALL read DATABASE_URL from environment variable for database connection
3. THE Backend SHALL read ALLOWED_ORIGINS from environment variable for CORS configuration
4. THE Backend SHALL read ENVIRONMENT from environment variable to determine production vs development mode
5. WHEN required environment variables are missing, THE Backend SHALL fail to start with a clear error message
6. THE Backend SHALL never include sensitive credentials in source code or version control

### Requirement 27: Optimization Determinism

**User Story:** As a quality assurance engineer, I want optimization to produce consistent results, so that running it multiple times with the same data gives the same recommendations.

#### Acceptance Criteria

1. WHEN optimization runs twice with identical product and box data, THE Optimization_Engine SHALL produce identical recommendations
2. WHEN optimization runs twice with identical product and box data, THE Optimization_Engine SHALL calculate identical savings amounts
3. THE Optimization_Engine SHALL use deterministic algorithms without random elements
4. THE Optimization_Engine SHALL process products in consistent order based on product ID

### Requirement 28: Savings Trend Visualization

**User Story:** As a financial analyst, I want to see savings trends over time, so that I can demonstrate the value of optimization efforts to stakeholders.

#### Acceptance Criteria

1. WHEN a user views the dashboard, THE Frontend SHALL display a chart showing savings trends over recent optimization runs
2. WHEN displaying the savings trend, THE Frontend SHALL show monthly savings on the Y-axis and run dates on the X-axis
3. WHEN there are fewer than 2 optimization runs, THE Frontend SHALL display a message "Run more optimizations to see trends"
4. THE Frontend SHALL support viewing trends for the last 3, 6, or 12 months
5. THE Frontend SHALL use a line chart or bar chart for trend visualization

### Requirement 29: Pareto Analysis Visualization

**User Story:** As a business analyst, I want to see a Pareto chart of cost leakage by category, so that I can apply the 80/20 rule to prioritize improvements.

#### Acceptance Criteria

1. WHEN a user views the leakage page, THE Frontend SHALL display a Pareto chart with categories on X-axis and leakage on Y-axis
2. WHEN displaying the Pareto chart, THE Frontend SHALL sort categories by leakage in descending order
3. WHEN displaying the Pareto chart, THE Frontend SHALL include a cumulative percentage line
4. THE Frontend SHALL highlight the categories that represent 80% of total leakage
5. THE Frontend SHALL use distinct colors for bars and the cumulative line

### Requirement 30: Bulk Product Import

**User Story:** As a data administrator, I want to import multiple products from a CSV file, so that I can quickly populate the system with existing inventory data.

#### Acceptance Criteria

1. WHEN a user uploads a CSV file with product data, THE System SHALL parse the file and validate each row
2. WHEN parsing CSV, THE System SHALL expect columns: name, sku, category, length_cm, width_cm, height_cm, weight_kg, current_box_id, monthly_order_volume
3. WHEN a CSV row has invalid data, THE System SHALL skip that row and report the error
4. WHEN CSV parsing completes, THE System SHALL create all valid products in a single transaction
5. WHEN CSV import succeeds, THE System SHALL return a summary of products created and errors encountered
6. THE System SHALL validate SKU uniqueness across all imported products
7. THE System SHALL enforce a maximum file size of 10MB for CSV uploads
