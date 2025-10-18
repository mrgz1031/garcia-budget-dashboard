import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Family Budget Dashboard", layout="wide")

# --- STYLES ---
st.markdown("""
    <style>
        body { background-color: #F5F5F5; color: #1A1A1A; font-family: 'Segoe UI', sans-serif; }
        .metric-card { background-color: #E0E0E0; border-radius: 10px; padding: 12px; text-align: center; margin: 5px; box-shadow: 2px 2px 6px rgba(0,0,0,0.08); }
        .positive { color: green; font-weight:bold; }
        .yellow { color: orange; font-weight:bold; }
        .orange { color: darkorange; font-weight:bold; }
        .red { color: red; font-weight:bold; }
        .dataframe td, .dataframe th { text-align: center !important; vertical-align: middle !important; padding: 6px 10px !important; color: #1A1A1A !important; }
        div[data-testid="stMetricValue"] { color: #1A1A1A; }
    </style>
""", unsafe_allow_html=True)

# --- EDITABLE TITLE ---
dashboard_title = st.text_input("Dashboard Title", value="Garcia Family Budget")
st.markdown(f"## 💰 {dashboard_title}")
st.markdown("##### Live Overview — Pay Periods: 1st & 15th")

# --- INPUT: Monthly Income & Variable Expenses ---
monthly_income = st.number_input("Monthly Income ($)", value=8757.60, step=100.0, format="%.2f")
variable_expenses = st.number_input("Estimated Variable Expenses ($)", value=1850.00, step=50.0, format="%.2f")

# --- SESSION STATE INIT ---
if "bills_df" not in st.session_state:
    st.session_state.bills_df = pd.DataFrame({
        "Bill": [
            "Cross Country Mortgage", "Navy Federal HELOC", "NuVision Solar Loan", "USAA Car Insurance (split)",
            "Progressive RV Insurance", "Geico Motorcycle Insurance", "T-Mobile Cell Phone", "SoCal Gas",
            "Elsinore Valley Water/Sewer", "SoFi Consolidation Loan", "Home Internet"
        ],
        "Due Date #1": ["1", "1", "8", "1", "21", "26", "10", "1", "14", "6", "17"],
        "Due Date #2": ["15", "15", "", "15", "", "", "", "", "", "", ""],
        "Amount ($)": [3489.00, 379.00, 219.00, 300.00, 79.00, 60.00, 340.00, 65.00, 150.00, 1225.82, 71.74],
        "Paid ($)": [0.00]*11
    })

if "savings_df" not in st.session_state:
    st.session_state.savings_df = pd.DataFrame({
        "Account": [
            "School's First Savings", "Navy Fed Savings", "Fidelity Brokerage", "Fidelity Cash Management",
            "Vanguard Roth IRA", "Thrift Savings Plan TSP",
            "Micah Savings", "Zeke Savings", "Anuhea Savings"
        ],
        "Monthly Contribution ($)": [50,50,50,50,300,400,50,50,50]
    })

if "credit_df" not in st.session_state:
    st.session_state.credit_df = pd.DataFrame({
        "Card": ["Chase Sapphire Reserve", "Sam's Club", "Capital One (USCCA)", "AMEX Blue Cash Preferred", "NavyFed Cash Rewards"],
        "Balance ($)": [811.00, 268.15, 60.00, 0.00, 0.00],
        "Limit ($)": [10000, 5000, 3000, 6000, 5000]
    })

# --- BILLS & PAYMENTS ---
st.subheader("📋 Bills & Payments")
bills_df = st.data_editor(
    st.session_state.bills_df,
    num_rows="dynamic",
    use_container_width=True
)
st.session_state.bills_df = bills_df

# --- SAVINGS & RETIREMENT CONTRIBUTIONS ---
st.subheader("💾 Savings & Retirement Accounts")
savings_df = st.data_editor(
    st.session_state.savings_df,
    num_rows="dynamic",
    use_container_width=True
)
st.session_state.savings_df = savings_df

# --- CREDIT CARDS ---
st.subheader("💳 Credit Cards")
credit_editable = st.data_editor(
    st.session_state.credit_df,
    num_rows="dynamic",
    use_container_width=True
)
st.session_state.credit_df = credit_editable

# --- CALCULATE UTILIZATION AND STATUS ---
def get_status(balance):
    if balance <= 100:
        return "Low", "positive"
    elif 101 <= balance <= 500:
        return "Medium", "yellow"
    elif 501 <= balance <= 800:
        return "High", "orange"
    else:
        return "Very High", "red"

credit_df = st.session_state.credit_df.copy()
credit_df["Utilization (%)"] = ((credit_df["Balance ($)"] / credit_df["Limit ($)"]) * 100).round(1)
credit_df["Status"] = credit_df["Balance ($)"].apply(lambda x: get_status(x)[0])
credit_df["Status_Color"] = credit_df["Balance ($)"].apply(lambda x: get_status(x)[1])

# Display credit card table with colors
credit_display = credit_df[["Card","Balance ($)","Limit ($)","Utilization (%)","Status"]].copy()
for i, row in credit_df.iterrows():
    color = row["Status_Color"]
    credit_display.loc[i,"Status"] = f"{row['Status']}"
st.dataframe(credit_display, use_container_width=True)

# --- CALCULATE TOTALS ---
total_bills = bills_df["Amount ($)"].sum()
total_variable = variable_expenses
total_savings = savings_df["Monthly Contribution ($)"].sum()
remaining_cash = monthly_income - total_bills - total_variable  # exclude savings for remaining cash

# --- TOP METRICS DYNAMICALLY ---
st.markdown("---")
st.subheader("📊 Monthly Overview")
col1, col2, col3, col4, col5 = st.columns(5)
metrics = [
    (f"${monthly_income:,.2f}", "Monthly Income"),
    (f"${total_bills:,.2f}", "Total Bills"),
    (f"${variable_expenses:,.2f}", "Variable Expenses"),
    (f"${total_savings:,.2f}", "Total Savings"),
    (f"${remaining_cash:,.2f}", "Remaining Cash")
]

for idx, (value, label) in enumerate(metrics):
    card_class = "metric-card"
    if label == "Remaining Cash":
        card_class += " positive" if remaining_cash >= 0 else "red"
    with [col1, col2, col3, col4, col5][idx]:
        st.markdown(
            f"<div class='{card_class}'><div style='font-size:20px;'>{value}</div><div style='font-size:12px;color:#333;'>{label}</div></div>",
            unsafe_allow_html=True
        )

# --- SAVINGS & RETIREMENT OVERVIEW ---
st.markdown("---")
st.subheader("📊 Savings and Retirement Accounts Overview")

# Dynamically display all accounts
accounts = st.session_state.savings_df
cols = st.columns(len(accounts))
for i, row in accounts.iterrows():
    with cols[i % len(accounts)]:
        st.markdown(
            f"<div class='metric-card'><div style='font-size:18px;'>${row['Monthly Contribution ($)']:,.2f}</div><div style='font-size:12px;color:#333;'>{row['Account']}</div></div>",
            unsafe_allow_html=True
        )

# Totals by category
savings_accounts = ["School's First Savings", "Navy Fed Savings", "Fidelity Brokerage", "Fidelity Cash Management","Micah Savings","Zeke Savings","Anuhea Savings"]
retirement_accounts = ["Vanguard Roth IRA", "Thrift Savings Plan TSP"]

total_savings_amount = accounts[accounts["Account"].isin(savings_accounts)]["Monthly Contribution ($)"].sum()
total_retirement_amount = accounts[accounts["Account"].isin(retirement_accounts)]["Monthly Contribution ($)"].sum()

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"<div class='metric-card'><div style='font-size:20px;'>${total_savings_amount:,.2f}</div><div style='font-size:12px;color:#333;'>Total Savings</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><div style='font-size:20px;'>${total_retirement_amount:,.2f}</div><div style='font-size:12px;color:#333;'>Total Retirement</div></div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("✅ Tip: Edit amounts, add/remove rows, or mark bills as paid — all changes recalculate automatically.")
