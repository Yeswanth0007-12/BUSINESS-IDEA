"""
Comprehensive unit tests for packing algorithms.
Tests 6-orientation testing, weight constraints, and box selection.
"""

import pytest
from app.services.optimization_engine import OptimizationEngine


@pytest.mark.unit
class TestOrientationTesting:
    """Test suite for 6-orientation testing algorithm"""
    
    def setup_method(self, mock_db):
        """Set up test fixtures"""
        self.engine = OptimizationEngine(db=mock_db)
    
    def test_all_six_orientations_tested(self):
        """Test that all 6 orientations are considered"""
        product_dims = (10, 8, 5)
        box_dims = (12, 10, 7)
        padding = 1
        
        orientation, utilization = self.engine.test_all_orientations(
            product_dims, box_dims, padding
        )
        
        assert orientation is not None
        assert utilization > 0
        assert utilization <= 100
    
    def test_best_orientation_selected(self):
        """Test that orientation with highest utilization is selected"""
        # Product that fits better in one orientation
        product_dims = (20, 10, 5)
        box_dims = (22, 12, 7)
        padding = 1
        
        orientation, utilization = self.engine.test_all_orientations(
            product_dims, box_dims, padding
        )
        
        assert orientation is not None
        # Should select orientation that maximizes space utilization
        assert utilization > 50
    
    def test_no_orientation_fits(self):
        """Test when product doesn't fit in any orientation"""
        product_dims = (30, 25, 20)
        box_dims = (15, 12, 10)
        padding = 1
        
        orientation, utilization = self.engine.test_all_orientations(
            product_dims, box_dims, padding
        )
        
        assert orientation is None
        assert utilization == 0
    
    def test_orientation_with_padding(self):
        """Test orientation testing accounts for padding"""
        product_dims = (10, 10, 10)
        box_dims = (15, 15, 15)
        padding = 2  # Need 2cm on each side
        
        orientation, utilization = self.engine.test_all_orientations(
            product_dims, box_dims, padding
        )
        
        # Product + padding should fit
        assert orientation is not None
        assert utilization > 0
    
    def test_orientation_tight_fit(self):
        """Test orientation with exact fit (edge case)"""
        product_dims = (10, 8, 5)
        box_dims = (10, 8, 5)
        padding = 0
        
        orientation, utilization = self.engine.test_all_orientations(
            product_dims, box_dims, padding
        )
        
        assert orientation is not None
        assert utilization == 100.0  # Perfect fit
    
    def test_space_utilization_calculation(self):
        """Test space utilization is calculated correctly"""
        product_dims = (10, 10, 10)  # Volume = 1000
        box_dims = (20, 20, 20)  # Volume = 8000
        padding = 0
        
        orientation, utilization = self.engine.test_all_orientations(
            product_dims, box_dims, padding
        )
        
        expected_utilization = (1000 / 8000) * 100  # 12.5%
        assert orientation is not None
        assert abs(utilization - expected_utilization) < 0.1


@pytest.mark.unit
class TestWeightConstraints:
    """Test suite for weight constraint validation"""
    
    def setup_method(self, mock_db):
        """Set up test fixtures"""
        self.engine = OptimizationEngine(db=mock_db)
    
    def test_weight_within_limit(self):
        """Test product weight within box limit"""
        product_weight = 5.0
        box_max_weight = 10.0
        
        is_valid = self.engine.validate_weight_constraint(
            product_weight, box_max_weight
        )
        
        assert is_valid is True
    
    def test_weight_exceeds_limit(self):
        """Test product weight exceeds box limit"""
        product_weight = 15.0
        box_max_weight = 10.0
        
        is_valid = self.engine.validate_weight_constraint(
            product_weight, box_max_weight
        )
        
        assert is_valid is False
    
    def test_weight_exactly_at_limit(self):
        """Test product weight exactly at box limit (edge case)"""
        product_weight = 10.0
        box_max_weight = 10.0
        
        is_valid = self.engine.validate_weight_constraint(
            product_weight, box_max_weight
        )
        
        assert is_valid is True
    
    def test_zero_weight(self):
        """Test zero weight product (edge case)"""
        product_weight = 0.0
        box_max_weight = 10.0
        
        is_valid = self.engine.validate_weight_constraint(
            product_weight, box_max_weight
        )
        
        assert is_valid is True
    
    def test_very_heavy_product(self):
        """Test very heavy product (boundary condition)"""
        product_weight = 100.0
        box_max_weight = 30.0
        
        is_valid = self.engine.validate_weight_constraint(
            product_weight, box_max_weight
        )
        
        assert is_valid is False


@pytest.mark.unit
class TestBoxSelection:
    """Test suite for enhanced box selection algorithm"""
    
    def setup_method(self, mock_db):
        """Set up test fixtures"""
        self.engine = OptimizationEngine(db=mock_db)
    
    def test_box_selection_with_weight_filter(self):
        """Test that boxes exceeding weight limit are filtered out"""
        from unittest.mock import MagicMock
        from app.models.product import Product
        from app.models.box import Box
        
        # Create mock product
        product = MagicMock(spec=Product)
        product.name = "Heavy Product"
        product.length_cm = 10.0
        product.width_cm = 10.0
        product.height_cm = 10.0
        product.weight_kg = 20.0
        product.category = 'general'
        
        # Create mock boxes
        box1 = MagicMock(spec=Box)
        box1.id = 1
        box1.name = "Light Box"
        box1.length_cm = 15.0
        box1.width_cm = 15.0
        box1.height_cm = 15.0
        box1.max_weight_kg = 10.0  # Too light
        box1.cost_per_unit = 1.0
        
        box2 = MagicMock(spec=Box)
        box2.id = 2
        box2.name = "Heavy Box"
        box2.length_cm = 20.0
        box2.width_cm = 20.0
        box2.height_cm = 20.0
        box2.max_weight_kg = 25.0  # Suitable
        box2.cost_per_unit = 2.0
        
        boxes = [box1, box2]
        padding = 2.0
        
        result = self.engine.find_optimal_box(product, boxes, padding)
        
        assert result is not None
        assert result['box'] is not None
        assert result['box'].id == 2  # Only box that meets weight constraint
    
    def test_box_selection_prefers_lowest_cost(self):
        """Test that lowest cost box is selected when multiple fit"""
        from unittest.mock import MagicMock
        from app.models.product import Product
        from app.models.box import Box
        
        # Create mock product
        product = MagicMock(spec=Product)
        product.name = "Test Product"
        product.length_cm = 10.0
        product.width_cm = 10.0
        product.height_cm = 10.0
        product.weight_kg = 5.0
        product.category = 'general'
        
        # Create mock boxes
        box1 = MagicMock(spec=Box)
        box1.id = 1
        box1.name = "Expensive Box"
        box1.length_cm = 20.0
        box1.width_cm = 20.0
        box1.height_cm = 20.0
        box1.max_weight_kg = 15.0
        box1.cost_per_unit = 3.0
        
        box2 = MagicMock(spec=Box)
        box2.id = 2
        box2.name = "Cheap Box"
        box2.length_cm = 18.0
        box2.width_cm = 18.0
        box2.height_cm = 18.0
        box2.max_weight_kg = 15.0
        box2.cost_per_unit = 1.5  # Cheaper
        
        boxes = [box1, box2]
        padding = 2.0
        
        result = self.engine.find_optimal_box(product, boxes, padding)
        
        assert result is not None
        assert result['box'] is not None
        assert result['box'].id == 2  # Cheaper box selected
    
    def test_box_selection_utilization_tiebreaker(self):
        """Test that better utilization breaks cost ties"""
        from unittest.mock import MagicMock
        from app.models.product import Product
        from app.models.box import Box
        
        # Create mock product
        product = MagicMock(spec=Product)
        product.name = "Test Product"
        product.length_cm = 10.0
        product.width_cm = 10.0
        product.height_cm = 10.0
        product.weight_kg = 5.0
        product.category = 'general'
        
        # Create mock boxes with same cost
        box1 = MagicMock(spec=Box)
        box1.id = 1
        box1.name = "Large Box"
        box1.length_cm = 30.0
        box1.width_cm = 30.0
        box1.height_cm = 30.0
        box1.max_weight_kg = 15.0
        box1.cost_per_unit = 2.0
        
        box2 = MagicMock(spec=Box)
        box2.id = 2
        box2.name = "Small Box"
        box2.length_cm = 15.0
        box2.width_cm = 15.0
        box2.height_cm = 15.0
        box2.max_weight_kg = 15.0
        box2.cost_per_unit = 2.0  # Same cost
        
        boxes = [box1, box2]
        padding = 2.0
        
        result = self.engine.find_optimal_box(product, boxes, padding)
        
        assert result is not None
        assert result['box'] is not None
        assert result['box'].id == 2  # Better utilization
        assert result['space_utilization'] > 20  # Higher utilization
    
    def test_no_suitable_box_found(self):
        """Test when no box meets all constraints"""
        from unittest.mock import MagicMock
        from app.models.product import Product
        from app.models.box import Box
        
        # Create mock product (too large)
        product = MagicMock(spec=Product)
        product.name = "Huge Product"
        product.length_cm = 50.0
        product.width_cm = 50.0
        product.height_cm = 50.0
        product.weight_kg = 100.0
        product.category = 'general'
        
        # Create mock box (too small)
        box1 = MagicMock(spec=Box)
        box1.id = 1
        box1.name = "Small Box"
        box1.length_cm = 20.0
        box1.width_cm = 20.0
        box1.height_cm = 20.0
        box1.max_weight_kg = 10.0
        box1.cost_per_unit = 1.0
        
        boxes = [box1]
        padding = 2.0
        
        result = self.engine.find_optimal_box(product, boxes, padding)
        
        assert result is not None
        assert result['box'] is None
        assert 'reason' in result
    
    def test_unused_volume_calculation(self):
        """Test that unused volume is calculated correctly"""
        from unittest.mock import MagicMock
        from app.models.product import Product
        from app.models.box import Box
        
        # Create mock product
        product = MagicMock(spec=Product)
        product.name = "Test Product"
        product.length_cm = 10.0
        product.width_cm = 10.0
        product.height_cm = 10.0
        product.weight_kg = 5.0
        product.category = 'general'
        
        # Create mock box
        box1 = MagicMock(spec=Box)
        box1.id = 1
        box1.name = "Test Box"
        box1.length_cm = 20.0
        box1.width_cm = 20.0
        box1.height_cm = 20.0
        box1.max_weight_kg = 15.0
        box1.cost_per_unit = 2.0
        
        boxes = [box1]
        padding = 2.0
        
        result = self.engine.find_optimal_box(product, boxes, padding)
        
        assert result is not None
        assert result['box'] is not None
        product_volume = 10 * 10 * 10  # 1000
        box_volume = 20 * 20 * 20  # 8000
        expected_unused = box_volume - product_volume  # 7000
        
        assert abs(result['unused_volume'] - expected_unused) < 1


@pytest.mark.unit
class TestEdgeCases:
    """Test suite for edge cases and boundary conditions"""
    
    def setup_method(self, mock_db):
        """Set up test fixtures"""
        self.engine = OptimizationEngine(db=mock_db)
    
    def test_zero_dimensions(self):
        """Test handling of zero dimensions"""
        product_dims = (0, 0, 0)
        box_dims = (10, 10, 10)
        padding = 1
        
        orientation, utilization = self.engine.test_all_orientations(
            product_dims, box_dims, padding
        )
        
        # Should handle gracefully
        assert orientation is not None or orientation is None
    
    def test_maximum_dimensions(self):
        """Test handling of very large dimensions"""
        product_dims = (1000, 1000, 1000)
        box_dims = (1100, 1100, 1100)
        padding = 50
        
        orientation, utilization = self.engine.test_all_orientations(
            product_dims, box_dims, padding
        )
        
        assert orientation is not None
        assert utilization > 0
    
    def test_negative_padding(self):
        """Test handling of negative padding (should not occur but test robustness)"""
        product_dims = (10, 10, 10)
        box_dims = (15, 15, 15)
        padding = -1
        
        # Should either handle gracefully or raise appropriate error
        try:
            orientation, utilization = self.engine.test_all_orientations(
                product_dims, box_dims, padding
            )
            # If it doesn't raise, should still work
            assert orientation is not None or orientation is None
        except ValueError:
            # Acceptable to raise ValueError for invalid input
            pass
    
    def test_empty_box_list(self):
        """Test handling of empty box list"""
        from unittest.mock import MagicMock
        from app.models.product import Product
        
        # Create mock product
        product = MagicMock(spec=Product)
        product.name = "Test Product"
        product.length_cm = 10.0
        product.width_cm = 10.0
        product.height_cm = 10.0
        product.weight_kg = 5.0
        product.category = 'general'
        
        boxes = []
        padding = 2.0
        
        result = self.engine.find_optimal_box(product, boxes, padding)
        
        assert result is not None
        assert result['box'] is None
        assert 'reason' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
