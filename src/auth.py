import hashlib
import streamlit as st

from src.database import create_users_table, insert_user, get_user_by_email


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def init_auth():
    create_users_table()

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "user" not in st.session_state:
        st.session_state.user = None


def signup_user(full_name: str, email: str, password: str, role: str, pharmacy_id: str = None):
    existing_user = get_user_by_email(email)
    if existing_user:
        return False, "A user with this email already exists."

    password_hash = hash_password(password)
    insert_user(full_name, email, password_hash, role, pharmacy_id)
    return True, "User account created successfully."


def login_user(email: str, password: str):
    user = get_user_by_email(email)

    if not user:
        return False, "User not found."

    user_id, full_name, email, password_hash, role, pharmacy_id = user

    if not verify_password(password, password_hash):
        return False, "Incorrect password."

    st.session_state.authenticated = True
    st.session_state.user = {
        "id": user_id,
        "full_name": full_name,
        "email": email,
        "role": role,
        "pharmacy_id": pharmacy_id,
    }

    return True, "Login successful."


def logout_user():
    st.session_state.authenticated = False
    st.session_state.user = None


def get_current_user():
    return st.session_state.user


def require_login():
    if not st.session_state.get("authenticated", False):
        st.warning("Please log in to access this page.")
        st.stop()


def has_role(allowed_roles):
    user = st.session_state.get("user")
    if not user:
        return False
    return user["role"] in allowed_roles


def require_role(allowed_roles):
    require_login()
    if not has_role(allowed_roles):
        st.error("You do not have permission to access this page.")
        st.stop()