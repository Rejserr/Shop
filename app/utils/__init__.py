from flask import Flask
from app.extensions import db, login_manager
from .navigation import get_nav_items
from .decorators import *
from .init_permissions import *
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'your-secret-key'
    connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=tcp:STU-MODU-03230,49170;DATABASE=PY_SHOPS;UID=mlackovic;PWD=rejserr;"
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
    
    from app.cli import init_permissions_command
    app.cli.add_command(init_permissions_command)
    
    return app