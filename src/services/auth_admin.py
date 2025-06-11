import os

ADMIN_ID = os.getenv("ADMIN_ID")

def auth_admin(user_id: int) -> bool:
    """
    Authenticates the user as an admin.
    """
    if user_id != int(ADMIN_ID):
        return False
    return True