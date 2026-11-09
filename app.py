import streamlit as st
from frontend.styles import apply_custom_styles
from frontend.login import render_login_page
from frontend.member_dashboard import render_member_dashboard
from frontend.admin_dashboard import render_admin_dashboard

# Streamlit Page Config
st.set_page_config(
    page_title="Library Management System (LMS)",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styles()

def main():
    if "user" not in st.session_state or not st.session_state["user"]:
        render_login_page()
    else:
        role = st.session_state["user"].get("role", "member")
        if role == "admin":
            render_admin_dashboard()
        else:
            render_member_dashboard()

if __name__ == "__main__":
    main()

