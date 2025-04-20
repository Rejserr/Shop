from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from app import db
from sqlalchemy import text
from app.utils.decorators import requires_permission  # Changed from permission_required

msi_api_bp = Blueprint('msi_api', __name__)

@msi_api_bp.route('/')
@login_required
@requires_permission('NAV_MSI_API')  # Changed from permission_required
def index():
    return render_template('msi_api/index.html')

@msi_api_bp.route('/view-missing-msi', methods=['GET', 'POST'])
@login_required
@requires_permission('NAV_MSI_API')  # Changed from permission_required
def view_missing_msi():
    results = []
    delivery_note = request.form.get('delivery_note', '')
    
    if delivery_note:
        # If delivery_note is '%', show all records with missing MSI
        if delivery_note == '%':
            query = text("""
                SELECT TOP 1000
                    ig.id,
                    ig.delivery_note,
                    ig.item_code,
                    ig.sscc,
                    ig.sales_order,
                    ig.document_msi AS current_msi,
                    pl.MSI AS new_msi
                FROM [dbo].[incoming_goods] ig
                INNER JOIN [dbo].[Mantis_PackingList] pl
                    ON ig.delivery_note COLLATE Croatian_CI_AS = pl.DeliveryNote COLLATE Croatian_CI_AS
                    AND ig.item_code COLLATE Croatian_CI_AS = pl.ItemCode COLLATE Croatian_CI_AS
                    AND ig.sscc COLLATE Croatian_CI_AS = pl.SSCC COLLATE Croatian_CI_AS
                WHERE ig.document_msi IS NULL
                ORDER BY ig.delivery_note
            """)
            results = db.session.execute(query).fetchall()
        else:
            # Normal search by specific delivery note
            query = text("""
                SELECT
                    ig.id,
                    ig.delivery_note,
                    ig.item_code,
                    ig.sscc,
                    ig.sales_order,
                    ig.document_msi AS current_msi,
                    pl.MSI AS new_msi
                FROM [dbo].[incoming_goods] ig
                INNER JOIN [dbo].[Mantis_PackingList] pl
                    ON ig.delivery_note COLLATE Croatian_CI_AS = pl.DeliveryNote COLLATE Croatian_CI_AS
                    AND ig.item_code COLLATE Croatian_CI_AS = pl.ItemCode COLLATE Croatian_CI_AS
                    AND ig.sscc COLLATE Croatian_CI_AS = pl.SSCC COLLATE Croatian_CI_AS
                WHERE ig.document_msi IS NULL
                AND ig.delivery_note = :delivery_note
            """)
            results = db.session.execute(query, {'delivery_note': delivery_note}).fetchall()
    
    return render_template('msi_api/view_missing_msi.html', results=results, delivery_note=delivery_note)

@msi_api_bp.route('/update-msi-auto', methods=['POST'])
@login_required
@requires_permission('NAV_MSI_API')  # Changed from permission_required
def update_msi_auto():
    delivery_note = request.form.get('delivery_note', '')
    
    if not delivery_note or delivery_note == '%':
        flash('Specific delivery note is required for updates', 'error')
        return redirect(url_for('msi_api.view_missing_msi'))
    
    update_query = text("""
        UPDATE ig
        SET document_msi = pl.MSI
        FROM [dbo].[incoming_goods] ig
        INNER JOIN [dbo].[Mantis_PackingList] pl
            ON ig.delivery_note COLLATE Croatian_CI_AS = pl.DeliveryNote COLLATE Croatian_CI_AS
            AND ig.item_code COLLATE Croatian_CI_AS = pl.ItemCode COLLATE Croatian_CI_AS
            AND ig.sscc COLLATE Croatian_CI_AS = pl.SSCC COLLATE Croatian_CI_AS
        WHERE ig.document_msi IS NULL
        AND ig.delivery_note = :delivery_note
    """)
    
    result = db.session.execute(update_query, {'delivery_note': delivery_note})
    db.session.commit()
    
    rows_affected = result.rowcount
    flash(f'Successfully updated {rows_affected} records', 'success')
    return redirect(url_for('msi_api.view_missing_msi'))

@msi_api_bp.route('/manual-update', methods=['GET', 'POST'])
@login_required
@requires_permission('NAV_MSI_API')  # Changed from permission_required
def manual_update():
    results = []
    delivery_note = request.form.get('delivery_note', '')
    sales_order = request.form.get('sales_order', '')
    
    if delivery_note and sales_order:
        query = text("""
            SELECT
                [id],
                [delivery_note],
                [sscc],
                [sales_order],
                [document_msi],
                [item_code]
            FROM [PY_SHOPS].[dbo].[incoming_goods]
            WHERE document_msi IS NULL
            AND delivery_note = :delivery_note
            AND sales_order = :sales_order
        """)
        
        results = db.session.execute(query, {
            'delivery_note': delivery_note,
            'sales_order': sales_order
        }).fetchall()
    
    return render_template('msi_api/manual_update.html', 
                          results=results, 
                          delivery_note=delivery_note, 
                          sales_order=sales_order)

@msi_api_bp.route('/perform-manual-update', methods=['POST'])
@login_required
@requires_permission('NAV_MSI_API')  # Changed from permission_required
def perform_manual_update():
    delivery_note = request.form.get('delivery_note', '')
    sales_order = request.form.get('sales_order', '')
    msi_value = request.form.get('msi_value', '')
    
    if not all([delivery_note, sales_order, msi_value]):
        flash('All fields are required', 'error')
        return redirect(url_for('msi_api.manual_update'))
    
    update_query = text("""
        UPDATE [PY_SHOPS].[dbo].[incoming_goods]
        SET document_msi = :msi_value
        WHERE document_msi IS NULL
        AND delivery_note = :delivery_note
        AND sales_order = :sales_order
    """)
    
    result = db.session.execute(update_query, {
        'delivery_note': delivery_note,
        'sales_order': sales_order,
        'msi_value': msi_value
    })
    db.session.commit()
    
    rows_affected = result.rowcount
    flash(f'Successfully updated {rows_affected} records with MSI value: {msi_value}', 'success')
    return redirect(url_for('msi_api.manual_update'))
