from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Branch

bp = Blueprint('branches', __name__)

@bp.route('/branches')
@login_required
def index():  # Changed from 'list' to 'index'
    branches = Branch.query.all()
    return render_template('branches/list.html', branches=branches)

@bp.route('/branches/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        branch = Branch(
            branch_code=request.form['branch_code'],
            branch_name=request.form['name'],  # Changed to branch_name to match DB schema
            address=request.form['address'],
            city=request.form['city'],
            contact_person=request.form['contact_person'],
            phone=request.form['phone'],
            email=request.form['email']
        )
        db.session.add(branch)
        db.session.commit()
        flash('Branch created successfully!')
        return redirect(url_for('branches.index'))
    return render_template('branches/create.html')
@bp.route('/branches/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    branch = Branch.query.get_or_404(id)
    if request.method == 'POST':
        branch.branch_code = request.form['branch_code']
        branch.branch_name = request.form['name']
        branch.address = request.form['address']
        branch.city = request.form['city']
        branch.contact_person = request.form['contact_person']
        branch.phone = request.form['phone']
        branch.email = request.form['email']
        db.session.commit()
        flash('Branch updated successfully!')
        return redirect(url_for('branches.index'))
    return render_template('branches/edit.html', branch=branch)

@bp.route('/branches/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    branch = Branch.query.get_or_404(id)
    db.session.delete(branch)
    db.session.commit()
    flash('Branch deleted successfully!')
    return redirect(url_for('branches.index'))
