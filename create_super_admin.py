from src.database import create_users_table, get_user_by_email, insert_user
from src.auth import hash_password

create_users_table()

email = "admin@developer.com"

existing = get_user_by_email(email)

if existing:
    print("Super admin already exists.")
else:
    insert_user(
        full_name="Developer Admin",
        email=email,
        password_hash=hash_password("Admin123!"),
        role="super_admin",
        pharmacy_id=None
    )
    print("Super admin created.")