"""Create a new admin user able to view the /reports endpoint."""
from werkzeug.security import generate_password_hash
from getpass import getpass
import sys

from flask import current_app
from app import create_app
from app.models import User, Role, role_user_table
from flask_sqlalchemy import SQLAlchemy


def main():
    """Main entry point for script."""
    app = create_app()
    db = SQLAlchemy()
    db.init_app(app)

    with app.app_context():
        db.metadata.create_all(db.engine)     
        role = "admin"    
        description = "god"   
        role = Role(
            name=role,
            description=description
        )          
        db.session.add(role)
        db.session.commit()
        print ('Role added.')

        role = "user"    
        description = "nobody"   
        role = Role(
            name=role,
            description=description
        )          
        db.session.add(role)
        db.session.commit()
        print ('Role added.')

        email = "admin@admin.admin"
        username = "admin"
        password = "admin"
        user = User(
            username=username,
            email=email, 
            password_hash=generate_password_hash(password),
            active=True,
        )
        role = Role.query.get(1) 
        db.session.add(user)
        db.session.commit()
        db.session.execute(role_user_table.insert(),params={"user_id": user.id, "role_id": role.id},)  
        db.session.commit()
        print ('User added.')

        email = "user@user.user"
        username = "user"
        password = "user"
        user = User(
            username=username,
            email=email, 
            password_hash=generate_password_hash(password),
            active=False,
        )
        role = Role.query.get(2) 
        db.session.add(user)
        db.session.commit()
        db.session.execute(role_user_table.insert(),params={"user_id": user.id, "role_id": role.id},)  
        db.session.commit()
        print ('User added.')
if __name__ == '__main__':
    sys.exit(main())
