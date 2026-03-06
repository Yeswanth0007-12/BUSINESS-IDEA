"""
Fix migration revision IDs to use full filenames consistently.
"""

import re
import os

migrations = [
    ('001_initial_migration.py', '001_initial_migration', None),
    ('002_enterprise_upgrade.py', '002_enterprise_upgrade', '001_initial_migration'),
    ('003_fix_optimization_nullable.py', '003_fix_optimization_nullable', '002_enterprise_upgrade'),
    ('004_enhanced_data_models.py', '004_enhanced_data_models', '003_fix_optimization_nullable'),
    ('005_phase2_orientation_fields.py', '005_phase2_orientation_fields', '004_enhanced_data_models'),
    ('006_phase3_shipping_cost_fields.py', '006_phase3_shipping_cost_fields', '005_phase2_orientation_fields'),
    ('007_multi_product_orders.py', '007_multi_product_orders', '006_phase3_shipping_cost_fields'),
    ('008_optimization_tasks.py', '008_optimization_tasks', '007_multi_product_orders'),
    ('009_bulk_uploads.py', '009_bulk_uploads', '008_optimization_tasks'),
    ('010_analytics_tables.py', '010_analytics_tables', '009_bulk_uploads'),
    ('011_warehouse_integration.py', '011_warehouse_integration', '010_analytics_tables'),
]

versions_dir = 'alembic/versions'

for filename, revision_id, down_revision in migrations:
    filepath = os.path.join(versions_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found")
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace revision ID
    content = re.sub(
        r"revision = '[^']*'",
        f"revision = '{revision_id}'",
        content,
        count=1
    )
    
    # Replace down_revision
    if down_revision:
        content = re.sub(
            r"down_revision = '[^']*'",
            f"down_revision = '{down_revision}'",
            content,
            count=1
        )
    else:
        content = re.sub(
            r"down_revision = '[^']*'",
            "down_revision = None",
            content,
            count=1
        )
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"Fixed {filename}: revision={revision_id}, down_revision={down_revision}")

print("\nAll migrations fixed!")
