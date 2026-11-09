import streamlit as st
from utils.api_client import api_client

def render_login_page():
    st.markdown("<h1 class='main-header'>📖 Library Management System</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>A modular Python & Streamlit LMS with FastAPI microservices</p>", unsafe_allow_html=True)

    mode = st.radio("Choose Action", ["Login", "Register as New Member"], horizontal=True)

    if mode == "Login":
        st.subheader("Sign In")
        with st.form("login_form"):
            user_id = st.text_input("User ID", placeholder="e.g. ADMIN001 or MEM0001")
            password = st.text_input("Password", type="password", placeholder=" ")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if not user_id:
                    st.error("Please enter your User ID.")
                else:
                    res = api_client.login(user_id.strip(), password)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.session_state["user"] = res
                        st.success(f"Welcome back, {res['name']}!")
                        st.rerun()

       

    else:
        st.subheader("New Member Registration")
        with st.form("register_form"):
            name = st.text_input("Full Name *", placeholder="e.g. John Doe")
            email = st.text_input("Email Address *", placeholder="e.g. john@example.com")
            phone = st.text_input("Phone Number", placeholder="e.g. 9876543210")
            address = st.text_area("Address", placeholder="e.g. 12 Baker Street")
            reg_submitted = st.form_submit_button("Register", use_container_width=True)

            if reg_submitted:
                if not name or not email:
                    st.error("Full Name and Email are required.")
                else:
                    payload = {
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "address": address
                    }
                    res = api_client.register_member(payload)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success(f"🎉 {res.get('message')}")
                        st.balloons()

