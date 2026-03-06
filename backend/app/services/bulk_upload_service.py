"""
Bulk Upload Service

Service layer for processing bulk CSV uploads of orders.
"""
import csv
import io
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from datetime import datetime

from ..models.bulk_upload import BulkUpload, BulkUploadOrder
from ..models.order import Order, OrderItem
from ..models.product import Product
from ..tasks.optimization_tasks import optimize_order_packing_task


class BulkUploadService:
    """Service for handling bulk CSV uploads."""
    
    # Constants
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_ROWS = 10000
    REQUIRED_HEADERS = ["order_number", "customer_name", "product_sku", "quantity"]
    
    def __init__(self, db: Session):
        self.db = db
    
    def parse_bulk_upload_csv(self, csv_content: str) -> List[Dict[str, Any]]:
        """
        Parse and validate CSV content.
        
        Args:
            csv_content: CSV file content as string or StringIO
            
        Returns:
            List of order dictionaries grouped by order_number
            
        Raises:
            HTTPException: If CSV is invalid or malformed
        """
        # Parse CSV - handle both string and StringIO
        if isinstance(csv_content, str):
            csv_file = io.StringIO(csv_content)
        else:
            csv_file = csv_content  # Already a StringIO object
        reader = csv.DictReader(csv_file)
        
        # Validate headers
        if not reader.fieldnames:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        missing_headers = set(self.REQUIRED_HEADERS) - set(reader.fieldnames)
        if missing_headers:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_headers)}"
            )
        
        # Parse rows
        rows = []
        row_count = 0
        
        for row_number, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            row_count += 1
            
            # Check row limit
            if row_count > self.MAX_ROWS:
                raise HTTPException(
                    status_code=400,
                    detail=f"CSV exceeds maximum row limit of {self.MAX_ROWS}"
                )
            
            # Validate required fields are not empty
            for header in self.REQUIRED_HEADERS:
                if not row.get(header, "").strip():
                    raise HTTPException(
                        status_code=400,
                        detail=f"Row {row_number}: Missing value for '{header}'"
                    )
            
            # Validate quantity is a positive integer
            try:
                quantity = int(row["quantity"])
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Row {row_number}: Invalid quantity '{row['quantity']}' - must be a positive integer"
                )
            
            rows.append({
                "row_number": row_number,
                "order_number": row["order_number"].strip(),
                "customer_name": row["customer_name"].strip(),
                "product_sku": row["product_sku"].strip(),
                "quantity": quantity
            })
        
        if not rows:
            raise HTTPException(status_code=400, detail="CSV file contains no data rows")
        
        return rows
    
    def group_by_order_number(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group CSV rows by order_number to create complete orders.
        
        Args:
            rows: List of parsed CSV rows
            
        Returns:
            List of order dictionaries with items
        """
        orders_dict = {}
        
        for row in rows:
            order_number = row["order_number"]
            
            if order_number not in orders_dict:
                orders_dict[order_number] = {
                    "order_number": order_number,
                    "customer_name": row["customer_name"],
                    "items": []
                }
            
            orders_dict[order_number]["items"].append({
                "product_sku": row["product_sku"],
                "quantity": row["quantity"],
                "row_number": row["row_number"]
            })
        
        return list(orders_dict.values())
    
    def validate_order_data(self, order: Dict[str, Any], company_id: int) -> Tuple[bool, str, List[str]]:
        """
        Validate that all SKUs in an order exist in the company's product catalog.
        
        Args:
            order: Order dictionary with items
            company_id: Company ID
            
        Returns:
            Tuple of (is_valid, error_message, missing_skus_list)
        """
        skus = [item["product_sku"] for item in order["items"]]
        
        # Query products by SKU
        products = self.db.query(Product).filter(
            Product.company_id == company_id,
            Product.sku.in_(skus)
        ).all()
        
        found_skus = {p.sku for p in products}
        missing_skus = list(set(skus) - found_skus)
        
        if missing_skus:
            error_msg = f"Unknown product SKUs: {', '.join(missing_skus)}. Please add these products to your catalog first."
            return False, error_msg, missing_skus
        
        return True, "", []
    
    def create_order_from_data(self, order_data: Dict[str, Any], company_id: int) -> Order:
        """
        Create an Order record from order data.
        
        Args:
            order_data: Order dictionary with items
            company_id: Company ID
            
        Returns:
            Created Order object
        """
        # Create order
        order = Order(
            company_id=company_id,
            order_number=order_data["order_number"],
            customer_name=order_data["customer_name"],
            status="pending"
        )
        self.db.add(order)
        self.db.flush()  # Get order ID
        
        # Get products by SKU
        skus = [item["product_sku"] for item in order_data["items"]]
        products = self.db.query(Product).filter(
            Product.company_id == company_id,
            Product.sku.in_(skus)
        ).all()
        
        product_map = {p.sku: p for p in products}
        
        # Create order items
        for item_data in order_data["items"]:
            product = product_map[item_data["product_sku"]]
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item_data["quantity"]
            )
            self.db.add(order_item)
        
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    async def process_bulk_upload(
        self,
        upload_id: int,
        csv_file: UploadFile,
        company_id: int
    ) -> Dict[str, Any]:
        """
        Process a bulk CSV upload.
        
        Args:
            upload_id: Bulk upload record ID
            csv_file: Uploaded CSV file
            company_id: Company ID
            
        Returns:
            Summary dictionary with processing results
        """
        # Read and validate file size
        content = await csv_file.read()
        
        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum of {self.MAX_FILE_SIZE / (1024*1024):.0f} MB"
            )
        
        # Decode content
        try:
            csv_content = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
        
        # Parse CSV
        rows = self.parse_bulk_upload_csv(csv_content)
        
        # Group by order number
        orders = self.group_by_order_number(rows)
        
        # Get bulk upload record
        bulk_upload = self.db.query(BulkUpload).filter(BulkUpload.id == upload_id).first()
        if not bulk_upload:
            raise HTTPException(status_code=404, detail="Bulk upload not found")
        
        # Update upload record
        bulk_upload.total_orders = len(orders)
        bulk_upload.status = "processing"
        self.db.commit()
        
        # Process each order
        task_ids = []
        processed = 0
        failed = 0
        failed_details = []  # Track detailed failure info
        
        for order_data in orders:
            try:
                # Validate order data
                is_valid, error_msg, missing_skus = self.validate_order_data(order_data, company_id)
                
                if not is_valid:
                    # Create failed bulk upload order record
                    bulk_order = BulkUploadOrder(
                        upload_id=upload_id,
                        row_number=order_data["items"][0]["row_number"],
                        order_data=order_data,
                        status="failed",
                        error_message=error_msg
                    )
                    self.db.add(bulk_order)
                    failed += 1
                    
                    # Track detailed failure info
                    failed_details.append({
                        "order_number": order_data["order_number"],
                        "error": error_msg,
                        "missing_skus": missing_skus
                    })
                    continue
                
                # Create order record
                order = self.create_order_from_data(order_data, company_id)
                
                # Queue optimization task
                task = optimize_order_packing_task.delay(order.id, company_id)
                task_id = task.id
                task_ids.append(task_id)
                
                # Create bulk upload order record
                bulk_order = BulkUploadOrder(
                    upload_id=upload_id,
                    row_number=order_data["items"][0]["row_number"],
                    order_data=order_data,
                    status="pending",
                    task_id=task_id
                )
                self.db.add(bulk_order)
                processed += 1
                
            except Exception as e:
                # Log failed order
                error_message = str(e)
                bulk_order = BulkUploadOrder(
                    upload_id=upload_id,
                    row_number=order_data["items"][0]["row_number"],
                    order_data=order_data,
                    status="failed",
                    error_message=error_message
                )
                self.db.add(bulk_order)
                failed += 1
                
                # Track detailed failure info
                failed_details.append({
                    "order_number": order_data["order_number"],
                    "error": error_message,
                    "missing_skus": []
                })
        
        # Update upload status
        bulk_upload.processed_orders = processed
        bulk_upload.failed_orders = failed
        bulk_upload.status = "completed"
        bulk_upload.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "upload_id": upload_id,
            "total_orders": len(orders),
            "successful": processed,
            "failed": failed,
            "task_ids": task_ids,
            "status": "completed",
            "failed_details": failed_details  # Include detailed failure info
        }
    
    def get_bulk_upload_status(self, upload_id: int, company_id: int) -> BulkUpload:
        """
        Get bulk upload status.
        
        Args:
            upload_id: Bulk upload ID
            company_id: Company ID for isolation
            
        Returns:
            BulkUpload object
        """
        upload = self.db.query(BulkUpload).filter(
            BulkUpload.id == upload_id,
            BulkUpload.company_id == company_id
        ).first()
        
        if not upload:
            raise HTTPException(status_code=404, detail="Bulk upload not found")
        
        return upload
    
    def get_failed_orders(self, upload_id: int, company_id: int) -> List[BulkUploadOrder]:
        """
        Get failed orders for a bulk upload.
        
        Args:
            upload_id: Bulk upload ID
            company_id: Company ID for isolation
            
        Returns:
            List of failed BulkUploadOrder objects
        """
        # Verify upload belongs to company
        upload = self.get_bulk_upload_status(upload_id, company_id)
        
        # Get failed orders
        failed_orders = self.db.query(BulkUploadOrder).filter(
            BulkUploadOrder.upload_id == upload_id,
            BulkUploadOrder.status == "failed"
        ).all()
        
        return failed_orders
