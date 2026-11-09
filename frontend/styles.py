import streamlit as st

def apply_custom_styles():
    st.markdown(
        """
        <style>
        /* Modern aesthetic styling */
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1.1rem;
            color: #4B5563;
            margin-bottom: 1.5rem;
        }
        .metric-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .status-badge-issued {
            background-color: #FEF3C7;
            color: #92400E;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
        }
        .status-badge-overdue {
            background-color: #FEE2E2;
            color: #991B1B;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
        }
        .status-badge-returned {
            background-color: #D1FAE5;
            color: #065F46;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

