from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user, login_user
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.models.branch import Branch
from app.models.role import Role
from app.models.permission import Permission
from app.models.user_session import UserSession
from app.extensions import db


bp = Blueprint('users', __name__)

@bp.route('/users')
@login_required
def list():
    if current_user.has_permission('ADMIN'):
        users = User.query.all()  # Admin sees all users
    else:
        users = User.query.filter_by(branch_id=current_user.branch_id).all()  # Others see only their branch
    return render_template('users/list.html', users=users)
@bp.route('/users/<int:id>/settings', methods=['GET', 'POST'])
@login_required
def settings(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.email = request.form.get('email')
        user.full_name = request.form.get('full_name')
        db.session.commit()
        flash('User settings updated successfully', 'success')
        return redirect(url_for('users.users_list'))
    return render_template('users/settings.html', user=user)

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.has_permission('ADMIN'):
        branches = Branch.query.all()
        # Only admin can see admin role
        roles = Role.query.filter(Role.role_name != 'Admin').all() if not current_user.is_admin else Role.query.all()
    else:
        branches = Branch.query.filter_by(id=current_user.branch_id).all()
        roles = Role.query.filter(Role.role_name != 'Admin').all()
    
    if request.method == 'POST':
        user = User(
            username=request.form.get('username'),
            email=request.form.get('email'),
            full_name=request.form.get('full_name'),
            branch_id=request.form.get('branch_id'),
            role_id=request.form.get('role_id'),
            is_active=True
        )
        user.set_password(request.form.get('password'))
        db.session.add(user)
        db.session.commit()
        flash('User created successfully', 'success')
        return redirect(url_for('users.list'))
        
    return render_template('users/create.html', branches=branches, roles=roles)
@bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    user = User.query.get_or_404(id)
    if current_user.has_permission('ADMIN'):
        branches = Branch.query.all()
    else:
        branches = Branch.query.filter_by(id=current_user.branch_id).all()
    roles = Role.query.all()
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.full_name = request.form.get('full_name')
        user.branch_id = request.form.get('branch_id')
        user.role_id = request.form.get('role_id')
        if request.form.get('password'):
            user.set_password(request.form.get('password'))
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('users.list'))
    return render_template('users/edit.html', user=user, branches=branches, roles=roles)

@bp.route('/users/<int:id>/delete')
@login_required
def delete(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('users.list'))

@bp.route('/connected')
@login_required
def connected():
    connected_ids = current_app.config.get('CONNECTED_USERS', set())
    connected_users = User.query.filter(User.id.in_(connected_ids)).all()
    return render_template('users/connected_users.html', connected_users=connected_users)
    

@bp.route('/mobile/login', methods=['GET', 'POST'])
def mobile_login():
    if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
        
    if user and user.check_password(password):
                # Close any existing active sessions for this user/IP
                UserSession.close_active_sessions(user.id, request.remote_addr)
            
                # Create new session
                session = UserSession(
                    user_id=user.id,
                    ip_address=request.remote_addr,
                    device_type='mobile'
                )
                db.session.add(session)
                db.session.commit()
            
                login_user(user)
                return redirect(url_for('mobile.menu'))
            
    return render_template('mobile/login.html')
