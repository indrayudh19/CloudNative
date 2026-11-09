import streamlit as st

def render_sidebar_header(title="Library Management System", subtitle=""):
    st.sidebar.markdown(f"## 📚 {title}")
    if subtitle:
        st.sidebar.caption(subtitle)
    st.sidebar.divider()

def render_user_info_sidebar():
    user = st.session_state.get("user")
    if user:
        st.sidebar.markdown(f"**Logged in as:** {user.get('name')}")
        st.sidebar.caption(f"Role: **{user.get('role').capitalize()}** | ID: `{user.get('user_id')}`")
        if st.sidebar.button("🚪 Logout", key="logout_btn", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.sidebar.divider()

