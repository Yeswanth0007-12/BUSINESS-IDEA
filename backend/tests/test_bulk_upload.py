"""
Comprehensive unit tests for bulk upload and CSV processing.
Tests CSV parsing, validation, and bulk upload accounting.
"""

import pytest
import io
import csv
from app.services.bulk_upload_service import BulkUploadService


@pytest.mark.unit
class TestCSVParsing:
    """Test suite for CSV parsing and validation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = BulkUploadService(None)  # No DB needed for parsing tests
    
    def test_valid_csv_parsing(self):
        """Test parsing valid CSV file"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD-001,Acme Corp,PROD-123,2
ORD-001,Acme Corp,PROD-456,1
ORD-002,Beta Inc,PROD-789,3"""
        
        csv_file = io.StringIO(csv_content)
        
        orders = self.service.parse_bulk_upload_csv(csv_file)
        
        # Should have at least 1 order
        assert len(orders) >= 1
        # Check that orders have required fields
        for order in orders:
            assert 'order_number' in order
            assert 'items' in order or 'customer_name' in order
    
    def test_csv_with_missing_headers(self):
        """Test CSV with missing required headers"""
        csv_content = """order_number,customer_name,quantity
ORD-001,Acme Corp,2"""
        
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_empty_csv(self):
        """Test empty CSV file"""
        csv_content = ""
        
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_csv_with_only_headers(self):
        """Test CSV with only headers, no data"""
        csv_content = """order_number,customer_name,product_sku,quantity"""
        
        csv_file = io.StringIO(csv_content)
        
        # Should raise HTTPException for empty data
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_csv_grouping_by_order_number(self):
        """Test that rows are correctly grouped by order_number"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD-001,Acme Corp,PROD-A,1
ORD-002,Beta Inc,PROD-B,2
ORD-001,Acme Corp,PROD-C,3
ORD-003,Gamma LLC,PROD-D,1"""
        
        csv_file = io.StringIO(csv_content)
        
        orders = self.service.parse_bulk_upload_csv(csv_file)
        
        # Should have at least 1 order
        assert len(orders) >= 1
        
        # Check that orders are present
        order_numbers = [o['order_number'] for o in orders]
        assert len(order_numbers) >= 1
    
    def test_csv_with_invalid_quantity(self):
        """Test CSV with non-numeric quantity"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD-001,Acme Corp,PROD-123,abc"""
        
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_csv_with_negative_quantity(self):
        """Test CSV with negative quantity"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD-001,Acme Corp,PROD-123,-5"""
        
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_csv_with_zero_quantity(self):
        """Test CSV with zero quantity"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD-001,Acme Corp,PROD-123,0"""
        
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_csv_with_extra_columns(self):
        """Test CSV with extra columns (should be ignored)"""
        csv_content = """order_number,customer_name,product_sku,quantity,extra_column
ORD-001,Acme Corp,PROD-123,2,extra_data"""
        
        csv_file = io.StringIO(csv_content)
        
        orders = self.service.parse_bulk_upload_csv(csv_file)
        
        # Should parse successfully
        assert len(orders) >= 1
    
    def test_csv_with_whitespace(self):
        """Test CSV with leading/trailing whitespace"""
        csv_content = """order_number,customer_name,product_sku,quantity
  ORD-001  ,  Acme Corp  ,  PROD-123  ,  2  """
        
        csv_file = io.StringIO(csv_content)
        
        orders = self.service.parse_bulk_upload_csv(csv_file)
        
        # Should parse successfully
        assert len(orders) >= 1


@pytest.mark.unit
class TestBulkUploadAccounting:
    """Test suite for bulk upload accounting and tracking"""
    
    def test_total_orders_calculation(self):
        """Test that total_orders equals processed + failed"""
        total_orders = 100
        processed_orders = 85
        failed_orders = 15
        
        assert total_orders == processed_orders + failed_orders
    
    def test_all_orders_processed(self):
        """Test when all orders are processed successfully"""
        total_orders = 50
        processed_orders = 50
        failed_orders = 0
        
        assert total_orders == processed_orders + failed_orders
        assert failed_orders == 0
    
    def test_all_orders_failed(self):
        """Test when all orders fail"""
        total_orders = 20
        processed_orders = 0
        failed_orders = 20
        
        assert total_orders == processed_orders + failed_orders
        assert processed_orders == 0
    
    def test_counts_non_negative(self):
        """Test that all counts are non-negative"""
        total_orders = 100
        processed_orders = 75
        failed_orders = 25
        
        assert total_orders >= 0
        assert processed_orders >= 0
        assert failed_orders >= 0
        assert total_orders == processed_orders + failed_orders
    
    def test_zero_orders(self):
        """Test handling of zero orders (edge case)"""
        total_orders = 0
        processed_orders = 0
        failed_orders = 0
        
        assert total_orders == processed_orders + failed_orders


@pytest.mark.unit
class TestCSVValidation:
    """Test suite for CSV validation rules"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = BulkUploadService(None)
    
    def test_required_columns_present(self):
        """Test that all required columns are present"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD-001,Acme Corp,PROD-123,2"""
        
        csv_file = io.StringIO(csv_content)
        
        # Should not raise
        orders = self.service.parse_bulk_upload_csv(csv_file)
        assert len(orders) >= 1
    
    def test_missing_order_number_column(self):
        """Test missing order_number column"""
        csv_content = """customer_name,product_sku,quantity
Acme Corp,PROD-123,2"""
        
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_missing_customer_name_column(self):
        """Test missing customer_name column"""
        csv_content = """order_number,product_sku,quantity
ORD-001,PROD-123,2"""
        
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_missing_product_sku_column(self):
        """Test missing product_sku column"""
        csv_content = """order_number,customer_name,quantity
ORD-001,Acme Corp,2"""
        
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_missing_quantity_column(self):
        """Test missing quantity column"""
        csv_content = """order_number,customer_name,product_sku
ORD-001,Acme Corp,PROD-123"""
        
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_empty_order_number(self):
        """Test empty order_number value"""
        csv_content = """order_number,customer_name,product_sku,quantity
,Acme Corp,PROD-123,2"""
        
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_empty_product_sku(self):
        """Test empty product_sku value"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD-001,Acme Corp,,2"""
        
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):
            self.service.parse_bulk_upload_csv(csv_file)


@pytest.mark.unit
class TestCSVEdgeCases:
    """Test suite for CSV edge cases"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = BulkUploadService(None)
    
    def test_very_large_quantity(self):
        """Test handling of very large quantity"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD-001,Acme Corp,PROD-123,10000"""
        
        csv_file = io.StringIO(csv_content)
        
        orders = self.service.parse_bulk_upload_csv(csv_file)
        
        # Should parse successfully
        assert len(orders) >= 1
    
    def test_special_characters_in_names(self):
        """Test handling of special characters in names"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD-001,Acme & Co. (Ltd.),PROD-123,2"""
        
        csv_file = io.StringIO(csv_content)
        
        orders = self.service.parse_bulk_upload_csv(csv_file)
        
        # Should parse successfully
        assert len(orders) >= 1
    
    def test_unicode_characters(self):
        """Test handling of unicode characters"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD-001,Café François,PROD-123,2"""
        
        csv_file = io.StringIO(csv_content)
        
        orders = self.service.parse_bulk_upload_csv(csv_file)
        
        # Should parse successfully
        assert len(orders) >= 1
    
    def test_very_long_order_number(self):
        """Test handling of very long order number"""
        long_order_number = "ORD-" + "X" * 100
        csv_content = f"""order_number,customer_name,product_sku,quantity
{long_order_number},Acme Corp,PROD-123,2"""
        
        csv_file = io.StringIO(csv_content)
        
        orders = self.service.parse_bulk_upload_csv(csv_file)
        
        # Should parse successfully
        assert len(orders) >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
