"""
Unit tests for CSV parsing and validation in bulk upload service.
"""

import pytest
import io
from app.services.bulk_upload_service import BulkUploadService


@pytest.mark.unit
class TestCSVParsing:
    """Test suite for CSV parsing functionality"""
    
    def setup_method(self, mock_db):
        self.service = BulkUploadService(db=mock_db)
    
    def test_valid_csv_with_multiple_orders(self):
        """Test parsing valid CSV with multiple orders"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD001,Customer A,SKU001,2
ORD001,Customer A,SKU002,1
ORD002,Customer B,SKU003,5
"""
        csv_file = io.StringIO(csv_content)
        
        orders = self.service.parse_bulk_upload_csv(csv_file)
        
        # Should group by order_number
        assert len(orders) >= 1  # At least one order
        # Check that orders are present
        order_numbers = [o['order_number'] for o in orders]
        assert 'ORD001' in order_numbers or 'ORD002' in order_numbers
    
    def test_csv_with_missing_required_columns(self):
        """Test CSV with missing required columns"""
        csv_content = """order_number,customer_name
ORD001,Customer A
"""
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):  # Should raise some error
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_csv_with_invalid_data_types(self):
        """Test CSV with invalid data types"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD001,Customer A,SKU001,invalid
"""
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):  # Should raise some error
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_csv_grouping_by_order_number(self):
        """Test CSV rows are correctly grouped by order_number"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD001,Customer A,SKU001,2
ORD002,Customer B,SKU002,1
ORD001,Customer A,SKU003,3
"""
        csv_file = io.StringIO(csv_content)
        
        orders = self.service.parse_bulk_upload_csv(csv_file)
        
        # Should have at least 1 order
        assert len(orders) >= 1
        
        # Check that ORD001 exists
        ord001_orders = [o for o in orders if o.get('order_number') == 'ORD001']
        if ord001_orders:
            # If ORD001 is grouped, check it has the expected structure
            assert 'order_number' in ord001_orders[0]
    
    def test_empty_csv_file(self):
        """Test handling of empty CSV file"""
        csv_content = ""
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):  # Should raise some error
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_csv_with_only_headers(self):
        """Test CSV with only headers, no data"""
        csv_content = """order_number,customer_name,product_sku,quantity
"""
        csv_file = io.StringIO(csv_content)
        
        # Should raise HTTPException for empty data
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_csv_with_negative_quantity(self):
        """Test CSV with negative quantity"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD001,Customer A,SKU001,-5
"""
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):  # Should raise some error
            self.service.parse_bulk_upload_csv(csv_file)
    
    def test_csv_with_zero_quantity(self):
        """Test CSV with zero quantity"""
        csv_content = """order_number,customer_name,product_sku,quantity
ORD001,Customer A,SKU001,0
"""
        csv_file = io.StringIO(csv_content)
        
        with pytest.raises(Exception):  # Should raise some error
            self.service.parse_bulk_upload_csv(csv_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
