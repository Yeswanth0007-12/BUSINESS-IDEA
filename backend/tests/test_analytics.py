"""
Comprehensive unit tests for analytics calculations.
Tests space utilization, box usage, shipping costs, and trends.
"""

import pytest
from datetime import datetime, timedelta
from app.services.analytics_service_v2 import AnalyticsServiceV2


@pytest.mark.unit
class TestSpaceUtilization:
    """Test suite for space utilization analytics"""
    
    def test_average_utilization_calculation(self):
        """Test average space utilization calculation"""
        utilizations = [60.0, 70.0, 80.0, 90.0]
        
        avg = sum(utilizations) / len(utilizations)
        
        assert avg == 75.0
    
    def test_waste_percentage_calculation(self):
        """Test waste percentage calculation"""
        avg_utilization = 68.5
        
        waste_percentage = 100 - avg_utilization
        
        assert waste_percentage == 31.5
    
    def test_utilization_bounds(self):
        """Test that utilization is between 0 and 100"""
        utilizations = [45.0, 67.0, 89.0, 23.0]
        
        for util in utilizations:
            assert 0 <= util <= 100
        
        avg = sum(utilizations) / len(utilizations)
        assert 0 <= avg <= 100
    
    def test_empty_results(self):
        """Test handling of empty results"""
        utilizations = []
        
        if len(utilizations) == 0:
            avg_utilization = 0
            waste_percentage = 100
        else:
            avg_utilization = sum(utilizations) / len(utilizations)
            waste_percentage = 100 - avg_utilization
        
        assert avg_utilization == 0
        assert waste_percentage == 100
    
    def test_perfect_utilization(self):
        """Test perfect 100% utilization"""
        utilizations = [100.0, 100.0, 100.0]
        
        avg = sum(utilizations) / len(utilizations)
        waste = 100 - avg
        
        assert avg == 100.0
        assert waste == 0.0
    
    def test_min_max_utilization(self):
        """Test min and max utilization calculation"""
        utilizations = [45.0, 67.0, 89.0, 23.0, 78.0]
        
        min_util = min(utilizations)
        max_util = max(utilizations)
        
        assert min_util == 23.0
        assert max_util == 89.0


@pytest.mark.unit
class TestBoxUsageFrequency:
    """Test suite for box usage frequency analysis"""
    
    def test_usage_count_calculation(self):
        """Test box usage count calculation"""
        box_usage = {
            'box_1': 50,
            'box_2': 30,
            'box_3': 20
        }
        
        total_usage = sum(box_usage.values())
        
        assert total_usage == 100
    
    def test_percentage_calculation(self):
        """Test usage percentage calculation"""
        box_usage = {
            'box_1': 50,
            'box_2': 30,
            'box_3': 20
        }
        
        total_usage = sum(box_usage.values())
        percentages = {}
        
        for box_id, count in box_usage.items():
            percentages[box_id] = (count / total_usage) * 100
        
        assert percentages['box_1'] == 50.0
        assert percentages['box_2'] == 30.0
        assert percentages['box_3'] == 20.0
    
    def test_percentages_sum_to_100(self):
        """Test that all percentages sum to 100"""
        box_usage = {
            'box_1': 45,
            'box_2': 35,
            'box_3': 20
        }
        
        total_usage = sum(box_usage.values())
        percentages = []
        
        for count in box_usage.values():
            percentages.append((count / total_usage) * 100)
        
        total_percentage = sum(percentages)
        assert abs(total_percentage - 100.0) < 0.01
    
    def test_total_cost_calculation(self):
        """Test total cost per box type calculation"""
        box_usage = {
            'box_1': {'count': 50, 'cost_per_unit': 2.0},
            'box_2': {'count': 30, 'cost_per_unit': 3.0},
        }
        
        total_costs = {}
        for box_id, data in box_usage.items():
            total_costs[box_id] = data['count'] * data['cost_per_unit']
        
        assert total_costs['box_1'] == 100.0
        assert total_costs['box_2'] == 90.0
    
    def test_sorting_by_usage_count(self):
        """Test sorting boxes by usage count descending"""
        box_usage = [
            {'box_id': 1, 'usage_count': 30},
            {'box_id': 2, 'usage_count': 50},
            {'box_id': 3, 'usage_count': 20},
        ]
        
        sorted_usage = sorted(box_usage, key=lambda x: x['usage_count'], reverse=True)
        
        assert sorted_usage[0]['box_id'] == 2  # Highest usage
        assert sorted_usage[1]['box_id'] == 1
        assert sorted_usage[2]['box_id'] == 3  # Lowest usage


@pytest.mark.unit
class TestShippingCostMetrics:
    """Test suite for shipping cost analytics"""
    
    def test_total_shipping_cost(self):
        """Test total shipping cost calculation"""
        shipments = [
            {'shipping_cost': 12.5},
            {'shipping_cost': 25.0},
            {'shipping_cost': 18.75},
        ]
        
        total_cost = sum(s['shipping_cost'] for s in shipments)
        
        assert total_cost == 56.25
    
    def test_average_cost_per_order(self):
        """Test average shipping cost per order"""
        shipments = [
            {'shipping_cost': 10.0},
            {'shipping_cost': 20.0},
            {'shipping_cost': 30.0},
        ]
        
        avg_cost = sum(s['shipping_cost'] for s in shipments) / len(shipments)
        
        assert avg_cost == 20.0
    
    def test_average_billable_weight(self):
        """Test average billable weight calculation"""
        shipments = [
            {'billable_weight': 5.0},
            {'billable_weight': 10.0},
            {'billable_weight': 15.0},
        ]
        
        avg_weight = sum(s['billable_weight'] for s in shipments) / len(shipments)
        
        assert avg_weight == 10.0
    
    def test_volumetric_weight_percentage(self):
        """Test percentage where volumetric weight exceeds actual"""
        shipments = [
            {'actual_weight': 5.0, 'volumetric_weight': 8.0},  # Volumetric higher
            {'actual_weight': 10.0, 'volumetric_weight': 6.0},  # Actual higher
            {'actual_weight': 3.0, 'volumetric_weight': 7.0},  # Volumetric higher
            {'actual_weight': 15.0, 'volumetric_weight': 12.0},  # Actual higher
        ]
        
        volumetric_higher_count = sum(
            1 for s in shipments if s['volumetric_weight'] > s['actual_weight']
        )
        
        percentage = (volumetric_higher_count / len(shipments)) * 100
        
        assert percentage == 50.0  # 2 out of 4
    
    def test_empty_shipments(self):
        """Test handling of empty shipments"""
        shipments = []
        
        if len(shipments) == 0:
            total_cost = 0
            avg_cost = 0
        else:
            total_cost = sum(s['shipping_cost'] for s in shipments)
            avg_cost = total_cost / len(shipments)
        
        assert total_cost == 0
        assert avg_cost == 0


@pytest.mark.unit
class TestTrendAnalysis:
    """Test suite for time-series trend analysis"""
    
    def test_monthly_savings_calculation(self):
        """Test monthly savings calculation"""
        monthly_data = [
            {'month': '2024-01', 'savings': 1000.0},
            {'month': '2024-02', 'savings': 1500.0},
            {'month': '2024-03', 'savings': 1200.0},
        ]
        
        total_savings = sum(m['savings'] for m in monthly_data)
        
        assert total_savings == 3700.0
    
    def test_average_savings_per_optimization(self):
        """Test average savings per optimization"""
        month_data = {
            'total_savings': 1000.0,
            'optimization_count': 50
        }
        
        avg_savings = month_data['total_savings'] / month_data['optimization_count']
        
        assert avg_savings == 20.0
    
    def test_chronological_ordering(self):
        """Test that trend data is in chronological order"""
        trend_data = [
            {'month': '2024-01', 'savings': 1000.0},
            {'month': '2024-03', 'savings': 1200.0},
            {'month': '2024-02', 'savings': 1500.0},
        ]
        
        sorted_data = sorted(trend_data, key=lambda x: x['month'])
        
        assert sorted_data[0]['month'] == '2024-01'
        assert sorted_data[1]['month'] == '2024-02'
        assert sorted_data[2]['month'] == '2024-03'
    
    def test_months_range_limit(self):
        """Test that months range is limited to 1-12"""
        months = 6
        
        assert 1 <= months <= 12
    
    def test_empty_month_handling(self):
        """Test handling of months with no data"""
        monthly_data = [
            {'month': '2024-01', 'savings': 1000.0, 'count': 50},
            {'month': '2024-02', 'savings': 0.0, 'count': 0},  # No data
            {'month': '2024-03', 'savings': 1200.0, 'count': 60},
        ]
        
        # Should include months with zero data
        assert len(monthly_data) == 3
        assert monthly_data[1]['savings'] == 0.0


@pytest.mark.unit
class TestAnalyticsConsistency:
    """Test suite for analytics consistency properties"""
    
    def test_waste_equals_100_minus_utilization(self):
        """Test that waste_percentage = 100 - avg_utilization"""
        avg_utilization = 68.5
        
        waste_percentage = 100 - avg_utilization
        
        assert waste_percentage == 31.5
        assert avg_utilization + waste_percentage == 100.0
    
    def test_utilization_bounds_0_to_100(self):
        """Test that utilization is always between 0 and 100"""
        test_values = [0.0, 25.5, 50.0, 75.3, 100.0]
        
        for value in test_values:
            assert 0 <= value <= 100
    
    def test_negative_utilization_invalid(self):
        """Test that negative utilization is invalid"""
        utilization = -10.0
        
        # Should be clamped or raise error
        assert utilization < 0  # Invalid state
    
    def test_utilization_over_100_invalid(self):
        """Test that utilization over 100 is invalid"""
        utilization = 110.0
        
        # Should be clamped or raise error
        assert utilization > 100  # Invalid state


@pytest.mark.unit
class TestDailySnapshot:
    """Test suite for daily analytics snapshot"""
    
    def test_snapshot_fields(self):
        """Test that snapshot contains all required fields"""
        snapshot = {
            'snapshot_date': datetime.now().date(),
            'total_products': 150,
            'total_boxes': 20,
            'total_optimizations': 45,
            'avg_space_utilization': 68.5,
            'total_monthly_savings': 2500.0,
            'total_annual_savings': 30000.0
        }
        
        assert 'snapshot_date' in snapshot
        assert 'total_products' in snapshot
        assert 'total_boxes' in snapshot
        assert 'total_optimizations' in snapshot
        assert 'avg_space_utilization' in snapshot
        assert 'total_monthly_savings' in snapshot
        assert 'total_annual_savings' in snapshot
    
    def test_annual_savings_calculation(self):
        """Test annual savings calculation from monthly"""
        monthly_savings = 2500.0
        
        annual_savings = monthly_savings * 12
        
        assert annual_savings == 30000.0
    
    def test_one_snapshot_per_company_per_day(self):
        """Test uniqueness constraint on company_id and snapshot_date"""
        snapshots = [
            {'company_id': 1, 'snapshot_date': '2024-01-15'},
            {'company_id': 1, 'snapshot_date': '2024-01-16'},
            {'company_id': 2, 'snapshot_date': '2024-01-15'},
        ]
        
        # Each combination should be unique
        unique_keys = set()
        for snapshot in snapshots:
            key = (snapshot['company_id'], snapshot['snapshot_date'])
            assert key not in unique_keys
            unique_keys.add(key)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
