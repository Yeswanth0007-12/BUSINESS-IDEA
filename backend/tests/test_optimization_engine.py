"""
Unit tests for the Optimization Engine
Tests core algorithms and optimization logic
"""

import pytest
from app.services.optimization_engine import OptimizationEngine


class TestOptimizationEngine:
    """Test suite for OptimizationEngine"""
    
    def setup_method(self, mock_db):
        """Set up test fixtures"""
        self.engine = OptimizationEngine(db=mock_db)
    
    def test_calculate_volumetric_weight(self):
        """Test volumetric weight calculation"""
        # Test case 1: Standard box
        vol_weight = self.engine.calculate_volumetric_weight(30, 20, 10)
        assert abs(vol_weight - 1.2) < 0.01  # (30 * 20 * 10) / 5000, allow small rounding difference
        
        # Test case 2: Small box
        vol_weight = self.engine.calculate_volumetric_weight(10, 10, 10)
        assert abs(vol_weight - 0.2) < 0.01  # (10 * 10 * 10) / 5000
        
        # Test case 3: Large box
        vol_weight = self.engine.calculate_volumetric_weight(50, 40, 30)
        assert abs(vol_weight - 12.0) < 0.01  # (50 * 40 * 30) / 5000
    
    def test_get_category_padding(self):
        """Test category-based padding rules"""
        # Electronics: 3cm padding (matches current implementation)
        padding = self.engine.get_category_padding("electronics")
        assert padding == 3.0
        
        # Fragile: 4cm padding (matches current implementation)
        padding = self.engine.get_category_padding("fragile")
        assert padding == 4.0
        
        # General: 2cm padding (default)
        padding = self.engine.get_category_padding("general")
        assert padding == 2.0
        
        # Unknown category: default 2cm
        padding = self.engine.get_category_padding("unknown")
        assert padding == 2.0
    
    def test_find_optimal_box_exact_fit(self):
        """Test finding optimal box with exact fit"""
        from unittest.mock import MagicMock
        from app.models.product import Product
        from app.models.box import Box
        
        # Create mock product
        product = MagicMock(spec=Product)
        product.name = "Test Product"
        product.length_cm = 20.0
        product.width_cm = 15.0
        product.height_cm = 10.0
        product.weight_kg = 2.0
        product.category = 'general'
        
        # Create mock boxes
        box1 = MagicMock(spec=Box)
        box1.id = 1
        box1.name = "Small Box"
        box1.length_cm = 25.0
        box1.width_cm = 20.0
        box1.height_cm = 15.0
        box1.max_weight_kg = 10.0
        box1.cost_per_unit = 2.0
        
        box2 = MagicMock(spec=Box)
        box2.id = 2
        box2.name = "Medium Box"
        box2.length_cm = 30.0
        box2.width_cm = 25.0
        box2.height_cm = 20.0
        box2.max_weight_kg = 15.0
        box2.cost_per_unit = 3.0
        
        boxes = [box1, box2]
        padding = 2.0  # General category padding
        
        result = self.engine.find_optimal_box(product, boxes, padding)
        assert result is not None
        assert result['box'].id == 1  # Smallest box that fits
        assert result['box'].cost_per_unit == 2.0
    
    def test_find_optimal_box_no_fit(self):
        """Test when no box fits the product"""
        from unittest.mock import MagicMock
        from app.models.product import Product
        from app.models.box import Box
        
        # Create mock product (too large)
        product = MagicMock(spec=Product)
        product.name = "Large Product"
        product.length_cm = 100.0
        product.width_cm = 80.0
        product.height_cm = 60.0
        product.weight_kg = 50.0
        product.category = 'general'
        
        # Create mock boxes (too small)
        box1 = MagicMock(spec=Box)
        box1.id = 1
        box1.name = "Small Box"
        box1.length_cm = 25.0
        box1.width_cm = 20.0
        box1.height_cm = 15.0
        box1.max_weight_kg = 10.0
        box1.cost_per_unit = 2.0
        
        box2 = MagicMock(spec=Box)
        box2.id = 2
        box2.name = "Medium Box"
        box2.length_cm = 30.0
        box2.width_cm = 25.0
        box2.height_cm = 20.0
        box2.max_weight_kg = 15.0
        box2.cost_per_unit = 3.0
        
        boxes = [box1, box2]
        padding = 2.0
        
        result = self.engine.find_optimal_box(product, boxes, padding)
        assert result is not None
        assert result['box'] is None  # No box fits
    
    def test_find_optimal_box_with_padding(self):
        """Test optimal box selection with category padding"""
        from unittest.mock import MagicMock
        from app.models.product import Product
        from app.models.box import Box
        
        # Create mock product (fragile category)
        product = MagicMock(spec=Product)
        product.name = "Fragile Product"
        product.length_cm = 20.0
        product.width_cm = 15.0
        product.height_cm = 10.0
        product.weight_kg = 2.0
        product.category = 'fragile'
        
        # Create mock boxes
        box1 = MagicMock(spec=Box)
        box1.id = 1
        box1.name = "Medium Box"
        box1.length_cm = 30.0
        box1.width_cm = 25.0
        box1.height_cm = 20.0
        box1.max_weight_kg = 10.0
        box1.cost_per_unit = 2.0
        
        box2 = MagicMock(spec=Box)
        box2.id = 2
        box2.name = "Large Box"
        box2.length_cm = 40.0
        box2.width_cm = 35.0
        box2.height_cm = 30.0
        box2.max_weight_kg = 15.0
        box2.cost_per_unit = 3.5
        
        boxes = [box1, box2]
        padding = 4.0  # Fragile category padding (matches current implementation)
        
        result = self.engine.find_optimal_box(product, boxes, padding)
        assert result is not None
        # Should select box that accommodates product + 5cm padding
        assert result['box'].id == 1
    
    def test_calculate_savings(self):
        """Test savings calculation"""
        from unittest.mock import MagicMock
        from app.models.box import Box
        
        # Create mock boxes
        current_box = MagicMock(spec=Box)
        current_box.cost_per_unit = 5.0
        
        optimal_box = MagicMock(spec=Box)
        optimal_box.cost_per_unit = 3.0
        
        monthly_volume = 100
        
        monthly_savings, annual_savings = self.engine.calculate_savings(
            current_box, optimal_box, monthly_volume
        )
        assert monthly_savings == 200.0  # (5.0 - 3.0) * 100
        assert annual_savings == 2400.0  # 200.0 * 12
        
        # Test no savings
        optimal_box.cost_per_unit = 5.0
        monthly_savings, annual_savings = self.engine.calculate_savings(
            current_box, optimal_box, monthly_volume
        )
        assert monthly_savings == 0.0
        assert annual_savings == 0.0
        
        # Test negative savings (more expensive)
        optimal_box.cost_per_unit = 7.0
        monthly_savings, annual_savings = self.engine.calculate_savings(
            current_box, optimal_box, monthly_volume
        )
        assert monthly_savings == -200.0  # (5.0 - 7.0) * 100
        assert annual_savings == -2400.0  # -200.0 * 12
    
    def test_volumetric_weight_edge_cases(self):
        """Test edge cases for volumetric weight"""
        # Zero dimensions
        vol_weight = self.engine.calculate_volumetric_weight(0, 0, 0)
        assert vol_weight == 0.0
        
        # Very small dimensions
        vol_weight = self.engine.calculate_volumetric_weight(1, 1, 1)
        assert abs(vol_weight - 0.0002) < 0.001  # Allow reasonable rounding difference
        
        # Very large dimensions
        vol_weight = self.engine.calculate_volumetric_weight(200, 150, 100)
        assert abs(vol_weight - 600.0) < 0.01  # Allow small rounding difference
    
    def test_box_selection_prefers_smallest(self):
        """Test that engine prefers smallest fitting box"""
        from unittest.mock import MagicMock
        from app.models.product import Product
        from app.models.box import Box
        
        # Create mock product
        product = MagicMock(spec=Product)
        product.name = "Small Product"
        product.length_cm = 10.0
        product.width_cm = 10.0
        product.height_cm = 10.0
        product.weight_kg = 1.0
        product.category = 'general'
        
        # Create mock boxes (all fit, but different sizes)
        box1 = MagicMock(spec=Box)
        box1.id = 1
        box1.name = "Large Box"
        box1.length_cm = 50.0
        box1.width_cm = 50.0
        box1.height_cm = 50.0
        box1.max_weight_kg = 20.0
        box1.cost_per_unit = 10.0
        
        box2 = MagicMock(spec=Box)
        box2.id = 2
        box2.name = "Small Box"
        box2.length_cm = 15.0
        box2.width_cm = 15.0
        box2.height_cm = 15.0
        box2.max_weight_kg = 5.0
        box2.cost_per_unit = 2.0
        
        box3 = MagicMock(spec=Box)
        box3.id = 3
        box3.name = "Medium Box"
        box3.length_cm = 30.0
        box3.width_cm = 30.0
        box3.height_cm = 30.0
        box3.max_weight_kg = 10.0
        box3.cost_per_unit = 5.0
        
        boxes = [box1, box2, box3]
        padding = 2.0
        
        result = self.engine.find_optimal_box(product, boxes, padding)
        assert result is not None
        assert result['box'].id == 2  # Smallest (cheapest) box that fits
        assert result['box'].cost_per_unit == 2.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
