"""VyaparScore — single-file, offline Streamlit hackathon demonstration.

Run with: streamlit run main.py --server.address 0.0.0.0
Dependencies: streamlit, pandas, numpy, plotly (see requirements.txt).
Navigation lives in the sidebar as a five-tab menu; only the selected tab is rendered.
No uploaded document is parsed, retained on disk, or sent to an external API.
"""

import time
from datetime import datetime
from html import escape

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="VyaparScore | Credit & Fraud Guard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

GST_REFERENCE = 4_000_000
PROFILES = {
    "Ramesh Tea Stall": {
        "owner": "Ramesh Kumar", "city": "Bengaluru, Karnataka",
        "business": "Street-food vendor", "income": 85_000, "customers": 324,
        "base_score": 738, "loan_cap": 75_000, "seed": 21,
        "expenses": [12_000, 3_500, 36_000], "vendor": True,
        "cash": 8_500, "inventory_due": 43_000,
    },
    "Sharma Kirana": {
        "owner": "Anita Sharma", "city": "Mysuru, Karnataka",
        "business": "Neighbourhood grocery", "income": 325_000, "customers": 910,
        "base_score": 804, "loan_cap": 250_000, "seed": 42,
        "expenses": [25_000, 9_000, 219_000], "vendor": False,
        "cash": 65_000, "inventory_due": 150_000,
    },
    "Suspicious Merchant": {
        "owner": "Demo Risk Account", "city": "Bengaluru, Karnataka",
        "business": "Unverified retail account", "income": 210_000,
        "customers": 76, "base_score": 438, "loan_cap": 15_000, "seed": 63,
        "expenses": [18_000, 6_000, 174_000], "vendor": False,
        "cash": 3_000, "inventory_due": 115_000,
    },
}
# Sidebar tab order matches COPY[*]["tabs"]; icons are shared across languages.
TAB_ICONS = ["📊", "📈", "📒", "🛡️", "💳"]
COPY = {
    "English": {
        "title": "Bharat's Micro-Merchant Credit & Fraud Guard",
        "tabs": ["Overview & Credit Health", "Seasonality & Cash Flow",
                 "Bahi-Khata OCR", "Fraud Guard", "Micro-Loan & Bank Report"],
        "tab_hints": [
            "Credit score, GST safety meter and scheme match.",
            "12-month revenue rhythm and the 14-day cash outlook.",
            "Scan the register, edit expenses, watch profit update.",
            "Fake screenshot check and synthetic UPI review events.",
            "EMI calculator, demo approval and bank-ready summary.",
        ],
        "nav": "Workspace tabs", "nav_hint": "Use ↑ ↓ arrow keys to switch tabs.",
        "previous": "← Previous", "next": "Next →",
        "profile": "Merchant profile", "health": "Your business, in one clear picture",
        "revenue": "Monthly UPI Revenue", "profit": "Net Profit",
        "customers": "Active Customers", "limit": "Max Loan Limit",
        "gst": "GST Tax Safety Meter", "scheme": "Government Scheme Finder",
        "season": "Understand your seasonal rhythm", "ocr": "Turn your bahi-khata into insights",
        "fraud": "Protect every payment", "loan": "Your next step toward growth",
    },
    "हिंदी": {
        "title": "भारत के छोटे व्यापारियों का क्रेडिट और धोखाधड़ी सुरक्षा साथी",
        "tabs": ["व्यापार और क्रेडिट स्वास्थ्य", "मौसमी आय और नकदी प्रवाह",
                 "बही-खाता OCR", "धोखाधड़ी सुरक्षा", "सूक्ष्म ऋण और बैंक रिपोर्ट"],
        "tab_hints": [
            "क्रेडिट स्कोर, GST सुरक्षा मीटर और योजना मिलान।",
            "12 महीने की आय और 14-दिन का नकदी अनुमान।",
            "बही-खाता स्कैन करें, खर्च बदलें, लाभ देखें।",
            "नकली स्क्रीनशॉट जाँच और UPI समीक्षा संकेत।",
            "EMI कैलकुलेटर, डेमो स्वीकृति और बैंक रिपोर्ट।",
        ],
        "nav": "कार्यस्थल टैब", "nav_hint": "↑ ↓ तीर कुंजियों से टैब बदलें।",
        "previous": "← पिछला", "next": "अगला →",
        "profile": "व्यापारी प्रोफ़ाइल", "health": "आपके व्यापार की स्पष्ट तस्वीर",
        "revenue": "मासिक UPI आय", "profit": "शुद्ध लाभ",
        "customers": "सक्रिय ग्राहक", "limit": "अधिकतम ऋण सीमा",
        "gst": "GST कर सुरक्षा मीटर", "scheme": "सरकारी योजना खोजें",
        "season": "अपनी मौसमी आय को समझें", "ocr": "बही-खाते से व्यापार की जानकारी",
        "fraud": "हर भुगतान की सुरक्षा", "loan": "व्यापार की तरक्की का अगला कदम",
    },
}

# Explicit foreground/background pairs prevent browser dark-mode defaults from
# leaving white text on the light canvas (or dark text in the sidebar).
st.markdown("""
<style>
:root {color-scheme: light;}
.stApp {
    --text-color: #16352c;
    --background-color: #f5f8fa;
    --secondary-background-color: #ffffff;
    --primary-color: #087f5b;
    background: #f5f8fa; color: #16352c;
}
.block-container {max-width: 1400px; padding-top: 2rem; padding-bottom: 3rem;}
[data-testid="stHeader"] {background: #f5f8fa; color: #16352c;}
[data-testid="stMain"] {color: #16352c;}
h1, h2, h3, h4 {color: #12372e !important; letter-spacing: -.025em;}
[data-testid="stMain"] [data-testid="stMarkdownContainer"],
[data-testid="stMain"] [data-testid="stWidgetLabel"],
[data-testid="stMain"] [data-testid="stWidgetLabel"] p {color: #16352c;}
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {color: #52675f !important;}
[data-testid="stSidebar"] {background: #102e29; color: #e6f5ee;}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color: #e6f5ee !important;}
[data-testid="stSidebar"] hr {border-color: #35594e;}
[data-testid="stSidebar"] [data-testid="stRadio"] label {padding: 7px 4px;}
/* Navigation uses real radio controls, with persistent active and focus states. */
.st-key-section_nav [role="radiogroup"] {gap: 7px;}
.st-key-section_nav [role="radiogroup"] > div {width: 100%;}
.st-key-section_nav [role="radiogroup"] label {
    width: 100%; box-sizing: border-box; margin: 0;
    padding: 12px 10px !important; border-radius: 10px;
    background: #173d34; border: 1px solid #3c6557; cursor: pointer;
}
.st-key-section_nav [role="radiogroup"] label:hover {background: #245444;}
.st-key-section_nav [role="radiogroup"] label p {white-space: normal; line-height: 1.35;}
.st-key-section_nav [role="radiogroup"] label:has(input:checked) {
    background: #d1fae5; border-color: #6ee7b7; box-shadow: inset 4px 0 0 #059669;
}
[data-testid="stSidebar"] .st-key-section_nav label:has(input:checked) p {
    color: #064e3b !important; font-weight: 700;
}
.st-key-section_nav label:focus-within {outline: 3px solid #6ee7b7; outline-offset: 2px;}
/* Menus live in a portal outside the sidebar: style both trigger and menu. */
[data-testid="stSelectbox"] div:has(> input[role="combobox"]),
[data-testid="stSelectbox"] input[role="combobox"],
[data-baseweb="select"] > div,
[data-baseweb="input"], [data-baseweb="base-input"],
[data-baseweb="textarea"] {background: #ffffff !important; color: #16352c !important; border-color: #94b4a5 !important;}
[data-baseweb="select"] span, [data-baseweb="select"] input,
[data-testid="stSelectbox"] button,
[data-baseweb="select"] svg {color: #16352c !important; -webkit-text-fill-color: #16352c;}
[data-testid="stSelectboxVirtualDropdown"],
[data-testid="stSelectboxVirtualDropdown"] [role="option"],
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [role="option"] {background: #ffffff !important; color: #16352c !important;}
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-focused],
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-hovered],
[data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"],
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"][aria-selected="true"] {background: #d1fae5 !important; color: #064e3b !important;}
input, textarea {color: #16352c !important; caret-color: #087f5b;}
input::placeholder, textarea::placeholder {color: #52675f !important; opacity: 1;}
[data-testid="stMetric"] {background: #ffffff; padding: 22px 18px;
    border: 1px solid #dce8e2; border-radius: 16px; min-height: 140px;
    box-shadow: 0 5px 20px rgba(16,46,41,.035);}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {color: #52675f !important;}
[data-testid="stMetricValue"] {color: #087f5b !important; font-size: 1.85rem;}
[data-testid="stMetricDelta"] {color: #365b4d !important;}
.stButton > button, .stDownloadButton > button,
[data-testid="stFileUploader"] button {
    background: #ffffff !important; color: #075d43 !important;
    border-radius: 10px; border: 1px solid #7aa48f !important; font-weight: 600;
}
.stButton > button p, .stDownloadButton > button p,
[data-testid="stFileUploader"] button p {color: inherit !important;}
.stButton > button:hover, .stDownloadButton > button:hover,
[data-testid="stFileUploader"] button:hover {background: #e4f5ed !important; color: #064e3b !important;}
.stButton > button[kind="primary"] {background: #087f5b !important; color: #ffffff !important; border-color: #087f5b !important;}
.stButton > button[kind="primary"]:hover {background: #065f46 !important; color: #ffffff !important;}
.stButton > button:disabled {background: #e2e8e5 !important; color: #53665d !important; border-color: #bdcbc3 !important; opacity: 1;}
button:focus-visible, a:focus-visible {outline: 3px solid #0d966b !important; outline-offset: 3px;}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"] button {background: #d1fae5 !important; color: #064e3b !important;}
[data-testid="stFileUploaderDropzone"] {background: #ffffff !important; border: 1px dashed #7aa48f; color: #16352c !important;}
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small {color: #365b4d !important;}
[data-testid="stExpander"] details {background: #ffffff; color: #16352c; border-color: #b8cec2;}
[data-testid="stExpander"] summary {background: #edf5f0; color: #16352c !important;}
[data-testid="stSliderTickBar"], [data-testid="stSliderThumbValue"],
[data-testid="stSlider"] [data-testid="stTickBar"],
[data-testid="stSlider"] [data-testid="stThumbValue"] {color: #075d43 !important;}
[data-baseweb="slider"] [role="slider"] {background: #087f5b !important;}
[data-testid="stAlert"] {border: 1px solid #b8cec2; border-radius: 12px;}
[data-testid="stAlert"] [data-baseweb="notification"] {background: #edf5f0 !important; color: #16352c !important;}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]),
[data-testid="stAlert"] [data-testid="stAlertContentInfo"] {background: #eff6ff !important; color: #1e3a5f !important;}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]),
[data-testid="stAlert"] [data-testid="stAlertContentWarning"] {background: #fffbeb !important; color: #78350f !important;}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]),
[data-testid="stAlert"] [data-testid="stAlertContentError"] {background: #fff1f2 !important; color: #991b1b !important;}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]),
[data-testid="stAlert"] [data-testid="stAlertContentSuccess"] {background: #ecfdf5 !important; color: #065f46 !important;}
[data-testid="stAlert"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stAlert"] p,
[data-testid="stMain"] [data-testid="stAlertContainer"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stAlertContainer"] p {color: inherit !important;}
.hero {background: linear-gradient(110deg, #103b30, #087f5b); color: white;
    padding: 30px; border-radius: 20px; margin-bottom: 22px;}
.hero h1 {color: white !important; margin: 3px 0; font-size: 2.6rem;}
.hero p {color: #d6f5e5; margin: 8px 0 0;}
/* Active-tab header mirrors the sidebar selection in the main canvas. */
.page-head {display: flex; align-items: center; gap: 14px; background: #ffffff;
    border: 1px solid #dce8e2; border-left: 5px solid #087f5b; border-radius: 14px;
    padding: 14px 18px; margin: 2px 0 18px; box-shadow: 0 5px 20px rgba(16,46,41,.035);}
.page-head-icon {font-size: 1.6rem; line-height: 1;}
.page-head-text {display: flex; flex-direction: column; gap: 2px; min-width: 0;}
.page-head-title {color: #12372e; font-size: 1.12rem; font-weight: 700; letter-spacing: -.02em;}
.page-head-hint {color: #52675f; font-size: .85rem;}
.page-head-count {margin-left: auto; color: #065f46; font-weight: 700; font-size: .78rem;
    background: #ecfdf5; border: 1px solid #b7e4cd; border-radius: 20px;
    padding: 4px 10px; white-space: nowrap;}
.eyebrow {font-size: .74rem; letter-spacing: .16em; font-weight: 700;}
.card {padding: 22px; border-radius: 16px; border: 1px solid #dce8e2;
    background: white; color: #16352c; margin: 10px 0 16px;}
.card p {margin-bottom: 6px;}
.certificate {border: 2px solid #059669; background: #ecfdf5; padding: 26px;
    border-radius: 16px; margin-top: 20px; color: #064e3b;}
.demo {display: inline-block; background: #dcfce7; color: #065f46;
    padding: 5px 10px; border-radius: 20px; font-size: .75rem; font-weight: 700;}
</style>
""", unsafe_allow_html=True)


def inr(value):
    """Format rupees using Indian digit grouping, without locale dependencies."""
    rounded = int(round(float(value)))
    digits = str(abs(rounded))
    if len(digits) > 3:
        prefix, suffix = digits[:-3], digits[-3:]
        groups = []
        while prefix:
            groups.insert(0, prefix[-2:])
            prefix = prefix[:-2]
        digits = ",".join(groups + [suffix])
    return f"{'−' if rounded < 0 else ''}₹{digits}"


@st.cache_data(show_spinner=False)
def revenue_history(profile_name):
    """Generate stable synthetic data, with September as the demo's anchor month."""
    profile = PROFILES[profile_name]
    rng = np.random.default_rng(profile["seed"])
    months = pd.date_range("2025-10-01", periods=12, freq="MS")
    seasonal = np.array([1.55, 1.20, 1.12, .96, .92, 1.02, 1.04, 1.01, .77, .68, .83, 1.0])
    revenue = np.rint(profile["income"] * seasonal * rng.uniform(.96, 1.04, 12)).astype(int)
    revenue[-1] = profile["income"]
    return pd.DataFrame({
        "Month": months.strftime("%b %Y"), "Revenue": revenue,
        "Season": ["Festive Peak (Diwali)"] + ["Regular"] * 7
                  + ["Monsoon Slump"] * 3 + ["Regular"],
    })


def initial_expenses(profile):
    return pd.DataFrame({"Expense": ["Rent", "Electricity", "Inventory"],
                         "Amount (₹)": profile["expenses"]})


def sanitize_expenses(frame):
    """Treat blank values as zero and keep scoring inputs finite and bounded."""
    amounts = pd.to_numeric(frame["Amount (₹)"], errors="coerce")
    invalid = amounts.isna() | ~np.isfinite(amounts) | (amounts < 0) | (amounts > 10_000_000)
    clean = frame.copy()
    clean["Amount (₹)"] = amounts.replace([np.inf, -np.inf], np.nan).fillna(0).clip(0, 10_000_000)
    clean["Expense"] = clean["Expense"].fillna("Other").astype(str)
    return clean, bool(invalid.any())


def credit_health(profile, expense_total):
    """Transparent demonstration heuristic; not an underwriting model."""
    income = profile["income"]
    profit = income - expense_total
    reference_profit = income - sum(profile["expenses"])
    adjustment = int(round(np.clip((profit - reference_profit) / income * 180, -100, 60)))
    score = int(np.clip(profile["base_score"] + adjustment, 300, 900))
    limit = int(min(profile["loan_cap"], max(0, profit) * 2.5) // 1000 * 1000)
    if score < 500:
        limit = 0
    return profit, score, limit, adjustment


def style_transaction(row):
    flagged = row["Status"] != "🟢 Clear"
    return ["background-color: #fff1f2; color: #991b1b; font-weight: 600;"
            if flagged else "background-color: #ffffff; color: #16352c;" for _ in row]


def transaction_history(risk_account):
    """Build synthetic review events independently of the selected page."""
    transactions = pd.DataFrame([
        {"Event ID": "DEMO-101", "Time": "18 Sep, 09:12", "Amount (₹)": 120 if not risk_account else 499,
         "Status": "🟢 Clear", "Signal": "Routine customer payment"},
        {"Event ID": "DEMO-102", "Time": "18 Sep, 11:35", "Amount (₹)": 450 if not risk_account else 999,
         "Status": "🟢 Clear", "Signal": "Within typical business hours"},
        {"Event ID": "DEMO-103", "Time": "18 Sep, 14:00–14:10", "Amount (₹)": 5000,
         "Status": "🔴 Review", "Signal": "Structuring: 50 micro-transactions in 10 mins"},
        {"Event ID": "DEMO-104", "Time": "18 Sep, 03:00", "Amount (₹)": 25000,
         "Status": "🔴 High risk" if risk_account else "🔴 Review",
         "Signal": "Midnight Spike: ₹25,000 at 3 AM"},
    ])
    if risk_account:
        transactions.loc[len(transactions)] = ["DEMO-105", "18 Sep, 03:04", 24800,
                                               "🔴 High risk", "Rapid reversal to the same counterparty"]
    return transactions


def tab_label(index, copy, flagged_events):
    """Sidebar tab caption: icon, translated title and a live fraud badge."""
    label = f"{TAB_ICONS[index]}  {copy['tabs'][index]}"
    if index == 3 and flagged_events:
        label += f"   🔴 {flagged_events}"
    return label


def goto_section(index):
    """Widget callback: switch tabs before the script reruns, so state stays in sync."""
    st.session_state["section_nav"] = index


with st.sidebar:
    st.markdown("## 🛡️ VyaparScore")
    st.caption("SMALL BUSINESSES. BIG POSSIBILITIES.")
    language = st.radio("Language / भाषा", list(COPY), horizontal=True)
    text = COPY[language]
    # Stable key: the label is translated, and a changing label would otherwise
    # reset this widget (losing the merchant) every time the language switches.
    merchant = st.selectbox(text["profile"], list(PROFILES), key="merchant_select")
    profile = PROFILES[merchant]
    # Derived once here so the tab badge and the Fraud Guard page always agree.
    risk_account = merchant == "Suspicious Merchant"
    flagged_events = int((transaction_history(risk_account)["Status"] != "🟢 Clear").sum())
    st.divider()
    section = st.radio(
        text["nav"],
        options=range(len(text["tabs"])),
        format_func=lambda index: tab_label(index, text, flagged_events),
        key="section_nav",
    )
    st.caption(f"{TAB_ICONS[section]} {text['tab_hints'][section]}")
    st.caption(text["nav_hint"])
    st.divider()
    st.markdown(f"### {merchant}")
    st.write(profile["owner"])
    st.caption(f"{profile['business']} · {profile['city']}")
    st.divider()
    st.caption("DEMO DATA WINDOW")
    st.write("Oct 2025 – Sep 2026")
    st.caption("Offline sandbox · No bank connection")
    st.info("All scores, OCR, fraud findings and approvals are simulated. No money moves.")
    st.caption("Language selection translates key headings; demo data remains in English.")

prefix = f"merchant::{merchant}"
expense_key = f"{prefix}::expenses"
scan_key = f"{prefix}::scan_version"
baseline_key = f"{prefix}::editor_baseline"
if expense_key not in st.session_state:
    st.session_state[expense_key] = initial_expenses(profile)
if scan_key not in st.session_state:
    st.session_state[scan_key] = 0

st.markdown(
    f'<div class="hero"><div class="eyebrow">BUILT FOR BHARAT · OFFLINE DEMO</div>'
    f'<h1>VyaparScore</h1><p>{escape(text["title"])}</p></div>',
    unsafe_allow_html=True,
)
st.caption(f"{merchant} / September 2026 snapshot / Synthetic financial data")
# The sidebar owns the tab list; this header shows the active tab and lets you
# step through tabs without reopening a collapsed sidebar.
head_title, head_nav = st.columns([0.74, 0.26], vertical_alignment="center")
with head_title:
    st.markdown(
        f'<div class="page-head"><span class="page-head-icon">{TAB_ICONS[section]}</span>'
        f'<span class="page-head-text">'
        f'<span class="page-head-title">{escape(text["tabs"][section])}</span>'
        f'<span class="page-head-hint">{escape(text["tab_hints"][section])}</span></span>'
        f'<span class="page-head-count">{section + 1} / {len(TAB_ICONS)}</span></div>',
        unsafe_allow_html=True,
    )
with head_nav:
    prev_col, next_col = st.columns(2)
    prev_col.button(text["previous"], key="nav_prev", on_click=goto_section, args=(section - 1,),
                    disabled=section == 0, width="stretch")
    next_col.button(text["next"], key="nav_next", on_click=goto_section,
                    args=(section + 1,), disabled=section == len(TAB_ICONS) - 1, width="stretch")

# Data lives outside widgets so navigating away cannot discard register edits.
editor_context = (merchant, section)
if section == 2 and st.session_state.get("last_editor_context") != editor_context:
    st.session_state[baseline_key] = st.session_state[expense_key].copy()
    st.session_state[scan_key] += 1
st.session_state["last_editor_context"] = editor_context

if section == 2:
    st.subheader(text["ocr"])
    st.write("Digitise everyday expenses and see how verified cash flow could influence credit health.")
    st.warning("Demo OCR: uploads are not read. Every scan returns the same profile-specific sample expenses.")
    notebook = st.file_uploader("Upload a notebook photo", type=["png", "jpg", "jpeg", "webp"],
                                key=f"{prefix}::notebook")
    use_sample = st.checkbox("Use a sample register instead", value=True, key=f"{prefix}::sample")
    st.caption("Use non-sensitive demo images only. Files stay in this Streamlit session; no OCR service is called.")
    if st.button("Scan Register", type="primary", key=f"{prefix}::scan"):
        if notebook is None and not use_sample:
            st.warning("Upload a notebook photo or enable the sample register first.")
        elif notebook is not None and notebook.size > 10 * 1024 * 1024:
            st.error("Please upload an image smaller than 10 MB.")
        else:
            with st.spinner("Extracting handwritten text..."):
                time.sleep(2)
            st.session_state[expense_key] = initial_expenses(profile)
            st.session_state[baseline_key] = st.session_state[expense_key].copy()
            st.session_state[scan_key] += 1
            st.success("Simulated extraction complete. Review and edit the sample expenses below.")
    st.caption("The table starts with sample values. Scanning resets edits to the profile's sample register.")
    edited = st.data_editor(
        st.session_state[baseline_key], hide_index=True, num_rows="dynamic",
        column_config={
            "Expense": st.column_config.TextColumn("Expense", required=True, max_chars=80),
            "Amount (₹)": st.column_config.NumberColumn(
                "Amount (₹)", min_value=0, max_value=10_000_000, step=100,
                format="₹%.0f", required=True,
            ),
        },
        key=f"{prefix}::editor::{st.session_state[scan_key]}",
        width="stretch",
    )
    expenses, corrected = sanitize_expenses(edited)
    if corrected:
        st.warning("Missing or invalid amounts are treated as zero; values are bounded to ₹1 crore per row.")
    # Save canonical values while keeping the editor's delta baseline stable.
    st.session_state[expense_key] = expenses.copy()
    total_expenses = float(expenses["Amount (₹)"].sum())
    profit, score, max_loan, score_adjustment = credit_health(profile, total_expenses)
    st.markdown("#### Live profit calculation")
    st.info(f"Net Profit = UPI Income − Bahi-Khata Expenses\n\n"
            f"{inr(profit)} = {inr(profile['income'])} − {inr(total_expenses)}")
    col1, col2 = st.columns(2)
    col1.metric("Adjusted demo credit score", f"{score} / 900", f"{score_adjustment:+d} vs baseline")
    col2.metric("Recorded monthly expenses", inr(total_expenses))
    st.caption("Demo formula: baseline score + 180 × change in profit margin, with the adjustment "
               "limited to −100/+60 points. Final score is bounded to 300–900. "
               "This is not a bureau score; real lenders require verified income and expenses.")

# Every destination can be opened first, without running another page's UI.
expenses, _ = sanitize_expenses(st.session_state[expense_key])
total_expenses = float(expenses["Amount (₹)"].sum())
profit, score, max_loan, score_adjustment = credit_health(profile, total_expenses)
history = revenue_history(merchant)
annual_revenue = int(history["Revenue"].sum())
health_label = "Strong" if score >= 750 else "Building" if score >= 600 else "Needs review"

transactions = transaction_history(risk_account)
projected_receipts = profile["income"] * 14 / 30 * .70
operating_outflow = max(0, total_expenses - profile["expenses"][2]) * 14 / 30
projected_cash = profile["cash"] + projected_receipts - operating_outflow - profile["inventory_due"]

if section == 0:
    st.subheader(text["health"])
    gauge_col, insight_col = st.columns([1.1, 1])
    with gauge_col:
        gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=score,
            title={"text": "VyaparScore · Demo credit health", "font": {"size": 18}},
            number={"font": {"size": 58, "color": "#087f5b"}},
            gauge={
                "axis": {"range": [300, 900], "tickvals": [300, 450, 600, 750, 900]},
                "bar": {"color": "#087f5b", "thickness": .25},
                "bgcolor": "white", "borderwidth": 0,
                "steps": [{"range": [300, 600], "color": "#fee2e2"},
                          {"range": [600, 750], "color": "#fef3c7"},
                          {"range": [750, 900], "color": "#d1fae5"}],
                "threshold": {"line": {"color": "#103b30", "width": 4},
                              "thickness": .8, "value": score},
            },
        ))
        gauge.update_layout(height=300, margin=dict(l=35, r=35, t=55, b=20),
                            paper_bgcolor="rgba(0,0,0,0)", template="plotly_white",
                            font={"family": "sans-serif", "color": "#16352c"})
        st.plotly_chart(gauge, width="stretch", theme=None, config={"displayModeBar": False})
    with insight_col:
        st.markdown(
            f'<div class="card"><span class="demo">{health_label.upper()}</span>'
            f'<h3>{escape(merchant)}</h3><p>Understand your cash flow. Build a stronger borrowing profile.</p>'
            f'<p>Monthly margin: <strong>{profit / profile["income"]:.1%}</strong></p>'
            f'<p>Expense-driven score adjustment: <strong>{score_adjustment:+d} points</strong></p></div>',
            unsafe_allow_html=True,
        )
        if risk_account:
            st.error("Synthetic anomaly flags require manual review. Automated demo lending is paused.")
        else:
            st.success("Keep your bahi-khata updated to make your income story clearer.")
    metrics = st.columns(4)
    metrics[0].metric(text["revenue"], inr(profile["income"]))
    metrics[1].metric(text["profit"], inr(profit))
    metrics[2].metric(text["customers"], f"{profile['customers']:,}")
    metrics[3].metric(text["limit"], inr(max_loan))
    st.divider()
    gst_col, scheme_col = st.columns(2)
    with gst_col:
        st.markdown(f"### {text['gst']}")
        ratio = annual_revenue / GST_REFERENCE
        st.progress(float(np.clip(ratio, 0, 1)), text=f"{ratio:.1%} of illustrative ₹40 lakh threshold")
        st.write(f"Trailing 12-month UPI receipts: **{inr(annual_revenue)}**")
        if ratio >= 1:
            st.error("Illustrative threshold crossed. Review applicable registration requirements with a tax adviser.")
        elif ratio >= .85:
            st.warning(f"Approaching the reference limit: {inr(GST_REFERENCE - annual_revenue)} remaining.")
        else:
            st.success(f"Reference headroom: {inr(GST_REFERENCE - annual_revenue)}.")
        st.caption("₹40 lakh is an illustrative reference for certain eligible goods suppliers, not a universal "
                   "GST exemption. Services, food businesses and compulsory registration rules may differ. "
                   "Actual assessment uses financial-year aggregate turnover, including non-UPI sales, "
                   "not this rolling UPI-only total. This is not tax advice.")
    with scheme_col:
        st.markdown(f"### {text['scheme']}")
        if profile["vendor"]:
            st.success("Based on your profile, you are eligible for PM SVANidhi ₹10,000 Loan — simulated demo match.")
            st.caption("Illustrative scheme amount, not a verified current offer. Actual eligibility, vendor "
                       "documentation and current scheme terms must be checked with the official programme.")
            if st.button("Apply", key=f"{prefix}::scheme_apply"):
                st.session_state[f"{prefix}::scheme_interest"] = True
            if st.session_state.get(f"{prefix}::scheme_interest"):
                st.info("Demo interest recorded only. No application submitted. Verify vendor ID / "
                        "certificate, KYC and current terms with the relevant authority.")
        else:
            st.info("No street-vendor scheme match for this sample profile. PM SVANidhi eligibility "
                    "requires verification; a retail account alone does not establish eligibility.")

if section == 1:
    st.subheader(text["season"])
    st.caption("Synthetic 12-month UPI receipts · Hover over a bar for details.")
    chart = px.bar(history, x="Month", y="Revenue", color="Season", text_auto=".2s",
                   category_orders={"Month": history["Month"].tolist()},
                   color_discrete_map={"Regular": "#10b981", "Festive Peak (Diwali)": "#f59e0b",
                                       "Monsoon Slump": "#64748b"},
                   labels={"Revenue": "Monthly UPI revenue (₹)"})
    chart.update_traces(hovertemplate="%{x}<br>Revenue: ₹%{y:,.0f}<extra>%{fullData.name}</extra>")
    chart.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=10, r=10, t=20, b=10), legend_title_text="",
                        legend=dict(orientation="h", y=1.15), yaxis=dict(gridcolor="#e3eae6"),
                        template="plotly_white", font=dict(color="#16352c"))
    st.plotly_chart(chart, width="stretch", theme=None)
    c1, c2 = st.columns(2)
    c1.info("🪔 Festive Peak (Diwali) · October 2025\n\nPlan inventory ahead of the demo's festive demand surge.")
    c2.info("🌧️ Monsoon Slump · June–August 2026\n\nBuild a cash buffer before the quieter trading season.")
    st.markdown("### 14-day cash flow outlook")
    if projected_cash < 0:
        st.warning("Warning: High probability of negative cash flow in the next 14 days based on inventory cycle.")
    else:
        st.success("The illustrative 14-day cash balance is positive. Continue monitoring inventory payments.")
    st.metric("Projected closing cash", inr(projected_cash))
    with st.expander("Forecast assumptions — illustrative, not predictive AI"):
        st.write(f"Opening cash {inr(profile['cash'])} + stressed receipts {inr(projected_receipts)} "
                 f"− operating expenses {inr(operating_outflow)} − scheduled inventory payment "
                 f"{inr(profile['inventory_due'])} = {inr(projected_cash)}.")
        st.caption("Receipts assume 70% of the current daily run rate. Operating expenses exclude the "
                   "baseline inventory amount; the next supplier payment is a separate mock obligation. "
                   "The warning is rule-based; 'high probability' is demo copy, not a calibrated probability.")

if section == 3:
    st.subheader(text["fraud"])
    st.markdown("### A · Fake Screenshot Detector")
    st.caption("Controlled demo: every scan returns a fake-screenshot scenario, regardless of the image. "
               "This cannot authenticate a payment; verify receipt in your bank or merchant app.")
    screenshot = st.file_uploader("Upload a customer payment screenshot", type=["png", "jpg", "jpeg", "webp"],
                                  key=f"{prefix}::payment_image")
    screenshot_sample = st.checkbox("Use a sample fake screenshot", value=False,
                                    key=f"{prefix}::fake_sample")
    if st.button("Scan Payment Screenshot", type="primary", key=f"{prefix}::fraud_scan"):
        if screenshot is None and not screenshot_sample:
            st.warning("Upload a payment screenshot or select the sample scenario first.")
        elif screenshot is not None and screenshot.size > 10 * 1024 * 1024:
            st.error("Please upload an image smaller than 10 MB.")
        else:
            with st.spinner("Checking payment authenticity — simulated AI scan..."):
                time.sleep(2)
            st.error("FAKE SCREENSHOT DETECTED: Font mismatch and missing bank SMS confirmation.")
            st.info("SIMULATED RESULT ONLY. No pixels, bank records or SMS messages were inspected. "
                    "Do not accuse a customer or release goods based on this demo result.")
    st.divider()
    st.markdown("### B · UPI Anomaly Monitor")
    st.caption("Synthetic transaction events; grouped bursts appear as one row. Red badges indicate "
               "rule-based review signals, not proof of fraud.")
    st.dataframe(transactions.style.apply(style_transaction, axis=1).format({"Amount (₹)": inr}),
                 hide_index=True, width="stretch")
    st.warning(f"{int((transactions['Status'] != '🟢 Clear').sum())} synthetic events need review. "
               "Confirm settlement and transaction IDs before taking action.")

if section == 4:
    st.subheader(text["loan"])
    st.caption("Indicative demo offers only. No credit check, bank submission or disbursement occurs.")
    calculator, report_col = st.columns(2)
    with calculator:
        st.markdown("### Instant Micro-Loan Calculator")
        if max_loan > 1000:
            loan_amount = st.slider("Loan amount (₹)", min_value=1000, max_value=max_loan,
                                    value=min(10000, max_loan), step=1000,
                                    key=f"{prefix}::loan_amount::{max_loan}")
        elif max_loan == 1000:
            loan_amount = 1000
            st.info("Available demo loan amount: ₹1,000 (fixed minimum offer).")
        else:
            loan_amount = 0
            st.info("No automated loan limit in this scenario. Resolve negative cash flow or request manual review.")
        term = st.select_slider("Repayment term (months)", options=[3, 6, 9, 12], value=6,
                                key=f"{prefix}::term")
        annual_rate = .18
        monthly_rate = annual_rate / 12
        emi = loan_amount * monthly_rate * (1 + monthly_rate) ** term / ((1 + monthly_rate) ** term - 1)
        st.metric("Indicative monthly EMI", inr(emi))
        st.caption(f"Illustrative interest: 18% p.a., reducing balance · {term} months · No fees assumed.")
        st.write(f"Total repayment: **{inr(emi * term)}** · Interest: **{inr(emi * term - loan_amount)}**")
        consent = st.checkbox("I understand this is a simulated approval, not a real loan.",
                               key=f"{prefix}::loan_consent")
        approval_signature = (loan_amount, term, score, total_expenses, max_loan)
        if st.button("Apply for 1-Click Loan", type="primary", disabled=loan_amount == 0,
                     key=f"{prefix}::apply_loan"):
            if not consent:
                st.warning("Please acknowledge the demo notice before continuing.")
            elif risk_account or score < 500 or loan_amount > max_loan:
                st.error("Manual review required. This profile cannot receive an automated demo approval.")
            else:
                with st.spinner("Preparing your simulated approval..."):
                    time.sleep(1)
                st.session_state[f"{prefix}::approval"] = approval_signature
                st.balloons()
        if (loan_amount > 0 and consent
                and st.session_state.get(f"{prefix}::approval") == approval_signature):
            st.markdown(
                '<div class="certificate"><div class="eyebrow">DEMO · NOT A FINANCIAL INSTRUMENT</div>'
                '<h3>✓ Digital Approval Certificate</h3>'
                f'<p><strong>{escape(merchant)}</strong></p>'
                f'<p>Simulated sanctioned amount: <strong>{inr(loan_amount)}</strong></p>'
                f'<p>Tenure: {term} months · Indicative EMI: {inr(emi)}</p>'
                '<p>No lender has approved this loan. No application was transmitted and no funds will be disbursed.</p>'
                '</div>', unsafe_allow_html=True,
            )
    with report_col:
        st.markdown("### Bank-Ready Financial Summary")
        st.write("Prepare a clean snapshot of cash flow, recorded expenses and demo risk signals.")
        st.caption("The PDF-labelled action is simulated: the actual download is a UTF-8 text report, not a PDF.")
        report = "\n".join([
            "VYAPARSCORE | MICRO-MERCHANT FINANCIAL SUMMARY",
            "DEMONSTRATION ONLY — NOT VERIFIED, NOT A CREDIT BUREAU REPORT",
            "=" * 65,
            f"Merchant: {merchant}", f"Owner: {profile['owner']}",
            f"Location: {profile['city']}", "Snapshot: September 2026 (synthetic)",
            f"Monthly UPI revenue: {inr(profile['income'])}",
            f"Recorded Bahi-Khata expenses: {inr(total_expenses)}",
            f"Net profit: {inr(profit)}", f"Active customers: {profile['customers']}",
            f"Demo credit score: {score}/900 ({health_label})",
            f"Illustrative max loan limit: {inr(max_loan)}",
            f"Trailing 12-month UPI receipts: {inr(annual_revenue)}",
            f"Illustrative GST reference: {inr(GST_REFERENCE)} (not a tax determination)",
            f"14-day projected closing cash: {inr(projected_cash)}",
            f"Synthetic review events: {int((transactions['Status'] != '🟢 Clear').sum())}",
            f"Risk profile: {'Manual review required' if risk_account else 'Sample standard profile'}",
            "", "EDITED EXPENSE REGISTER",
            *[f"- {str(row['Expense']).replace(chr(10), ' ').replace(chr(13), ' ')}: {inr(row['Amount (₹)'])}"
              for _, row in expenses.iterrows()],
            "", "ILLUSTRATIVE LOAN CALCULATION",
            f"Requested amount: {inr(loan_amount)}", f"Term: {term} months",
            "Annual reducing-balance interest rate: 18%; fees assumed: zero",
            f"Monthly EMI: {inr(emi)}", f"Total repayment: {inr(emi * term)}",
            "", "IMPORTANT LIMITATIONS",
            "All financial records and transaction signals are synthetic.",
            "OCR and screenshot scans use fixed mock responses; no document is inspected.",
            "Credit scores use an unvalidated illustrative profit-margin heuristic.",
            "Loan limits: min(profile cap, 2.5 x positive monthly profit), rounded down",
            "to the nearest INR 1,000; scores below 500 receive a zero limit.",
            "GST thresholds vary; financial-year aggregate turnover must be verified.",
            "Scheme amounts and eligibility require official confirmation.",
            "This report is not tax advice, proof of fraud, or a real loan approval.",
        ])
        report_key = f"{prefix}::report"
        if st.button("Generate Bank-Ready PDF Report", key=f"{prefix}::generate_report"):
            with st.spinner("Preparing your demo financial summary..."):
                time.sleep(1)
            st.session_state[report_key] = {
                "source": report,
                "content": report + f"\n\nGenerated at: {datetime.now().isoformat(timespec='seconds')} (server time)\n",
            }
            st.success("Financial summary generated as a text file.")
        saved_report = st.session_state.get(report_key)
        if saved_report and saved_report["source"] == report:
            st.download_button(
                "Download Financial Summary (.txt)", data=saved_report["content"].encode("utf-8"),
                file_name=f"VyaparScore_{merchant.replace(' ', '_')}_Summary.txt",
                mime="text/plain", key=f"{prefix}::download_report",
            )
        elif saved_report:
            st.info("Your inputs changed. Generate a fresh report to download the updated summary.")

st.divider()
st.caption("VyaparScore · Built for Bharat · Hackathon sandbox. Synthetic data and simulated AI only. "
           "Not financial, lending, legal or tax advice. No external APIs are used.")