from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
import logging
from flask_login import login_required, current_user
from app.models import (
    IncomingGoods, 
    SSCCZaprimanje, 
    SSCCZaprimljeno, 
    IncomingGoodsAnnouncement,
    IncomingGoodsCompleted
)
from app import db
from datetime import datetime
from decimal import Decimal
from sqlalchemy import text
from app.utils.decorators import requires_permission
logger = logging.getLogger(__name__)

mobile_bp = Blueprint('mobile_zaprimanje', __name__, url_prefix='/mobile')

@mobile_bp.route('/')
@mobile_bp.route('/menu')
@login_required
def mobile_menu():
    return render_template('mobile/zaprimanje/mobile_menu.html')

@mobile_bp.route('/scan-sscc', methods=['GET', 'POST'])
@login_required
def mobile_scan_sscc():
    if request.method == 'POST':
        scanned_code = request.form.get('sscc').upper()
        
        # First try to find items by SSCC
        items = IncomingGoods.query.filter_by(sscc=scanned_code).all()
        
        # If no items found, check if it's a PSSCC
        if not items:
            # Query for all items with matching PSSCC
            items = IncomingGoods.query.filter_by(PSSCC=scanned_code).all()
            
        if not items:
            return render_template('mobile/zaprimanje/scan_sscc.html', error=True)
            
        return render_template('mobile/zaprimanje/scan_sscc.html', 
                             items=items, 
                             sscc=scanned_code)
                             
    return render_template('mobile/zaprimanje/scan_sscc.html')

@mobile_bp.route('/mobile-receiving-menu')
@login_required
def mobile_receiving_menu():
    return render_template('mobile/zaprimanje/receiving.html')

def apply_branch_filter(query, model):
    if not current_user.has_permission('ADMIN'):
        branch_code = current_user.branch.branch_code.zfill(2)
        return query.filter(model.poslovnica == branch_code)  
    return query

@mobile_bp.route('/documents')
@login_required
def mobile_documents():
    query = db.session.query(
        IncomingGoods.delivery_note,
        IncomingGoods.document_msi,
        db.func.count(IncomingGoods.id).label('item_count'),
        db.case(
            (db.func.sum(IncomingGoods.quantity) == db.func.sum(IncomingGoods.received_qty), 'Completed'),
            else_='In Progress'
        ).label('status')
    )
    
    query = apply_branch_filter(query, IncomingGoods)
    
    documents = query.group_by(
        IncomingGoods.delivery_note,
        IncomingGoods.document_msi
    ).order_by(IncomingGoods.delivery_note.desc()).limit(1000).all()
    return render_template('mobile/zaprimanje/documents.html', documents=documents)

@mobile_bp.route('/api/filter-documents')
@login_required
def filter_documents():
    delivery_note = request.args.get('delivery_note', '')
    document_msi = request.args.get('document_msi', '')
    
    query = db.session.query(IncomingGoods)
    
    if delivery_note:
        query = query.filter(IncomingGoods.delivery_note.ilike(f'%{delivery_note}%'))
    if document_msi:
        query = query.filter(IncomingGoods.document_msi.ilike(f'%{document_msi}%'))
        
    documents = query.group_by(
        IncomingGoods.delivery_note,
        IncomingGoods.document_msi
    ).all()
    
    return jsonify([{
        'delivery_note': doc.delivery_note,
        'document_msi': doc.document_msi,
        'item_count': doc.item_count,
        'status': doc.status
    } for doc in documents])

@mobile_bp.route('/api/scan-sscc')
@login_required
def mobile_scan_sscc_api():
    sscc = request.args.get('sscc')
    items = IncomingGoods.query.filter_by(sscc=sscc.upper()).all()
    return jsonify([{
        'delivery_note': item.delivery_note,
        'item_code': item.item_code,
        'quantity': float(item.quantity),
        'uom': item.uom
    } for item in items])

@mobile_bp.route('/preuzmi-paletu', methods=['POST'])
@login_required
def mobile_preuzmi_paletu():
    sscc = request.form.get('sscc')
    
    # Check if any items already exist for this SSCC or PSSCC
    existing_items = SSCCZaprimanje.query.filter(
        (SSCCZaprimanje.sscc == sscc) | 
        (SSCCZaprimanje.PSSCC == sscc)
    ).first()
    
    if existing_items:
        flash('Paleta je već preuzeta', 'warning')
        return redirect(url_for('mobile_zaprimanje.mobile_scan_items', sscc=sscc))
    
    # Get items by SSCC or PSSCC
    incoming_items = IncomingGoods.query.filter(
        (IncomingGoods.sscc == sscc) | 
        (IncomingGoods.PSSCC == sscc)
    ).all()

    # Create SSCCZaprimanje entries for all found items
    for item in incoming_items:
        # Check if this specific item already exists
        existing_item = SSCCZaprimanje.query.filter(
            SSCCZaprimanje.incoming_goods_id == item.id,
            SSCCZaprimanje.item_code == item.item_code,
            (SSCCZaprimanje.sscc == item.sscc) | 
            (SSCCZaprimanje.PSSCC == item.PSSCC)
        ).first()
        
        if not existing_item:
            new_item = SSCCZaprimanje(
                incoming_goods_id=item.id,
                sscc=item.sscc,
                PSSCC=item.PSSCC,
                barcode=item.barcode,
                item_code=item.item_code,
                description=item.description,
                uom=item.uom,
                quantity=item.quantity,
                received_qty=item.received_qty,
                delivery_note=item.delivery_note,
                document_msi=item.document_msi,
                order_type=item.order_type,
            )
            db.session.add(new_item)
    
    db.session.commit()
    return redirect(url_for('mobile_zaprimanje.mobile_scan_items', sscc=sscc))


@mobile_bp.route('/scan-items/<sscc>', methods=['GET', 'POST'])
@login_required
def mobile_scan_items(sscc):
    if request.method == 'POST':
        search_term = request.form.get('barcode') or request.form.get('artikl')
        new_quantity = Decimal(request.form.get('kolicina', 0))
        selected_item_id = request.form.get('selected_item_id')

        if selected_item_id:
            sscc_item = SSCCZaprimanje.query.get(selected_item_id)
            if sscc_item:
                current_qty = Decimal(sscc_item.received_qty or 0)
                sscc_item.received_qty = current_qty + new_quantity
                db.session.commit()
                return jsonify({'success': True, 'last_scanned_id': sscc_item.id})
        else:
            # Existing lookup logic for single matches
            item = SSCCZaprimanje.query.filter(
                (SSCCZaprimanje.sscc == sscc.upper()) | (SSCCZaprimanje.PSSCC == sscc.upper()),
                ((SSCCZaprimanje.barcode == search_term) |
                 (SSCCZaprimanje.item_code == search_term.upper()))
            ).first()
            
            if item:
                current_qty = Decimal(item.received_qty or 0)
                item.received_qty = current_qty + new_quantity
                db.session.commit()
                return jsonify({'success': True, 'last_scanned_id': item.id})
        
        return jsonify({'success': False, 'message': 'Item not found'})

    # Get items that need processing
    items = SSCCZaprimanje.query.filter(
        (SSCCZaprimanje.sscc == sscc.upper()) |
        (SSCCZaprimanje.PSSCC == sscc.upper())
    ).all()

    last_scanned = None
    if request.args.get('last_scanned_id'):
        last_scanned = next((item for item in items
                           if str(item.id) == request.args.get('last_scanned_id')), None)
    
    return render_template('mobile/zaprimanje/scan_items.html',
                         items=items,
                         sscc=sscc,
                         last_scanned=last_scanned)




@mobile_bp.route('/api/lookup-barcode')
@login_required
def mobile_lookup_barcode_api():
    barcode = request.args.get('barcode')
    sscc = request.args.get('sscc')
    
    items = SSCCZaprimanje.query.filter(
        (SSCCZaprimanje.sscc == sscc.upper()) | (SSCCZaprimanje.PSSCC == sscc.upper()),
        ((SSCCZaprimanje.barcode == barcode) | 
         (SSCCZaprimanje.item_code == barcode.upper()))
    ).all()
    
    if not items:
        # Check in incoming_goods
        incoming_item = IncomingGoods.query.filter(
            IncomingGoods.item_code == barcode.upper()
        ).first()
        
        if not incoming_item:
            # Check Mantis_Products
            master_item = db.session.execute(
                text("SELECT ItemCode FROM Mantis_Products WHERE BarCode = :barcode"),
                {"barcode": barcode}
            ).first()
            
            if master_item:
                items = SSCCZaprimanje.query.filter(
                    (SSCCZaprimanje.sscc == sscc.upper()) | (SSCCZaprimanje.PSSCC == sscc.upper()),
                    SSCCZaprimanje.item_code == master_item[0]
                ).all()
        else:
            items = SSCCZaprimanje.query.filter(
                (SSCCZaprimanje.sscc == sscc.upper()) | (SSCCZaprimanje.PSSCC == sscc.upper()),
                SSCCZaprimanje.item_code == incoming_item.item_code
            ).all()
    
    if items:
        return jsonify({
            'found': True,
            'items': [{
                'id': item.id,
                'item_code': item.item_code,
                'description': item.description,
                'quantity': float(item.quantity) if item.quantity else 0,
                'uom': item.uom,
                'received_qty': float(item.received_qty) if item.received_qty else 0,
                'sscc': item.sscc
            } for item in items]
        })
    
    return jsonify({'found': False})

@mobile_bp.route('/complete-receiving/<sscc>', methods=['POST'])
@login_required
def mobile_complete_receiving(sscc):
    try:
        sscc_items = SSCCZaprimanje.query.filter(
            (SSCCZaprimanje.sscc == sscc.upper()) |
            (SSCCZaprimanje.PSSCC == sscc.upper())
        ).all()
        
        for sscc_item in sscc_items:
            # Calculate difference
            difference = float(sscc_item.received_qty or 0) - float(sscc_item.quantity or 0)
            
            # Update incoming_goods record using the direct ID relationship
            incoming_item = IncomingGoods.query.get(sscc_item.incoming_goods_id)
            if incoming_item and sscc_item.received_qty and float(sscc_item.received_qty) > 0:
                incoming_item.received_qty = sscc_item.received_qty
                incoming_item.user_received = current_user.username
                incoming_item.status_text = 'Zaprimljeno' if difference == 0 else 'Parcijalno'
            
            # Only move to SSCCZaprimljeno and delete from SSCCZaprimanje if difference = 0
            if difference == 0:
                new_item = SSCCZaprimljeno(
                    delivery_note=sscc_item.delivery_note,
                    sscc=sscc_item.sscc,
                    PSSCC=sscc_item.PSSCC,
                    document_msi=sscc_item.document_msi,
                    barcode=sscc_item.barcode,
                    item_code=sscc_item.item_code,
                    description=sscc_item.description,
                    uom=sscc_item.uom,
                    quantity=sscc_item.quantity,
                    received_qty=sscc_item.received_qty,
                    difference=difference,
                    status_text='Zaprimljeno',
                    created_at=datetime.now(),
                    user_received=current_user.username
                )
                db.session.add(new_item)
                db.session.delete(sscc_item)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})



@mobile_bp.route('/pregled-sscc')
@mobile_bp.route('/mobile-pregled-sscc')  # Changed from '/pregled-sscc'
@login_required
def mobile_pregled_sscc():
    items = db.session.query(SSCCZaprimanje).order_by(SSCCZaprimanje.created_at.desc()).all()
    return render_template('mobile/zaprimanje/pregled_sscc.html', items=items)



@mobile_bp.route('/najave-preuzete')
@login_required
def mobile_preuzete_najave():
    delivery_notes_query = db.session.query(IncomingGoods.delivery_note).distinct()
    query = IncomingGoods.query
    
    delivery_notes_query = apply_branch_filter(delivery_notes_query, IncomingGoods)
    query = apply_branch_filter(query, IncomingGoods)
    
    delivery_note_filter = request.args.get('delivery_note', '')
    show_differences = request.args.get('show_differences')
    show_received = request.args.get('show_received')
    
    if delivery_note_filter:
        query = query.filter(IncomingGoods.delivery_note == delivery_note_filter)
    
    if show_differences:
        query = query.filter(db.text('received_qty != quantity'))
        
    if show_received:
        query = query.filter(IncomingGoods.received_qty > 0)
    
    delivery_notes = delivery_notes_query.order_by(IncomingGoods.delivery_note).limit(1000).all()
    goods = query.order_by(IncomingGoods.created_at.desc()).limit(1000).all()
    
    return render_template('mobile/zaprimanje/preuzete_najave.html',
                         goods=goods,
                         delivery_notes=delivery_notes)



@mobile_bp.route('/announcements')
@login_required
def mobile_announcements():
    # Query for distinct delivery notes in dropdown
    delivery_notes_query = text("""
        SELECT DISTINCT DeliveryNote
        FROM [PY_SHOPS].[dbo].[Mantis_PackingList] WITH (NOLOCK)
        WHERE NOT EXISTS (
            SELECT 1 FROM [PY_SHOPS].[dbo].[incoming_goods] ig 
            WHERE ig.delivery_note COLLATE Croatian_CI_AS = DeliveryNote COLLATE Croatian_CI_AS
        )
        AND NOT EXISTS (
            SELECT 1 FROM [PY_SHOPS].[dbo].[incoming_goods_completed] igc 
            WHERE igc.delivery_note COLLATE Croatian_CI_AS = DeliveryNote COLLATE Croatian_CI_AS
        )
        AND Receiver LIKE :branch_filter
        ORDER BY DeliveryNote DESC
    """)
    
    branch_filter = f'%{current_user.branch.branch_code}%' if not current_user.has_permission('ADMIN') else '%'
    delivery_notes = db.session.execute(delivery_notes_query, {'branch_filter': branch_filter}).fetchall()

    # Query for announcement details with optional filter
    selected_delivery = request.args.get('delivery_note', '')
    announcements_query = """
        SELECT 
            DeliveryNote, SSCC, PSSCC, MSI, 
            ItemCode, ItemDescription, 
            Quantity, ItemUOM, Receiver
        FROM [PY_SHOPS].[dbo].[Mantis_PackingList] WITH (NOLOCK)
        WHERE Receiver LIKE :branch_filter
    """
    
    params = {'branch_filter': branch_filter}
    if selected_delivery:
        announcements_query += " AND DeliveryNote = :delivery_note"
        params['delivery_note'] = selected_delivery

    announcements = db.session.execute(text(announcements_query), params).fetchall()

    return render_template('mobile/zaprimanje/announcements.html', 
                         announcements=announcements,
                         delivery_notes=delivery_notes)


@mobile_bp.route('/copy-announcement', methods=['POST'])
@login_required
def mobile_copy_announcement():
      try:
          data = request.get_json()
          delivery_note = data.get('delivery_note')

          insert_stmt = text("""
              INSERT INTO incoming_goods (
                  delivery_note, sscc, PSSCC, sales_order, document_msi, 
                  barcode, item_code, description, uom, 
                  quantity, received_qty, receiver, customer, 
                  delivery_type, order_type, created_at
              )
              SELECT 
                  DeliveryNote, SSCC, PSSCC, OrderCode, MSI,
                  ItemCode, ItemCode, ItemDescription, ItemUOM,
                  Quantity, 0, Receiver, Customer,
                  DeliveryType, OrderType, :created_at
              FROM [PY_SHOPS].[dbo].[Mantis_PackingList]
              WHERE DeliveryNote = :delivery_note
          """)

          db.session.execute(insert_stmt, {
              'delivery_note': delivery_note,
              'created_at': datetime.now()
          })

          db.session.commit()
          return jsonify({'success': True})

      except Exception as e:
          db.session.rollback()
          return jsonify({'success': False, 'error': str(e)})



@mobile_bp.route('/received-items')
@login_required
def mobile_received_items():
    item_code = request.args.get('item_code')
    sscc = request.args.get('sscc')
    delivery_note = request.args.get('delivery_note')
    document_msi = request.args.get('document_msi')
    barcode = request.args.get('barcode')
    
    all_items = []
    
    if any([item_code, sscc, delivery_note, document_msi, barcode]):
        completed_items = IncomingGoodsCompleted.query
        current_items = IncomingGoods.query
        
        filters = {
            'item_code': item_code,
            'sscc': sscc,
            'delivery_note': delivery_note,
            'document_msi': document_msi,
            'barcode': barcode
        }
        
        for field, value in filters.items():
            if value:
                completed_items = completed_items.filter(getattr(IncomingGoodsCompleted, field).ilike(f'%{value}%'))
                current_items = current_items.filter(getattr(IncomingGoods, field).ilike(f'%{value}%'))

        completed_items = apply_branch_filter(completed_items, IncomingGoodsCompleted)
        current_items = apply_branch_filter(current_items, IncomingGoods)
        
        completed_results = completed_items.all()
        current_results = current_items.all()
        all_items = completed_results + current_results
    
    return render_template('mobile/zaprimanje/received_items.html', items=all_items)




@mobile_bp.route('/document-items')
@login_required
def mobile_document_items():
    delivery_note = request.args.get('delivery_note')
    document_msi = request.args.get('document_msi')
    
    if delivery_note or document_msi:
        completed_items = IncomingGoodsCompleted.query
        current_items = IncomingGoods.query
        
        if delivery_note:
            completed_items = completed_items.filter(IncomingGoodsCompleted.delivery_note.ilike(f'%{delivery_note}%'))
            current_items = current_items.filter(IncomingGoods.delivery_note.ilike(f'%{delivery_note}%'))
            
        if document_msi:
            completed_items = completed_items.filter(IncomingGoodsCompleted.document_msi.ilike(f'%{document_msi}%'))
            current_items = current_items.filter(IncomingGoods.document_msi.ilike(f'%{document_msi}%'))

        if not current_user.has_permission('ADMIN'):
            branch_code = current_user.branch.branch_code
            current_items = current_items.filter(IncomingGoods.receiver.like(f'%{branch_code}%'))
            completed_results = [item for item in completed_items.all() 
                               if branch_code in (item.receiver or '')]
            current_results = current_items.all()
        else:
            completed_results = completed_items.all()
            current_results = current_items.all()
        
        all_items = completed_results + current_results
        return render_template('mobile/zaprimanje/document_items.html', items=all_items)
    
    return render_template('mobile/zaprimanje/document_items.html', items=[])


       
@mobile_bp.route('/close-document')
@login_required
def mobile_close_document_view():
    branch_code = current_user.branch.branch_code.zfill(2) if not current_user.has_permission('ADMIN') else None
    
    logger.info(f"User branch code: {branch_code}")
    logger.info(f"User permissions: {current_user.has_permission('ADMIN')}")
    
    query = db.session.query(IncomingGoods.delivery_note).distinct()
    if branch_code:
        query = query.filter(IncomingGoods.poslovnica == branch_code)
    
    logger.info(f"SQL Query: {query}")
    delivery_notes = query.order_by(IncomingGoods.delivery_note).all()
    logger.info(f"Found delivery notes: {delivery_notes}")
    
    selected_note = request.args.get('delivery_note')
    show_differences = request.args.get('show_differences')
    items = []
    
    if selected_note:
        query = IncomingGoods.query.filter_by(delivery_note=selected_note)
        if branch_code:
            query = query.filter(IncomingGoods.poslovnica == branch_code)
        if show_differences:
            query = query.filter(IncomingGoods.quantity != IncomingGoods.received_qty)
        items = query.all()
    
    return render_template('mobile/zaprimanje/close_document.html',
                         delivery_notes=delivery_notes,
                         selected_note=selected_note,
                         items=items)       



@mobile_bp.route('/api/close-document/<delivery_note>', methods=['POST'])
@login_required
def mobile_process_close_document_api(delivery_note):
    try:
        branch_code = current_user.branch.branch_code.zfill(2) if not current_user.has_permission('ADMIN') else None
        
        # Get items to be closed
        query = IncomingGoods.query.filter_by(delivery_note=delivery_note)
        if branch_code:
            query = query.filter(IncomingGoods.poslovnica == branch_code)
        items = query.all()

        # Insert into completed table
        for item in items:
            completed_item = IncomingGoodsCompleted(
                delivery_note=item.delivery_note,
                sscc=item.sscc,
                document_msi=item.document_msi,
                barcode=item.barcode,
                item_code=item.item_code,
                description=item.description,
                uom=item.uom,
                quantity=item.quantity,
                received_qty=item.received_qty,
                receiver=item.receiver,
                user_received=current_user.username,
                created_at=datetime.now(),
                completed_at=datetime.now()
            )
            db.session.add(completed_item)
            
            # Clean up related records
            SSCCZaprimanje.query.filter_by(delivery_note=delivery_note).delete()
            SSCCZaprimljeno.query.filter_by(delivery_note=delivery_note).delete()
            db.session.delete(item)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})




                

@mobile_bp.route('/mobile/status')
@login_required
@requires_permission('NAV_REPORTS')
def mobile_shipment_report():
    # Get unique delivery notes for dropdown
    delivery_query = """
    SELECT DISTINCT delivery_note 
    FROM [PY_SHOPS].[dbo].[incoming_goods]
    ORDER BY delivery_note DESC
    """
    deliveries = db.session.execute(text(delivery_query)).fetchall()
    
    delivery_note_filter = request.args.get('delivery_note', '')
    status_filters = request.args.getlist('status_filter')

    if not status_filters:
        status_filters = ['Zaprimljeno', 'Parcijalno', 'Nije zaprimljeno']

    status_placeholders = ','.join(f"'{status}'" for status in status_filters)

    query = f"""
    SELECT TOP 2000
        delivery_note,
        document_msi,
        CASE 
            WHEN MIN(status) = MAX(status) AND MIN(status) = 'Zaprimljeno' THEN 'Zaprimljeno'
            WHEN MIN(status) = MAX(status) AND MIN(status) = 'Nije zaprimljeno' THEN 'Nije zaprimljeno'
            ELSE 'Parcijalno'
        END as status
    FROM [PY_SHOPS].[dbo].[incoming_goods]
    WHERE delivery_note LIKE :delivery_note
    GROUP BY delivery_note, document_msi
    HAVING CASE 
        WHEN MIN(status) = MAX(status) AND MIN(status) = 'Zaprimljeno' THEN 'Zaprimljeno'
        WHEN MIN(status) = MAX(status) AND MIN(status) = 'Nije zaprimljeno' THEN 'Nije zaprimljeno'
        ELSE 'Parcijalno'
    END IN ({status_placeholders})
    ORDER BY document_msi ASC, delivery_note
    """

    shipments = db.session.execute(
        text(query),
        {'delivery_note': f'%{delivery_note_filter}%'}
    ).fetchall()

    return render_template('mobile/zaprimanje/mobile_shipment_status.html', 
                         shipments=shipments, 
                         selected_statuses=status_filters,
                         deliveries=deliveries)




@mobile_bp.route('/mobile/shipment-items/<string:document_msi>')
@login_required
@requires_permission('NAV_REPORTS')
def mobile_shipment_items(document_msi):
    query = """
        SELECT 
            item_code,
            description,
            quantity,
            received_qty,
            difference,
            uom,
            status,
            user_received
        FROM [PY_SHOPS].[dbo].[incoming_goods]
        WHERE document_msi = :document_msi
        ORDER BY item_code
        """
    
    items = db.session.execute(
            text(query),
            {'document_msi': document_msi}
        ).fetchall()
    
    return render_template('mobile/zaprimanje/mobile_document_items.html', 
                         items=items, 
                         document_msi=document_msi)






@mobile_bp.route('/bulk-receipt', methods=['GET', 'POST'])
@login_required
def bulk_receipt():
    delivery_note = request.form.get('delivery_note') or request.args.get('delivery_note')
    
    if request.method == 'POST':
        if 'barcode' in request.form:
            item_id = request.form.get('item_id')
            quantity = Decimal(request.form.get('kolicina', 0))
            
            if item_id:
                item = IncomingGoods.query.get(item_id)
                if item:
                    current_qty = Decimal(item.received_qty or 0)
                    item.received_qty = current_qty + quantity
                    item.user_received = current_user.username
                    db.session.commit()
                    
                    return jsonify({
                        'success': True,
                        'delivery_note': delivery_note
                    })
    
    if delivery_note:
        items = IncomingGoods.query.filter_by(delivery_note=delivery_note)\
            .order_by(IncomingGoods.item_code.asc())\
            .all()
        display_items = [item for item in items if float(item.quantity or 0) - float(item.received_qty or 0) != 0]
        return render_template('mobile/zaprimanje/bulk_receipt.html',
                            items=display_items,
                            delivery_note=delivery_note)
    
    return render_template('mobile/zaprimanje/bulk_receipt.html')
  
    
@mobile_bp.route('/api/bulk-update-quantity', methods=['POST'])
@login_required
def bulk_update_quantity():
    data = request.get_json()
    delivery_note = data.get('delivery_note')
    barcode = data.get('barcode')
    quantity = data.get('quantity')

    # Get item_code from Mantis_Products instead of Master_data
    master_item = db.session.execute(
        text("SELECT ItemCode FROM Mantis_Products WHERE BarCode = :barcode"),
        {"barcode": barcode}
    ).first()

    if master_item:
        item_code = master_item[0]
        
        # Update the incoming goods record
        item = IncomingGoods.query.filter_by(
            delivery_note=delivery_note,
            item_code=item_code
        ).first()
        
        if item:
            item.received_qty = quantity
            item.user_received = current_user.username
            db.session.commit()
            return jsonify({'success': True})

    return jsonify({'success': False})






@mobile_bp.route('/api/bulk-lookup-item')
@login_required
def bulk_lookup_item():
    search_term = request.args.get('barcode')
    delivery_note = request.args.get('delivery_note')
    
    # Initialize master_item as None
    master_item = None
    
    # Get ALL matching items, including completed ones
    items = IncomingGoods.query.filter(
        IncomingGoods.delivery_note == delivery_note,
        ((IncomingGoods.barcode == search_term) | 
         (IncomingGoods.item_code == search_term.upper()) |  
         (IncomingGoods.item_code == search_term))  
    ).all()
    
    if not items:
        master_item = db.session.execute(
            text("SELECT ItemCode FROM Mantis_Products WHERE BarCode = :barcode"),
            {"barcode": search_term}
        ).first()
        
        if master_item:
            items = IncomingGoods.query.filter(
                IncomingGoods.delivery_note == delivery_note,
                IncomingGoods.item_code == master_item[0]
            ).all()
    
    if items:
        return jsonify({
            'found': True,
            'multiple': len(items) > 1,
            'items': [{
                'id': item.id,
                'item_code': item.item_code,
                'description': item.description,
                'quantity': float(item.quantity),
                'uom': item.uom,
                'received_qty': float(item.received_qty) if item.received_qty else 0,
                'sscc': item.sscc,
                'sales_order': item.sales_order,
                'customer': item.customer,
                'document_msi': item.document_msi,
                'receiver': item.receiver,
                'order_type': item.order_type
            } for item in items]
        })
    return jsonify({'found': False})