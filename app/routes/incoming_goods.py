from flask import Blueprint, render_template
from flask_login import login_required
from app import db
from app.models import IncomingGoods
from datetime import datetime

bp = Blueprint('incoming_goods', __name__)

@bp.route('/')
@login_required
def index():
    # Get unique delivery note count
    delivery_note_count = db.session.query(
        db.func.count(db.func.distinct(IncomingGoods.delivery_note))
    ).scalar()

    context = {
        'stats': {
            'incoming_goods': {
                'delivery_note_count': delivery_note_count
            }
        },
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return render_template('index.html', **context)

@bp.route('/zaprimanje/receiving-menu')
@login_required
def receiving_menu():
    # Add logging to verify query execution
    goods = IncomingGoods.query.order_by(IncomingGoods.created_at.desc()).all()
    print(f"Found {len(goods)} records") # Debug line
    
    # Add some basic data validation
    for item in goods:
        print(f"Item: {item.delivery_note} - {item.sscc}") # Debug line
        
    return render_template('zaprimanje/receiving_menu.html', goods=goods)