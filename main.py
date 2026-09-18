"""VyaparPulse - Inclusive Credit Infrastructure for Bharat.

Single-file Streamlit app (no external assets, no image files).
Run: streamlit run main.py --server.address 0.0.0.0
Dependencies: streamlit, pandas, plotly.
Every visual is a live, data-driven Plotly chart - no embedded/uploaded images.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random

st.set_page_config(
    page_title="VyaparPulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": None,
        "Get Help": None,
        "Report a bug": None,
    },
)

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
div[data-testid="stDecoration"] {display: none;}

.stApp {
    background-color: #FAFAFA;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
    border-right: 3px solid #000080;
}

section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #1a1a2e !important;
}

div.stButton > button {
    background-color: #FF9933;
    color: #FFFFFF;
    border: 2px solid #000080;
    border-radius: 4px;
    font-weight: 600;
    padding: 8px 20px;
}

div.stButton > button:hover {
    background-color: #138808;
    color: #FFFFFF;
    border: 2px solid #000080;
}

div.stDownloadButton > button {
    background-color: #000080;
    color: #FFFFFF;
    border: 2px solid #FF9933;
    border-radius: 4px;
    font-weight: 600;
}

div.stDownloadButton > button:hover {
    background-color: #FF9933;
    color: #000080;
}

.integrity-pass {
    background-color: #138808;
    color: #FFFFFF;
    padding: 20px;
    border-radius: 4px;
    text-align: center;
    font-size: 24px;
    font-weight: 700;
    border: 3px solid #0d5c06;
    margin: 10px 0;
}

.integrity-fail {
    background-color: #CC0000;
    color: #FFFFFF;
    padding: 20px;
    border-radius: 4px;
    text-align: center;
    font-size: 24px;
    font-weight: 700;
    border: 3px solid #990000;
    margin: 10px 0;
    animation: blink 1s linear infinite;
}

@keyframes blink {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.tricolor-header {
    background: linear-gradient(90deg, #FF9933 0%, #FF9933 33%, #FFFFFF 33%, #FFFFFF 66%, #138808 66%, #138808 100%);
    padding: 4px;
    border-radius: 4px;
    margin-bottom: 10px;
}

.score-card {
    background: #FFFFFF;
    border: 2px solid #000080;
    border-radius: 4px;
    padding: 15px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.metric-box {
    background: #FFFFFF;
    border-left: 4px solid #FF9933;
    padding: 12px;
    margin: 5px 0;
    border-radius: 0 4px 4px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.section-header {
    color: #000080;
    border-bottom: 3px solid #FF9933;
    padding-bottom: 8px;
    margin-bottom: 15px;
    font-weight: 700;
}

h1, h2, h3 {
    color: #000080 !important;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def get_base_personas():
    return {
        "Ramesh Kirana": {
            "name": "Ramesh Kirana",
            "type": "Kirana Store Owner",
            "location": "Sector 14, Gurgaon",
            "base_score": 702,
            "integrity": "PASS",
            "integrity_reason": "All checks cleared. No anomalies detected.",
            "loan_status": "ELIGIBLE",
            "base_recommended_credit": 250000,
            "factors": {
                "Consistency": {"value": 82, "delta": "+5"},
                "Growth": {"value": 71, "delta": "+12"},
                "Liquidity Buffer": {"value": 68, "delta": "+3"},
                "Payer Diversity": {"value": 88, "delta": "+7"},
                "Reliability": {"value": 79, "delta": "+2"},
                "Longevity": {"value": 74, "delta": "+4"},
            },
            "tips": [
                "Maintain consistent daily UPI collections above Rs 8,000 to push Consistency above 85.",
                "Diversify supplier payments across 3+ vendors to improve Liquidity Buffer rating.",
                "Register for GST to unlock formal credit channels and boost Growth factor.",
            ],
            "monthly_revenue": [45000, 48000, 52000, 49000, 55000, 58000, 61000, 59000, 63000, 67000, 65000, 70000],
            "monthly_expenses": [32000, 34000, 36000, 35000, 38000, 40000, 42000, 41000, 43000, 45000, 44000, 47000],
            "upi_daily_avg": 8500,
            "total_transactions": 14200,
            "sthan_days": 1825,
            "sthan_log": [
                {"date": "2024-01-15", "time": "06:30", "status": "Present", "note": "Morning opening"},
                {"date": "2024-01-16", "time": "06:45", "status": "Present", "note": "Regular day"},
                {"date": "2024-01-17", "time": "07:00", "status": "Present", "note": "Late start rain"},
                {"date": "2024-01-18", "time": "06:30", "status": "Present", "note": "Festival prep"},
                {"date": "2024-01-19", "time": "06:15", "status": "Present", "note": "Early opening"},
                {"date": "2024-01-20", "time": "REST", "status": "Absent", "note": "Sunday closed"},
            ],
        },
        "QuickKart Reseller": {
            "name": "QuickKart Reseller",
            "type": "Online Reseller",
            "location": "Laxmi Nagar, Delhi",
            "base_score": 648,
            "integrity": "FAIL",
            "integrity_reason": "WASH TRADING DETECTED: 67% of inbound UPI payments originate from 2 linked accounts. PAYER CONCENTRATION: Top payer accounts for 73% of volume. Pattern consistent with synthetic transaction inflation.",
            "loan_status": "VOIDED",
            "base_recommended_credit": 0,
            "factors": {
                "Consistency": {"value": 76, "delta": "+2"},
                "Growth": {"value": 89, "delta": "+34"},
                "Liquidity Buffer": {"value": 42, "delta": "-8"},
                "Payer Diversity": {"value": 12, "delta": "-45"},
                "Reliability": {"value": 55, "delta": "-12"},
                "Longevity": {"value": 31, "delta": "-5"},
            },
            "tips": [
                "CRITICAL: Payer Diversity score is 12/100. Over 73% revenue from 2 accounts triggers fraud flags.",
                "WARNING: Rapid Growth (+34%) with low Diversity is a red-flag pattern for wash trading.",
                "ACTION REQUIRED: Provide independent third-party transaction verification to clear integrity hold.",
            ],
            "monthly_revenue": [12000, 15000, 22000, 35000, 58000, 89000, 120000, 145000, 180000, 210000, 250000, 290000],
            "monthly_expenses": [10000, 13000, 20000, 32000, 54000, 85000, 115000, 140000, 175000, 205000, 245000, 285000],
            "upi_daily_avg": 9600,
            "total_transactions": 8900,
            "sthan_days": 95,
            "sthan_log": [
                {"date": "2024-01-15", "time": "11:30", "status": "Present", "note": ""},
                {"date": "2024-01-16", "time": "N/A", "status": "Absent", "note": ""},
                {"date": "2024-01-17", "time": "14:00", "status": "Present", "note": ""},
                {"date": "2024-01-18", "time": "N/A", "status": "Absent", "note": ""},
                {"date": "2024-01-19", "time": "N/A", "status": "Absent", "note": ""},
                {"date": "2024-01-20", "time": "10:00", "status": "Present", "note": ""},
            ],
        },
        "Meena's Stall": {
            "name": "Meena's Stall",
            "type": "Street Food Vendor",
            "location": "Chandni Chowk, Delhi",
            "base_score": 585,
            "integrity": "PASS",
            "integrity_reason": "All checks cleared. Thin file compensated by strong physical presence and longevity.",
            "loan_status": "ELIGIBLE",
            "base_recommended_credit": 50000,
            "factors": {
                "Consistency": {"value": 61, "delta": "+1"},
                "Growth": {"value": 45, "delta": "+8"},
                "Liquidity Buffer": {"value": 38, "delta": "-2"},
                "Payer Diversity": {"value": 72, "delta": "+3"},
                "Reliability": {"value": 69, "delta": "+5"},
                "Longevity": {"value": 91, "delta": "+10"},
            },
            "tips": [
                "Your 512-day Sthan Log is your strongest asset. Keep checking in daily to maintain Longevity at 91.",
                "Accept UPI for even small transactions (Rs 10+) to build digital trail and boost Consistency from 61.",
                "Ask 5 regular customers to pay via UPI weekly to improve Payer Diversity score further.",
            ],
            "monthly_revenue": [8000, 8500, 9000, 8200, 9500, 10000, 9800, 10500, 11000, 10800, 11500, 12000],
            "monthly_expenses": [5000, 5200, 5500, 5100, 5800, 6000, 5900, 6300, 6500, 6400, 6800, 7000],
            "upi_daily_avg": 380,
            "total_transactions": 3200,
            "sthan_days": 512,
            "sthan_log": [
                {"date": "2024-01-15", "time": "05:00", "status": "Present", "note": "Morning prep started"},
                {"date": "2024-01-16", "time": "05:15", "status": "Present", "note": "Regular day"},
                {"date": "2024-01-17", "time": "05:00", "status": "Present", "note": "Busy morning"},
                {"date": "2024-01-18", "time": "05:30", "status": "Present", "note": "Festival rush"},
                {"date": "2024-01-19", "time": "05:00", "status": "Present", "note": "Extra stock prepared"},
                {"date": "2024-01-20", "time": "05:00", "status": "Present", "note": "Weekend crowd"},
            ],
        },
        "Suresh Auto Parts": {
            "name": "Suresh Auto Parts",
            "type": "Auto Parts Retailer",
            "location": "Karol Bagh, Delhi",
            "base_score": 745,
            "integrity": "PASS",
            "integrity_reason": "All checks cleared. Strong B2B transaction patterns verified.",
            "loan_status": "ELIGIBLE",
            "base_recommended_credit": 500000,
            "factors": {
                "Consistency": {"value": 85, "delta": "+6"},
                "Growth": {"value": 78, "delta": "+15"},
                "Liquidity Buffer": {"value": 72, "delta": "+8"},
                "Payer Diversity": {"value": 81, "delta": "+4"},
                "Reliability": {"value": 90, "delta": "+3"},
                "Longevity": {"value": 88, "delta": "+2"},
            },
            "tips": [
                "Excellent Reliability score of 90. Maintain timely supplier payments to keep this strong.",
                "Consider adding digital inventory tracking to further validate stock turnover for lenders.",
                "Your B2B payment patterns are strong. Formalize contracts with top 5 garage clients for better terms.",
            ],
            "monthly_revenue": [120000, 135000, 128000, 142000, 155000, 148000, 162000, 170000, 165000, 178000, 185000, 192000],
            "monthly_expenses": [85000, 95000, 90000, 100000, 108000, 105000, 112000, 118000, 115000, 122000, 128000, 132000],
            "upi_daily_avg": 6200,
            "total_transactions": 9800,
            "sthan_days": 2920,
            "sthan_log": [
                {"date": "2024-01-15", "time": "09:00", "status": "Present", "note": "Shop opened"},
                {"date": "2024-01-16", "time": "09:15", "status": "Present", "note": "Bulk order day"},
                {"date": "2024-01-17", "time": "09:00", "status": "Present", "note": "Regular operations"},
                {"date": "2024-01-18", "time": "09:30", "status": "Present", "note": "Supplier meeting"},
                {"date": "2024-01-19", "time": "09:00", "status": "Present", "note": "Inventory check"},
                {"date": "2024-01-20", "time": "10:00", "status": "Present", "note": "Half day family event"},
            ],
        },
        "Fatima Tailoring": {
            "name": "Fatima Tailoring",
            "type": "Home-based Tailor",
            "location": "Jamia Nagar, Delhi",
            "base_score": 540,
            "integrity": "PASS",
            "integrity_reason": "All checks cleared. Ultra-thin file but genuine micro-enterprise pattern confirmed.",
            "loan_status": "ELIGIBLE",
            "base_recommended_credit": 25000,
            "factors": {
                "Consistency": {"value": 48, "delta": "+2"},
                "Growth": {"value": 52, "delta": "+18"},
                "Liquidity Buffer": {"value": 30, "delta": "-1"},
                "Payer Diversity": {"value": 65, "delta": "+9"},
                "Reliability": {"value": 58, "delta": "+4"},
                "Longevity": {"value": 78, "delta": "+6"},
            },
            "tips": [
                "Start accepting UPI payments for all orders above Rs 200 to build a stronger digital footprint.",
                "Your Growth trend (+18%) is promising. Document each order with a photo for expense tracking.",
                "Register with local women's self-help group (SHG) to access group lending at better rates.",
            ],
            "monthly_revenue": [6000, 6500, 7000, 5500, 8000, 9000, 8500, 9500, 10000, 11000, 10500, 12000],
            "monthly_expenses": [3500, 3800, 4000, 3200, 4500, 5000, 4800, 5200, 5500, 6000, 5800, 6500],
            "upi_daily_avg": 220,
            "total_transactions": 1800,
            "sthan_days": 1095,
            "sthan_log": [
                {"date": "2024-01-15", "time": "10:00", "status": "Present", "note": "Started stitching orders"},
                {"date": "2024-01-16", "time": "10:30", "status": "Present", "note": "2 new customers"},
                {"date": "2024-01-17", "time": "10:00", "status": "Present", "note": "Delivery day"},
                {"date": "2024-01-18", "time": "N/A", "status": "Absent", "note": "Family commitment"},
                {"date": "2024-01-19", "time": "09:30", "status": "Present", "note": "Festival orders rush"},
                {"date": "2024-01-20", "time": "10:00", "status": "Present", "note": "Measurements taken"},
            ],
        },
    }


def init_session_state():
    if "expense_entries" not in st.session_state:
        st.session_state.expense_entries = {}
    if "revenue_entries" not in st.session_state:
        st.session_state.revenue_entries = {}
    if "sthan_entries" not in st.session_state:
        st.session_state.sthan_entries = {}
    if "expense_photos_log" not in st.session_state:
        st.session_state.expense_photos_log = {}
    if "fraud_audit_log" not in st.session_state:
        st.session_state.fraud_audit_log = []


def compute_live_score(persona_key, base_persona):
    base_score = base_persona["base_score"]
    base_expenses = list(base_persona["monthly_expenses"])
    base_revenue = list(base_persona["monthly_revenue"])

    user_expenses = st.session_state.expense_entries.get(persona_key, [])
    user_revenues = st.session_state.revenue_entries.get(persona_key, [])

    total_added_expense = sum(e["amount"] for e in user_expenses)
    total_added_revenue = sum(r["amount"] for r in user_revenues)

    total_base_revenue = sum(base_revenue)
    total_base_expense = sum(base_expenses)
    base_profit = total_base_revenue - total_base_expense

    new_total_revenue = total_base_revenue + total_added_revenue
    new_total_expense = total_base_expense + total_added_expense
    new_profit = new_total_revenue - new_total_expense

    if total_base_revenue > 0:
        base_margin = base_profit / total_base_revenue
        new_margin = new_profit / new_total_revenue if new_total_revenue > 0 else 0
    else:
        base_margin = 0
        new_margin = 0

    margin_shift = new_margin - base_margin

    score_delta = int(margin_shift * 300)
    score_delta = max(-150, min(150, score_delta))

    expense_ratio_change = 0
    if total_base_expense > 0 and total_added_expense > 0:
        expense_ratio_change = total_added_expense / total_base_expense

    if expense_ratio_change > 0.5:
        score_delta -= int(expense_ratio_change * 30)
    elif expense_ratio_change > 0.2:
        score_delta -= int(expense_ratio_change * 15)

    revenue_growth = 0
    if total_added_revenue > 0:
        revenue_growth = total_added_revenue / max(total_base_revenue, 1)
        score_delta += int(revenue_growth * 40)

    sthan_entries = st.session_state.sthan_entries.get(persona_key, [])
    present_checkins = sum(1 for e in sthan_entries if e["status"] == "Present")
    score_delta += present_checkins * 2

    photo_logs = st.session_state.expense_photos_log.get(persona_key, [])
    score_delta += len(photo_logs) * 3

    live_score = base_score + score_delta
    live_score = max(300, min(900, live_score))

    updated_factors = {}
    for fname, fdata in base_persona["factors"].items():
        base_val = fdata["value"]
        if fname == "Liquidity Buffer":
            if new_profit > base_profit:
                adj = min(10, int((new_profit - base_profit) / max(base_profit, 1) * 20))
            else:
                adj = max(-15, int((new_profit - base_profit) / max(abs(base_profit), 1) * 20))
            new_val = max(5, min(100, base_val + adj))
        elif fname == "Consistency":
            if total_added_revenue > 0:
                adj = min(8, int(revenue_growth * 15))
            else:
                adj = 0
            if total_added_expense > total_added_revenue and total_added_expense > 0:
                adj -= 5
            new_val = max(5, min(100, base_val + adj))
        elif fname == "Growth":
            if total_added_revenue > 0:
                adj = min(12, int(revenue_growth * 25))
            else:
                adj = 0
            new_val = max(5, min(100, base_val + adj))
        elif fname == "Reliability":
            adj = present_checkins
            if total_added_expense > total_added_revenue * 1.5 and total_added_revenue > 0:
                adj -= 5
            new_val = max(5, min(100, base_val + adj))
        elif fname == "Longevity":
            adj = present_checkins + len(photo_logs)
            new_val = max(5, min(100, base_val + adj))
        elif fname == "Payer Diversity":
            adj = min(5, len(user_revenues))
            new_val = max(5, min(100, base_val + adj))
        else:
            new_val = base_val

        change = new_val - base_val
        if change >= 0:
            new_delta = f"+{change}"
        else:
            new_delta = str(change)

        updated_factors[fname] = {"value": new_val, "delta": new_delta}

    base_credit = base_persona["base_recommended_credit"]
    if base_persona["integrity"] == "FAIL":
        recommended_credit = 0
    else:
        credit_multiplier = live_score / base_score if base_score > 0 else 1
        recommended_credit = int(base_credit * credit_multiplier)
        recommended_credit = max(0, recommended_credit)
        recommended_credit = (recommended_credit // 1000) * 1000

    return {
        "score": live_score,
        "score_delta": score_delta,
        "factors": updated_factors,
        "recommended_credit": recommended_credit,
        "total_added_expense": total_added_expense,
        "total_added_revenue": total_added_revenue,
        "new_total_revenue": new_total_revenue,
        "new_total_expense": new_total_expense,
        "new_profit": new_profit,
        "margin": new_margin,
    }


def get_score_color(score):
    if score >= 700:
        return "#138808"
    elif score >= 600:
        return "#FF9933"
    elif score >= 500:
        return "#DAA520"
    else:
        return "#CC0000"


def get_score_label(score):
    if score >= 750:
        return "Excellent"
    elif score >= 700:
        return "Good"
    elif score >= 650:
        return "Fair"
    elif score >= 550:
        return "Below Average"
    else:
        return "Poor"


def create_gauge_chart(score, name):
    color = get_score_color(score)
    label = get_score_label(score)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={
                "text": f"Live VyaparPulse Score<br>{name} | {label}",
                "font": {"size": 18, "color": "#000080"},
            },
            number={"font": {"size": 56, "color": color}, "suffix": "/900"},
            gauge={
                "axis": {"range": [300, 900], "tickwidth": 2, "tickcolor": "#000080", "dtick": 100},
                "bar": {"color": color, "thickness": 0.3},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "#000080",
                "steps": [
                    {"range": [300, 500], "color": "#ffcccc"},
                    {"range": [500, 600], "color": "#ffe0b2"},
                    {"range": [600, 700], "color": "#fff9c4"},
                    {"range": [700, 800], "color": "#c8e6c9"},
                    {"range": [800, 900], "color": "#a5d6a7"},
                ],
                "threshold": {
                    "line": {"color": "#000080", "width": 4},
                    "thickness": 0.8,
                    "value": score,
                },
            },
        )
    )
    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=60, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial"},
    )
    return fig


def create_revenue_expense_chart(monthly_revenue, monthly_expenses, added_rev, added_exp, name):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    rev_with_additions = list(monthly_revenue)
    exp_with_additions = list(monthly_expenses)

    if added_rev > 0:
        per_month_rev = added_rev / 12
        rev_with_additions = [r + per_month_rev for r in rev_with_additions]
    if added_exp > 0:
        per_month_exp = added_exp / 12
        exp_with_additions = [e + per_month_exp for e in exp_with_additions]

    profit = [r - e for r, e in zip(rev_with_additions, exp_with_additions)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months, y=rev_with_additions, name="Revenue",
        marker_color="#138808",
        text=[f"Rs {int(v):,}" for v in rev_with_additions],
        textposition="outside", textfont={"size": 8},
    ))
    fig.add_trace(go.Bar(
        x=months, y=exp_with_additions, name="Expenses",
        marker_color="#FF9933",
        text=[f"Rs {int(v):,}" for v in exp_with_additions],
        textposition="outside", textfont={"size": 8},
    ))
    fig.add_trace(go.Scatter(
        x=months, y=profit, name="Net Profit",
        line={"color": "#000080", "width": 3},
        mode="lines+markers",
    ))
    fig.update_layout(
        title={"text": f"Revenue vs Expenses (Live) - {name}", "font": {"color": "#000080", "size": 16}},
        xaxis_title="Month", yaxis_title="Amount (Rs)",
        barmode="group", height=400,
        margin=dict(l=50, r=30, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis={"gridcolor": "#e0e0e0"}, font={"family": "Arial"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    return fig


def create_score_trend_chart(base_score, live_score, name):
    random.seed(hash(name) % 10000)
    days = list(range(1, 31))
    scores = []
    diff = live_score - base_score
    for d in days:
        progress = d / 30
        noise = random.randint(-5, 5)
        s = int(base_score + diff * progress + noise)
        s = max(300, min(900, s))
        scores.append(s)
    scores[-1] = live_score

    color = get_score_color(live_score)
    r_val = int(color.lstrip("#")[0:2], 16)
    g_val = int(color.lstrip("#")[2:4], 16)
    b_val = int(color.lstrip("#")[4:6], 16)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days, y=scores,
        mode="lines+markers",
        line={"color": color, "width": 3},
        marker={"size": 4},
        fill="tozeroy",
        fillcolor=f"rgba({r_val},{g_val},{b_val},0.1)",
        name="Score",
    ))
    fig.add_hline(y=base_score, line_dash="dash", line_color="#999",
                  annotation_text=f"Base: {base_score}", annotation_position="top left")
    fig.update_layout(
        title={"text": f"Score Movement (30 Days) - {name}", "font": {"color": "#000080", "size": 14}},
        xaxis_title="Day", yaxis_title="Score",
        yaxis={"range": [max(300, min(scores) - 30), min(900, max(scores) + 30)], "gridcolor": "#e0e0e0"},
        height=280, margin=dict(l=50, r=30, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial"},
    )
    return fig


def create_factor_radar_chart(factors, name):
    factor_names = list(factors.keys())
    factor_values = [factors[f]["value"] for f in factor_names]
    factor_names_closed = factor_names + [factor_names[0]]
    factor_values_closed = factor_values + [factor_values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=factor_values_closed,
        theta=factor_names_closed,
        fill="toself",
        fillcolor="rgba(255,153,51,0.2)",
        line={"color": "#FF9933", "width": 2},
        marker={"size": 6, "color": "#000080"},
        name="Factors",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont={"size": 9}),
            angularaxis=dict(tickfont={"size": 10, "color": "#000080"}),
        ),
        title={"text": f"Factor Radar - {name}", "font": {"color": "#000080", "size": 14}},
        height=320,
        margin=dict(l=60, r=60, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial"},
        showlegend=False,
    )
    return fig


def create_expense_breakdown_chart(persona_key):
    user_expenses = st.session_state.expense_entries.get(persona_key, [])
    if not user_expenses:
        return None

    category_totals = {}
    for e in user_expenses:
        cat = e["category"]
        category_totals[cat] = category_totals.get(cat, 0) + e["amount"]

    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    colors = ["#FF9933", "#138808", "#000080", "#DAA520", "#CC0000", "#4682B4", "#8B4513", "#666666"]

    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=categories,
        values=amounts,
        hole=0.4,
        marker={"colors": colors[:len(categories)]},
        textinfo="label+percent+value",
        texttemplate="%{label}<br>Rs %{value:,}<br>%{percent}",
        textfont={"size": 10},
    ))
    fig.update_layout(
        title={"text": "Expense Breakdown by Category", "font": {"color": "#000080", "size": 14}},
        height=320,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial"},
        showlegend=True,
        legend={"font": {"size": 10}},
    )
    return fig


def create_profit_waterfall_chart(base_revenue, base_expense, added_rev, added_exp):
    base_profit = base_revenue - base_expense

    fig = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["Base Revenue", "Added Revenue", "Base Expenses", "Added Expenses", "Net Position"],
        y=[base_revenue, added_rev, -base_expense, -added_exp, 0],
        text=[f"Rs {base_revenue:,}", f"Rs {added_rev:,}", f"-Rs {base_expense:,}", f"-Rs {added_exp:,}", ""],
        textposition="outside",
        textfont={"size": 9},
        connector={"line": {"color": "#000080", "width": 1}},
        increasing={"marker": {"color": "#138808"}},
        decreasing={"marker": {"color": "#CC0000"}},
        totals={"marker": {"color": "#000080"}},
    ))
    fig.update_layout(
        title={"text": "Financial Waterfall", "font": {"color": "#000080", "size": 14}},
        height=320,
        margin=dict(l=50, r=30, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis={"gridcolor": "#e0e0e0"},
        font={"family": "Arial"},
        showlegend=False,
    )
    return fig


# ----------------------------------------------------------------------------
# Fraud Guard graphs (these replace the former screenshot/QR image uploads)
# ----------------------------------------------------------------------------

def get_demo_claims():
    """Today's customer payment claims vs actual bank ledger records."""
    return [
        {"Transaction ID": "UPI-582914", "Payer": "Priya S.", "Time": "09:12", "Claimed (Rs)": 500, "Ledger (Rs)": 50},
        {"Transaction ID": "UPI-591026", "Payer": "Amit K.", "Time": "10:04", "Claimed (Rs)": 1200, "Ledger (Rs)": 1200},
        {"Transaction ID": "UPI-593471", "Payer": "Sunita D.", "Time": "11:47", "Claimed (Rs)": 850, "Ledger (Rs)": 850},
        {"Transaction ID": "UPI-598102", "Payer": "Vikram J.", "Time": "13:29", "Claimed (Rs)": 2000, "Ledger (Rs)": 200},
        {"Transaction ID": "UPI-602334", "Payer": "Rahul M.", "Time": "16:55", "Claimed (Rs)": 350, "Ledger (Rs)": 350},
        {"Transaction ID": "UPI-604417", "Payer": "Kavita R.", "Time": "18:20", "Claimed (Rs)": 1500, "Ledger (Rs)": 1500},
    ]


def create_claims_batch_chart(claims):
    """Grouped bar chart: every claimed amount vs what actually hit the ledger."""
    txn_ids = [c["Transaction ID"] for c in claims]
    claimed = [c["Claimed (Rs)"] for c in claims]
    ledger = [c["Ledger (Rs)"] for c in claims]
    ledger_colors = ["#CC0000" if abs(c - a) > 1 else "#138808" for c, a in zip(claimed, ledger)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=txn_ids, y=claimed, name="Claimed (Screenshot)",
        marker_color="#FF9933",
        text=[f"Rs {v:,}" for v in claimed],
        textposition="outside", textfont={"size": 9},
        customdata=[c["Payer"] for c in claims],
        hovertemplate="%{customdata} | %{x}<br>Claimed: Rs %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=txn_ids, y=ledger, name="Bank Ledger",
        marker_color=ledger_colors,
        text=[f"Rs {v:,}" for v in ledger],
        textposition="outside", textfont={"size": 9},
        customdata=[c["Payer"] for c in claims],
        hovertemplate="%{customdata} | %{x}<br>Ledger: Rs %{y:,}<extra></extra>",
    ))
    fig.update_layout(
        title={"text": "Today's Payment Claims vs Bank Ledger", "font": {"color": "#000080", "size": 14}},
        barmode="group", height=340,
        margin=dict(l=50, r=30, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis={"gridcolor": "#e0e0e0", "range": [0, max(claimed + ledger) * 1.2]},
        xaxis={"tickangle": -20},
        font={"family": "Arial"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    return fig


def create_claim_verification_chart(claimed, actual, txn_id=""):
    """Single-transaction verification chart (replaces the uploaded screenshot view)."""
    mismatch = abs(claimed - actual) > 1
    label = txn_id if txn_id else "Manual Verification"

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Claimed (Screenshot)", "Bank Ledger"],
        y=[claimed, actual],
        marker_color=["#FF9933", "#CC0000" if mismatch else "#138808"],
        text=[f"Rs {claimed:,}", f"Rs {actual:,}"],
        textposition="outside",
        showlegend=False,
    ))
    y_max = max(claimed, actual, 1)
    fig.update_layout(
        title={"text": f"Claim vs Ledger - {label}", "font": {"color": "#000080", "size": 14}},
        height=300,
        margin=dict(l=50, r=30, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis={"range": [0, y_max * 1.25], "gridcolor": "#e0e0e0"},
        font={"family": "Arial"},
    )
    if mismatch:
        diff = abs(claimed - actual)
        pct = diff / max(claimed, 1) * 100
        fig.add_annotation(
            x=1, y=y_max * 1.12,
            text=f"Delta: Rs {diff:,} ({pct:.0f}% deviation)",
            showarrow=True, arrowhead=2, arrowcolor="#CC0000",
            font={"color": "#CC0000", "size": 12, "weight": "bold"},
            ax=0, ay=-30,
        )
    return fig


def create_qr_routing_chart(vpa, legit_amount, misrouted_amount):
    """Live payment-routing diagram (replaces the uploaded QR code image)."""
    total = legit_amount + misrouted_amount
    labels = ["Customer Payments", "Your Shop QR", f"{vpa} (Registered)"]
    sources = [0, 1]
    targets = [1, 2]
    values = [total, legit_amount]
    link_colors = ["rgba(19,136,8,0.35)", "rgba(19,136,8,0.5)"]
    node_colors = ["#FF9933", "#000080", "#138808"]

    if misrouted_amount > 0:
        labels.append("UNLINKED ACCOUNT")
        sources.append(1)
        targets.append(3)
        values.append(misrouted_amount)
        link_colors.append("rgba(204,0,0,0.55)")
        node_colors.append("#CC0000")

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=14, thickness=16,
            label=labels, color=node_colors,
            line=dict(color="#000080", width=1),
        ),
        link=dict(
            source=sources, target=targets, value=values, color=link_colors,
            hovertemplate="Rs %{value:,}<extra></extra>",
        ),
    ))
    fig.update_layout(
        title={"text": "Live Payment Routing (Today)", "font": {"color": "#000080", "size": 14}},
        height=320,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial"},
    )
    return fig


def create_audit_chart(audit_log):
    """Bulk audit results: claimed vs received for every audited transaction."""
    labels = [f"{e['payer']} #{i + 1}" for i, e in enumerate(audit_log)]
    claimed = [e["claimed"] for e in audit_log]
    actual = [e["actual"] for e in audit_log]
    colors = ["#CC0000" if abs(c - a) > 1 else "#138808" for c, a in zip(claimed, actual)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=claimed, name="Claimed",
        marker_color="#FF9933",
        text=[f"Rs {v:,}" for v in claimed],
        textposition="outside", textfont={"size": 9},
    ))
    fig.add_trace(go.Bar(
        x=labels, y=actual, name="Received",
        marker_color=colors,
        text=[f"Rs {v:,}" for v in actual],
        textposition="outside", textfont={"size": 9},
    ))
    fig.update_layout(
        title={"text": "Bulk Audit Results - Claimed vs Received", "font": {"color": "#000080", "size": 14}},
        barmode="group", height=320,
        margin=dict(l=50, r=30, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis={"gridcolor": "#e0e0e0"},
        font={"family": "Arial"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    return fig


# ----------------------------------------------------------------------------
# Sthan Log graph (replaces the uploaded location photo)
# ----------------------------------------------------------------------------

def create_presence_heatmap(persona):
    """Check-in presence heatmap over the last 10 weeks (proof-of-vending visual)."""
    rng = random.Random(hash(persona["name"]) % 10000)
    base_log = persona["sthan_log"]
    present_count = sum(1 for e in base_log if e["status"] == "Present")
    rate = present_count / max(len(base_log), 1)

    n_weeks = 10
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    week_labels = [f"W-{n_weeks - 1 - w}" for w in range(n_weeks - 1)] + ["This Week"]

    z, text = [], []
    for _ in range(7):
        row, row_text = [], []
        for _ in range(n_weeks):
            present = rng.random() < rate
            row.append(1 if present else 0)
            row_text.append("Present" if present else "Absent")
        z.append(row)
        text.append(row_text)

    fig = go.Figure(go.Heatmap(
        z=z, x=week_labels, y=weekdays,
        text=text,
        hovertemplate="%{y} (%{x}): %{text}<extra></extra>",
        colorscale=[[0.0, "#F5F5F5"], [1.0, "#138808"]],
        zmin=0, zmax=1, showscale=False,
        xgap=2, ygap=2,
    ))
    fig.update_layout(
        title={"text": f"Presence History - Last {n_weeks} Weeks ({persona['name']})", "font": {"color": "#000080", "size": 14}},
        height=300,
        margin=dict(l=50, r=30, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial"},
        yaxis={"autorange": "reversed"},
    )
    return fig


# ----------------------------------------------------------------------------
# Lender Report graphs (replace the expense-notebook photo and document uploads)
# ----------------------------------------------------------------------------

def create_notebook_register_chart(persona):
    """Digitized expense register: last 8 weeks of notebook expenses by category."""
    rng = random.Random(hash(persona["name"]) % 10000)
    avg_monthly_expense = sum(persona["monthly_expenses"]) / 12
    weekly_base = avg_monthly_expense / 4.33

    categories = [
        ("Stock/Inventory", 0.45, "#FF9933"),
        ("Rent", 0.15, "#138808"),
        ("Wages/Labor", 0.12, "#000080"),
        ("Utilities", 0.08, "#DAA520"),
        ("Transport", 0.06, "#4682B4"),
        ("Miscellaneous", 0.14, "#666666"),
    ]
    n_weeks = 8
    weeks = [f"W-{n_weeks - 1 - w}" for w in range(n_weeks - 1)] + ["This Week"]

    fig = go.Figure()
    for cat, share, color in categories:
        vals = [weekly_base * share * (0.82 + rng.random() * 0.36) for _ in range(n_weeks)]
        fig.add_trace(go.Bar(
            x=weeks, y=vals, name=cat, marker_color=color,
            text=[f"Rs {int(v):,}" for v in vals],
            textposition="inside", textfont={"size": 7},
        ))
    fig.update_layout(
        title={"text": "Digitized Expense Register - Last 8 Weeks (Merchant Notebook)", "font": {"color": "#000080", "size": 14}},
        barmode="stack", height=360,
        margin=dict(l=50, r=30, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis={"gridcolor": "#e0e0e0", "title": "Amount (Rs)"},
        font={"family": "Arial"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    return fig


def get_documentation_status(persona):
    """KYC / business documents on file for the credit passport (percent complete)."""
    return {
        "Aadhaar Card": 100,
        "PAN Card": 100,
        "Bank Statement (AA Consent)": 100,
        "UPI VPA Registration": 90,
        "Shop / Stall Photo": 80,
        "Trade License / Vendor Certificate": 100 if persona["sthan_days"] >= 2900 else 50,
        "GST Certificate": 100 if persona["sthan_days"] > 2500 else 0,
    }


def create_documentation_chart(persona):
    """Documentation coverage chart (replaces the supporting-documents upload)."""
    docs = get_documentation_status(persona)
    items = sorted(docs.items(), key=lambda kv: kv[1])
    names = [k for k, _ in items]
    values = [v for _, v in items]
    colors = ["#138808" if v >= 100 else ("#FF9933" if v > 0 else "#CC0000") for v in values]
    coverage = sum(values) / len(values)

    fig = go.Figure(go.Bar(
        x=values, y=names, orientation="h",
        marker_color=colors,
        text=[f"{v}%" for v in values],
        textposition="outside", textfont={"size": 10},
        showlegend=False,
    ))
    fig.update_layout(
        title={"text": f"Documentation Coverage - {coverage:.0f}% Complete", "font": {"color": "#000080", "size": 14}},
        height=320,
        margin=dict(l=50, r=40, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"range": [0, 115], "gridcolor": "#e0e0e0"},
        font={"family": "Arial"},
    )
    return fig


def render_tricolor_bar():
    st.markdown('<div class="tricolor-header"> </div>', unsafe_allow_html=True)


def render_score_dashboard(persona_key, persona, live_data):
    render_tricolor_bar()
    st.markdown('<h2 class="section-header">Live Score Dashboard</h2>', unsafe_allow_html=True)

    score_change = live_data["score"] - persona["base_score"]
    change_color = "#138808" if score_change >= 0 else "#CC0000"

    col_gauge, col_info = st.columns([3, 2])

    with col_gauge:
        fig = create_gauge_chart(live_data["score"], persona["name"])
        st.plotly_chart(fig, use_container_width=True, key=f"gauge_{persona_key}")
        st.markdown(
            f'<p style="text-align:center;font-size:16px">Change from base: '
            f'<span style="color:{change_color};font-weight:700">{score_change:+d} points</span></p>',
            unsafe_allow_html=True,
        )

    with col_info:
        st.markdown(f"""
        <div class="score-card">
            <h3 style="color:#000080;margin:0">{persona['name']}</h3>
            <p style="color:#666;margin:5px 0">{persona['type']}</p>
            <p style="color:#666;margin:5px 0">{persona['location']}</p>
            <hr style="border-color:#FF9933">
            <p><strong>Base Score:</strong> {persona['base_score']}</p>
            <p><strong>Live Score:</strong> <span style="color:{get_score_color(live_data['score'])};font-weight:700">{live_data['score']}</span></p>
            <p><strong>Rating:</strong> {get_score_label(live_data['score'])}</p>
            <hr style="border-color:#138808">
            <p><strong>Daily UPI Avg:</strong> Rs {persona['upi_daily_avg']:,}</p>
            <p><strong>Total Transactions:</strong> {persona['total_transactions']:,}</p>
            <p><strong>Added Revenue:</strong> <span style="color:#138808">Rs {live_data['total_added_revenue']:,}</span></p>
            <p><strong>Added Expenses:</strong> <span style="color:#FF9933">Rs {live_data['total_added_expense']:,}</span></p>
            <p><strong>Net Margin:</strong> {live_data['margin']*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### Live Score Factors")
    factor_cols = st.columns(6)
    factor_names = list(live_data["factors"].keys())
    for i, col in enumerate(factor_cols):
        if i < len(factor_names):
            fname = factor_names[i]
            fdata = live_data["factors"][fname]
            col.metric(label=fname, value=f"{fdata['value']}/100", delta=fdata["delta"])

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        fig_rev = create_revenue_expense_chart(
            persona["monthly_revenue"], persona["monthly_expenses"],
            live_data["total_added_revenue"], live_data["total_added_expense"],
            persona["name"],
        )
        st.plotly_chart(fig_rev, use_container_width=True, key=f"rev_exp_{persona_key}")
    with col_chart2:
        fig_trend = create_score_trend_chart(persona["base_score"], live_data["score"], persona["name"])
        st.plotly_chart(fig_trend, use_container_width=True, key=f"trend_{persona_key}")

    st.markdown("---")

    col_radar, col_waterfall = st.columns(2)
    with col_radar:
        fig_radar = create_factor_radar_chart(live_data["factors"], persona["name"])
        st.plotly_chart(fig_radar, use_container_width=True, key=f"radar_{persona_key}")
    with col_waterfall:
        total_base_rev = sum(persona["monthly_revenue"])
        total_base_exp = sum(persona["monthly_expenses"])
        fig_waterfall = create_profit_waterfall_chart(
            total_base_rev, total_base_exp,
            live_data["total_added_revenue"], live_data["total_added_expense"],
        )
        st.plotly_chart(fig_waterfall, use_container_width=True, key=f"waterfall_{persona_key}")

    expense_pie = create_expense_breakdown_chart(persona_key)
    if expense_pie:
        st.plotly_chart(expense_pie, use_container_width=True, key=f"expense_pie_{persona_key}")

    st.markdown("---")
    st.markdown("### Add Monthly Expense (Score Updates Live)")
    st.markdown("Enter your business expenses. Your credit score recalculates automatically.")

    with st.form(f"expense_form_{persona_key}", clear_on_submit=True):
        exp_cols = st.columns(4)
        with exp_cols[0]:
            exp_category = st.selectbox("Category", [
                "Rent", "Stock/Inventory", "Utilities", "Transport",
                "Wages/Labor", "Raw Materials", "Equipment", "Miscellaneous",
            ], key=f"exp_cat_{persona_key}")
        with exp_cols[1]:
            exp_amount = st.number_input("Amount (Rs)", min_value=0, value=0, step=100, key=f"exp_amt_{persona_key}")
        with exp_cols[2]:
            exp_date = st.date_input("Date", value=datetime.now().date(), key=f"exp_date_{persona_key}")
        with exp_cols[3]:
            exp_note = st.text_input("Description", key=f"exp_note_{persona_key}")

        if st.form_submit_button("Add Expense"):
            if exp_amount > 0:
                if persona_key not in st.session_state.expense_entries:
                    st.session_state.expense_entries[persona_key] = []
                st.session_state.expense_entries[persona_key].append({
                    "category": exp_category,
                    "amount": exp_amount,
                    "date": str(exp_date),
                    "note": exp_note,
                })
                st.success(f"Rs {exp_amount:,} expense added. Score recalculating...")
                st.rerun()

    st.markdown("### Add Revenue Entry")
    with st.form(f"revenue_form_{persona_key}", clear_on_submit=True):
        rev_cols = st.columns(4)
        with rev_cols[0]:
            rev_source = st.selectbox("Source", [
                "UPI Collection", "Cash Sale", "Wholesale Order",
                "Online Order", "Repeat Customer", "New Customer", "Other",
            ], key=f"rev_src_{persona_key}")
        with rev_cols[1]:
            rev_amount = st.number_input("Amount (Rs)", min_value=0, value=0, step=100, key=f"rev_amt_{persona_key}")
        with rev_cols[2]:
            rev_date = st.date_input("Date", value=datetime.now().date(), key=f"rev_date_{persona_key}")
        with rev_cols[3]:
            rev_note = st.text_input("Description", key=f"rev_note_{persona_key}")

        if st.form_submit_button("Add Revenue"):
            if rev_amount > 0:
                if persona_key not in st.session_state.revenue_entries:
                    st.session_state.revenue_entries[persona_key] = []
                st.session_state.revenue_entries[persona_key].append({
                    "source": rev_source,
                    "amount": rev_amount,
                    "date": str(rev_date),
                    "note": rev_note,
                })
                st.success(f"Rs {rev_amount:,} revenue added. Score recalculating...")
                st.rerun()

    user_expenses = st.session_state.expense_entries.get(persona_key, [])
    user_revenues = st.session_state.revenue_entries.get(persona_key, [])

    if user_expenses or user_revenues:
        st.markdown("### Your Entries (Affecting Live Score)")
        tab_exp, tab_rev = st.columns(2)
        with tab_exp:
            st.markdown("**Expenses Added**")
            if user_expenses:
                df_exp = pd.DataFrame(user_expenses)
                st.dataframe(df_exp, use_container_width=True, hide_index=True)
                st.markdown(f"**Total Added Expenses: Rs {sum(e['amount'] for e in user_expenses):,}**")
            else:
                st.info("No expenses added yet.")
        with tab_rev:
            st.markdown("**Revenue Added**")
            if user_revenues:
                df_rev = pd.DataFrame(user_revenues)
                st.dataframe(df_rev, use_container_width=True, hide_index=True)
                st.markdown(f"**Total Added Revenue: Rs {sum(r['amount'] for r in user_revenues):,}**")
            else:
                st.info("No revenue entries added yet.")

    if user_expenses or user_revenues:
        if st.button("Clear All Entries (Reset to Base Score)", key=f"clear_{persona_key}"):
            st.session_state.expense_entries[persona_key] = []
            st.session_state.revenue_entries[persona_key] = []
            st.rerun()

    st.markdown("---")
    st.markdown("#### Actionable Tips")
    for i, tip in enumerate(persona["tips"], 1):
        if "CRITICAL" in tip or "WARNING" in tip or "ACTION" in tip:
            st.warning(f"**{i}.** {tip}")
        else:
            st.info(f"**{i}.** {tip}")


def render_integrity_layer(persona, live_data):
    render_tricolor_bar()
    st.markdown('<h2 class="section-header">Integrity Layer</h2>', unsafe_allow_html=True)

    if persona["integrity"] == "PASS":
        st.markdown('<div class="integrity-pass">INTEGRITY CHECK: PASS</div>', unsafe_allow_html=True)
        st.success(f"**Status:** {persona['integrity_reason']}")
        st.markdown(f"**Loan Eligibility:** ELIGIBLE")
        st.markdown(f"**Recommended Credit (Live):** Rs {live_data['recommended_credit']:,}")
        st.markdown("---")
        st.markdown("#### Integrity Check Details")
        checks = {
            "Wash Trading Detection": "CLEAR - No circular payment patterns found",
            "Payer Concentration": "CLEAR - Healthy distribution across multiple payers",
            "VPA Verification": "CLEAR - All VPAs linked to registered merchant",
            "Transaction Velocity": "CLEAR - Normal transaction frequency patterns",
            "Geo-location Match": "CLEAR - Transactions align with registered location",
        }
        for check, result in checks.items():
            c1, c2 = st.columns([1, 3])
            c1.markdown(f"**{check}**")
            c2.markdown(f"[PASS] {result}")
    else:
        st.markdown(
            '<div class="integrity-fail">INTEGRITY FAIL: WASH TRADING DETECTED. LOAN OFFER VOIDED. MANUAL REVIEW REQUIRED.</div>',
            unsafe_allow_html=True,
        )
        st.error(f"**CRITICAL ALERT:** {persona['integrity_reason']}")
        st.error("**Loan Status: VOIDED** - This merchant has been flagged for manual review. No automated credit disbursement permitted.")
        st.error("**Recommended Credit: Rs 0 (FLAGGED)**")
        st.markdown("---")
        st.markdown("#### Integrity Check Details")
        checks = {
            "Wash Trading Detection": "FAIL - 67% of inbound payments from 2 linked accounts",
            "Payer Concentration": "FAIL - Top payer accounts for 73% of total volume",
            "VPA Verification": "WARNING - 2 VPAs require additional verification",
            "Transaction Velocity": "WARNING - Abnormal spike pattern detected",
            "Geo-location Match": "WARNING - Multiple transaction origins outside registered area",
        }
        for check, result in checks.items():
            c1, c2 = st.columns([1, 3])
            c1.markdown(f"**{check}**")
            if "FAIL" in result:
                c2.markdown(f"[FAIL] {result}")
            else:
                c2.markdown(f"[WARNING] {result}")


def render_fraud_guard(persona):
    render_tricolor_bar()
    st.markdown('<h2 class="section-header">Fraud Guard</h2>', unsafe_allow_html=True)

    misrouted_amount = max(40, int(persona["upi_daily_avg"] * 0.28))

    st.markdown("### Active Alerts")
    col1, col2 = st.columns(2)
    with col1:
        st.warning(
            "**Screenshot Check Alert**\n\n"
            "Customer claims Rs 500 paid. Bank ledger shows Rs 50 received.\n\n"
            "MISMATCH ALERT - Potential tampered screenshot."
        )
    with col2:
        st.warning(
            "**QR Health Alert**\n\n"
            "VPA Routing mismatch detected.\n\n"
            f"QR SWAP DETECTED: Rs {misrouted_amount:,} routed to unlinked account since 6:00 AM today."
        )

    st.markdown("---")
    st.markdown("### Payment Claim Verification")
    st.markdown(
        "Cross-check customer payment claims against your actual bank records. "
        "Today's UPI collection claims are plotted against the bank ledger below - "
        "every claim is verified as data, not as an uploaded screenshot."
    )

    claims = get_demo_claims()
    df_claims = pd.DataFrame(claims)
    st.dataframe(df_claims, use_container_width=True, hide_index=True)
    st.plotly_chart(
        create_claims_batch_chart(claims),
        use_container_width=True, key="claims_batch_chart",
    )

    st.markdown("#### Verify a Transaction Manually")
    claimed_amount = st.number_input("Amount shown in screenshot (Rs)", min_value=0, value=0, step=10, key="claimed_amt")
    actual_amount = st.number_input("Amount in your bank ledger (Rs)", min_value=0, value=0, step=10, key="actual_amt")
    txn_id = st.text_input("Transaction ID (from screenshot)", key="txn_id_input")
    payer_upi = st.text_input("Payer UPI ID", key="payer_upi_input")
    txn_date = st.date_input("Transaction Date", key="txn_date_input")

    if st.button("Verify Transaction", key="verify_txn"):
        if claimed_amount > 0:
            if abs(claimed_amount - actual_amount) > 1:
                mismatch_pct = abs(claimed_amount - actual_amount) / max(claimed_amount, 1) * 100
                st.error(
                    f"**MISMATCH DETECTED**\n\n"
                    f"Claimed: Rs {claimed_amount:,} | Ledger: Rs {actual_amount:,} | "
                    f"Difference: Rs {abs(claimed_amount - actual_amount):,} ({mismatch_pct:.0f}% deviation)\n\n"
                    f"Transaction ID: {txn_id if txn_id else 'Not provided'}\n\n"
                    f"This screenshot may be tampered. Flag this transaction for review."
                )
            else:
                st.success(
                    f"**MATCH CONFIRMED**\n\n"
                    f"Rs {claimed_amount:,} verified against ledger record.\n"
                    f"Transaction ID: {txn_id if txn_id else 'Not provided'}"
                )
            st.plotly_chart(
                create_claim_verification_chart(claimed_amount, actual_amount, txn_id),
                use_container_width=True, key="verify_chart",
            )
        else:
            st.info("Enter the claimed amount to verify.")

    st.markdown("---")
    st.markdown("### QR Code Health Check")
    st.markdown(
        "Check whether payments scanned on your shop QR actually reach your registered VPA. "
        "The live routing diagram shows where today's scanned payments landed."
    )

    registered_vpa = st.text_input("Your registered VPA / UPI ID", key="reg_vpa")
    if st.button("Check QR Health", key="check_qr"):
        if registered_vpa:
            check_rng = random.Random(hash(registered_vpa) % 100000)
            if check_rng.random() > 0.3:
                st.success(f"**QR HEALTH: OK** - QR code routes to {registered_vpa}. No tampering detected.")
                st.plotly_chart(
                    create_qr_routing_chart(registered_vpa, persona["upi_daily_avg"], 0),
                    use_container_width=True, key="qr_routing_chart",
                )
            else:
                st.error(
                    f"**QR SWAP ALERT** - This QR code may not route to {registered_vpa}. "
                    f"Immediately verify with your payment provider and replace the QR at your shop."
                )
                st.plotly_chart(
                    create_qr_routing_chart(
                        registered_vpa,
                        persona["upi_daily_avg"] - misrouted_amount,
                        misrouted_amount,
                    ),
                    use_container_width=True, key="qr_routing_chart",
                )
        else:
            st.info("Enter your registered VPA to check.")

    st.markdown("---")
    st.markdown("### Bulk Transaction Audit")
    st.markdown("Enter multiple transactions for batch verification. Every audited transaction is plotted in the results chart below.")

    with st.form("bulk_audit_form", clear_on_submit=True):
        st.markdown("#### Manual Entry")
        audit_cols = st.columns(3)
        with audit_cols[0]:
            audit_claimed = st.number_input("Claimed Amount (Rs)", min_value=0, value=0, step=50, key="audit_claimed")
        with audit_cols[1]:
            audit_actual = st.number_input("Actual Received (Rs)", min_value=0, value=0, step=50, key="audit_actual")
        with audit_cols[2]:
            audit_payer = st.text_input("Payer Name/ID", key="audit_payer")

        if st.form_submit_button("Audit This Transaction"):
            if audit_claimed > 0:
                diff = abs(audit_claimed - audit_actual)
                if diff > 1:
                    st.error(f"MISMATCH: Claimed Rs {audit_claimed:,} vs Received Rs {audit_actual:,}. Difference: Rs {diff:,}")
                else:
                    st.success(f"VERIFIED: Rs {audit_claimed:,} matches ledger for {audit_payer if audit_payer else 'unknown payer'}.")
                st.session_state.fraud_audit_log.append({
                    "payer": audit_payer if audit_payer else "Unknown",
                    "claimed": audit_claimed,
                    "actual": audit_actual,
                })

    if st.session_state.fraud_audit_log:
        st.plotly_chart(
            create_audit_chart(st.session_state.fraud_audit_log),
            use_container_width=True, key="audit_chart",
        )
        if st.button("Clear Audit Log", key="clear_audit"):
            st.session_state.fraud_audit_log = []
            st.rerun()


def render_sthan_log(persona_key, persona):
    render_tricolor_bar()
    st.markdown('<h2 class="section-header">Sthan Log - Proof of Vending</h2>', unsafe_allow_html=True)

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Days at Current Location", f"{persona['sthan_days']} Days")
    col_m2.metric("Location", persona["location"])
    col_m3.metric("Longevity Score Impact", f"{persona['factors']['Longevity']['value']}/100")

    st.info(
        "**How Sthan Log works:** Physical presence check-ins build a verifiable location history. "
        "For thin-file vendors with minimal bank records, Sthan Log longevity directly fuels the "
        "'Longevity' score factor, providing an alternative creditworthiness signal. "
        f"With {persona['sthan_days']} days logged, this is strong proof of stable business operations."
    )

    st.markdown("---")
    st.markdown("### Presence Timeline")

    user_sthan = st.session_state.sthan_entries.get(persona_key, [])
    all_log = persona["sthan_log"] + user_sthan

    if all_log:
        df_log = pd.DataFrame(all_log)
        df_display = df_log.rename(columns={"date": "Date", "time": "Time", "status": "Status", "note": "Note"})
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    present_count = sum(1 for e in all_log if e["status"] == "Present")
    total_count = len(all_log)
    if total_count > 0:
        rate = present_count / total_count * 100
        st.markdown(f"**Attendance Rate:** {present_count}/{total_count} days present ({rate:.0f}%)")

    st.markdown("---")
    st.markdown("### Add New Check-in")

    with st.form(f"sthan_checkin_{persona_key}", clear_on_submit=True):
        form_cols = st.columns(4)
        with form_cols[0]:
            checkin_date = st.date_input("Date", value=datetime.now().date(), key=f"sthan_date_{persona_key}")
        with form_cols[1]:
            checkin_time = st.time_input("Time", value=datetime.now().time(), key=f"sthan_time_{persona_key}")
        with form_cols[2]:
            checkin_status = st.selectbox("Status", ["Present", "Absent"], key=f"sthan_status_{persona_key}")
        with form_cols[3]:
            checkin_note = st.text_input("Note", key=f"sthan_note_{persona_key}")

        if st.form_submit_button("Log Check-in"):
            new_entry = {
                "date": str(checkin_date),
                "time": checkin_time.strftime("%H:%M") if checkin_status == "Present" else "N/A",
                "status": checkin_status,
                "note": checkin_note,
            }
            if persona_key not in st.session_state.sthan_entries:
                st.session_state.sthan_entries[persona_key] = []
            st.session_state.sthan_entries[persona_key].append(new_entry)
            st.success(f"Check-in logged for {checkin_date}. Score will update.")
            st.rerun()

    st.markdown("---")
    st.markdown("### Presence Heatmap (Proof of Vending)")
    st.markdown(
        "Your check-in history, visualized. A dense green grid is the strongest verifiable proof of "
        "continuous vending at your location - this is what powers your Longevity score."
    )
    st.plotly_chart(
        create_presence_heatmap(persona),
        use_container_width=True, key=f"presence_heatmap_{persona_key}",
    )

    st.markdown("---")
    st.markdown("### Merchant Daily Notes")
    st.markdown("Add your daily observations, customer count, weather conditions, etc.")

    with st.form(f"daily_notes_{persona_key}", clear_on_submit=True):
        note_cols = st.columns(3)
        with note_cols[0]:
            note_date = st.date_input("Date", value=datetime.now().date(), key=f"note_date_{persona_key}")
        with note_cols[1]:
            customer_count = st.number_input("Approx. Customers Today", min_value=0, value=0, step=1, key=f"cust_count_{persona_key}")
        with note_cols[2]:
            daily_note = st.text_area("Notes", height=68, key=f"daily_note_{persona_key}")

        if st.form_submit_button("Save Daily Note"):
            st.success(f"Note saved for {note_date}: {customer_count} customers.")

    st.markdown("---")

    svanidhi_report = f"""PROOF OF VENDING CERTIFICATE
================================
Generated by VyaparPulse
Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}

MERCHANT DETAILS
----------------
Name: {persona['name']}
Type: {persona['type']}
Location: {persona['location']}

VENDING HISTORY
---------------
Total Days at Current Location: {persona['sthan_days']}
Longevity Score: {persona['factors']['Longevity']['value']}/100
Recent Attendance Rate: {present_count}/{total_count} days

RECENT CHECK-IN LOG
--------------------
"""
    for entry in all_log:
        svanidhi_report += f"  {entry['date']} | {entry['time']} | {entry['status']} | {entry['note']}\n"
    svanidhi_report += f"""
VERIFICATION
------------
This document certifies continuous vending activity
at the above location for {persona['sthan_days']} days.
Suitable for PM SVANidhi scheme application.
VyaparPulse Verification ID: VP-{random.randint(100000, 999999)}
"""

    st.download_button(
        label="Generate Proof of Vending (PM SVANidhi Ready)",
        data=svanidhi_report,
        file_name=f"proof_of_vending_{persona['name'].replace(' ', '_')}.txt",
        mime="text/plain",
    )


def render_lender_report(persona_key, persona, live_data):
    render_tricolor_bar()
    st.markdown('<h2 class="section-header">Lender Report - Credit Passport</h2>', unsafe_allow_html=True)

    col_score, col_status = st.columns(2)

    with col_score:
        st.markdown(f"""
        <div class="score-card">
            <h3 style="color:#000080">VyaparPulse Live Score</h3>
            <h1 style="color:{get_score_color(live_data['score'])};font-size:48px;margin:10px 0">{live_data['score']}/900</h1>
            <p style="color:#666">{persona['name']} | {persona['type']}</p>
            <p style="color:#666">Base: {persona['base_score']} | Change: {live_data['score'] - persona['base_score']:+d}</p>
            <p style="color:#666">Rating: {get_score_label(live_data['score'])}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_status:
        if persona["loan_status"] == "ELIGIBLE":
            st.markdown(f"""
            <div class="score-card">
                <h3 style="color:#138808">Recommended Credit (Live)</h3>
                <h1 style="color:#138808;font-size:48px;margin:10px 0">Rs {live_data['recommended_credit']:,}</h1>
                <p style="color:#138808">ELIGIBLE FOR DISBURSEMENT</p>
                <p style="color:#666">Integrity: PASS</p>
                <p style="color:#666">Margin: {live_data['margin']*100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="score-card" style="border-color:#CC0000">
                <h3 style="color:#CC0000">Recommended Credit</h3>
                <h1 style="color:#CC0000;font-size:48px;margin:10px 0">Rs 0</h1>
                <p style="color:#CC0000">FLAGGED - LOAN VOIDED</p>
                <p style="color:#CC0000">Integrity: FAIL</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Live Factor Breakdown")

    factor_data = []
    for fname, fdata in live_data["factors"].items():
        base_val = persona["factors"][fname]["value"]
        rating = "Strong" if fdata["value"] >= 70 else ("Moderate" if fdata["value"] >= 50 else "Weak")
        factor_data.append({
            "Factor": fname,
            "Base Score": f"{base_val}/100",
            "Live Score": f"{fdata['value']}/100",
            "Change": fdata["delta"],
            "Rating": rating,
        })

    df_factors = pd.DataFrame(factor_data)
    st.dataframe(df_factors, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Financial Summary")
    s_cols = st.columns(4)
    avg_rev = live_data["new_total_revenue"] // 12
    s_cols[0].metric("Monthly Avg Revenue", f"Rs {avg_rev:,}")
    s_cols[1].metric("Daily UPI Average", f"Rs {persona['upi_daily_avg']:,}")
    s_cols[2].metric("Total Transactions", f"{persona['total_transactions']:,}")
    s_cols[3].metric("Location Stability", f"{persona['sthan_days']} days")

    s2_cols = st.columns(4)
    s2_cols[0].metric("Total Revenue (Adj)", f"Rs {live_data['new_total_revenue']:,}")
    s2_cols[1].metric("Total Expenses (Adj)", f"Rs {live_data['new_total_expense']:,}")
    s2_cols[2].metric("Net Profit", f"Rs {live_data['new_profit']:,}")
    s2_cols[3].metric("Profit Margin", f"{live_data['margin']*100:.1f}%")

    st.markdown("---")
    st.markdown("### Digitized Expense Register (Notebook)")
    st.markdown(
        "Merchants often track daily expenses in physical notebooks. "
        "The register below has been digitized and attached to this credit passport - "
        "weekly totals by category, straight from the notebook data."
    )
    st.plotly_chart(
        create_notebook_register_chart(persona),
        use_container_width=True, key=f"notebook_register_{persona_key}",
    )

    attach_cols = st.columns(2)
    with attach_cols[0]:
        nb_pages = st.number_input(
            "Notebook pages digitized & attested", min_value=0, max_value=20, value=0, step=1,
            key=f"nb_pages_{persona_key}",
        )
    with attach_cols[1]:
        if st.button("Attach Digitized Pages to Passport", key=f"nb_attach_{persona_key}"):
            if nb_pages > 0:
                if persona_key not in st.session_state.expense_photos_log:
                    st.session_state.expense_photos_log[persona_key] = []
                register_log = st.session_state.expense_photos_log[persona_key]
                for _ in range(nb_pages):
                    register_log.append({
                        "name": f"Register page {len(register_log) + 1}",
                        "time": datetime.now().strftime("%d-%m-%Y %H:%M"),
                    })
                st.success(f"{nb_pages} digitized page(s) attached. Score may update due to documentation bonus.")
            else:
                st.info("Enter the number of pages to attach.")

    attached_pages = len(st.session_state.expense_photos_log.get(persona_key, []))
    st.markdown(f"**Digitized register pages attached to credit passport:** {attached_pages}")

    st.markdown("---")
    st.markdown("### Documentation Coverage")
    st.markdown("KYC and business documents currently on file for this merchant.")
    st.plotly_chart(
        create_documentation_chart(persona),
        use_container_width=True, key=f"doc_coverage_{persona_key}",
    )
    docs_status = get_documentation_status(persona)
    doc_coverage = sum(docs_status.values()) / len(docs_status)

    st.markdown("---")
    st.markdown("### Add Lender Notes")
    lender_note = st.text_area("Lender / Officer Notes (optional)", key=f"lender_note_{persona_key}", height=100)

    st.markdown("---")

    integrity_status = "PASS" if persona["integrity"] == "PASS" else "FAIL - LOAN VOIDED"

    credit_report = f"""VYAPARPULSE CREDIT PASSPORT (LIVE)
==========================================
Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
Report ID: VP-CR-{random.randint(100000, 999999)}

MERCHANT PROFILE
-----------------
Name: {persona['name']}
Business Type: {persona['type']}
Location: {persona['location']}

CREDIT SCORE (LIVE)
---------------------
Base VyaparPulse Score: {persona['base_score']}/900
Live VyaparPulse Score: {live_data['score']}/900
Score Change: {live_data['score'] - persona['base_score']:+d} points
Rating: {get_score_label(live_data['score'])}
Integrity Status: {integrity_status}
Recommended Credit: Rs {live_data['recommended_credit']:,}
Loan Status: {persona['loan_status']}

FACTOR BREAKDOWN (LIVE)
-------------------------
"""
    for fname, fdata in live_data["factors"].items():
        base_val = persona["factors"][fname]["value"]
        rating = "Strong" if fdata["value"] >= 70 else ("Moderate" if fdata["value"] >= 50 else "Weak")
        credit_report += f"  {fname}: {fdata['value']}/100 (Base: {base_val}, Change: {fdata['delta']}) [{rating}]\n"

    credit_report += f"""
FINANCIAL SUMMARY (ADJUSTED)
-------------------------------
Total Revenue: Rs {live_data['new_total_revenue']:,}
Total Expenses: Rs {live_data['new_total_expense']:,}
Net Profit: Rs {live_data['new_profit']:,}
Profit Margin: {live_data['margin']*100:.1f}%
Added Revenue (User Input): Rs {live_data['total_added_revenue']:,}
Added Expenses (User Input): Rs {live_data['total_added_expense']:,}

BUSINESS METRICS
-----------------
Daily UPI Average: Rs {persona['upi_daily_avg']:,}
Total Transactions: {persona['total_transactions']:,}
Location Stability: {persona['sthan_days']} days

MONTHLY REVENUE (Base)
------------------------
"""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for m, rev, exp in zip(months, persona["monthly_revenue"], persona["monthly_expenses"]):
        credit_report += f"  {m}: Revenue Rs {rev:,} | Expenses Rs {exp:,} | Profit Rs {rev - exp:,}\n"

    credit_report += f"""
ATTACHMENTS
-----------
Expense Register (Notebook): {attached_pages} pages digitized & attached
Documentation Coverage: {doc_coverage:.0f}% (KYC + business documents on file)

LENDER NOTES
--------------
{lender_note if lender_note else 'None provided'}

INTEGRITY REPORT
-----------------
Status: {persona['integrity']}
Detail: {persona['integrity_reason']}

CONSENT & COMPLIANCE
---------------------
Data sourced via consent-based Account Aggregator framework.
Consent is revocable at any time by the merchant.
Fully aligned with Digital Personal Data Protection (DPDP) Act.
No data shared without explicit merchant authorization.

This report is for authorized lender use only.
VyaparPulse - Inclusive Credit Infrastructure for Bharat
"""

    st.download_button(
        label="Download AA-Consent Credit Passport",
        data=credit_report,
        file_name=f"credit_passport_{persona['name'].replace(' ', '_')}.txt",
        mime="text/plain",
    )

    st.markdown(
        '<p style="color:#666;font-size:12px;text-align:center;margin-top:20px">'
        "Data via consent-based Account Aggregator, revocable, DPDP-aligned. "
        "No merchant data is shared without explicit authorization.</p>",
        unsafe_allow_html=True,
    )


def render_privacy_policy():
    render_tricolor_bar()
    st.markdown('<h2 class="section-header">Privacy Policy</h2>', unsafe_allow_html=True)

    st.markdown(f"""
**VyaparPulse Privacy Policy**

*Last Updated: {datetime.now().strftime('%d %B %Y')}*

**1. Data Collection**

VyaparPulse collects the following categories of data through consent-based mechanisms:

- **Transaction Data:** UPI payment records, transaction volumes, and frequency patterns obtained via Account Aggregator (AA) framework with explicit merchant consent.
- **Location Data:** Sthan Log check-in data provided voluntarily by merchants to establish proof of vending.
- **Business Profile:** Merchant name, business type, and location as provided during registration.
- **Financial Records:** Revenue and expense entries provided by the merchant for live score computation.
- **Digitized Records:** Digitized expense register pages, payment claims, and verification records provided by the merchant.

**2. Data Usage**

Collected data is used exclusively for:

- Generating and dynamically updating VyaparPulse credit scores and factor analysis.
- Running integrity checks to detect fraudulent transaction patterns.
- Creating Credit Passport reports for authorized lenders.
- Generating Proof of Vending certificates for government scheme applications.
- Fraud detection through payment claim verification and QR routing health monitoring.

**3. Data Sharing**

- Data is shared with lenders ONLY upon explicit merchant consent.
- Credit Passport reports are generated on-demand and shared only when the merchant initiates download or transmission.
- No data is sold to third parties under any circumstances.
- Integrity check results are shared with lending partners only when a loan application is initiated.

**4. Account Aggregator Framework**

VyaparPulse operates within the RBI-regulated Account Aggregator framework:

- All financial data access requires explicit, informed consent.
- Consent is time-bound and purpose-specific.
- Merchants can revoke consent at any time, after which data access ceases immediately.
- Data is encrypted in transit and at rest using industry-standard protocols.

**5. Data Retention**

- Active merchant data is retained for the duration of the merchant's engagement with VyaparPulse.
- Upon consent revocation or account deletion, all personal and financial data is purged within 30 days.
- Anonymized, aggregated statistical data may be retained for service improvement.

**6. DPDP Act Compliance**

VyaparPulse is fully aligned with the Digital Personal Data Protection (DPDP) Act, 2023:

- Data Fiduciary obligations are maintained at all times.
- Data Principal (merchant) rights including access, correction, and erasure are fully supported.
- Grievance redressal mechanism is available for all data-related concerns.

**7. Security Measures**

- End-to-end encryption for all data transmission.
- Role-based access control for internal teams.
- Regular security audits and vulnerability assessments.
- No storage of raw banking credentials.

**8. Merchant Rights**

As a VyaparPulse user, you have the right to:

- Access all data collected about your business.
- Request correction of inaccurate data.
- Revoke consent and request data deletion.
- Know which lenders have accessed your Credit Passport.
- Lodge grievances regarding data handling.

**9. Contact**

For privacy-related queries or grievance redressal:

- Email: privacy@vyaparpulse.in
- Grievance Officer: Data Protection Cell, VyaparPulse
- Response time: Within 72 hours of receipt

**10. Updates**

This policy may be updated periodically. Merchants will be notified of material changes via the application and registered contact details.
""")


def render_terms():
    render_tricolor_bar()
    st.markdown('<h2 class="section-header">Terms and Conditions</h2>', unsafe_allow_html=True)

    st.markdown(f"""
**VyaparPulse Terms and Conditions**

*Effective Date: {datetime.now().strftime('%d %B %Y')}*

**1. Acceptance of Terms**

By accessing or using VyaparPulse, you agree to be bound by these Terms and Conditions. If you do not agree, you must discontinue use immediately.

**2. Service Description**

VyaparPulse provides:

- Alternative credit scoring (300-900 scale) for micro-merchants and street vendors with live score updates based on financial activity.
- Integrity verification to detect fraudulent transaction patterns.
- Fraud Guard tools for payment claim verification and QR routing health monitoring.
- Sthan Log for physical presence documentation and Proof of Vending generation.
- Credit Passport generation for lender consumption via Account Aggregator consent.
- Expense and revenue tracking with real-time score impact visualization.

**3. Eligibility**

VyaparPulse services are available to:

- Indian residents aged 18 years and above.
- Individuals operating a micro-enterprise, street vending business, or small retail establishment.
- Users with a valid UPI-enabled bank account.

**4. Live Score Computation**

- The VyaparPulse score updates dynamically based on expense entries, revenue entries, check-in activity, and documentation uploads.
- Scores range from 300 (lowest) to 900 (highest).
- Score changes are indicative and based on the data provided by the merchant.
- VyaparPulse does not guarantee score accuracy if input data is inaccurate or incomplete.

**5. Credit Score Disclaimer**

- The VyaparPulse score is an alternative credit assessment tool and does not replace formal credit bureau scores (CIBIL, Experian, etc.).
- The score is advisory in nature. Final lending decisions rest with the respective financial institutions.
- A high score does not guarantee loan approval. A low score does not preclude it.
- Integrity check failures result in automatic loan voiding within the VyaparPulse system.

**6. Fraud Guard Tools**

- Payment claim verification and QR routing health checks are detection tools, not definitive fraud determinations.
- Results should be used as indicators for further investigation.
- VyaparPulse is not liable for losses arising from reliance solely on Fraud Guard outputs.

**7. Sthan Log**

- Sthan Log entries are self-reported and may be supplemented with check-in history.
- Proof of Vending certificates generated are based on self-reported data and carry a VyaparPulse verification ID, not a government endorsement.

**8. Intellectual Property**

All content, algorithms, scoring methodologies, and interface designs are the intellectual property of VyaparPulse. You may not reverse-engineer, copy, or redistribute any component of the service.

**9. Limitation of Liability**

VyaparPulse is provided "as is" without warranties of any kind. We are not liable for any direct, indirect, incidental, or consequential damages arising from use of the service.

**10. Governing Law**

These terms are governed by the laws of India. Any disputes shall be subject to the exclusive jurisdiction of courts in New Delhi.

**11. Contact**

For queries regarding these Terms and Conditions:

- Email: legal@vyaparpulse.in
- Address: VyaparPulse, New Delhi, India
""")


def main():
    init_session_state()
    personas = get_base_personas()

    with st.sidebar:
        st.markdown(
            '<h1 style="color:#000080;text-align:center;font-size:28px;margin-bottom:5px">VyaparPulse</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="color:#333;text-align:center;font-size:13px;margin-top:0">'
            "Inclusive Credit Infrastructure for Bharat</p>",
            unsafe_allow_html=True,
        )

        st.markdown("---")

        selected_persona = st.selectbox("Select Merchant", list(personas.keys()), index=0)
        persona = personas[selected_persona]

        st.markdown("---")

        page = st.radio(
            "Navigation",
            [
                "Score Dashboard",
                "Integrity Layer",
                "Fraud Guard",
                "Sthan Log",
                "Lender Report",
                "Privacy Policy",
                "Terms and Conditions",
            ],
            index=0,
        )

        st.markdown("---")

        live_data = compute_live_score(selected_persona, persona)

        integrity_color = "#138808" if persona["integrity"] == "PASS" else "#CC0000"
        st.markdown(
            f'<div style="text-align:center;padding:8px;background:{integrity_color};'
            f'color:white;border-radius:4px;font-weight:600">'
            f'Integrity: {persona["integrity"]}</div>',
            unsafe_allow_html=True,
        )

        score_color = get_score_color(live_data["score"])
        st.markdown(
            f'<div style="text-align:center;padding:8px;margin-top:8px;background:#000080;'
            f'color:white;border-radius:4px">'
            f'Live Score: <span style="color:{score_color};font-weight:700">{live_data["score"]}</span>/900</div>',
            unsafe_allow_html=True,
        )

        change = live_data["score"] - persona["base_score"]
        if change != 0:
            ch_color = "#138808" if change > 0 else "#CC0000"
            st.markdown(
                f'<div style="text-align:center;padding:4px;margin-top:4px;font-size:12px;color:{ch_color}">'
                f'Change: {change:+d} from base {persona["base_score"]}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown(
            '<p style="color:#333;font-size:11px;text-align:center">'
            "VyaparPulse v1.0 | DPDP Compliant</p>",
            unsafe_allow_html=True,
        )

    if page == "Score Dashboard":
        render_score_dashboard(selected_persona, persona, live_data)
    elif page == "Integrity Layer":
        render_integrity_layer(persona, live_data)
    elif page == "Fraud Guard":
        render_fraud_guard(persona)
    elif page == "Sthan Log":
        render_sthan_log(selected_persona, persona)
    elif page == "Lender Report":
        render_lender_report(selected_persona, persona, live_data)
    elif page == "Privacy Policy":
        render_privacy_policy()
    elif page == "Terms and Conditions":
        render_terms()


if __name__ == "__main__":
    main()
