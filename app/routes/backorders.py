from flask import Blueprint, render_template, request, jsonify, make_response
from flask_login import login_required, current_user
from app.models import db
from sqlalchemy import text
from io import StringIO
import csv
from app.utils.decorators import requires_permission

bp = Blueprint('backorders', __name__)

@bp.route('/backorders', methods=['GET'])
@login_required
@requires_permission('NAV_BACKORDERS')
def index():
    order_code = request.args.get('order_code', '')
    
    # Default empty result set
    backorders = []
    
    if order_code:
        # Query the v_FeroTermOrders view when an order code is provided
        query = text("""
            SELECT 
                OrderCode,
                OrderType,
                Customer,
                Receiver,
                Product AS ItemDescription,
                ProductID AS ItemCode,
                Quantity AS OrderedQty,
                CASE 
                    WHEN ItemStatusID = 10 THEN Quantity  -- If completed, all quantity was shipped
                    ELSE 0                               -- Otherwise, nothing shipped yet
                END AS ShippedQty,
                ItemStatus AS Status
            FROM [dbo].[v_FeroTermOrders]
            WHERE OrderCode LIKE :order_code
            ORDER BY Product ASC
        """)
        
        backorders = db.session.execute(query, {'order_code': f'%{order_code}%'}).fetchall()
    
    return render_template('backorders/index.html', 
                          backorders=backorders,
                          order_code=order_code)

@bp.route('/export', methods=['GET'])
@login_required
@requires_permission('BACKORDERS_EXPORT')
def export():
    order_code = request.args.get('order_code', '')
    
    # Query the data with the same column aliases as the index route
    query = text("""
        SELECT 
            OrderCode,
            OrderType,
            Customer,
            Receiver,
            Product AS ItemDescription,
            ProductID AS ItemCode,
            Quantity AS OrderedQty,
            CASE 
                WHEN ItemStatusID = 10 THEN Quantity  -- If completed, all quantity was shipped
                ELSE 0                               -- Otherwise, nothing shipped yet
            END AS ShippedQty,
            ItemStatus AS Status
        FROM [dbo].[v_FeroTermOrders]
        WHERE OrderCode LIKE :order_code
        ORDER BY Product ASC
    """)
    
    backorders = db.session.execute(query, {'order_code': f'%{order_code}%'}).fetchall()
    
    # Create a CSV file
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Order Code', 'Order Type', 'Customer', 'Receiver', 'Item Code', 'Description', 
                    'Ordered Qty', 'Shipped Qty', 'Remaining Qty', 'Status'])
    
    # Write data
    for item in backorders:
        writer.writerow([
            item.OrderCode,
            item.OrderType,
            item.Customer,
            item.Receiver,
            item.ItemCode,
            item.ItemDescription,
            item.OrderedQty,
            item.ShippedQty,
            item.OrderedQty - item.ShippedQty,
            item.Status
        ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=backorders_{order_code}.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response
