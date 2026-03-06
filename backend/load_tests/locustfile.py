"""
Locust load testing script for PackOptima.

Scenarios:
1. 100 concurrent users, 10 optimization requests each
2. 10 concurrent bulk uploads, 500 orders each
3. 50 concurrent dashboard loads

Usage:
    locust -f locustfile.py --host=http://localhost:8000
    
    # Or with specific scenario:
    locust -f locustfile.py --host=http://localhost:8000 --tags optimization
    locust -f locustfile.py --host=http://localhost:8000 --tags bulk_upload
    locust -f locustfile.py --host=http://localhost:8000 --tags dashboard
"""

from locust import HttpUser, task, between, tag
import random
import json


class PackOptimaUser(HttpUser):
    """Base user class for PackOptima load testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts - login and get token"""
        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
        
        # Get sample product and box IDs
        self.product_ids = self._get_product_ids()
        self.box_ids = self._get_box_ids()
    
    def _get_product_ids(self):
        """Get list of product IDs"""
        response = self.client.get("/api/v1/products", headers=self.headers)
        if response.status_code == 200:
            products = response.json()
            return [p["id"] for p in products[:10]]  # Get first 10
        return [1, 2, 3]  # Fallback
    
    def _get_box_ids(self):
        """Get list of box IDs"""
        response = self.client.get("/api/v1/boxes", headers=self.headers)
        if response.status_code == 200:
            boxes = response.json()
            return [b["id"] for b in boxes[:10]]  # Get first 10
        return [1, 2, 3]  # Fallback


class OptimizationUser(PackOptimaUser):
    """User that performs optimization requests"""
    
    @tag('optimization')
    @task(10)
    def optimize_single_product(self):
        """Optimize single product packaging"""
        product_id = random.choice(self.product_ids)
        
        with self.client.post(
            "/api/v1/optimize",
            json={"product_id": product_id},
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @tag('optimization')
    @task(5)
    def optimize_async(self):
        """Submit async optimization request"""
        product_id = random.choice(self.product_ids)
        
        # Submit async task
        with self.client.post(
            "/api/v1/optimize/async",
            json={"product_id": product_id},
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 202:
                task_id = response.json().get("task_id")
                response.success()
                
                # Check task status
                if task_id:
                    self.client.get(
                        f"/api/v1/tasks/{task_id}",
                        headers=self.headers,
                        name="/api/v1/tasks/[task_id]"
                    )
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @tag('optimization')
    @task(3)
    def optimize_order(self):
        """Optimize multi-product order"""
        # Create order with random products
        order_data = {
            "order_number": f"LOAD-TEST-{random.randint(1000, 9999)}",
            "customer_name": "Load Test Customer",
            "items": [
                {
                    "product_id": random.choice(self.product_ids),
                    "quantity": random.randint(1, 5)
                }
                for _ in range(random.randint(3, 10))
            ]
        }
        
        # Create order
        response = self.client.post(
            "/api/v1/orders",
            json=order_data,
            headers=self.headers
        )
        
        if response.status_code == 201:
            order_id = response.json()["id"]
            
            # Optimize order packing
            self.client.post(
                f"/api/v1/orders/{order_id}/optimize",
                headers=self.headers,
                name="/api/v1/orders/[order_id]/optimize"
            )


class BulkUploadUser(PackOptimaUser):
    """User that performs bulk uploads"""
    
    @tag('bulk_upload')
    @task
    def upload_bulk_orders(self):
        """Upload CSV with multiple orders"""
        # Generate CSV content
        csv_content = "order_number,customer_name,product_sku,quantity\n"
        
        num_orders = random.randint(50, 100)
        for i in range(num_orders):
            order_num = f"BULK-{random.randint(10000, 99999)}"
            customer = f"Customer {i}"
            
            # Add 2-5 items per order
            for j in range(random.randint(2, 5)):
                sku = f"PROD-{random.randint(100, 999)}"
                qty = random.randint(1, 10)
                csv_content += f"{order_num},{customer},{sku},{qty}\n"
        
        # Upload CSV
        files = {
            'file': ('orders.csv', csv_content, 'text/csv')
        }
        
        with self.client.post(
            "/api/v1/bulk-upload",
            files=files,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 202:
                upload_id = response.json().get("upload_id")
                response.success()
                
                # Check upload status
                if upload_id:
                    self.client.get(
                        f"/api/v1/bulk-upload/{upload_id}",
                        headers=self.headers,
                        name="/api/v1/bulk-upload/[upload_id]"
                    )
            else:
                response.failure(f"Got status code {response.status_code}")


class DashboardUser(PackOptimaUser):
    """User that loads dashboard and analytics"""
    
    @tag('dashboard')
    @task(10)
    def load_analytics_summary(self):
        """Load analytics summary"""
        self.client.get(
            "/api/v1/analytics/summary?period=30",
            headers=self.headers,
            name="/api/v1/analytics/summary"
        )
    
    @tag('dashboard')
    @task(5)
    def load_box_usage(self):
        """Load box usage analytics"""
        self.client.get(
            "/api/v1/analytics/box-usage",
            headers=self.headers,
            name="/api/v1/analytics/box-usage"
        )
    
    @tag('dashboard')
    @task(5)
    def load_shipping_costs(self):
        """Load shipping cost analytics"""
        self.client.get(
            "/api/v1/analytics/shipping-cost?period=30",
            headers=self.headers,
            name="/api/v1/analytics/shipping-cost"
        )
    
    @tag('dashboard')
    @task(3)
    def load_trends(self):
        """Load trends analytics"""
        self.client.get(
            "/api/v1/analytics/trends?months=6",
            headers=self.headers,
            name="/api/v1/analytics/trends"
        )
    
    @tag('dashboard')
    @task(8)
    def list_products(self):
        """List products"""
        self.client.get(
            "/api/v1/products",
            headers=self.headers,
            name="/api/v1/products"
        )
    
    @tag('dashboard')
    @task(8)
    def list_boxes(self):
        """List boxes"""
        self.client.get(
            "/api/v1/boxes",
            headers=self.headers,
            name="/api/v1/boxes"
        )
    
    @tag('dashboard')
    @task(5)
    def list_orders(self):
        """List orders"""
        self.client.get(
            "/api/v1/orders",
            headers=self.headers,
            name="/api/v1/orders"
        )


class WarehouseAPIUser(HttpUser):
    """User that uses warehouse API with API key"""
    
    wait_time = between(0.5, 2)
    
    def on_start(self):
        """Set up API key authentication"""
        self.api_key = "test_warehouse_api_key_12345"
        self.headers = {"X-API-Key": self.api_key}
    
    @tag('warehouse')
    @task
    def warehouse_optimize(self):
        """Call warehouse optimization endpoint"""
        request_data = {
            "order_id": f"WH-{random.randint(1000, 9999)}",
            "items": [
                {
                    "sku": f"PROD-{random.randint(100, 999)}",
                    "quantity": random.randint(1, 5),
                    "dimensions": {
                        "length_cm": random.uniform(10, 50),
                        "width_cm": random.uniform(10, 50),
                        "height_cm": random.uniform(10, 50)
                    },
                    "weight_kg": random.uniform(0.5, 10.0)
                }
                for _ in range(random.randint(1, 10))
            ],
            "shipping_address": {
                "country": "US",
                "postal_code": "12345"
            }
        }
        
        with self.client.post(
            "/api/v1/warehouse/optimize-package",
            json=request_data,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.failure("Rate limit exceeded")
            else:
                response.failure(f"Got status code {response.status_code}")


# Load test scenarios
class Scenario1_OptimizationLoad(OptimizationUser):
    """Scenario 1: 100 concurrent users, 10 optimization requests each"""
    weight = 3


class Scenario2_BulkUploadLoad(BulkUploadUser):
    """Scenario 2: 10 concurrent bulk uploads"""
    weight = 1


class Scenario3_DashboardLoad(DashboardUser):
    """Scenario 3: 50 concurrent dashboard loads"""
    weight = 2


class Scenario4_WarehouseLoad(WarehouseAPIUser):
    """Scenario 4: Warehouse API load"""
    weight = 1
