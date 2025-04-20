from app import create_app, db
from app.models.user import User
from app.models.role import Role

app = create_app()

with app.app_context():
    # Create Admin role if it doesn't exist
    admin_role = Role.query.filter_by(role_name='Admin').first()
    if not admin_role:
        admin_role = Role(role_name='Admin')
        db.session.add(admin_role)
        db.session.commit()

    # Create Admin user
    admin = User(
        username='admin',
        email='mladen.lackovic@fero-term.hr',
        full_name='System Administrator',
        role_id=admin_role.id
    )
    admin.set_password('rejserr')
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully!")
