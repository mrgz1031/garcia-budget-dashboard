import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Family Budget Dashboard", layout="wide")

# --- STYLES ---
st.markdown("""
    <style>
        body { background-color: #F5F5F5; color: #1A1A1A; font-family: 'Segoe UI', sans-serif; }
        .metric-card {
            background-color: #E8E8E8; 
            border-radius: 10px; 
            padding: 12px; 
            text-align: center; 
            margin: 5px; 
            box-shadow: 2px 2px 6px rgba(0,0,0,0.08);
        }
        .positive { background-color: #4CAF50; color: white; border-radius: 6px; padding: 5px; text-align: center; }
        .neutral { background-color: #FFEB3B; color: #1A1A1A; border-radius: 6px; padding: 5px; text-align: center; }
        .warning { background-color: #FF9800; color: white; border-radius: 6px; padding: 5px; text-align: center; }
        .negative { background-color: #E53935; color: white; border-radius: 6px; padding: 5px; text-align: center; }
        .dataframe td, .dataframe th { text-align: center !important; vertical-align: middle !important; padding: 6px 10px !important; color: #1A1A1A !important; }
        div[data-testid="stMetricValue"] { color: #1A1A1A; }
    </style>
""", unsafe_allow_html=True)

# --- EDITABLE DASHBOARD TITLE ---
dashboard_title = st.text_input("Dashboard Title", value="Family Budget Dashboard")
st.markdown(f"## 💰 {dashboard_title}")
st.markdown("##### Live Overview — Pay Periods: 1st & 15th")

# --- INPUT: MONTHLY INCOME & VARIABLE EXPENSES ---
monthly_income = st.number_input("Monthly Income ($)", value=8757.60, step=100.0, format="%.2f")
variable_expenses = st.number_input("Estimated Variable Expenses ($)", value=1850.00, step=50.0, format="%.2f")

# --- SESSION STATE INITIALIZATION ---
if "bills_df" not in st.session_state:
    st.session_state.bills_df = pd.DataFrame({
        "Bill": [
            "Mortgage", "HELOC", "Solar Loan", "Car Insurance", "RV Insurance", 
            "Motorcycle Insurance", "Cell Phone", "Gas", "Water/Sewer", "SoFi Loan", "Internet"
        ],
        "Category": ["Fixed"]*11,
        "Due Date #1": ["1","1","8","1","21","26","10","1","14","6","17"],
        "Due Date #2": ["15","15","—","15","—","—","—","15","—","15","—"],
        "Amount ($)": [3489, 379, 219, 300, 79, 60, 340, 65, 150, 1225.82, 71.74],
        "Paid ($)": [0.00]*11
    })

if "savings_df" not in st.session_state:
    st.session_state.savings_df = pd.DataFrame({
        "Account": [
            "School's First Savings", "Navy Fed Savings", "Fidelity Brokerage", "Fidelity Cash Management",
            "Micah's Savings", "Zeke's Savings", "Anuhea's Savings",
            "Vanguard Roth IRA", "Thrift Savings Plan TSP"
        ],
        "Category": ["Savings"]*7 + ["Retirement"]*2,
        "Transfer #1 Date": ["1"]*9,
        "Transfer #2 Date": ["15"]*9,
        "Monthly Contribution ($)": [50, 50, 50, 50, 25, 25, 25, 300, 400]
    })

if "credit_df" not in st.session_state:
    st.session_state.credit_df = pd.DataFrame({
        "Card": ["Chase Sapphire Reserve", "Sam's Club", "Capital One (USCCA)", "AMEX Blue Cash Preferred", "NavyFed Cash Rewards"],
        "Balance ($)": [811.00, 268.15, 60.00, 0.00, 0.00],
        "Limit ($)": [10000, 5000, 3000, 6000, 5000]
    })

# --- BILLS & PAYMENTS (Editable) ---
st.subheader("📋 Bills & Payments")
bills_df = st.data_editor(st.session_state.bills_df, num_rows="dynamic", use_container_width=True)
st.session_state.bills_df = bills_df

# --- SAVINGS & RETIREMENT (Editable) ---
st.subheader("💾 Savings & Retirement Accounts")
savings_df = st.data_editor(st.session_state.savings_df, num_rows="dynamic", use_container_width=True)
st.session_state.savings_df = savings_df

# --- CREDIT CARDS (Editable) ---
st.subheader("💳 Credit Cards")
credit_df = st.data_editor(st.session_state.credit_df, num_rows="dynamic", use_container_width=True)
st.session_state.credit_df = credit_df

# --- CALCULATIONS ---
total_bills_due = bills_df["Amount ($)"].sum()
total_bills_paid = bills_df["Paid ($)"].sum()
remaining_cash = monthly_income - total_bills_paid - variable_expenses

# Credit utilization & status coloring
def utilization_status(balance):
    if balance <= 100:
        return "<div class='positive'>Low</div>"
    elif balance <= 500:
        return "<div class='neutral'>Moderate</div>"
    elif balance <= 800:
        return "<div class='warning'>High</div>"
    else:
        return "<div class='negative'>Critical</div>"

credit_df["Utilization (%)"] = ((credit_df["Balance ($)"] / credit_df["Limit ($)"]) * 100).round(1)
credit_df["Status"] = credit_df["Balance ($)"].apply(utilization_status)

# --- MONTHLY OVERVIEW METRICS ---
st.markdown("---")
st.subheader("📊 Monthly Overview")
col1, col2, col3, col4, col5 = st.columns(5)
metrics = [
    (f"${monthly_income:,.2f}", "Monthly Income"),
    (f"${total_bills_due:,.2f}", "Total Bills"),
    (f"${variable_expenses:,.2f}", "Variable Expenses"),
    (f"N/A", "Total Savings"),
    (f"${remaining_cash:,.2f}", "Remaining Cash")
]

for idx, (value, label) in enumerate(metrics):
    card_class = "metric-card"
    if label == "Remaining Cash":
        card_class += " positive" if remaining_cash >= 0 else "negative"
    with [col1, col2, col3, col4, col5][idx]:
        st.markdown(
            f"<div class='{card_class}'><div style='font-size:20px;'>{value}</div>"
            f"<div style='font-size:12px;color:#333;'>{label}</div></div>", unsafe_allow_html=True
        )

# --- DYNAMIC SAVINGS & RETIREMENT OVERVIEW ---
st.markdown("---")
st.subheader("📊 Savings and Retirement Accounts Overview")

for category in savings_df["Category"].unique():
    st.markdown(f"**{category} Accounts**")
    accounts_in_category = savings_df[savings_df["Category"] == category]["Account"].tolist()
    cols = st.columns(len(accounts_in_category))
    for i, account in enumerate(accounts_in_category):
        contribution = savings_df.loc[savings_df["Account"] == account, "Monthly Contribution ($)"].values[0]
        card_class = "metric-card positive" if contribution >= 0 else "metric-card negative"
        with cols[i]:
            st.markdown(
                f"<div class='{card_class}'><div style='font-size:18px;'>${contribution:,.2f}</div>"
                f"<div style='font-size:12px;color:#333;'>{account}</div></div>", unsafe_allow_html=True
            )

# --- TOTALS FOR DYNAMIC CATEGORIES ---
st.markdown("---")
categories = savings_df["Category"].unique()
cols = st.columns(len(categories))
for i, cat in enumerate(categories):
    total = savings_df[savings_df["Category"] == cat]["Monthly Contribution ($)"].sum()
    with cols[i]:
        st.markdown(
            f"<div class='metric-card'><div style='font-size:20px;'>${total:,.2f}</div>"
            f"<div style='font-size:12px;color:#333;'>Total {cat}</div></div>", unsafe_allow_html=True
        )

# --- CREDIT CARDS DISPLAY ---
st.markdown("---")
st.write(credit_df.to_html(escape=False, index=False), unsafe_allow_html=True)

st.markdown("---")
st.markdown("✅ Tip: Add, remove, or edit any row in Bills, Savings, Retirement, or Credit Cards — all metrics update automatically for any family setup.")
