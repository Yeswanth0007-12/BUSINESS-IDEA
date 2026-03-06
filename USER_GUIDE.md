# PackOptima AI - User Guide

## Application Overview

PackOptima AI is a professional SaaS platform for optimizing packaging costs using AI-powered algorithms. The application helps businesses reduce packaging waste and costs by finding the most efficient box sizes for their products.

## Accessing the Application

**Frontend URL**: http://localhost:8080
**Backend API**: http://localhost:8000

## Getting Started

### 1. Registration

1. Open http://localhost:8080 in your browser
2. Click "Register here" on the login page
3. Fill in the registration form:
   - **Email**: Your email address (e.g., user@company.com)
   - **Company Name**: Your company name (e.g., "Acme Corp")
   - **Password**: At least 8 characters
   - **Confirm Password**: Re-enter your password
4. Click "Create Account"
5. You will be automatically logged in and redirected to the Dashboard

### 2. Login

1. Open http://localhost:8080 in your browser
2. Enter your email and password
3. Click "Sign In"
4. You will be redirected to the Dashboard

## Application Features

### Dashboard
- View key performance indicators (KPIs):
  - Total Products
  - Total Boxes
  - Optimization Runs
  - Total Savings
- View recent optimization history
- See top inefficient products
- Analyze savings trends over time

### Products Management
- **Add Products**: Click "Add Product" button
  - SKU: Product identifier (e.g., "PROD-001")
  - Name: Product name (e.g., "Laptop")
  - Category: Product category (e.g., "Electronics")
  - Dimensions: Length, Width, Height (in cm)
  - Weight: Product weight (in kg)
  - Monthly Order Volume: Number of orders per month
  - Current Box Cost: Current packaging cost (optional)
- **View Products**: See all your products in a table
- **Edit Products**: Click edit icon to modify product details
- **Delete Products**: Click delete icon to remove products

### Boxes Management
- **Add Boxes**: Click "Add Box" button
  - Name: Box name (e.g., "Small Box")
  - Dimensions: Length, Width, Height (in cm)
  - Cost Per Unit: Box cost in dollars
- **View Boxes**: See all available box sizes
- **Edit Boxes**: Click edit icon to modify box details
- **Delete Boxes**: Click delete icon to remove boxes

### Optimization
- **Run Optimization**: Click "Run Optimization" button
  - The AI algorithm will analyze all products and boxes
  - Find the most cost-effective box for each product
  - Calculate potential savings
- **View Results**: See optimization results including:
  - Products analyzed
  - Recommended boxes
  - Cost savings
  - Space utilization

### History
- View all past optimization runs
- See detailed results for each run
- Track optimization performance over time
- Filter and search through history

### Leakage Analysis
- View space utilization metrics
- Identify products with poor box fit
- See wasted space percentages
- Get recommendations for improvement

## Complete Workflow Example

### Step 1: Add Products
1. Navigate to "Products" tab
2. Click "Add Product"
3. Add your first product:
   - SKU: LAPTOP-001
   - Name: Gaming Laptop
   - Category: Electronics
   - Length: 40 cm
   - Width: 30 cm
   - Height: 5 cm
   - Weight: 3.5 kg
   - Monthly Volume: 100
4. Click "Save"
5. Repeat for more products

### Step 2: Add Boxes
1. Navigate to "Boxes" tab
2. Click "Add Box"
3. Add your first box:
   - Name: Medium Box
   - Length: 45 cm
   - Width: 35 cm
   - Height: 10 cm
   - Cost: $2.50
4. Click "Save"
5. Add more box sizes (Small, Large, etc.)

### Step 3: Run Optimization
1. Navigate to "Optimize" tab
2. Click "Run Optimization"
3. Wait for the algorithm to complete
4. View the results showing:
   - Best box for each product
   - Cost savings
   - Space utilization

### Step 4: Review Results
1. Navigate to "History" tab
2. Click on a recent optimization run
3. Review detailed results
4. Export or save results if needed

### Step 5: Analyze Leakage
1. Navigate to "Leakage" tab
2. View products with high wasted space
3. Consider adding new box sizes for inefficient products
4. Re-run optimization after adding new boxes

## Tips for Best Results

1. **Add Multiple Box Sizes**: The more box options you provide, the better the optimization results
2. **Accurate Dimensions**: Ensure product and box dimensions are accurate
3. **Regular Optimization**: Run optimization regularly as your product catalog changes
4. **Monitor Leakage**: Check leakage analysis to identify opportunities for improvement
5. **Track History**: Use history to track savings over time

## Troubleshooting

### Cannot Login
- Ensure password is at least 8 characters
- Check that email is correctly formatted
- Try registering a new account if you forgot credentials

### Optimization Not Working
- Ensure you have added at least one product
- Ensure you have added at least one box
- Check that all dimensions are positive numbers

### Data Not Showing
- Refresh the page
- Check that you're logged in
- Verify backend is running (http://localhost:8000/health should return "healthy")

## Technical Details

### Architecture
- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL
- **Deployment**: Docker containers

### API Documentation
Full API documentation is available at: http://localhost:8000/docs

### Security
- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Rate limiting
- Input validation

## Support

For technical issues or questions, please refer to:
- API Documentation: http://localhost:8000/docs
- Backend Health: http://localhost:8000/health
- Frontend: http://localhost:8080

## Next Steps

1. Register your account
2. Add your products and boxes
3. Run your first optimization
4. Start saving on packaging costs!
