from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.inventory import Inventory

bp = Blueprint('inventory', __name__)

@bp.route('/inventory/manage')
@login_required
def manage():
    inventory_items = Inventory.query.filter_by(branch_id=current_user.branch_id).all()
    return render_template('inventory/manage.html', inventory_items=inventory_items)

@bp.route('/inventory/view')
@login_required
def view():
    inventory_items = Inventory.query.filter_by(branch_id=current_user.branch_id).all()
    return render_template('inventory/view.html', inventory_items=inventory_items)
