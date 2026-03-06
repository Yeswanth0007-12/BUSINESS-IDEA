"""
End-to-end workflow tests for complete user journeys.
Tests complete workflows from start to finish.

**Validates: Requirements 43.1, 43.2, 43.3, 43.4, 43.5**
"""

import pytest
import io
import time
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def create_test_user(email: str = "test@example.com", company_name: str = "Test Company"):
    """Helper to create and login a test user."""
    # Register user
    register_response = client.post("/auth/register", json={
        "email": email,
        "password": "TestPass123!",
        "company_name": company_name
    })
    
    if register_response.status_code != 201:
        # User might already exist, try login
        pass
    
    # Login
    login_response = client.post("/auth/login", json={
        "email": email,
        "password": "TestPass123!"
    })
    
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
    token = login_response.json()['access_token']
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.e2e
class TestCompleteUserWorkflow:
    """Test complete user journey: products → boxes → optimize → results"""
    
    def test_complete_optimization_workflow(self):
        """
        Test end-to-end optimization workflow.
        
        Journey:
        1. Register user
        2. Login
        3. Create product
        4. Create box
        5. Optimize packaging
        6. View results
        """
        # Step 1 & 2: Register and login
        headers = create_test_user("workflow1@example.com", "Workflow Test Co")
        
        # Step 3: Create product
        product_response = client.post("/products", json={
            "sku": "WF-TEST001",
            "name": "Workflow Test Product",
            "length_cm": 10,
            "width_cm": 10,
            "height_cm": 10,
            "weight_kg": 1.0,
            "category": "general",
            "fragile": False,
            "stackable": True
        }, headers=headers)
        assert product_response.status_code == 201, f"Product creation failed: {product_response.json()}"
        product_id = product_response.json()['id']
        
        # Step 4: Create box
        box_response = client.post("/boxes", json={
            "name": "Workflow Small Box",
            "length_cm": 20,
            "width_cm": 20,
            "height_cm": 20,
            "cost_per_unit": 2.0,
            "max_weight_kg": 10.0,
            "material_type": "cardboard"
        }, headers=headers)
        assert box_response.status_code == 201, f"Box creation failed: {box_response.json()}"
        
        # Step 5: Optimize packaging
        optimize_response = client.post("/optimize", json={
            "product_id": product_id,
            "courier_rate": 2.5
        }, headers=headers)
        assert optimize_response.status_code == 200, f"Optimization failed: {optimize_response.json()}"
        result = optimize_response.json()
        
        # Step 6: Verify results
        assert result['recommended_box'] is not None, "No box recommendation returned"
        assert result['space_utilization'] > 0, "Space utilization should be positive"
        assert result['total_cost_recommended'] > 0, "Total cost should be positive"
        assert 'orientation' in result, "Orientation should be in results"
        assert 'shipping_cost_recommended' in result, "Shipping cost should be in results"
        
        print(f"✓ Complete optimization workflow successful")
        print(f"  - Product created: {product_id}")
        print(f"  - Space utilization: {result['space_utilization']:.2f}%")
        print(f"  - Total cost: ${result['total_cost_recommended']:.2f}")


@pytest.mark.e2e
class TestCompleteOrderWorkflow:
    """Test complete order journey: create → optimize → results"""
    
    def test_complete_order_packing_workflow(self):
        """
        Test end-to-end order packing workflow.
        
        Journey:
        1. Setup: Create user, products, and boxes
        2. Create order with multiple items
        3. Optimize order packing
        4. View packing results
        """
        # Step 1: Setup
        headers = create_test_user("order@example.com", "Order Test Co")
        
        # Create products
        product1_response = client.post("/products", json={
            "sku": "ORD-PROD001",
            "name": "Order Product 1",
            "length_cm": 10,
            "width_cm": 10,
            "height_cm": 10,
            "weight_kg": 1.0,
            "category": "general",
            "fragile": False,
            "stackable": True
        }, headers=headers)
        assert product1_response.status_code == 201
        product1_id = product1_response.json()['id']
        
        product2_response = client.post("/products", json={
            "sku": "ORD-PROD002",
            "name": "Order Product 2",
            "length_cm": 8,
            "width_cm": 8,
            "height_cm": 8,
            "weight_kg": 0.5,
            "category": "general",
            "fragile": False,
            "stackable": True
        }, headers=headers)
        assert product2_response.status_code == 201
        product2_id = product2_response.json()['id']
        
        # Create boxes
        client.post("/boxes", json={
            "name": "Order Small Box",
            "length_cm": 20,
            "width_cm": 20,
            "height_cm": 20,
            "cost_per_unit": 2.0,
            "max_weight_kg": 10.0,
            "material_type": "cardboard"
        }, headers=headers)
        
        client.post("/boxes", json={
            "name": "Order Medium Box",
            "length_cm": 30,
            "width_cm": 30,
            "height_cm": 30,
            "cost_per_unit": 3.5,
            "max_weight_kg": 20.0,
            "material_type": "cardboard"
        }, headers=headers)
        
        # Step 2: Create order with multiple items
        order_response = client.post("/orders", json={
            "order_number": "ORD-E2E-001",
            "customer_name": "E2E Test Customer",
            "items": [
                {"product_id": product1_id, "quantity": 2},
                {"product_id": product2_id, "quantity": 1}
            ]
        }, headers=headers)
        assert order_response.status_code == 201, f"Order creation failed: {order_response.json()}"
        order_id = order_response.json()['id']
        
        # Step 3: Optimize order packing
        optimize_response = client.post(
            f"/orders/{order_id}/optimize",
            params={"courier_rate": 2.5},
            headers=headers
        )
        assert optimize_response.status_code == 200, f"Order optimization failed: {optimize_response.json()}"
        packing_result = optimize_response.json()
        
        # Step 4: View and verify results
        assert packing_result['success'] is True, "Order packing should succeed"
        assert packing_result['total_boxes'] > 0, "Should use at least one box"
        assert len(packing_result['boxes_used']) > 0, "Should have boxes in result"
        assert packing_result['total_cost'] > 0, "Total cost should be positive"
        
        # Verify all items were packed
        total_items_packed = sum(len(box['items']) for box in packing_result['boxes_used'])
        assert total_items_packed == 3, "Should pack all 3 items (2 + 1)"
        
        print(f"✓ Complete order workflow successful")
        print(f"  - Order created: {order_id}")
        print(f"  - Boxes used: {packing_result['total_boxes']}")
        print(f"  - Total cost: ${packing_result['total_cost']:.2f}")


@pytest.mark.e2e
class TestCompleteBulkUploadWorkflow:
    """Test complete bulk upload journey"""
    
    def test_complete_bulk_upload_workflow(self):
        """
        Test end-to-end bulk upload workflow.
        
        Journey:
        1. Setup: Create user, products, and boxes
        2. Upload CSV with multiple orders
        3. Track upload progress
        4. View results
        """
        # Step 1: Setup
        headers = create_test_user("bulk@example.com", "Bulk Test Co")
        
        # Create products
        product1_response = client.post("/products", json={
            "sku": "BULK-001",
            "name": "Bulk Product 1",
            "length_cm": 10,
            "width_cm": 10,
            "height_cm": 10,
            "weight_kg": 1.0,
            "category": "general"
        }, headers=headers)
        assert product1_response.status_code == 201
        
        product2_response = client.post("/products", json={
            "sku": "BULK-002",
            "name": "Bulk Product 2",
            "length_cm": 15,
            "width_cm": 15,
            "height_cm": 15,
            "weight_kg": 2.0,
            "category": "general"
        }, headers=headers)
        assert product2_response.status_code == 201
        
        # Create boxes
        client.post("/boxes", json={
            "name": "Bulk Box",
            "length_cm": 25,
            "width_cm": 25,
            "height_cm": 25,
            "cost_per_unit": 3.0,
            "max_weight_kg": 15.0,
            "material_type": "cardboard"
        }, headers=headers)
        
        # Step 2: Upload CSV
        csv_content = """order_number,customer_name,product_sku,quantity
BULK-ORD-001,Customer A,BULK-001,2
BULK-ORD-001,Customer A,BULK-002,1
BULK-ORD-002,Customer B,BULK-001,1
BULK-ORD-003,Customer C,BULK-002,3
"""
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        upload_response = client.post(
            "/api/v1/bulk-upload",
            files={"file": ("test_orders.csv", csv_file, "text/csv")},
            headers=headers
        )
        assert upload_response.status_code == 202, f"Bulk upload failed: {upload_response.json()}"
        upload_result = upload_response.json()
        
        # Step 3: Track progress
        upload_id = upload_result['upload_id']
        assert upload_id is not None, "Upload ID should be returned"
        
        # Wait a moment for processing
        time.sleep(2)
        
        status_response = client.get(
            f"/api/v1/bulk-upload/{upload_id}",
            headers=headers
        )
        assert status_response.status_code == 200, f"Status check failed: {status_response.json()}"
        status_data = status_response.json()
        
        # Step 4: Verify results
        assert status_data['total_orders'] == 3, "Should have 3 orders"
        assert status_data['processed_orders'] >= 0, "Processed count should be non-negative"
        assert status_data['status'] in ['processing', 'completed'], "Status should be processing or completed"
        
        print(f"✓ Complete bulk upload workflow successful")
        print(f"  - Upload ID: {upload_id}")
        print(f"  - Total orders: {status_data['total_orders']}")
        print(f"  - Status: {status_data['status']}")


@pytest.mark.e2e
class TestCompleteWarehouseIntegrationWorkflow:
    """Test complete warehouse integration journey"""
    
    def test_complete_warehouse_workflow(self):
        """
        Test end-to-end warehouse integration workflow.
        
        Journey:
        1. Setup: Create user, products, and boxes
        2. Generate API key
        3. Authenticate with API key
        4. Optimize package via warehouse API
        5. Register webhook
        6. Verify webhook configuration
        """
        # Step 1: Setup
        headers = create_test_user("warehouse@example.com", "Warehouse Test Co")
        
        # Create products
        product1_response = client.post("/products", json={
            "sku": "WH-PROD-001",
            "name": "Warehouse Product 1",
            "length_cm": 12,
            "width_cm": 10,
            "height_cm": 8,
            "weight_kg": 1.5,
            "category": "general"
        }, headers=headers)
        assert product1_response.status_code == 201
        
        # Create box
        client.post("/boxes", json={
            "name": "Warehouse Box",
            "length_cm": 30,
            "width_cm": 25,
            "height_cm": 20,
            "cost_per_unit": 4.0,
            "max_weight_kg": 20.0,
            "material_type": "cardboard"
        }, headers=headers)
        
        # Step 2: Generate API key
        api_key_response = client.post(
            "/api/v1/warehouse/api-keys",
            json={"name": "E2E Test Key"},
            headers=headers
        )
        assert api_key_response.status_code == 201, f"API key creation failed: {api_key_response.json()}"
        api_key_data = api_key_response.json()
        api_key = api_key_data['api_key']
        
        # Step 3: Authenticate with API key
        warehouse_headers = {"Authorization": f"Bearer {api_key}"}
        
        # Step 4: Optimize package via warehouse API
        warehouse_request = {
            "order_id": "WH-E2E-001",
            "items": [
                {
                    "sku": "WH-PROD-001",
                    "quantity": 2,
                    "dimensions": {"length_cm": 12, "width_cm": 10, "height_cm": 8},
                    "weight_kg": 1.5
                }
            ],
            "shipping_address": {
                "country": "US",
                "postal_code": "12345"
            }
        }
        
        optimize_response = client.post(
            "/api/v1/warehouse/optimize-package",
            json=warehouse_request,
            headers=warehouse_headers
        )
        assert optimize_response.status_code == 200, f"Warehouse optimization failed: {optimize_response.json()}"
        optimization_result = optimize_response.json()
        
        # Verify optimization results
        assert 'optimization_id' in optimization_result, "Should have optimization ID"
        assert 'boxes_required' in optimization_result, "Should have boxes required"
        assert optimization_result['total_boxes'] > 0, "Should use at least one box"
        assert optimization_result['total_cost'] > 0, "Total cost should be positive"
        
        # Step 5: Register webhook
        webhook_response = client.post(
            "/api/v1/warehouse/webhooks",
            json={
                "url": "https://example.com/webhook",
                "events": ["optimization.completed", "optimization.failed"],
                "secret": "test_webhook_secret_123"
            },
            headers=headers
        )
        assert webhook_response.status_code == 201, f"Webhook registration failed: {webhook_response.json()}"
        webhook_data = webhook_response.json()
        
        # Step 6: Verify webhook configuration
        assert webhook_data['url'] == "https://example.com/webhook", "Webhook URL should match"
        assert len(webhook_data['events']) == 2, "Should have 2 events"
        assert webhook_data['is_active'] is True, "Webhook should be active"
        
        print(f"✓ Complete warehouse integration workflow successful")
        print(f"  - API key created")
        print(f"  - Optimization ID: {optimization_result['optimization_id']}")
        print(f"  - Boxes required: {optimization_result['total_boxes']}")
        print(f"  - Webhook registered: {webhook_data['id']}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
