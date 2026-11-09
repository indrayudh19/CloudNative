import streamlit as st
import pandas as pd
from utils.api_client import api_client
from frontend.components import render_sidebar_header, render_user_info_sidebar

def render_member_dashboard():
    user = st.session_state.get("user", {})
    user_id = user.get("user_id")

    render_sidebar_header("Library System", "Member Portal")
    render_user_info_sidebar()

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Browse Catalog",
            "My Issue History",
            "My Fines & Payments",
            "My Profile"
        ]
    )

    if menu == "Dashboard":
        st.header("📊 Member Dashboard")
        st.write(f"Welcome to your library dashboard, **{user.get('name')}**!")

        # Fetch member data
        issues = api_client.get_member_issues(user_id)
        if isinstance(issues, dict) and "error" in issues:
            st.error(issues["error"])
            issues = []

        fines = api_client.get_member_fines(user_id)
        if isinstance(fines, dict) and "error" in fines:
            fines = []

        currently_borrowed = [i for i in issues if i.get("status") in ["issued", "overdue"]]
        overdue_books = [i for i in issues if i.get("status") == "overdue"]
        total_outstanding_fine = sum(f.get("outstanding_amount", 0.0) for f in fines)

        # First row: Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Books Currently Borrowed", len(currently_borrowed))
        col2.metric("Outstanding Fine", f"₹{total_outstanding_fine:.2f}")
        col3.metric("Total Borrowing Transactions", len(issues))

        st.divider()

        # Second row: Overdue notifications & Recently borrowed
        if overdue_books:
            st.warning(f"⚠️ You have {len(overdue_books)} overdue book(s)! Please return them to avoid escalating fines.")
            for ob in overdue_books:
                st.write(f"- **{ob.get('book_title')}** (Due Date: `{ob.get('due_date')}`)")

        st.subheader("Recently Borrowed Books")
        if issues:
            df = pd.DataFrame(issues[:5])
            display_cols = ["book_title", "author", "issue_date", "due_date", "status"]
            st.dataframe(df[[c for c in display_cols if c in df.columns]], use_container_width=True)
        else:
            st.info("No borrowing history found.")

    elif menu == "Browse Catalog":
        st.header("📚 Browse Book Catalog")
        st.caption("Explore books available in the central library catalog.")

        col1, col2, col3 = st.columns([2, 1, 1])
        search = col1.text_input("🔍 Search by Title, Author, or ISBN", placeholder="Type keywords...")
        category = col2.selectbox("Filter Category", ["All", "Programming", "Computer Science", "Technology", "AI", "Software Engineering", "History", "Fiction"])
        available_only = col3.checkbox("Available Copies Only", value=False)

        cat_filter = None if category == "All" else category
        books = api_client.get_books(search=search, category=cat_filter, available_only=available_only)

        if isinstance(books, dict) and "error" in books:
            st.error(books["error"])
        elif not books:
            st.info("No books match your criteria.")
        else:
            df = pd.DataFrame(books)
            display_cols = ["title", "author", "isbn", "category", "publisher", "publication_year", "available_copies", "total_copies"]
            st.dataframe(df[display_cols], use_container_width=True)

    elif menu == "My Issue History":
        st.header("📋 My Issue History")
        
        status_filter = st.selectbox("Filter Transactions", ["All Transactions", "Currently Issued", "Returned", "Overdue"])
        
        issues = api_client.get_member_issues(user_id)
        if isinstance(issues, dict) and "error" in issues:
            st.error(issues["error"])
        elif not issues:
            st.info("You haven't borrowed any books yet.")
        else:
            if status_filter == "Currently Issued":
                filtered = [i for i in issues if i.get("status") == "issued"]
            elif status_filter == "Returned":
                filtered = [i for i in issues if i.get("status") == "returned"]
            elif status_filter == "Overdue":
                filtered = [i for i in issues if i.get("status") == "overdue"]
            else:
                filtered = issues

            if not filtered:
                st.info(f"No transactions found for filter: {status_filter}")
            else:
                df = pd.DataFrame(filtered)
                cols = ["issue_id", "book_title", "author", "issue_date", "due_date", "return_date", "status", "fine_amount"]
                st.dataframe(df[[c for c in cols if c in df.columns]], use_container_width=True)

    elif menu == "My Fines & Payments":
        st.header("💳 My Fines & Payments")

        tabs = st.tabs(["Outstanding Fines & Pay", "Payment History"])

        with tabs[0]:
            fines = api_client.get_member_fines(user_id)
            if isinstance(fines, dict) and "error" in fines:
                st.error(fines["error"])
                fines = []

            unpaid = [f for f in fines if f.get("outstanding_amount", 0) > 0]
            if not unpaid:
                st.success("🎉 You have no outstanding fines! Great job returning books on time.")
            else:
                st.write("### Outstanding Fines")
                for f in unpaid:
                    with st.expander(f"Fine #{f['fine_id']} - {f['book_title']} (Outstanding: ₹{f['outstanding_amount']:.2f})"):
                        st.write(f"**Total Fine Amount:** ₹{f['amount']:.2f}")
                        st.write(f"**Amount Already Paid:** ₹{f['paid_amount']:.2f}")
                        st.write(f"**Remaining Outstanding Balance:** ₹{f['outstanding_amount']:.2f}")
                        st.write(f"**Status:** `{f['status'].upper()}`")

                        with st.form(f"pay_form_{f['fine_id']}"):
                            pay_amt = st.number_input(
                                "Payment Amount (₹)",
                                min_value=1.0,
                                max_value=float(f['outstanding_amount']),
                                value=float(f['outstanding_amount']),
                                step=1.0
                            )
                            pay_method = st.selectbox("Simulated Payment Method", ["UPI", "Card", "NetBanking", "Cash"])
                            submitted = st.form_submit_button("Proceed to Pay", use_container_width=True)

                            if submitted:
                                res = api_client.pay_fine(
                                    fine_id=f['fine_id'],
                                    user_id=user_id,
                                    amount=pay_amt,
                                    payment_method=pay_method
                                )
                                if "error" in res:
                                    st.error(res["error"])
                                else:
                                    st.success(f"✅ {res.get('message')}")
                                    st.info(f"Transaction Reference: `{res.get('transaction_reference')}`")
                                    st.rerun()

        with tabs[1]:
            st.subheader("Your Payment Records")
            history = api_client.get_payment_history(user_id)
            if isinstance(history, dict) and "error" in history:
                st.error(history["error"])
            elif not history:
                st.info("No payment records found.")
            else:
                df = pd.DataFrame(history)
                display_cols = ["payment_id", "fine_id", "amount", "payment_method", "payment_date", "status", "transaction_reference"]
                st.dataframe(df[[c for c in display_cols if c in df.columns]], use_container_width=True)

    elif menu == "My Profile":
        st.header("👤 My Profile")
        profile = api_client.get_user(user_id)
        if isinstance(profile, dict) and "error" in profile:
            st.error(profile["error"])
        else:
            col1, col2 = st.columns(2)
            col1.write(f"**Member ID:** `{profile.get('user_id')}`")
            col1.write(f"**Full Name:** {profile.get('name')}")
            col1.write(f"**Email:** {profile.get('email')}")
            col2.write(f"**Phone:** {profile.get('phone') or '-'}")
            col2.write(f"**Address:** {profile.get('address') or '-'}")
            col2.write(f"**Account Status:** `{profile.get('status').upper()}`")

