import streamlit as st
import pandas as pd
from bank import Bank

st.set_page_config(
    page_title="Bank Management System",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Bank Management System")

# ===============================
# HELPER — reload data from file
# ===============================

def reload_data():
    """Re-read data.json so the table always shows the latest state."""
    import json
    from pathlib import Path
    db = Path(__file__).resolve().parent / "data.json"
    if db.exists():
        content = db.read_text(encoding="utf-8").strip()
        if content:
            Bank.data = json.loads(content)

def show_data_table():
    """Display all accounts in a styled table with a show/hide PIN toggle."""
    reload_data()
    st.markdown("---")
    
    col_title, col_toggle = st.columns([3, 1])
    col_title.subheader("📋 Live Database — All Accounts")
    show_pins = col_toggle.checkbox("👁️ Show PINs", key="toggle_live_table")

    if not Bank.data:
        st.info("No accounts found in the database.")
        return

    # Build a display version
    rows = []
    for i, acc in enumerate(Bank.data, start=1):
        rows.append({
            "#"          : i,
            "Account No" : str(acc.get("accountNo.", "—")),
            "Name"       : str(acc.get("name", "—")),
            "Age"        : int(acc.get("age", 0)),
            "Email"      : str(acc.get("email", "—")),
            "Balance (₹)": int(acc.get("balance", 0)),
            "PIN"        : str(acc.get("pin", "")) if show_pins else "••••"
        })

    df = pd.DataFrame(rows).set_index("#")
    st.dataframe(df, use_container_width=True)
    st.caption(f"Total accounts: **{len(Bank.data)}**")

# ===============================
# SIDEBAR MENU
# ===============================

menu = st.sidebar.selectbox(
    "Choose Operation",
    [
        "📊 View All Accounts",
        "➕ Create Account",
        "💰 Deposit Money",
        "💸 Withdraw Money",
        "🔍 Check Details",
        "✏️  Update Details",
        "🗑️  Delete Account"
    ]
)

# ---- strip emoji prefix for matching ----
menu_key = menu.strip().lstrip("📊➕💰💸🔍✏️🗑️ ")

# ===============================
# VIEW ALL ACCOUNTS
# ===============================

if "View All Accounts" in menu:
    st.header("📊 All Accounts")
    reload_data()
    if not Bank.data:
        st.info("No accounts in the database yet.")
    else:
        show_pins = st.checkbox("👁️ Show PINs", key="toggle_all_accounts")
        rows = []
        for i, acc in enumerate(Bank.data, start=1):
            rows.append({
                "#"          : i,
                "Account No" : str(acc.get("accountNo.", "—")),
                "Name"       : str(acc.get("name", "—")),
                "Age"        : int(acc.get("age", 0)),
                "Email"      : str(acc.get("email", "—")),
                "Balance (₹)": int(acc.get("balance", 0)),
                "PIN"        : str(acc.get("pin", "")) if show_pins else "••••"
            })
        df = pd.DataFrame(rows).set_index("#")
        st.dataframe(df, use_container_width=True)
        st.caption(f"Total accounts: **{len(Bank.data)}**")

        # Balance bar chart
        st.subheader("💹 Balance Overview")
        chart_df = pd.DataFrame({
            "Account": [r["Account No"] for r in rows],
            "Balance (₹)": [int(r["Balance (₹)"]) for r in rows]
        }).set_index("Account")
        st.bar_chart(chart_df)

# ===============================
# CREATE ACCOUNT
# ===============================

elif "Create Account" in menu:
    st.header("➕ Create New Account")

    name  = st.text_input("Name")
    age   = st.number_input("Age", min_value=1)
    email = st.text_input("Email")
    pin   = st.text_input("4 Digit PIN", type="password")

    if st.button("Create Account", type="primary"):
        if age < 18:
            st.error("❌ Age must be 18+")
        elif len(pin) != 4 or not pin.isdigit():
            st.error("❌ PIN must be exactly 4 digits")
        else:
            account_no = Bank.account_generate()
            user = {
                "name"      : name,
                "age"       : age,
                "email"     : email,
                "pin"       : int(pin),
                "accountNo.": account_no,
                "balance"   : 0
            }
            Bank.data.append(user)
            Bank.update()
            st.success("✅ Account Created Successfully!")
            st.info(f"🔑 Your Account Number: **{account_no}**  — Save this!")

    show_data_table()

# ===============================
# DEPOSIT
# ===============================

elif "Deposit Money" in menu:
    st.header("💰 Deposit Money")

    account = st.text_input("Account Number")
    pin     = st.text_input("PIN", type="password")
    amount  = st.number_input("Amount (₹)", min_value=0)

    if st.button("Deposit", type="primary"):
        if not pin.isdigit():
            st.error("❌ PIN must be numeric")
        else:
            user = Bank.find_user(account, int(pin))
            if not user:
                st.error("❌ Invalid Account Number or PIN")
            elif amount <= 0:
                st.error("❌ Enter a valid amount greater than 0")
            elif amount > 10000:
                st.error("❌ Maximum single deposit = ₹10,000")
            else:
                user["balance"] += amount
                Bank.update()
                st.success(f"✅ ₹{amount:,.0f} Deposited Successfully!")
                st.metric("New Balance", f"₹{user['balance']:,.0f}")

    show_data_table()

# ===============================
# WITHDRAW
# ===============================

elif "Withdraw Money" in menu:
    st.header("💸 Withdraw Money")

    account = st.text_input("Account Number")
    pin     = st.text_input("PIN", type="password")
    amount  = st.number_input("Amount (₹)", min_value=0)

    if st.button("Withdraw", type="primary"):
        if not pin.isdigit():
            st.error("❌ PIN must be numeric")
        else:
            user = Bank.find_user(account, int(pin))
            if not user:
                st.error("❌ Invalid Account Number or PIN")
            elif amount <= 0:
                st.error("❌ Enter a valid amount greater than 0")
            elif user["balance"] < amount:
                st.error(f"❌ Insufficient Balance! Available: ₹{user['balance']:,.0f}")
            else:
                user["balance"] -= amount
                Bank.update()
                st.success(f"✅ ₹{amount:,.0f} Withdrawn Successfully!")
                st.metric("Remaining Balance", f"₹{user['balance']:,.0f}")

    show_data_table()

# ===============================
# CHECK DETAILS
# ===============================

elif "Check Details" in menu:
    st.header("🔍 Account Details")

    account = st.text_input("Account Number")
    pin     = st.text_input("PIN", type="password")

    if st.button("Show Details", type="primary"):
        if not pin.isdigit():
            st.error("❌ PIN must be numeric")
        else:
            user = Bank.find_user(account, int(pin))
            if not user:
                st.error("❌ Invalid Credentials")
            else:
                st.success("✅ Account Found!")
                col1, col2 = st.columns(2)
                col1.metric("Name",        user["name"])
                col1.metric("Age",         user["age"])
                col2.metric("Balance (₹)", f"₹{user['balance']:,.0f}")
                col2.metric("Email",       user["email"])
                st.info(f"Account No: **{user['accountNo.']}**")

    show_data_table()

# ===============================
# UPDATE DETAILS
# ===============================

elif "Update Details" in menu:
    st.header("✏️ Update Account")

    account = st.text_input("Account Number")
    pin     = st.text_input("Current PIN", type="password")

    if st.button("Load Details"):
        if not pin.isdigit():
            st.error("❌ PIN must be numeric")
        else:
            user = Bank.find_user(account, int(pin))
            if user:
                st.session_state.user = user
                st.success("✅ Account loaded!")
            else:
                st.error("❌ Invalid Credentials")

    if "user" in st.session_state:
        user    = st.session_state.user
        name    = st.text_input("New Name",  user["name"])
        age     = st.number_input("New Age", value=int(user["age"]))
        email   = st.text_input("New Email", user["email"])
        new_pin = st.text_input("New PIN",   value=str(user["pin"]))

        if st.button("Update", type="primary"):
            if len(new_pin) != 4 or not new_pin.isdigit():
                st.error("❌ PIN must be exactly 4 digits")
            else:
                user["name"]  = name
                user["age"]   = age
                user["email"] = email
                user["pin"]   = int(new_pin)
                Bank.update()
                del st.session_state.user      # clear after update
                st.success("✅ Details Updated Successfully!")

    show_data_table()

# ===============================
# DELETE ACCOUNT
# ===============================

elif "Delete Account" in menu:
    st.header("🗑️ Delete Account")

    account = st.text_input("Account Number")
    pin     = st.text_input("PIN", type="password")
    confirm = st.checkbox("⚠️ I understand this action cannot be undone")

    if st.button("Delete Account", type="primary"):
        if not pin.isdigit():
            st.error("❌ PIN must be numeric")
        else:
            user = Bank.find_user(account, int(pin))
            if not user:
                st.error("❌ Invalid Credentials")
            elif not confirm:
                st.warning("⚠️ Please tick the confirmation checkbox first")
            else:
                Bank.data.remove(user)
                Bank.update()
                st.success("✅ Account Deleted Successfully!")

    show_data_table()