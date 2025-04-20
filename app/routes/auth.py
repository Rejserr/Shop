from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from datetime import datetime
from datetime import datetime, timedelta
from app.extensions import db
from app.models.user_session import UserSession

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                print(f"User {username} authenticated successfully")
                
                # Close any existing active sessions for this user on desktop
                UserSession.close_active_sessions(user.id, 'desktop')
                
                # Create new session
                new_session = UserSession(
                    user_id=user.id,
                    ip_address=request.remote_addr,
                    login_time=datetime.now(),
                    status='active',
                    device_type='desktop'
                )
                db.session.add(new_session)
                db.session.commit()
                
                login_user(user)
                print(f"User {username} session created")
                
                return redirect(url_for('main.index'))
            else:
                print(f"Failed login attempt for {username}")
                flash('Invalid username or password', 'error')
                
        except Exception as e:
            print(f"Login error for {username}: {str(e)}")
            db.session.rollback()
            flash('An error occurred during login', 'error')
    
    return render_template('auth/login.html')                  

@bp.before_app_request
def check_user_session():
    target_ip = '10.10.2.231:8000'
    
    if request.path.startswith('/static/') or request.path == '/ping' or request.path == '/offline.html':
        return
        
    if request.path == '/mobile' or request.path == '/mobile/':
        return redirect(f'http://{target_ip}/mobile/login')
        
    if request.path.startswith('/mobile'):
        if request.host != target_ip:
            response = redirect(f'http://{target_ip}/mobile/login')
            # Force Chrome to use IP instead of domain
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
            return response

    if current_user.is_authenticated:
        # Get user's active session
        active_session = UserSession.query.filter_by(
            user_id=current_user.id,
            status='active',
            logout_time=None
        ).first()
        
        if active_session:
            # Check if last activity was more than 30 minutes ago
            timeout_minutes = 30
            if datetime.now() - active_session.login_time > timedelta(minutes=timeout_minutes):
                # Mark session as completed
                active_session.status = 'completed'
                active_session.logout_time = datetime.now()
                db.session.commit()
                logout_user()
                return redirect(url_for('auth.login'))
# Update the existing logout route
@bp.route('/logout')
@login_required
def logout():
    active_session = UserSession.query.filter_by(
        user_id=current_user.id,
        device_type='desktop',
        status='active',
        logout_time=None
    ).first()
    
    if active_session:
        active_session.logout_time = datetime.now()
        active_session.status = 'completed'
        db.session.commit()
    
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/auth/browser-close', methods=['POST'])
def handle_browser_close():
    if current_user.is_authenticated:
        active_session = UserSession.query.filter_by(
            user_id=current_user.id,
            status='active',
            logout_time=None
        ).first()
        
        if active_session:
            active_session.logout_time = datetime.now()
            active_session.status = 'completed'
            db.session.commit()
    
    return '', 204

@bp.route('/mobile/login', methods=['GET', 'POST'])
def mobile_login():
    print("Mobile login route accessed")
    if current_user.is_authenticated:
        print("User already authenticated")
        return redirect(url_for('mobile_zaprimanje.mobile_menu'))
        
    if request.method == 'POST':
        print("Processing POST request")
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            print(f"User {username} authenticated successfully")
            
            # Close any existing active sessions for this user on mobile
            UserSession.close_active_sessions(user.id, 'mobile')
            
            # Create new session
            new_session = UserSession(
                user_id=user.id,
                ip_address=request.remote_addr,
                login_time=datetime.now(),
                status='active',
                device_type='mobile'
            )
            db.session.add(new_session)
            db.session.commit()
            
            login_user(user)
            print(f"Created new session for user {username}")
            
            print("Redirecting to mobile menu")
            return redirect(url_for('mobile_zaprimanje.mobile_menu'))
            
        print(f"Failed login attempt for user {username}")
        flash('Unijeli ste pogrešne podatke, probajte ponovno.', 'login_error')
    
    return render_template('mobile/auth/login.html')

@bp.route('/mobile/logout')
@login_required
def mobile_logout():
    active_session = UserSession.query.filter_by(
        user_id=current_user.id,
        device_type='mobile',
        status='active',
        logout_time=None
    ).first()
    
    if active_session:
        active_session.logout_time = datetime.now()
        active_session.status = 'completed'
        db.session.commit()
    
    logout_user()
    return redirect(url_for('auth.mobile_login'))

@bp.route('/mobile')
def mobile_redirect():
    return redirect(url_for('auth.mobile_login'))

@bp.route('/ping')
def ping():
    """Simple endpoint to keep the session alive"""
    if current_user.is_authenticated:
        # Update the last activity time if needed
        pass
    return '', 204
