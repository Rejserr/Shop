from flask import Flask
from app.extensions import db, login_manager
from app.utils.navigation import get_nav_items
from flask_migrate import Migrate
from .branch import Branch
from .inventory import *
from .order import *
from .permission import *
from .role import *
from .user import *
from .incoming_goods import IncomingGoods
from .sscc_zaprimanje import SSCCZaprimanje
from .sscc_zaprimljeno import SSCCZaprimljeno
from .incoming_goods_announcement import IncomingGoodsAnnouncement
from .incoming_goods_completed import IncomingGoodsCompleted
from app.routes.mobile_zaprimanje import mobile_bp
from app.routes.zaprimanje import bp as zaprimanje_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key'
    connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=tcp:STU-MODU-03230,49170;DATABASE=PY_SHOPS;UID=mlackovic;PWD=rejserr;"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={connection_string}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Add navigation to templates
    app.jinja_env.globals.update(get_nav_items=get_nav_items)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Initialize migrations
    migrate = Migrate(app, db)

    # Register blueprints
    from app.routes import auth, main, users, branches, roles, reports, inventory, zaprimanje
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(branches.bp)
    app.register_blueprint(roles.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(inventory.bp)
    app.register_blueprint(zaprimanje_bp)
    app.register_blueprint(mobile_bp)

    # Initialize permissions
    from app.utils.init_permissions import init_permissions
    with app.app_context():
        db.create_all()
        init_permissions()

    return app
