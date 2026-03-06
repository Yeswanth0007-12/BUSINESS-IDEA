from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, List
import csv
import io
import json

from app.models.product import Product
from app.models.box import Box
from app.models.optimization_run import OptimizationRun
from app.models.audit_log import AuditLog
from app.schemas.export import ExportRequest, ExportResponse


class ExportService:
    """Data export service for CSV and PDF generation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def export_products(self, company_id: int, format: str = 'csv') -> str:
        """Export products to CSV."""
        products = self.db.query(Product).filter(
            Product.company_id == company_id
        ).all()
        
        if format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'ID', 'Name', 'SKU', 'Category',
                'Length (cm)', 'Width (cm)', 'Height (cm)', 'Weight (kg)',
                'Monthly Order Volume', 'Created At'
            ])
            
            # Write data
            for product in products:
                writer.writerow([
                    product.id,
                    product.name,
                    product.sku,
                    product.category,
                    product.length_cm,
                    product.width_cm,
                    product.height_cm,
                    product.weight_kg,
                    product.monthly_order_volume,
                    product.created_at.isoformat()
                ])
            
            return output.getvalue()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}"
        )
    
    def export_boxes(self, company_id: int, format: str = 'csv') -> str:
        """Export boxes to CSV."""
        boxes = self.db.query(Box).filter(
            Box.company_id == company_id
        ).all()
        
        if format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'ID', 'Name', 'Length (cm)', 'Width (cm)', 'Height (cm)',
                'Cost Per Unit', 'Usage Count', 'Created At'
            ])
            
            # Write data
            for box in boxes:
                writer.writerow([
                    box.id,
                    box.name,
                    box.length_cm,
                    box.width_cm,
                    box.height_cm,
                    box.cost_per_unit,
                    box.usage_count,
                    box.created_at.isoformat()
                ])
            
            return output.getvalue()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}"
        )
    
    def export_optimizations(
        self,
        company_id: int,
        format: str = 'csv',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """Export optimization runs to CSV."""
        query = self.db.query(OptimizationRun).filter(
            OptimizationRun.company_id == company_id
        )
        
        if start_date:
            query = query.filter(OptimizationRun.timestamp >= start_date)
        
        if end_date:
            query = query.filter(OptimizationRun.timestamp <= end_date)
        
        optimizations = query.all()
        
        if format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'ID', 'Total Products', 'Total Cost', 'Total Waste',
                'Waste Percentage', 'Created At'
            ])
            
            # Write data
            for opt in optimizations:
                writer.writerow([
                    opt.id,
                    opt.products_analyzed,
                    opt.total_monthly_savings,
                    0,  # total_waste - not in model
                    0,  # waste_percentage - not in model
                    opt.timestamp.isoformat()
                ])
            
            return output.getvalue()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}"
        )
    
    def export_audit_logs(
        self,
        company_id: int,
        format: str = 'csv',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """Export audit logs to CSV."""
        query = self.db.query(AuditLog).filter(
            AuditLog.company_id == company_id
        )
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        logs = query.all()
        
        if format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'ID', 'User ID', 'Action', 'Resource Type', 'Resource ID',
                'IP Address', 'Created At'
            ])
            
            # Write data
            for log in logs:
                writer.writerow([
                    log.id,
                    log.user_id,
                    log.action.value,
                    log.resource_type,
                    log.resource_id,
                    log.ip_address,
                    log.created_at.isoformat()
                ])
            
            return output.getvalue()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}"
        )
