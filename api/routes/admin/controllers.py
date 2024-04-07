"""
    DESC: 
        This module contains functions related to managing administrators (admins) in the system. 
        It includes functionalities for creating, updating, deleting, and retrieving admin records.
        Additionally, it provides a function to create a super admin during the initialization 
        of the application.

    Module Imports:
        - db: Database instance for SQLAlchemy
        - Admin: Admin model representing the administrator entity
        - hash_password: Function for hashing passwords

    Functions:
        - create_admin()
        - update_admin()
        - delete_admin()
        - get_admin_by_id()
        - get_admin_by_email()
        - get_all_admin()
        - create_super_admin()
"""

# Module Imports
from api.database import db
from api.models.admin import Admin
from api.utils.hasher import hash_password

# ----------------------------------------------- #

def create_admin(email, password, phone_number, id=None, role=None, **kwargs):
    """
        Creates a new admin with the provided details.

        Args:
            email (str): Email address of the admin.
            password (str): Password of the admin.
            phone_number (str): Phone number of the admin.
            id (int, optional): ID of the admin. Defaults to None.
            role (str, optional): Role of the admin. Defaults to None.
            **kwargs: Additional attributes for the admin.

        Returns:
            Admin: The newly created admin object if successful, otherwise None.
    """
    
    # Check for duplicate email.
    if Admin.query.filter_by(email=email).first():
        return None

    hashed_password = hash_password(password=password)
    
    new_admin = Admin(id=id, email=email, password=hashed_password, phone_number=phone_number, role=role, **kwargs)
    db.session.add(new_admin)
    db.session.commit()
    
    return new_admin

def update_admin(id, email=None, password=None, phone_number=None, **kwargs):
    """
        Updates an existing admin with the specified ID.

        Args:
            id (int): ID of the admin to update.
            email (str, optional): New email address for the admin. Defaults to None.
            password (str, optional): New password for the admin. Defaults to None.
            phone_number (str, optional): New phone number for the admin. Defaults to None.
            **kwargs: Additional attributes to update for the admin.

        Returns:
            Admin: The updated admin object if successful, otherwise None.
    """
    
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
    """
        Deletes an admin with the specified ID.

        Args:
            id (int): ID of the admin to delete.

        Returns:
            Admin: The deleted admin object if successful, otherwise None.
    """
    admin = Admin.query.get(id)
    if admin:
        db.session.delete(admin)
        db.session.commit()
        return admin
    return None

def get_admin_by_id(id):
    """
        Retrieves an admin by their ID.

        Args:
            id (int): ID of the admin to retrieve.

        Returns:
            Admin: The admin object if found, otherwise None.
    """
    
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
    """
        Retrieves all admin records from the database.

        Returns:
            list: List of admin objects.
    """
    return Admin.query.all()
        
def create_super_admin():
    """
        Initializes the application by creating a super admin if one doesn't already exist.

        Returns:
            Admin: The created super admin object.
    """
    
    super_admin = Admin.query.filter_by(id=1).first()
    
    if not super_admin:
        print('Super admin not present: Creating!')
        super_admin = create_admin(
            id=1,
            email='superadmin@example.com',
            password='superadminpassword',
            phone_number='1234567890',
            role='super-admin'
        )

    return super_admin
