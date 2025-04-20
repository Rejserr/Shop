from flask import Blueprint, render_template, request, jsonify, make_response
from flask_login import login_required, current_user
from app.extensions import db
from sqlalchemy import text
from app.utils import requires_permission
from flask import Blueprint, render_template, request
from app.extensions import db
from sqlalchemy import text
import datetime

bp = Blueprint('reports', __name__)

@bp.route('/reports/branch')
@login_required
def branch():
    return render_template('reports/branch.html')


bp = Blueprint('reports', __name__)

@bp.route('/reports/shipment-status')
@login_required
@requires_permission('NAV_REPORTS')
def shipment_status():
    delivery_note_filter = request.args.get('delivery_note', '')
    status_filters = request.args.getlist('status_filter')
    show_all = request.args.get('show_all', False)
    show_printed = request.args.get('show_printed', 'true') == 'true'  # Default to True
    
    # Initialize shipments as an empty list
    shipments = []
    
    # Only execute the query if a delivery_note filter is provided
    if delivery_note_filter:
        if not status_filters:
            status_filters = ['Zaprimljeno', 'Parcijalno', 'Nije zaprimljeno']

        status_placeholders = ','.join(f"'{status}'" for status in status_filters)
        
        # Add printed filter
        printed_filter = "" if show_printed else "AND (ig.printed = 0 OR ig.printed IS NULL)"

        base_query = f"""
        SELECT TOP {'' if show_all else '2000'}
            delivery_note,
            COALESCE(document_msi, 'NULL') as document_msi,
            COALESCE(b.branch_name, 'Centrala') as Poslovnica,  -- Provide a default branch name
            CASE 
                WHEN MIN(status) = MAX(status) AND MIN(status) = 'Zaprimljeno' THEN 'Zaprimljeno'
                WHEN MIN(status) = MAX(status) AND MIN(status) = 'Nije zaprimljeno' THEN 'Nije zaprimljeno'
                ELSE 'Parcijalno'
            END as status,
            CAST(MAX(CAST(ISNULL(printed, 0) AS INT)) AS BIT) as printed
        FROM [PY_SHOPS].[dbo].[incoming_goods] ig
        LEFT JOIN branches b ON SUBSTRING(ig.receiver, 3, 2) = b.branch_code  -- Change to LEFT JOIN
        WHERE delivery_note LIKE :delivery_note
        {printed_filter}
        GROUP BY delivery_note, document_msi, COALESCE(b.branch_name, 'Centrala')  -- Update GROUP BY
        HAVING CASE
            WHEN MIN(status) = MAX(status) AND MIN(status) = 'Zaprimljeno' THEN 'Zaprimljeno'
            WHEN MIN(status) = MAX(status) AND MIN(status) = 'Nije zaprimljeno' THEN 'Nije zaprimljeno'
            ELSE 'Parcijalno'
        END IN ({status_placeholders})
        ORDER BY 
            CASE WHEN document_msi IS NULL THEN 0 ELSE 1 END,  -- NULL values first
            document_msi ASC, 
            delivery_note
        """    
        shipments = db.session.execute(
            text(base_query),
            {'delivery_note': f'%{delivery_note_filter}%'}
        ).fetchall()

    return render_template('reports/shipment_status.html', 
                         shipments=shipments, 
                         selected_statuses=status_filters if 'status_filters' in locals() else ['Zaprimljeno', 'Parcijalno', 'Nije zaprimljeno'],
                         show_all=show_all,
                         is_search_performed=bool(delivery_note_filter))


@bp.route('/reports/document-items/<string:document_msi>')
@login_required
@requires_permission('NAV_REPORTS')
def document_items(document_msi):
    # Get the delivery_note from the query parameters
    delivery_note = request.args.get('delivery_note', '')
    
    if document_msi == 'NULL':
        # Handle NULL document_msi case, but filter by delivery_note
        query = """
        SELECT 
            id,
            customer,
            item_code,
            description,
            quantity,
            received_qty,
            difference,
            uom,
            status,
            user_received,
            sales_order
        FROM [PY_SHOPS].[dbo].[incoming_goods]
        WHERE document_msi IS NULL
        AND delivery_note LIKE :delivery_note
        ORDER BY item_code
        """
        items = db.session.execute(
            text(query),
            {'delivery_note': f'%{delivery_note}%'}
        ).fetchall()
        display_msi = "Nije kreiran MSI dokument"
    else:
        # Modified query for non-NULL document_msi to also filter by delivery_note
        query = """
        SELECT 
            id,
            customer,
            item_code,
            description,
            quantity,
            received_qty,
            difference,
            uom,
            status,
            user_received,
            sales_order
        FROM [PY_SHOPS].[dbo].[incoming_goods]
        WHERE document_msi = :document_msi
        AND delivery_note LIKE :delivery_note
        ORDER BY item_code
        """
        items = db.session.execute(
            text(query),
            {
                'document_msi': document_msi,
                'delivery_note': f'%{delivery_note}%'
            }
        ).fetchall()
        display_msi = document_msi
    
    return render_template('reports/reports_document_items.html', items=items, document_msi=display_msi)

@bp.route('/reports/print-documents', methods=['POST'])
@login_required
@requires_permission('NAV_REPORTS')
def print_documents():
    data = request.json
    documents = data.get('documents', [])
    
    if not documents:
        return jsonify({'success': False, 'error': 'No documents selected'})
    
    try:
        # Mark documents as printed
        for doc in documents:
            if doc != 'NULL':  # Skip NULL documents
                query = """
                UPDATE [PY_SHOPS].[dbo].[incoming_goods]
                SET printed = 1
                WHERE document_msi = :document_msi
                """
                db.session.execute(text(query), {'document_msi': doc})
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/reports/print-preview')
@login_required
@requires_permission('NAV_REPORTS')
def print_preview():
    document_ids = request.args.get('ids', '').split(',')
    print_format = request.args.get('format', 'detailed')  # Default to detailed format
    
    if not document_ids:
        return "No documents selected for printing"
    
    # Filter out 'NULL' values
    document_ids = [doc for doc in document_ids if doc != 'NULL']
    
    if not document_ids:
        return "No valid documents selected for printing"
    
    # Create placeholders for SQL query
    placeholders = ','.join(f"'{doc}'" for doc in document_ids)
    
    query = f"""
    SELECT 
        document_msi,
        delivery_note,
        customer,
        item_code,
        description,
        quantity,
        received_qty,
        uom,
        status,
        receiver
    FROM [PY_SHOPS].[dbo].[incoming_goods]
    WHERE document_msi IN ({placeholders})
    ORDER BY document_msi, item_code
    """
    
    print_items = db.session.execute(text(query)).fetchall()
    
    # Group items by document_msi
    documents = {}
    for item in print_items:
        if item.document_msi not in documents:
            documents[item.document_msi] = {
                'document_msi': item.document_msi,
                'delivery_note': item.delivery_note,
                'customer': item.customer,
                'receiver': item.receiver,
                'document_items': []
            }
        
        documents[item.document_msi]['document_items'].append({
            'item_code': item.item_code,
            'description': item.description,
            'quantity': item.quantity,
            'received_qty': item.received_qty,
            'uom': item.uom,
            'status': item.status
        })
    
    # Create a print-friendly template
    return render_template(
        'reports/print_preview.html',
        documents=documents,
        print_date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
        user=current_user.username,
        print_format=print_format
    )