from flask import Flask
from app.extensions import db, login_manager
from app.utils.navigation import get_nav_items 
from flask_migrate import Migrate
from app.routes import zaprimanje
from app.routes.mobile_zaprimanje import mobile_bp 
from app.routes.backorders import bp as backorders_bp

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'your-secret-key'
    connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=FT-APPSERVER01\\SQLEXPRESS;DATABASE=PY_SHOPS;UID=mlackovic;PWD=270902LaC;Trusted_Connection=no;"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={connection_string}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.jinja_env.globals.update(get_nav_items=get_nav_items)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    migrate = Migrate(app, db)
    from app.routes import auth, main, users, branches, roles, reports, inventory
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(branches.bp)
    app.register_blueprint(roles.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(inventory.bp)
    app.register_blueprint(zaprimanje.bp)
    app.register_blueprint(mobile_bp)
    
    # Register the MSI API blueprint
    from app.routes.msi_api import msi_api_bp
    app.register_blueprint(msi_api_bp, url_prefix='/msi-api')
    
    from app.cli import init_permissions_command
    app.cli.add_command(init_permissions_command)

    app.register_blueprint(backorders_bp, url_prefix='/backorders')
    
    return app
