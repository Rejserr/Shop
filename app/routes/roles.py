from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.role import Role
from app.models.permission import Permission
from app.extensions import db
bp = Blueprint('roles', __name__, url_prefix='/roles')

@bp.route('/')
@login_required
def list():
    roles = Role.query.all()
    print("Fetched roles:", [(role.id, role.role_name, role.description) for role in roles])
    return render_template('roles/list.html', roles=roles)
@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        role = Role(
            role_name=request.form.get('role_name'),
            description=request.form.get('description')
        )
        db.session.add(role)
        db.session.commit()
        flash('Role created successfully', 'success')
        return redirect(url_for('roles.list'))
    return render_template('roles/create.html')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    role = Role.query.get_or_404(id)
    if request.method == 'POST':
        role.role_name = request.form.get('role_name')
        role.description = request.form.get('description')
        db.session.commit()
        flash('Role updated successfully', 'success')
        return redirect(url_for('roles.list'))
    return render_template('roles/edit.html', role=role)

@bp.route('/<int:id>/delete')
@login_required
def delete(id):
    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash('Role deleted successfully', 'success')
    return redirect(url_for('roles.list'))

@bp.route('/update-descriptions')
@login_required
def update_descriptions():
    descriptions = {
        'Admin': 'Full system access',
        'Voditelj poslovnice': 'Upravljanje svim postavkama za poslovnicu',
        'Voditelj smjene': 'korisnici, izvještaji',
        'Skladistar': 'osnovne funkcije za rad',
        'Korisnik': 'pregled sustava bez uređivanja'
    }
    
    roles = Role.query.all()
    for role in roles:
        if role.role_name in descriptions:
            role.description = descriptions[role.role_name]
    
    db.session.commit()
    flash('Role descriptions updated successfully', 'success')
    return redirect(url_for('roles.list'))



@bp.route('/roles/<int:id>/permissions', methods=['GET', 'POST'])
@login_required
def manage_permissions(id):
    role = Role.query.get_or_404(id)
    
    if request.method == 'POST':
        selected_permissions = request.form.getlist('permissions')
        print(f"Selected permissions: {selected_permissions}")  # Debug log
        try:
            # Get all Permission objects for the selected permission names
            new_permissions = Permission.query.filter(
                Permission.permission_name.in_(selected_permissions)
            ).all()
            
            # Update role permissions
            role.permissions = new_permissions
            
            # Commit changes
            db.session.commit()
            
            print(f"Successfully saved permissions: {[p.permission_name for p in role.permissions]}")
            flash('Permissions updated successfully', 'success')
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saving permissions: {str(e)}")
            flash(f'Error saving permissions: {str(e)}', 'error')
        
        return redirect(url_for('roles.manage_permissions', id=id))
    
    permissions = Permission.get_permissions_by_category()
    current_permissions = [p.permission_name for p in role.permissions]
    
    return render_template('roles/permissions.html',
                         role=role,
                         permissions=permissions,                         current_permissions=current_permissions)                                                                                                     