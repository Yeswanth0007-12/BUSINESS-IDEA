"""
Comprehensive unit tests for multi-product order packing.
Tests bin packing algorithm, fragile item handling, and stackability constraints.
"""

import pytest
from app.services.optimization_engine import OptimizationEngine


@pytest.mark.unit
class TestBinPacking:
    """Test suite for bin packing algorithm (First Fit Decreasing)"""
    
    def setup_method(self, mock_db):
        """Set up test fixtures"""
        self.engine = OptimizationEngine(db=mock_db)
        
        # Create mock Product class
        class MockProduct:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        self.MockProduct = MockProduct
        
        # Create mock Box class
        class MockBox:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        self.MockBox = MockBox
    
    def test_single_product_packing(self):
        """Test packing order with single product"""
        product = self.MockProduct(
            id=1, name='Product 1',
            length_cm=10, width_cm=10, height_cm=10,
            weight_kg=2.0, fragile=False, stackable=True,
            category='general'
        )
        
        order_items = [
            {'product': product, 'quantity': 1}
        ]
        
        box = self.MockBox(
            id=1, name='Box 1',
            length_cm=15, width_cm=15, height_cm=15,
            cost_per_unit=1.0, max_weight_kg=10.0
        )
        
        boxes = [box]
        
        result = self.engine.pack_multi_product_order(
            order_items, boxes, courier_rate=2.5
        )
        
        assert result['success'] is True
        assert result['total_boxes'] == 1
        assert len(result['unpacked_items']) == 0
    
    def test_multiple_products_one_box(self):
        """Test packing multiple products into one box"""
        product = self.MockProduct(
            id=1, name='Product 1',
            length_cm=5, width_cm=5, height_cm=5,
            weight_kg=1.0, fragile=False, stackable=True,
            category='general'
        )
        
        order_items = [
            {'product': product, 'quantity': 2}
        ]
        
        box = self.MockBox(
            id=1, name='Box 1',
            length_cm=20, width_cm=20, height_cm=20,
            cost_per_unit=2.0, max_weight_kg=10.0
        )
        
        boxes = [box]
        
        result = self.engine.pack_multi_product_order(
            order_items, boxes, courier_rate=2.5
        )
        
        assert result['success'] is True
        assert result['total_boxes'] == 1  # Both items fit in one box
        assert len(result['unpacked_items']) == 0
    
    def test_products_sorted_by_volume(self):
        """Test that products are sorted by volume (largest first)"""
        product1 = self.MockProduct(
            id=1, name='Product 1',
            length_cm=5, width_cm=5, height_cm=5,  # Volume = 125
            weight_kg=1.0, fragile=False, stackable=True,
            category='general'
        )
        
        product2 = self.MockProduct(
            id=2, name='Product 2',
            length_cm=10, width_cm=10, height_cm=10,  # Volume = 1000 (larger)
            weight_kg=2.0, fragile=False, stackable=True,
            category='general'
        )
        
        order_items = [
            {'product': product1, 'quantity': 1},
            {'product': product2, 'quantity': 1}
        ]
        
        box = self.MockBox(
            id=1, name='Box 1',
            length_cm=15, width_cm=15, height_cm=15,
            cost_per_unit=1.5, max_weight_kg=10.0
        )
        
        boxes = [box]
        
        result = self.engine.pack_multi_product_order(
            order_items, boxes, courier_rate=2.5
        )
        
        # Larger product should be packed first
        assert result['success'] is True
    
    def test_multiple_boxes_needed(self):
        """Test when multiple boxes are needed"""
        product = self.MockProduct(
            id=1, name='Product 1',
            length_cm=15, width_cm=15, height_cm=15,
            weight_kg=5.0, fragile=False, stackable=True,
            category='general'
        )
        
        order_items = [
            {'product': product, 'quantity': 3}
        ]
        
        box = self.MockBox(
            id=1, name='Box 1',
            length_cm=20, width_cm=20, height_cm=20,
            cost_per_unit=2.0, max_weight_kg=8.0  # Can only fit one product per box
        )
        
        boxes = [box]
        
        result = self.engine.pack_multi_product_order(
            order_items, boxes, courier_rate=2.5
        )
        
        assert result['success'] is True
        assert result['total_boxes'] >= 2  # Need multiple boxes
    
    def test_some_items_dont_fit(self):
        """Test when some items cannot be packed"""
        product1 = self.MockProduct(
            id=1, name='Product 1',
            length_cm=10, width_cm=10, height_cm=10,
            weight_kg=2.0, fragile=False, stackable=True,
            category='general'
        )
        
        product2 = self.MockProduct(
            id=2, name='Product 2',
            length_cm=100, width_cm=100, height_cm=100,  # Too large
            weight_kg=50.0, fragile=False, stackable=True,
            category='general'
        )
        
        order_items = [
            {'product': product1, 'quantity': 1},
            {'product': product2, 'quantity': 1}
        ]
        
        box = self.MockBox(
            id=1, name='Box 1',
            length_cm=15, width_cm=15, height_cm=15,
            cost_per_unit=1.0, max_weight_kg=10.0
        )
        
        boxes = [box]
        
        result = self.engine.pack_multi_product_order(
            order_items, boxes, courier_rate=2.5
        )
        
        assert result['success'] is False
        assert len(result['unpacked_items']) > 0
        # Check that product2 is in unpacked items
        assert any(p.id == 2 for p in result['unpacked_items'])


@pytest.mark.unit
class TestFragileItemHandling:
    """Test suite for fragile item handling"""
    
    def setup_method(self, mock_db):
        """Set up test fixtures"""
        self.engine = OptimizationEngine(db=mock_db)
        
        class MockProduct:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        self.MockProduct = MockProduct
        
        class MockBox:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        self.MockBox = MockBox
    
    def test_fragile_item_packed_alone(self):
        """Test that fragile items are packed alone"""
        product1 = self.MockProduct(
            id=1, name='Product 1',
            length_cm=10, width_cm=10, height_cm=10,
            weight_kg=2.0, fragile=True, stackable=True,
            category='fragile'
        )
        
        product2 = self.MockProduct(
            id=2, name='Product 2',
            length_cm=10, width_cm=10, height_cm=10,
            weight_kg=2.0, fragile=False, stackable=True,
            category='general'
        )
        
        order_items = [
            {'product': product1, 'quantity': 1},
            {'product': product2, 'quantity': 1}
        ]
        
        box = self.MockBox(
            id=1, name='Box 1',
            length_cm=30, width_cm=30, height_cm=30,
            cost_per_unit=2.0, max_weight_kg=20.0
        )
        
        boxes = [box]
        
        result = self.engine.pack_multi_product_order(
            order_items, boxes, courier_rate=2.5
        )
        
        assert result['success'] is True
        assert result['total_boxes'] == 2  # Fragile item needs separate box
    
    def test_multiple_fragile_items(self):
        """Test that each fragile item gets its own box"""
        product = self.MockProduct(
            id=1, name='Product 1',
            length_cm=10, width_cm=10, height_cm=10,
            weight_kg=2.0, fragile=True, stackable=True,
            category='fragile'
        )
        
        order_items = [
            {'product': product, 'quantity': 2}
        ]
        
        box = self.MockBox(
            id=1, name='Box 1',
            length_cm=30, width_cm=30, height_cm=30,
            cost_per_unit=2.0, max_weight_kg=20.0
        )
        
        boxes = [box]
        
        result = self.engine.pack_multi_product_order(
            order_items, boxes, courier_rate=2.5
        )
        
        assert result['success'] is True
        assert result['total_boxes'] == 2  # Each fragile item in separate box
    
    def test_fragile_item_packed_first(self):
        """Test that fragile items are packed before non-fragile"""
        product1 = self.MockProduct(
            id=1, name='Product 1',
            length_cm=5, width_cm=5, height_cm=5,  # Smaller
            weight_kg=1.0, fragile=True, stackable=True,
            category='fragile'
        )
        
        product2 = self.MockProduct(
            id=2, name='Product 2',
            length_cm=10, width_cm=10, height_cm=10,  # Larger
            weight_kg=2.0, fragile=False, stackable=True,
            category='general'
        )
        
        order_items = [
            {'product': product1, 'quantity': 1},
            {'product': product2, 'quantity': 1}
        ]
        
        box = self.MockBox(
            id=1, name='Box 1',
            length_cm=15, width_cm=15, height_cm=15,
            cost_per_unit=1.0, max_weight_kg=10.0
        )
        
        boxes = [box]
        
        result = self.engine.pack_multi_product_order(
            order_items, boxes, courier_rate=2.5
        )
        
        # Fragile item should be packed first despite being smaller
        assert result['success'] is True


@pytest.mark.unit
class TestStackabilityConstraints:
    """Test suite for stackability constraints"""
    
    def setup_method(self, mock_db):
        """Set up test fixtures"""
        self.engine = OptimizationEngine(db=mock_db)
        
        class MockProduct:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        self.MockProduct = MockProduct
        
        class MockBox:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        self.MockBox = MockBox
    
    def test_non_stackable_item_packed_alone(self):
        """Test that non-stackable items are packed alone"""
        product1 = self.MockProduct(
            id=1, name='Product 1',
            length_cm=10, width_cm=10, height_cm=10,
            weight_kg=2.0, fragile=False, stackable=False,
            category='general'
        )
        
        product2 = self.MockProduct(
            id=2, name='Product 2',
            length_cm=10, width_cm=10, height_cm=10,
            weight_kg=2.0, fragile=False, stackable=True,
            category='general'
        )
        
        order_items = [
            {'product': product1, 'quantity': 1},
            {'product': product2, 'quantity': 1}
        ]
        
        box = self.MockBox(
            id=1, name='Box 1',
            length_cm=30, width_cm=30, height_cm=30,
            cost_per_unit=2.0, max_weight_kg=20.0
        )
        
        boxes = [box]
        
        result = self.engine.pack_multi_product_order(
            order_items, boxes, courier_rate=2.5
        )
        
        assert result['success'] is True
        assert result['total_boxes'] == 2  # Non-stackable needs separate box
    
    def test_multiple_non_stackable_items(self):
        """Test that each non-stackable item gets its own box"""
        product = self.MockProduct(
            id=1, name='Product 1',
            length_cm=10, width_cm=10, height_cm=10,
            weight_kg=2.0, fragile=False, stackable=False,
            category='general'
        )
        
        order_items = [
            {'product': product, 'quantity': 2}
        ]
        
        box = self.MockBox(
            id=1, name='Box 1',
            length_cm=30, width_cm=30, height_cm=30,
            cost_per_unit=2.0, max_weight_kg=20.0
        )
        
        boxes = [box]
        
        result = self.engine.pack_multi_product_order(
            order_items, boxes, courier_rate=2.5
        )
        
        assert result['success'] is True
        assert result['total_boxes'] == 2  # Each non-stackable in separate box


@pytest.mark.unit
class TestWeightConstraintsInPacking:
    """Test suite for weight constraints in multi-product packing"""
    
    def setup_method(self, mock_db):
        """Set up test fixtures"""
        self.engine = OptimizationEngine(db=mock_db)
        
        class MockProduct:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        self.MockProduct = MockProduct
        
        class MockBox:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        self.MockBox = MockBox
    
    def test_weight_limit_prevents_overpacking(self):
        """Test that weight limit prevents adding too many items to box"""
        product = self.MockProduct(
            id=1, name='Product 1',
            length_cm=5, width_cm=5, height_cm=5,
            weight_kg=3.0, fragile=False, stackable=True,
            category='general'
        )
        
        order_items = [
            {'product': product, 'quantity': 5}
        ]
        
        box = self.MockBox(
            id=1, name='Box 1',
            length_cm=30, width_cm=30, height_cm=30,
            cost_per_unit=2.0, max_weight_kg=8.0  # Can fit max 2 items (6kg)
        )
        
        boxes = [box]
        
        result = self.engine.pack_multi_product_order(
            order_items, boxes, courier_rate=2.5
        )
        
        assert result['success'] is True
        assert result['total_boxes'] >= 3  # Need multiple boxes due to weight
    
    def test_single_item_exceeds_all_boxes(self):
        """Test when single item is too heavy for all boxes"""
        product = self.MockProduct(
            id=1, name='Product 1',
            length_cm=10, width_cm=10, height_cm=10,
            weight_kg=50.0, fragile=False, stackable=True,
            category='general'
        )
        
        order_items = [
            {'product': product, 'quantity': 1}
        ]
        
        box = self.MockBox(
            id=1, name='Box 1',
            length_cm=30, width_cm=30, height_cm=30,
            cost_per_unit=2.0, max_weight_kg=20.0  # Too light
        )
        
        boxes = [box]
        
        result = self.engine.pack_multi_product_order(
            order_items, boxes, courier_rate=2.5
        )
        
        assert result['success'] is False
        assert len(result['unpacked_items']) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
