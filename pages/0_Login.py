import streamlit as st

from src.auth import init_auth, signup_user, login_user, logout_user, get_current_user
from src.ingest import load_pharmacies

st.set_page_config(page_title="Login", layout="centered")

init_auth()

st.title("User Access Portal")

user = get_current_user()

if user:
    st.success(f"Logged in as {user['full_name']} ({user['role']})")
    st.write(f"Email: {user['email']}")
    if user["pharmacy_id"]:
        st.write(f"Pharmacy ID: {user['pharmacy_id']}")

    if st.button("Logout"):
        logout_user()
        st.rerun()

else:
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Login")

        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            success, message = login_user(login_email, login_password)
            if success:
                st.success(message)
                st.switch_page("0_Overview.py")
            else:
                st.error(message)

    with tab2:
        st.subheader("Sign Up")

        pharmacies = load_pharmacies("data/sample/pharmacies.csv")

        full_name = st.text_input("Full name")
        email = st.text_input("Email address")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm password", type="password")

        role = st.selectbox(
            "Role",
            ["manager", "pharmacist"]
        )

        pharmacy_name = st.selectbox(
            "Pharmacy",
            pharmacies["pharmacy_name"].tolist()
        )

        selected_pharmacy = pharmacies[pharmacies["pharmacy_name"] == pharmacy_name].iloc[0]
        pharmacy_id = selected_pharmacy["pharmacy_id"]

        if st.button("Create account"):
            if not full_name or not email or not password:
                st.error("Please complete all required fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = signup_user(
                    full_name=full_name,
                    email=email,
                    password=password,
                    role=role,
                    pharmacy_id=pharmacy_id
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)