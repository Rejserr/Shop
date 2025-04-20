from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
import logging
from datetime import datetime
from decimal import Decimal
from sqlalchemy import text
from app.models import (
    IncomingGoods, 
    SSCCZaprimanje, 
    SSCCZaprimljeno,
    IncomingGoodsAnnouncement, 
    IncomingGoodsCompleted
)

bp = Blueprint('zaprimanje', __name__)
logger = logging.getLogger(__name__)

def apply_branch_filter(query, model):
    if not current_user.has_permission('ADMIN'):
        branch_code = current_user.branch.branch_code.zfill(2)
        return query.filter(model.poslovnica == branch_code)
    return query

@bp.route('/zaprimanje/scan-sscc', methods=['GET', 'POST'])
@login_required
def scan_sscc():
    if request.method == 'POST':
        sscc = request.form.get('sscc')
        items = IncomingGoods.query.filter_by(sscc=sscc.upper()).all()
        return render_template('zaprimanje/scan_sscc.html', items=items, sscc=sscc)
    return render_template('zaprimanje/scan_sscc.html')

@bp.route('/preuzmi_paletu', methods=['POST'])
@login_required
def preuzmi_paletu():
    sscc = request.form.get('sscc')
    
    existing_sscc = SSCCZaprimanje.query.filter_by(sscc=sscc).first()
    
    if existing_sscc:
        flash('Navedena paleta je već preuzeta, nastavi sa zaprimanjem', 'warning')
        return redirect(url_for('zaprimanje.scan_items', sscc=sscc))
    
    incoming_items = IncomingGoods.query.filter_by(sscc=sscc).all()
    
    for item in incoming_items:
        new_item = SSCCZaprimanje(
            incoming_goods_id=item.id,
            sscc=item.sscc,
            barcode=item.barcode,
            item_code=item.item_code,
            description=item.description,
            uom=item.uom,
            quantity=item.quantity,
            received_qty=item.received_qty,
            delivery_note=item.delivery_note,
            document_msi=item.document_msi,
        )
        db.session.add(new_item)
    
    db.session.commit()
    
    return redirect(url_for('zaprimanje.scan_items', sscc=sscc))

@bp.route('/zaprimanje/scan-items/<sscc>', methods=['GET', 'POST'])
@login_required
def scan_items(sscc):
    if request.method == 'POST':
        search_term = request.form.get('barcode') or request.form.get('artikl')
        new_quantity = Decimal(request.form.get('kolicina', 0))
        
        items = SSCCZaprimanje.query.filter(
            SSCCZaprimanje.sscc == sscc.upper(),
            ((SSCCZaprimanje.barcode == search_term) | 
             (SSCCZaprimanje.item_code == search_term.upper()))
        ).order_by(SSCCZaprimanje.id.desc()).all()        
        
        if not items:
            master_item = db.session.execute(
                text("SELECT item_code FROM Master_data WHERE barcode = :barcode"),
                {"barcode": search_term}
            ).first()
            
            if master_item:
                items = SSCCZaprimanje.query.filter(
                    SSCCZaprimanje.sscc == sscc.upper(),
                    SSCCZaprimanje.item_code == master_item[0]
                ).order_by(SSCCZaprimanje.id.desc()).all()
        
        if items:
            remaining_qty = new_quantity
            
            if len(items) == 1:
                item = items[0]
                current_qty = Decimal(item.received_qty or 0)
                
                if new_quantity < 0:
                    item.received_qty = max(0, current_qty + new_quantity)
                else:
                    item.received_qty = current_qty + new_quantity
                
            else:
                for item in items:
                    current_qty = Decimal(item.received_qty or 0)
                    max_qty = Decimal(item.quantity or 0)
                    
                    if new_quantity < 0:
                        qty_to_reduce = max(remaining_qty, -current_qty)
                        item.received_qty = current_qty + qty_to_reduce
                        remaining_qty -= qty_to_reduce
                        if remaining_qty >= 0:
                            break
                    else:
                        if items.index(item) == 0:
                            space_available = max_qty - current_qty
                            qty_to_add = min(remaining_qty, space_available)
                            item.received_qty = current_qty + qty_to_add
                            remaining_qty -= qty_to_add
                        elif remaining_qty > 0:
                            item.received_qty = current_qty + remaining_qty
                            remaining_qty = 0
                            break
            
            db.session.commit()
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': 'Item not found'})
    
    items = SSCCZaprimanje.query.filter_by(sscc=sscc.upper()).all()
    return render_template('zaprimanje/scan_items.html', items=items, sscc=sscc)

@bp.route('/api/lookup-barcode')
@login_required
def lookup_barcode():
    try:
        search_term = request.args.get('barcode')
        sscc = request.args.get('sscc')
        
        items = SSCCZaprimanje.query.filter(
            SSCCZaprimanje.sscc == sscc.upper(),
            ((SSCCZaprimanje.barcode == search_term) | 
             (SSCCZaprimanje.item_code == search_term.upper()))
        ).first()
        
        if not items:
            master_item = db.session.execute(
                text("SELECT item_code FROM Master_data WHERE barcode = :barcode"),
                {"barcode": search_term}
            ).first()
            
            if master_item:
                items = SSCCZaprimanje.query.filter(
                    SSCCZaprimanje.sscc == sscc.upper(),
                    SSCCZaprimanje.item_code == master_item[0]
                ).first()
        
        if items:
            return jsonify({
                'found': True,
                'barcode': items.barcode,
                'item_code': items.item_code,
                'description': items.description,
                'quantity': float(items.quantity) if items.quantity else 0,
                'uom': items.uom,
                'received_qty': float(items.received_qty) if items.received_qty else 0
            })
            
        return jsonify({'found': False})
        
    except Exception as e:
        logger.error(f"Error in barcode lookup: {str(e)}")
        return jsonify({'found': False, 'error': str(e)})

@bp.route('/zaprimanje/receiving-menu')
@login_required
def receiving_menu():
    delivery_notes_query = db.session.query(IncomingGoods.delivery_note).distinct()
    query = IncomingGoods.query
    
    delivery_notes_query = apply_branch_filter(delivery_notes_query, IncomingGoods)
    query = apply_branch_filter(query, IncomingGoods)
    
    delivery_notes = delivery_notes_query.order_by(IncomingGoods.delivery_note).limit(1000).all()
    
    delivery_note_filter = request.args.get('delivery_note', '')
    show_differences = request.args.get('show_differences')
    show_received = request.args.get('show_received')
    
    if delivery_note_filter:
        query = query.filter(IncomingGoods.delivery_note == delivery_note_filter)
    
    if show_differences:
        query = query.filter(db.text('received_qty != quantity'))
        
    if show_received:
        query = query.filter(IncomingGoods.received_qty > 0)
    
    goods = query.order_by(IncomingGoods.created_at.desc()).limit(1000).all()
    
    return render_template('zaprimanje/receiving_menu.html',
                         goods=goods,
                         delivery_notes=delivery_notes)

@bp.route('/zaprimanje/announcements')
@login_required
def announcements():
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
        ORDER BY DeliveryNote DESC
    """)
    
    delivery_notes = db.session.execute(delivery_notes_query).fetchall()

    # Query for announcement details with optional filter
    selected_delivery = request.args.get('delivery_note', '')
    announcements_query = """
        SELECT 
            DeliveryNote, SSCC, PSSCC, MSI, 
            ItemCode, ItemDescription, 
            Quantity, ItemUOM, Receiver
        FROM [PY_SHOPS].[dbo].[Mantis_PackingList] WITH (NOLOCK)
        WHERE 1=1
    """
    
    if selected_delivery:
        announcements_query += " AND DeliveryNote = :delivery_note"
        announcements = db.session.execute(text(announcements_query), 
                                         {'delivery_note': selected_delivery}).fetchall()
    else:
        announcements = db.session.execute(text(announcements_query)).fetchall()

    return render_template('zaprimanje/announcements.html', 
                         announcements=announcements,
                         delivery_notes=delivery_notes)

@bp.route('/zaprimanje/copy-announcement', methods=['POST'])
@login_required
def copy_announcement():
    try:
        data = request.get_json()
        delivery_note = data.get('delivery_note')

        # Insert all items from the delivery note using direct SQL
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



@bp.route('/zaprimanje/received-items')
@login_required
def received_items():
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
        
        if not all_items:
            flash('Navedeni artikl nije pronađen', 'warning')
    
    return render_template('zaprimanje/received_items.html', items=all_items)

@bp.route('/zaprimanje/close-document')
@login_required
def close_document():
    branch_code = current_user.branch.branch_code.zfill(2) if not current_user.has_permission('ADMIN') else None
    
    query = db.session.query(IncomingGoods.delivery_note).distinct()
    if branch_code:
        query = query.filter(IncomingGoods.poslovnica == branch_code)
    
    delivery_notes = query.order_by(IncomingGoods.delivery_note).all()
    
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
    
    return render_template('zaprimanje/close_document.html',
                         delivery_notes=delivery_notes,
                         selected_note=selected_note,
                         items=items)

@bp.route('/zaprimanje/document-items')
@login_required
def document_items():
    delivery_note = request.args.get('delivery_note')
    document_msi = request.args.get('document_msi')
    branch_code = current_user.branch.branch_code.zfill(2) if not current_user.has_permission('ADMIN') else None
    
    if delivery_note or document_msi:
        completed_items = IncomingGoodsCompleted.query
        current_items = IncomingGoods.query
        
        if delivery_note:
            completed_items = completed_items.filter(IncomingGoodsCompleted.delivery_note.ilike(f'%{delivery_note}%'))
            current_items = current_items.filter(IncomingGoods.delivery_note.ilike(f'%{delivery_note}%'))
            
        if document_msi:
            completed_items = completed_items.filter(IncomingGoodsCompleted.document_msi.ilike(f'%{document_msi}%'))
            current_items = current_items.filter(IncomingGoods.document_msi.ilike(f'%{document_msi}%'))

        if branch_code:
            completed_items = completed_items.filter(IncomingGoodsCompleted.poslovnica == branch_code)
            current_items = current_items.filter(IncomingGoods.poslovnica == branch_code)
        
        completed_results = completed_items.all()
        current_results = current_items.all()
        all_items = completed_results + current_results
        
        return render_template('zaprimanje/document_items.html', items=all_items)
    
    return render_template('zaprimanje/document_items.html', items=[])
@bp.route('/zaprimanje/pregled-sscc')
@login_required
def pregled_sscc():
    # Get all SSCC_zaprimanje records with all fields
    items = db.session.query(SSCCZaprimanje).order_by(SSCCZaprimanje.created_at.desc()).all()
    return render_template('zaprimanje/pregled_sscc.html', items=items)

@bp.route('/zaprimanje/edit-incoming/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_incoming(id):
    item = IncomingGoods.query.get_or_404(id)
    
    if request.method == 'POST':
        item.received_qty = request.form.get('received_qty', type=float)
        db.session.commit()
        flash('Zapis uspješno ažuriran', 'success')
        return redirect(url_for('zaprimanje.close_document', delivery_note=item.delivery_note))
        
    return render_template('zaprimanje/edit_incoming.html', item=item)

@bp.route('/zaprimanje/close-document/<delivery_note>', methods=['POST'])
@login_required
def process_close_document(delivery_note):
    try:
        items = IncomingGoods.query.filter_by(delivery_note=delivery_note).all()
        
        # Use direct SQL for insertion to avoid Poslovnica computed column
        insert_stmt = text("""
            INSERT INTO incoming_goods_completed (
                delivery_note, sscc, document_msi, barcode, 
                item_code, description, uom, quantity, 
                received_qty, receiver, user_received, 
                created_at, completed_at
            )
            VALUES (
                :delivery_note, :sscc, :document_msi, :barcode,
                :item_code, :description, :uom, :quantity,
                :received_qty, :receiver, :user_received,
                :created_at, :completed_at
            )
        """)
        
        for item in items:
            db.session.execute(insert_stmt, {
                'delivery_note': item.delivery_note,
                'sscc': item.sscc,
                'document_msi': item.document_msi,
                'barcode': item.barcode,
                'item_code': item.item_code,
                'description': item.description,
                'uom': item.uom,
                'quantity': item.quantity,
                'received_qty': item.received_qty,
                'receiver': item.receiver,
                'user_received': current_user.username,
                'created_at': datetime.now(),
                'completed_at': datetime.now()
            })
            
            # Clean up related records
            SSCCZaprimanje.query.filter_by(delivery_note=delivery_note).delete()
            SSCCZaprimljeno.query.filter_by(delivery_note=delivery_note).delete()
            db.session.delete(item)
            
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
        
@bp.route('/zaprimanje/delete-announcement/<delivery_note>', methods=['POST'])
@login_required
def delete_announcement(delivery_note):
    try:
        # Delete from SSCC_zaprimanje
        db.session.execute(
            text("DELETE FROM [PY_SHOPS].[dbo].[SSCC_zaprimanje] WHERE delivery_note = :delivery_note"),
            {"delivery_note": delivery_note}
        )
        
        # Delete from incoming_goods
        db.session.execute(
            text("DELETE FROM [PY_SHOPS].[dbo].[incoming_goods] WHERE delivery_note = :delivery_note"),
            {"delivery_note": delivery_note}
        )
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})