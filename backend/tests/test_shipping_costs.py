"""
Comprehensive unit tests for shipping cost calculations.
Tests volumetric weight, billable weight, and shipping cost algorithms.
"""

import pytest
from unittest.mock import MagicMock
from app.services.optimization_engine import OptimizationEngine
from app.models.box import Box


@pytest.mark.unit
class TestVolumetricWeight:
    """Test suite for volumetric weight calculation"""
    
    def setup_method(self, mock_db):
        """Set up test fixtures"""
        self.engine = OptimizationEngine(db=mock_db)
    
    def test_standard_volumetric_weight(self):
        """Test standard volumetric weight calculation"""
        length_cm = 30
        width_cm = 20
        height_cm = 10
        
        vol_weight = self.engine.calculate_volumetric_weight(
            length_cm, width_cm, height_cm
        )
        
        expected = (30 * 20 * 10) / 5000  # 1.2 kg
        assert abs(vol_weight - expected) < 0.01
    
    def test_volumetric_weight_rounding(self):
        """Test that volumetric weight is rounded to 2 decimal places"""
        length_cm = 33
        width_cm = 22
        height_cm = 11
        
        vol_weight = self.engine.calculate_volumetric_weight(
            length_cm, width_cm, height_cm
        )
        
        # Should be rounded to 2 decimal places
        assert len(str(vol_weight).split('.')[-1]) <= 2
    
    def test_small_box_volumetric_weight(self):
        """Test volumetric weight for small box"""
        vol_weight = self.engine.calculate_volumetric_weight(10, 10, 10)
        
        expected = (10 * 10 * 10) / 5000  # 0.2 kg
        assert abs(vol_weight - expected) < 0.01
    
    def test_large_box_volumetric_weight(self):
        """Test volumetric weight for large box"""
        vol_weight = self.engine.calculate_volumetric_weight(100, 80, 60)
        
        expected = (100 * 80 * 60) / 5000  # 96.0 kg
        assert abs(vol_weight - expected) < 0.01
    
    def test_zero_dimensions_volumetric_weight(self):
        """Test volumetric weight with zero dimensions (edge case)"""
        vol_weight = self.engine.calculate_volumetric_weight(0, 0, 0)
        
        assert vol_weight == 0.0
    
    def test_one_zero_dimension(self):
        """Test volumetric weight with one zero dimension"""
        vol_weight = self.engine.calculate_volumetric_weight(10, 0, 10)
        
        assert vol_weight == 0.0


@pytest.mark.unit
class TestBillableWeight:
    """Test suite for billable weight calculation"""
    
    def setup_method(self, mock_db):
        """Set up test fixtures"""
        self.engine = OptimizationEngine(db=mock_db)
    
    def test_actual_weight_higher(self):
        """Test when actual weight exceeds volumetric weight"""
        actual_weight = 10.0
        volumetric_weight = 5.0
        
        billable = self.engine.calculate_billable_weight(
            actual_weight, volumetric_weight
        )
        
        assert billable == actual_weight
    
    def test_volumetric_weight_higher(self):
        """Test when volumetric weight exceeds actual weight"""
        actual_weight = 3.0
        volumetric_weight = 8.0
        
        billable = self.engine.calculate_billable_weight(
            actual_weight, volumetric_weight
        )
        
        assert billable == volumetric_weight
    
    def test_equal_weights(self):
        """Test when actual and volumetric weights are equal"""
        actual_weight = 5.0
        volumetric_weight = 5.0
        
        billable = self.engine.calculate_billable_weight(
            actual_weight, volumetric_weight
        )
        
        assert billable == 5.0
    
    def test_zero_actual_weight(self):
        """Test with zero actual weight (edge case)"""
        actual_weight = 0.0
        volumetric_weight = 5.0
        
        billable = self.engine.calculate_billable_weight(
            actual_weight, volumetric_weight
        )
        
        assert billable == volumetric_weight
    
    def test_zero_volumetric_weight(self):
        """Test with zero volumetric weight (edge case)"""
        actual_weight = 5.0
        volumetric_weight = 0.0
        
        billable = self.engine.calculate_billable_weight(
            actual_weight, volumetric_weight
        )
        
        assert billable == actual_weight
    
    def test_both_zero(self):
        """Test with both weights zero (edge case)"""
        actual_weight = 0.0
        volumetric_weight = 0.0
        
        billable = self.engine.calculate_billable_weight(
            actual_weight, volumetric_weight
        )
        
        assert billable == 0.0


@pytest.mark.unit
class TestShippingCost:
    """Test suite for shipping cost calculation"""
    
    def setup_method(self, mock_db):
        """Set up test fixtures"""
        self.engine = OptimizationEngine(db=mock_db)
    
    def test_shipping_cost_with_default_rate(self):
        """Test shipping cost with default courier rate"""
        # Create mock box
        box = MagicMock(spec=Box)
        box.length_cm = 30.0
        box.width_cm = 20.0
        box.height_cm = 10.0
        
        product_weight = 5.0
        courier_rate = 2.5  # Default rate
        
        shipping_cost = self.engine.calculate_shipping_cost(
            box, product_weight, courier_rate
        )
        
        # Volumetric weight = (30*20*10)/5000 = 1.2 kg
        # Billable weight = max(5.0, 1.2) = 5.0 kg
        # Shipping cost = 5.0 * 2.5 = 12.5
        expected = 12.5
        assert abs(shipping_cost - expected) < 0.01
    
    def test_shipping_cost_volumetric_higher(self):
        """Test shipping cost when volumetric weight is higher"""
        # Create mock box
        box = MagicMock(spec=Box)
        box.length_cm = 100.0
        box.width_cm = 80.0
        box.height_cm = 60.0
        
        product_weight = 10.0
        courier_rate = 2.5
        
        shipping_cost = self.engine.calculate_shipping_cost(
            box, product_weight, courier_rate
        )
        
        # Volumetric weight = (100*80*60)/5000 = 96.0 kg
        # Billable weight = max(10.0, 96.0) = 96.0 kg
        # Shipping cost = 96.0 * 2.5 = 240.0
        expected = 240.0
        assert abs(shipping_cost - expected) < 0.01
    
    def test_shipping_cost_custom_rate(self):
        """Test shipping cost with custom courier rate"""
        # Create mock box
        box = MagicMock(spec=Box)
        box.length_cm = 30.0
        box.width_cm = 20.0
        box.height_cm = 10.0
        
        product_weight = 5.0
        courier_rate = 3.5  # Custom rate
        
        shipping_cost = self.engine.calculate_shipping_cost(
            box, product_weight, courier_rate
        )
        
        # Billable weight = 5.0 kg
        # Shipping cost = 5.0 * 3.5 = 17.5
        expected = 17.5
        assert abs(shipping_cost - expected) < 0.01
    
    def test_shipping_cost_rounding(self):
        """Test that shipping cost is rounded to 2 decimal places"""
        # Create mock box
        box = MagicMock(spec=Box)
        box.length_cm = 33.0
        box.width_cm = 22.0
        box.height_cm = 11.0
        
        product_weight = 5.0
        courier_rate = 2.33
        
        shipping_cost = self.engine.calculate_shipping_cost(
            box, product_weight, courier_rate
        )
        
        # Should be rounded to 2 decimal places
        assert len(str(shipping_cost).split('.')[-1]) <= 2
    
    def test_shipping_cost_zero_weight(self):
        """Test shipping cost with zero weight (edge case)"""
        # Create mock box
        box = MagicMock(spec=Box)
        box.length_cm = 10.0
        box.width_cm = 10.0
        box.height_cm = 10.0
        
        product_weight = 0.0
        courier_rate = 2.5
        
        shipping_cost = self.engine.calculate_shipping_cost(
            box, product_weight, courier_rate
        )
        
        # Volumetric weight = (10*10*10)/5000 = 0.2 kg
        # Billable weight = max(0.0, 0.2) = 0.2 kg
        # Shipping cost = 0.2 * 2.5 = 0.5
        expected = 0.5
        assert abs(shipping_cost - expected) < 0.01


@pytest.mark.unit
class TestTotalCost:
    """Test suite for total cost calculation (box + shipping)"""
    
    def setup_method(self, mock_db):
        """Set up test fixtures"""
        self.engine = OptimizationEngine(db=mock_db)
    
    def test_total_cost_calculation(self):
        """Test total cost includes box cost and shipping cost"""
        # Create mock box
        box = MagicMock(spec=Box)
        box.length_cm = 30.0
        box.width_cm = 20.0
        box.height_cm = 10.0
        box.cost_per_unit = 2.0
        
        product_weight = 5.0
        courier_rate = 2.5
        
        shipping_cost = self.engine.calculate_shipping_cost(
            box, product_weight, courier_rate
        )
        
        total_cost = box.cost_per_unit + shipping_cost
        
        # Box cost = 2.0
        # Shipping cost = 12.5 (from previous test)
        # Total = 14.5
        expected_total = 14.5
        assert abs(total_cost - expected_total) < 0.01
    
    def test_savings_with_shipping(self):
        """Test savings calculation includes shipping costs"""
        # Create mock current box
        current_box = MagicMock(spec=Box)
        current_box.length_cm = 50.0
        current_box.width_cm = 40.0
        current_box.height_cm = 30.0
        current_box.cost_per_unit = 5.0
        
        # Create mock recommended box
        recommended_box = MagicMock(spec=Box)
        recommended_box.length_cm = 30.0
        recommended_box.width_cm = 20.0
        recommended_box.height_cm = 10.0
        recommended_box.cost_per_unit = 2.0
        
        product_weight = 5.0
        courier_rate = 2.5
        monthly_volume = 100
        
        # Calculate shipping costs
        shipping_current = self.engine.calculate_shipping_cost(
            current_box, product_weight, courier_rate
        )
        shipping_recommended = self.engine.calculate_shipping_cost(
            recommended_box, product_weight, courier_rate
        )
        
        # Total costs
        total_current = (current_box.cost_per_unit + shipping_current) * monthly_volume
        total_recommended = (recommended_box.cost_per_unit + shipping_recommended) * monthly_volume
        
        savings = total_current - total_recommended
        
        # Savings should be positive (current is more expensive)
        assert savings > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
