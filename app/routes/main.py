
from flask import Blueprint, render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, Branch, Order, IncomingGoods
from app.models.user_session import UserSession
from datetime import datetime
bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    stats = {}
    
    if current_user.has_permission('VIEW_USERS_STATS'):
        if current_user.has_permission('ADMIN'):
            stats['users_count'] = User.query.count()
        else:
            stats['users_count'] = User.query.filter_by(branch_id=current_user.branch_id).count()
    
    if current_user.has_permission('VIEW_BRANCHES_STATS'):
        if current_user.has_permission('ADMIN'):
            stats['branches_count'] = Branch.query.count()
        else:
            stats['branches_count'] = 1
    
    if current_user.has_permission('VIEW_ORDERS_STATS'):
        if current_user.has_permission('ADMIN'):
            delivery_count = db.session.query(db.func.count(db.distinct(IncomingGoods.delivery_note))).scalar()
            document_count = db.session.query(db.func.count(db.distinct(IncomingGoods.document_msi))).scalar()
        else:
            branch_code = current_user.branch.branch_code
            delivery_count = db.session.query(db.func.count(db.distinct(IncomingGoods.delivery_note)))\
                .filter(IncomingGoods.receiver.like(f'%{branch_code}%')).scalar()
            document_count = db.session.query(db.func.count(db.distinct(IncomingGoods.document_msi)))\
                .filter(IncomingGoods.receiver.like(f'%{branch_code}%')).scalar()
        
        stats['incoming_goods'] = {
            'delivery_note_count': delivery_count,
            'document_msi_count': document_count
        }

    if current_user.has_permission('VIEW_CONNECTED_USERS'):
        if current_user.has_permission('ADMIN'):
            stats['connected_users'] = UserSession.query.filter_by(
                status='active', 
                logout_time=None
            ).count()
        else:
            stats['connected_users'] = UserSession.query.join(User).filter(
                UserSession.status == 'active',
                UserSession.logout_time == None,
                User.branch_id == current_user.branch_id
            ).count()

    return render_template('index.html', 
                         stats=stats,
                         user=current_user,
                         current_time=datetime.now())

@bp.route('/scan')
@login_required
def scan():
    return render_template('scan.html')
    return render_template('index.html', **context)

@bp.route('/offline.html')
def offline():
    return render_template('offline.html')
