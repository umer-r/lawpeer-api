from api.routes.admin.controllers import initialize_admin

def setup():
    # Other setup tasks...
    
    # Create admin
    initialize_admin()

# Call setup function
setup()