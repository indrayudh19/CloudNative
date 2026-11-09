import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from utils.api_client import api_client
from frontend.components import render_sidebar_header, render_user_info_sidebar

def render_admin_dashboard():
    user = st.session_state.get("user", {})

    render_sidebar_header("Library System", "Admin Portal")
    render_user_info_sidebar()

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Manage Books",
            "Manage Members",
            "Issue Book",
            "Return Book",
            "Fine Management",
            "Transaction History",
            "Reports"
        ]
    )

    if menu == "Dashboard":
        st.header("📊 Administrator Analytics Dashboard")

        summary = api_client.get_admin_dashboard()
        if isinstance(summary, dict) and "error" in summary:
            st.error(summary["error"])
            return

        # Metrics Row 1
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Registered Members", summary.get("total_registered_members", 0))
        m2.metric("Total Books", summary.get("total_unique_books", 0))
        m3.metric("Available Copies", summary.get("total_available_copies", 0))
        m4.metric("Currently Issued", summary.get("total_currently_issued", 0))

        # Metrics Row 2
        m5, m6, m7 = st.columns(3)
        m5.metric("Overdue Books", summary.get("total_overdue_books", 0), delta_color="inverse")
        m6.metric("Total Fines Collected", f"₹{summary.get('total_fines_collected', 0.0):,.2f}")
        m7.metric("Outstanding Fines", f"₹{summary.get('total_fines_outstanding', 0.0):,.2f}", delta_color="inverse")

        st.divider()

        # Visualizations with Plotly
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📈 Most Borrowed Books")
            top_books = summary.get("top_borrowed_books", [])
            if top_books:
                df_top = pd.DataFrame(top_books)
                fig_top = px.bar(
                    df_top,
                    x="title",
                    y="count",
                    title="Top Borrowed Books",
                    labels={"title": "Book Title", "count": "Times Borrowed"},
                    color="count",
                    color_continuous_scale="Blues"
                )
                fig_top.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.info("No borrowing transaction data yet.")

        with col_right:
            st.subheader("📅 Issues Over Time")
            timeline = summary.get("issues_timeline", [])
            if timeline:
                df_time = pd.DataFrame(timeline)
                fig_time = px.line(
                    df_time,
                    x="date",
                    y="count",
                    markers=True,
                    title="Books Issued Timeline",
                    labels={"date": "Date", "count": "Books Issued"}
                )
                st.plotly_chart(fig_time, use_container_width=True)
            else:
                st.info("No timeline data yet.")

    elif menu == "Manage Books":
        st.header("📚 Book Management")

        tab_view, tab_add, tab_edit = st.tabs(["Catalog & Inventory", "Add New Book", "Edit / Archive Book"])

        with tab_view:
            col1, col2 = st.columns([3, 1])
            search = col1.text_input("🔍 Search books", placeholder="Title, Author, or ISBN...")
            include_inactive = col2.checkbox("Show Inactive / Archived Books", value=False)

            books = api_client.get_admin_books()
            if isinstance(books, dict) and "error" in books:
                st.error(books["error"])
            elif not books:
                st.info("No books found.")
            else:
                df = pd.DataFrame(books)
                if not include_inactive:
                    df = df[df["status"] == "active"]
                if search:
                    s = search.lower()
                    df = df[
                        df["title"].str.lower().str.contains(s) |
                        df["author"].str.lower().str.contains(s) |
                        df["isbn"].str.lower().str.contains(s)
                    ]
                st.dataframe(df, use_container_width=True)

        with tab_add:
            st.subheader("Add a New Book to Catalog")
            with st.form("add_book_form"):
                isbn = st.text_input("ISBN *", placeholder="e.g. 9780132350884")
                title = st.text_input("Title *", placeholder="e.g. The Clean Coder")
                author = st.text_input("Author *", placeholder="e.g. Robert C. Martin")
                category = st.selectbox("Category *", ["Programming", "Computer Science", "Technology", "AI", "Software Engineering", "History", "Fiction", "General"])
                publisher = st.text_input("Publisher", placeholder="e.g. Prentice Hall")
                col_y, col_c = st.columns(2)
                year = col_y.number_input("Publication Year", min_value=1800, max_value=2030, value=2023)
                copies = col_c.number_input("Total Copies", min_value=1, max_value=100, value=3)
                add_btn = st.form_submit_button("Add Book", use_container_width=True)

                if add_btn:
                    if not isbn or not title or not author:
                        st.error("ISBN, Title, and Author are mandatory fields.")
                    else:
                        payload = {
                            "isbn": isbn,
                            "title": title,
                            "author": author,
                            "category": category,
                            "publisher": publisher,
                            "publication_year": int(year),
                            "total_copies": int(copies)
                        }
                        res = api_client.add_book(payload)
                        if "error" in res:
                            st.error(res["error"])
                        else:
                            st.success(f"✅ {res.get('message')}")
                            st.rerun()

        with tab_edit:
            st.subheader("Update Book Details / Archive")
            books = api_client.get_admin_books()
            if isinstance(books, list) and books:
                book_options = {f"{b['title']} (ISBN: {b['isbn']}) [ID: {b['book_id']}]": b for b in books}
                selected_label = st.selectbox("Select Book to Edit", list(book_options.keys()))
                sel_book = book_options[selected_label]

                with st.form("edit_book_form"):
                    e_title = st.text_input("Title", value=sel_book["title"])
                    e_author = st.text_input("Author", value=sel_book["author"])
                    e_cat = st.text_input("Category", value=sel_book["category"])
                    e_pub = st.text_input("Publisher", value=sel_book.get("publisher") or "")
                    e_total = st.number_input("Total Copies", min_value=1, max_value=100, value=int(sel_book["total_copies"]))
                    e_status = st.selectbox("Status", ["active", "inactive"], index=0 if sel_book["status"] == "active" else 1)

                    col_save, col_del = st.columns(2)
                    save_btn = col_save.form_submit_button("Save Changes", use_container_width=True)
                    archive_btn = col_del.form_submit_button("Archive / Remove Book", use_container_width=True)

                    if save_btn:
                        update_payload = {
                            "title": e_title,
                            "author": e_author,
                            "category": e_cat,
                            "publisher": e_pub,
                            "total_copies": int(e_total),
                            "status": e_status
                        }
                        res = api_client.update_book(sel_book["book_id"], update_payload)
                        if "error" in res:
                            st.error(res["error"])
                        else:
                            st.success("✅ Book updated successfully!")
                            st.rerun()

                    if archive_btn:
                        res = api_client.delete_book(sel_book["book_id"])
                        if "error" in res:
                            st.error(res["error"])
                        else:
                            st.success(res.get("message"))
                            st.rerun()

    elif menu == "Manage Members":
        st.header("👥 Member Management")
        members = api_client.get_admin_members()
        if isinstance(members, dict) and "error" in members:
            st.error(members["error"])
            return

        search_m = st.text_input("🔍 Search Members by Name, ID, or Email")
        df_m = pd.DataFrame(members)
        if search_m:
            s = search_m.lower()
            df_m = df_m[
                df_m["name"].str.lower().str.contains(s) |
                df_m["user_id"].str.lower().str.contains(s) |
                df_m["email"].str.lower().str.contains(s)
            ]

        st.dataframe(df_m, use_container_width=True)

        st.subheader("Member Details & Status Control")
        if not df_m.empty:
            member_dict = {f"{m['name']} ({m['user_id']})": m for m in members}
            chosen_label = st.selectbox("Select Member", list(member_dict.keys()))
            m_selected = member_dict[chosen_label]

            col1, col2 = st.columns(2)
            col1.write(f"**Member ID:** `{m_selected['user_id']}`")
            col1.write(f"**Email:** {m_selected['email']}")
            col1.write(f"**Phone:** {m_selected.get('phone') or '-'}")
            col2.write(f"**Status:** `{m_selected['status'].upper()}`")
            col2.write(f"**Active Issued Books:** {m_selected.get('active_issues_count', 0)}")
            col2.write(f"**Outstanding Fine:** ₹{m_selected.get('outstanding_fine', 0.0):.2f}")

            new_status = "inactive" if m_selected["status"] == "active" else "active"
            btn_label = "Deactivate Member" if m_selected["status"] == "active" else "Activate Member"
            if st.button(btn_label):
                res = api_client.update_user(m_selected["user_id"], {"status": new_status})
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success(f"Member status changed to {new_status} successfully.")
                    st.rerun()

    elif menu == "Issue Book":
        st.header("📖 Issue a Book")
        st.caption("Check member eligibility and assign book.")

        members = api_client.get_admin_members()
        books = api_client.get_admin_books()

        active_members = [m for m in members if m["status"] == "active"] if isinstance(members, list) else []
        avail_books = [b for b in books if b["status"] == "active" and b["available_copies"] > 0] if isinstance(books, list) else []

        if not active_members:
            st.warning("No active members available.")
            return
        if not avail_books:
            st.warning("No books currently available to issue.")
            return

        with st.form("issue_book_form"):
            member_opts = {f"{m['name']} ({m['user_id']}) - Issues: {m.get('active_issues_count', 0)}/3, Fine: ₹{m.get('outstanding_fine', 0):.2f}": m for m in active_members}
            sel_member_key = st.selectbox("Select Member", list(member_opts.keys()))
            sel_m = member_opts[sel_member_key]

            book_opts = {f"{b['title']} by {b['author']} (Available: {b['available_copies']}) [ID: {b['book_id']}]": b for b in avail_books}
            sel_book_key = st.selectbox("Select Book", list(book_opts.keys()))
            sel_b = book_opts[sel_book_key]

            issue_submit = st.form_submit_button("Confirm & Issue Book", use_container_width=True)

            if issue_submit:
                res = api_client.issue_book(
                    user_id=sel_m["user_id"],
                    book_id=sel_b["book_id"],
                    issued_by=user.get("user_id", "ADMIN001")
                )
                if "error" in res:
                    st.error(f"❌ Cannot issue: {res['error']}")
                else:
                    st.success(f"🎉 Successfully issued '{sel_b['title']}' to {sel_m['name']}!")
                    st.info(f"Due date: **{res.get('due_date')}**")
                    st.rerun()

    elif menu == "Return Book":
        st.header("🔄 Return a Book")
        st.caption("Process book returns and automatically calculate overdue fines.")

        issues = api_client.get_issues(status="issued")
        if isinstance(issues, dict) and "error" in issues:
            st.error(issues["error"])
            return

        if not issues:
            st.info("No active issued books to return.")
            return

        issue_options = {
            f"Issue #{i['issue_id']} - {i['book_title']} borrowed by {i['user_name']} ({i['user_id']}) [Due: {i['due_date']}]": i
            for i in issues
        }

        selected_issue_label = st.selectbox("Select Borrowing Record", list(issue_options.keys()))
        selected_issue = issue_options[selected_issue_label]

        # Calculate live overdue status
        due_d = date.fromisoformat(selected_issue["due_date"])
        today = date.today()
        is_over = today > due_d
        overdue_days = (today - due_d).days if is_over else 0
        est_fine = overdue_days * 5.0

        col1, col2 = st.columns(2)
        col1.write(f"**Borrower:** {selected_issue['user_name']} (`{selected_issue['user_id']}`)")
        col1.write(f"**Book:** {selected_issue['book_title']}")
        col2.write(f"**Issue Date:** {selected_issue['issue_date']}")
        col2.write(f"**Due Date:** {selected_issue['due_date']}")

        if is_over:
            st.error(f"⚠️ Book is Overdue by **{overdue_days}** day(s)! Overdue fine of **₹{est_fine:.2f}** will be generated.")
        else:
            st.success("✅ Book returned within due date. No overdue fine.")

        if st.button("Confirm Return", use_container_width=True):
            res = api_client.return_book(issue_id=selected_issue["issue_id"])
            if "error" in res:
                st.error(res["error"])
            else:
                st.success(f"✅ {res.get('message')}")
                st.rerun()

    elif menu == "Fine Management":
        st.header("💰 Fine Management")

        summary = api_client.get_payment_summary()
        if isinstance(summary, dict) and not "error" in summary:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Fines Generated", f"₹{summary.get('total_fine_amount', 0):,.2f}")
            c2.metric("Total Collected", f"₹{summary.get('total_collected', 0):,.2f}")
            c3.metric("Outstanding Balance", f"₹{summary.get('total_outstanding', 0):,.2f}")

        st.subheader("All Payment Transactions")
        payments = api_client.get_all_payments()
        if isinstance(payments, list) and payments:
            st.dataframe(pd.DataFrame(payments), use_container_width=True)
        else:
            st.info("No payment records recorded yet.")

    elif menu == "Transaction History":
        st.header("📜 All Transaction History")
        filter_status = st.selectbox("Status Filter", ["All", "issued", "returned", "overdue"])
        status_param = None if filter_status == "All" else filter_status
        issues = api_client.get_issues(status=status_param)
        if isinstance(issues, list) and issues:
            st.dataframe(pd.DataFrame(issues), use_container_width=True)
        else:
            st.info("No issue transactions found.")

    elif menu == "Reports":
        st.header("📑 Library Reports & Audit Logs")
        report_type = st.radio("Choose Report", ["Overdue Reports", "Payment Reports", "Audit Logs"], horizontal=True)

        if report_type == "Overdue Reports":
            st.subheader("Overdue Book Issues")
            overdue = api_client.get_overdue_reports()
            if isinstance(overdue, list) and overdue:
                st.dataframe(pd.DataFrame(overdue), use_container_width=True)
            else:
                st.success("No overdue books at this time!")

        elif report_type == "Payment Reports":
            st.subheader("Payment Logs")
            payments = api_client.get_payment_reports()
            if isinstance(payments, list) and payments:
                st.dataframe(pd.DataFrame(payments), use_container_width=True)
            else:
                st.info("No payment logs found.")

        elif report_type == "Audit Logs":
            st.subheader("System & Admin Audit Logs")
            admin_dash = api_client._request("GET", "admin", "/admin/audit-logs")
            if isinstance(admin_dash, list) and admin_dash:
                st.dataframe(pd.DataFrame(admin_dash), use_container_width=True)
            else:
                st.info("No audit logs found.")

