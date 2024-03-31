# Module Imports
from api.database import db
from api.models.admin import Admin
from api.utils.hasher import hash_password

# ----------------------------------------------- #

def create_admin(email, password, phone_number, role=None, **kwargs):
    
    # Check for duplicate email.
    if Admin.query.filter_by(email=email).first():
        return None

    hashed_password = hash_password(password=password)
    
    new_admin = Admin(email=email, password=hashed_password, phone_number=phone_number, role=role, **kwargs)
    db.session.add(new_admin)
    db.session.commit()
    
    return new_admin

def update_admin(id, email=None, password=None, phone_number=None, **kwargs):
    admin = Admin.query.get(id)
    if admin:
        if email:
            admin.email = email
        if password:
            admin.password = password
        if phone_number:
            admin.phone_number = phone_number
            
        # If the admin has a role-specific attributes, update them
        for key, value in kwargs.items():
            setattr(admin, key, value)
        db.session.commit()
        return admin
    return None

def delete_admin(id):
    admin = Admin.query.get(id)
    if admin:
        db.session.delete(admin)
        db.session.commit()
        return admin
    return None

def get_admin_by_id(id):
    return Admin.query.get(id)

def get_admin_by_email(email):
    """
        Retrieve an admin by email.
        
        Args:
            email (str): The email of the admin to retrieve.
            
        Returns:
            Admin: The admin object if found, otherwise None.
    """
    return Admin.query.filter_by(email=email).first()

def get_all_admin():
    return Admin.query.all()

def initialize_admin():
    # Check if admin already exists
    existing_admin = get_admin_by_email("admin@example.com")  # Replace with your desired admin email
    if existing_admin:
        print("Admin already exists.")
        return
    
    # Create admin
    admin_data = {
        "email": "admin@example.com",  # Replace with your desired admin email
        "password": "mypass123",  # Replace with your desired admin password
        "phone_number": "+923336783222"  # Replace with your desired admin phone number
    }
    create_admin(**admin_data)
    print("Admin created successfully.")
