import time
import zlib
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# PAGE CONFIG (must be the first Streamlit call)
# ============================================================
st.set_page_config(
    page_title="VyaparScore: Bharat's Micro-Merchant Credit & Fraud Guard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# HELPERS & MULTI-LINGUAL ENGINE
# ============================================================
IST = timezone(timedelta(hours=5, minutes=30))  # server runs in IST
NOW = datetime.now(IST)

# use_container_width support for modern vs legacy Streamlit versions
_ver = tuple(int(p) for p in st.__version__.split(".")[:2] if p.isdigit())
STRETCH = {"width": "stretch"} if _ver >= (1, 50) else {"use_container_width": True}


def t(en, hi, te=None, ta=None, kn=None):
    """
    Selects the translated string based on the active language.
    Cascades gracefully: Selected Lang -> Hindi -> English.
    """
    lang = st.session_state.get("lang_toggle", "English")
    if lang == "हिंदी":
        return hi if hi is not None else en
    elif lang == "తెలుగు":
        return te if te is not None else (hi if hi is not None else en)
    elif lang == "தமிழ்":
        return ta if ta is not None else (hi if hi is not None else en)
    elif lang == "ಕನ್ನಡ":
        return kn if kn is not None else (hi if hi is not None else en)
    return en


def inr(v):
    return f"-₹{abs(v):,.0f}" if v < 0 else f"₹{v:,.0f}"


def stable_id(*parts, prefix="", digits=6):
    """Deterministic ID so values don't change on every Streamlit rerun."""
    raw = "|".join(str(p) for p in parts).encode()
    return f"{prefix}{zlib.crc32(raw) % (10 ** digits):0{digits}d}"


MERCHANT_KEYS = ["Ramesh Tea Stall", "Sharma Kirana", "Suspicious Merchant"]

# Calendar-year series (Jan..Dec)
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_HI = ["जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितम्बर", "अक्टूबर", "नवंबर", "दिसंबर"]
MONTHS_TE = ["జనవరి", "ఫిబ్రవరి", "మార్చి", "ఏప్రిల్", "మే", "జూన్", "జూలై", "ఆగస్టు", "సెప్టెంబర్", "అక్టోబర్", "నవంబర్", "డిసెంబర్"]
MONTHS_TA = ["ஜனவரி", "பிப்ரவரி", "மார்ச்", "ஏப்ரல்", "மே", "ஜூன்", "ஜூலை", "ஆகஸ்ட்", "செப்டம்பர்", "அக்டோபர்", "நவம்பர்", "டிசம்பர்"]
MONTHS_KN = ["ಜನವರಿ", "ಫೆಬ್ರವರಿ", "ಮಾರ್ಚ್", "ಏಪ್ರಿಲ್", "ಮೇ", "ಜೂನ್", "ಜುಲೈ", "ಆಗಸ್ಟ್", "ಸೆಪ್ಟೆಂಬರ್", "ಅಕ್ಟೋಬರ್", "ನವೆಂಬರ್", "ಡಿಸೆಂಬರ್"]

FESTIVE_IDX = {9, 10}      # Oct, Nov
MONSOON_IDX = {5, 6, 7}    # Jun, Jul, Aug

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }

    /* Hide branding / menu actions while keeping sidebar controls fully functional */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    header[data-testid="stHeader"] {
        background: transparent;
        z-index: 99;
    }
    [data-testid="stToolbarActions"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}

    /* Native Sidebar Expand Button - styled & prominently visible */
    [data-testid="stExpandSidebarButton"] {
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
        background: linear-gradient(135deg, #0d3b28 0%, #1b5e20 100%) !important;
        color: #69f0ae !important;
        border-radius: 8px !important;
        padding: 4px 10px !important;
        margin: 6px 0 0 8px !important;
        box-shadow: 0 4px 14px rgba(0, 128, 80, 0.3) !important;
        border: 1px solid rgba(105, 240, 174, 0.5) !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stExpandSidebarButton"]:hover {
        transform: scale(1.06) !important;
        background: linear-gradient(135deg, #00c853 0%, #1de9b6 100%) !important;
        border-color: #00c853 !important;
    }
    [data-testid="stExpandSidebarButton"] svg {
        fill: #69f0ae !important;
        color: #69f0ae !important;
    }
    [data-testid="stExpandSidebarButton"]:hover svg {
        fill: #063a22 !important;
        color: #063a22 !important;
    }

    /* Sidebar Navigation Tabs Styling */
    .sidebar-section-title {
        font-size: 0.76rem;
        font-weight: 700;
        color: #a8e6cf !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 14px 0 8px 0;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Vertical radio items in sidebar (navigation tabs) */
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"]:not([aria-orientation="horizontal"]) {
        gap: 8px !important;
        display: flex !important;
        flex-direction: column !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"]:not([aria-orientation="horizontal"]) label[data-baseweb="radio"] {
        background: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"]:not([aria-orientation="horizontal"]) label[data-baseweb="radio"]:hover {
        background: rgba(0, 200, 83, 0.2) !important;
        border-color: rgba(105, 240, 174, 0.5) !important;
        transform: translateX(4px) !important;
    }

    /* Hide the radio circle dot for navigation tabs */
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"]:not([aria-orientation="horizontal"]) label[data-baseweb="radio"] > div:first-child {
        display: none !important;
    }

    /* Active selected radio tab in sidebar */
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"]:not([aria-orientation="horizontal"]) label[data-baseweb="radio"]:has(input:checked) {
        background: linear-gradient(135deg, #00c853 0%, #1de9b6 100%) !important;
        border: 1px solid #69f0ae !important;
        box-shadow: 0 4px 16px rgba(0, 200, 83, 0.35) !important;
        transform: translateX(4px) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"]:not([aria-orientation="horizontal"]) label[data-baseweb="radio"] [data-testid="stMarkdownContainer"] p {
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        color: #e0f2ec !important;
        margin: 0 !important;
        letter-spacing: 0.2px !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"]:not([aria-orientation="horizontal"]) label[data-baseweb="radio"]:has(input:checked) [data-testid="stMarkdownContainer"] p {
        color: #063a22 !important;
        font-weight: 800 !important;
    }

    /* Top Bar & In-Page Reopen Options */
    .top-nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(135deg, #ffffff 0%, #f4faf7 100%);
        border: 1px solid #e0f2ec;
        border-radius: 12px;
        padding: 10px 18px;
        margin: 12px 0 10px 0;
        box-shadow: 0 2px 10px rgba(0, 128, 80, 0.04);
        flex-wrap: wrap;
        gap: 10px;
    }
    .active-tab-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.9rem;
    }
    .active-tab-dot {
        width: 9px;
        height: 9px;
        background: #00c853;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #00c853;
    }

    /* Sidebar background design */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a2e1f 0%, #0d3b28 50%, #124a33 100%);
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] label *,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }

    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fffe 100%);
        border: 1px solid #e0f2ec;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 24px rgba(0, 128, 80, 0.06);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(0, 128, 80, 0.12);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #00c853, #1de9b6);
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0d3b28;
        margin: 8px 0 4px 0;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 500;
        color: #6b7c74;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-delta {
        font-size: 0.8rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 6px;
        display: inline-block;
        margin-top: 4px;
    }
    .delta-positive { background: #e8f5e9; color: #2e7d32; }
    .delta-negative { background: #ffebee; color: #c62828; }

    .gauge-title {
        text-align: center;
        font-size: 0.9rem;
        font-weight: 600;
        color: #6b7c74;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 4px;
    }

    .alert-success {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        border-left: 5px solid #00c853;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 16px 0;
        box-shadow: 0 2px 12px rgba(0, 200, 83, 0.08);
    }
    .alert-warning {
        background: linear-gradient(135deg, #fff8e1 0%, #fff3e0 100%);
        border-left: 5px solid #ff9800;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 16px 0;
        box-shadow: 0 2px 12px rgba(255, 152, 0, 0.08);
    }
    .alert-danger {
        background: linear-gradient(135deg, #ffebee 0%, #fce4ec 100%);
        border-left: 5px solid #f44336;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 16px 0;
        box-shadow: 0 2px 12px rgba(244, 67, 54, 0.08);
    }
    .alert-info {
        background: linear-gradient(135deg, #e3f2fd 0%, #e8eaf6 100%);
        border-left: 5px solid #2196f3;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 16px 0;
        box-shadow: 0 2px 12px rgba(33, 150, 243, 0.08);
    }

    .fraud-badge {
        background: #e53935;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .safe-badge {
        background: #00a844;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .approval-cert {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border: 3px solid #00c853;
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        margin: 24px 0;
    }
    .approval-title { font-size: 1.8rem; font-weight: 800; color: #1b5e20; margin-bottom: 12px; }
    .approval-amount { font-size: 3rem; font-weight: 800; color: #00a844; margin: 16px 0; }

    .gst-meter-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fffe 100%);
        border: 1px solid #e0f2ec;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 24px rgba(0, 128, 80, 0.06);
    }
    .gst-title { font-size: 1rem; font-weight: 700; color: #0d3b28; margin-bottom: 12px; }

    .stTabs [data-baseweb="tab-list"] {
        display: none !important; /* Hide old tabs styling */
    }

    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0d3b28;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 3px solid #00c853;
        display: inline-block;
    }
    .main-title {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0d3b28 0%, #00c853 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        line-height: 1.3;
    }
    .main-subtitle { font-size: 1rem; color: #6b7c74; font-weight: 400; margin-bottom: 24px; }

    .stDownloadButton button {
        background: linear-gradient(135deg, #0d3b28 0%, #1a5c40 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 32px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(0, 128, 80, 0.3) !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #00c853 0%, #00e676 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 28px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        font-size: 0.9rem !important;
    }
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 200, 83, 0.3) !important;
    }

    .stSlider [data-baseweb="slider"] [role="slider"] { background: #00c853 !important; }
    .stProgress > div > div { background: linear-gradient(90deg, #00c853, #1de9b6) !important; }

    .scheme-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        border: 2px solid #a5d6a7;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
    }
    .scheme-title { font-size: 1.1rem; font-weight: 700; color: #1b5e20; margin-bottom: 8px; }
    .scheme-amount { font-size: 1.8rem; font-weight: 800; color: #00a844; }

    .separator {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e0f2ec, transparent);
        margin: 24px 0;
    }

    /* Sthan Log Style Sheets */
    .sthan-badge {
        background: linear-gradient(135deg, #0d3b28 0%, #1b5e20 100%);
        color: #69f0ae;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: 1px solid rgba(105, 240, 174, 0.35);
    }
    .legal-alert {
        background: linear-gradient(135deg, #f0fdf4 0%, #e8f5e9 100%);
        border: 1px solid #a7f3d0;
        border-left: 6px solid #00c853;
        border-radius: 14px;
        padding: 20px 24px;
        margin: 16px 0;
        box-shadow: 0 4px 20px rgba(0, 200, 83, 0.08);
    }
    .squad-mode-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 2px solid #eab308;
        border-radius: 16px;
        padding: 24px;
        color: #ffffff;
        margin: 16px 0;
        box-shadow: 0 8px 32px rgba(234, 179, 8, 0.25);
    }
    .cert-official {
        background: #ffffff;
        border: 2px solid #0d3b28;
        border-radius: 16px;
        padding: 32px;
        margin: 20px 0;
        box-shadow: 0 6px 24px rgba(13, 59, 40, 0.08);
        position: relative;
    }
    .peer-card {
        background: #ffffff;
        border: 1px solid #e0f2ec;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# MOCK DATA IN FIVE LANGUAGES
# ============================================================
def _finalize(d):
    """Derive figures from the raw series so every tab agrees with every other tab."""
    revs = d["monthly_revenues"]
    d["monthly_revenue"] = revs[-1]
    d["gst_revenue_ytd"] = sum(revs)
    d["net_profit"] = revs[-1] - sum(d["bahi_khata"].values())
    d["revenue_pct"] = (revs[-1] / revs[-2] - 1) * 100
    d["revenue_delta"] = f"{d['revenue_pct']:+.1f}%"
    return d


def get_merchant_data(merchant_name):
    """Generate complete multi-lingual mock data for each merchant profile."""
    if merchant_name == "Ramesh Tea Stall":
        data = {
            "name": "Ramesh Tea Stall",
            "name_hi": "रमेश चाय स्टॉल",
            "name_te": "రమేష్ టీ స్టాల్",
            "name_ta": "ரமேஷ் டீ ஸ்டால்",
            "name_kn": "ರಮೇಶ್ ಟೀ ಸ್ಟಾಲ್",
            "owner": "Ramesh Kumar",
            "owner_hi": "रमेश कुमार",
            "owner_te": "రమేష్ కుమార్",
            "owner_ta": "ரமேஷ் குமார்",
            "owner_kn": "ರಮೇಶ್ ಕುಮಾರ್",
            "phone_masked": "+91 98765 •••21",
            "location": "Koramangala, Bengaluru",
            "location_hi": "कोरमंगला, बेंगलुरू",
            "location_te": "కోరమంగళ, బెంగళూరు",
            "location_ta": "கோரமங்களா, பெங்களூரு",
            "location_kn": "ಕೋರಮಂಗಲ, ಬೆಂಗಳೂರು",
            "type": "Food & Beverage",
            "type_hi": "खाद्य एवं पेय",
            "type_te": "ఆహారం & పానీయాలు",
            "type_ta": "உணவு & பானங்கள்",
            "type_kn": "ಆಹಾರ ಮತ್ತು ಪಾನೀಯಗಳು",
            "credit_score": 742,
            "credit_label": "Good",
            "credit_label_hi": "अच्छा",
            "credit_label_te": "మంచిది",
            "credit_label_ta": "நல்லது",
            "credit_label_kn": "ಉತ್ತಮ",
            "active_customers": 340,
            "max_loan": 150000,
            "gst_limit": 4000000,
            "eligible_scheme": "PM SVANidhi",
            "scheme_amount": 10000,
            "scheme_desc": "Street vendor micro-credit for working capital",
            "scheme_desc_hi": "स्ट्रीट वेंडर कार्यशील पूंजी के लिए माइक्रो-क्रेडिट",
            "scheme_desc_te": "వీధి వ్యాపారుల వర్కింగ్ క్యాపిటల్ కోసం మైక్రో-క్రెడిట్",
            "scheme_desc_ta": "தெரு வியாபாரிகள் மூலதனத்திற்கான மைக்ரோ-கிராப்ட்",
            "scheme_desc_kn": "ಬೀದಿ ಬದಿ ವ್ಯಾಪಾರಿಗಳ ದುಡಿಯುವ ಬಂಡವಾಳಕ್ಕಾಗಿ ಮೈಕ್ರೋ-ಕ್ರೆಡಿಟ್",
            "monthly_revenues": [
                145000, 152000, 160000, 155000, 148000, 135000,
                128000, 132000, 175000, 220000, 245000, 185000,
            ],
            "bahi_khata": {
                "Rent / किराया": 12000,
                "Electricity / बिजली": 3500,
                "Tea Supplies / चाय सामग्री": 45000,
                "Milk / दूध": 28000,
                "Sugar / चीनी": 8000,
                "Staff Salary / कर्मचारी वेतन": 18000,
                "Gas Cylinder / गैस सिलेंडर": 4500,
                "Miscellaneous / विविध": 4000,
            },
            "anomalies": [
                {"time": "14:32", "amount": 15, "from": "Unknown_453", "flag": "Micro-txn Burst: 32 txns of ₹15 in 8 mins", "risk": "Medium"},
                {"time": "06:15", "amount": 8500, "from": "Wholesale_Milk", "flag": "Normal: Routine supplier payment", "risk": "Low"},
            ],
            "profit_delta": "+8.2%",
            "customer_delta": "+15",
            "sthan_spot": "Opp. Jyoti Nivas College Gate, 5th Block, Koramangala, Bengaluru",
            "sthan_spot_hi": "ज्योति निवास कॉलेज गेट के सामने, 5वां ब्लॉक, कोरमंगला, बेंगलुरू",
            "sthan_spot_te": "జ్యోతి నివాస్ కాలేజ్ గేట్ ఎదురుగా, 5వ బ్లాక్, కోరమంగళ, బెంగళూరు",
            "sthan_spot_ta": "ஜோதி நிவாஸ் கல்லூரி வாயில் எதிரில், 5வது பிளாக், கோரமங்களா, பெங்களூரு",
            "sthan_spot_kn": "ಜ್ಯೋತಿ ನಿವಾಸ್ ಕಾಲೇಜು ಗೇಟ್ ಎದುರು, 5ನೇ ಬ್ಲಾಕ್, ಕೋರಮಂಗಲ, ಬೆಂಗಳೂರು",
            "sthan_ward": "Ward 151 (Koramangala, BBMP)",
            "sthan_ward_hi": "वार्ड 151 (कोरमंगला, बीबीएमपी)",
            "sthan_ward_te": "వార్డు 151 (కోరమంగళ, BBMP)",
            "sthan_ward_ta": "வார்டு 151 (கோரமங்களா, BBMP)",
            "sthan_ward_kn": "ವಾರ್ಡ್ 151 (ಕೋರಮಂಗಲ, ಬಿಬಿಎಂಪಿ)",
            "sthan_coords": (12.9343, 77.6192),
            "sthan_days": 512,
            "sthan_start_date": "24 Oct 2022",
            "sthan_streak": 184,
            "sthan_geofence_adherence": 99.4,
            "sthan_tvc_status": "Natural Market Cluster #151 — Survey Pending (Protected under Sec 3(3))",
            "sthan_tvc_status_hi": "प्राकृतिक बाजार क्लस्टर #151 — सर्वेक्षण लंबित (धारा 3(3) संरक्षित)",
            "sthan_tvc_status_te": "సహజ మార్కెట్ క్లస్టర్ #151 — సర్వే పెండింగ్‌లో ఉంది (సెక్షన్ 3(3) రక్షణలో ఉంది)",
            "sthan_tvc_status_ta": "இயற்கை சந்தை கிளஸ்டர் #151 — கணக்கெடுப்பு நிலுவையில் உள்ளது (பிரிவு 3(3) பாதுகாக்கப்பட்டது)",
            "sthan_tvc_status_kn": "ನೈಸರ್ಗಿಕ ಮಾರುಕಟ್ಟೆ ಕ್ಲಸ್ಟರ್ #151 — ಸಮೀಕ್ಷೆ ಬಾಕಿ ಇದೆ (ವಿಭಾಗ 3(3) ಅಡಿಯಲ್ಲಿ ರಕ್ಷಿಸಲಾಗಿದೆ)",
            "sthan_legal_shield": "Strong (Sec 3(3) Immunity Active)",
            "sthan_legal_shield_hi": "मजबूत (धारा 3(3) वैधानिक सुरक्षा)",
            "sthan_legal_shield_te": "బలమైనది (సెక్షన్ 3(3) చట్టపరమైన రక్షణ క్రియాశీలంగా ఉంది)",
            "sthan_legal_shield_ta": "வலிமையானது (பிரிவு 3(3) சட்டப்பூர்வ அரண் செயல்பாட்டில் உள்ளது)",
            "sthan_legal_shield_kn": "ಬಲವಾದ ರಕ್ಷಣೆ (ವಿಭಾಗ 3(3) ಶಾಸನಬದ್ಧ ಮುಕ್ತಿ ಸಕ್ರಿಯವಾಗಿದೆ)",
            "sthan_shield_score": 96,
            "sthan_svanidhi_tier": "PM SVANidhi Tranche-3 Pre-Qualified (LOR Automated)",
            "sthan_svanidhi_tier_hi": "पीएम स्वनिधि किश्त-3 पूर्व-स्वीकृत (LOR स्वचालित)",
            "sthan_svanidhi_tier_te": "పీఎం స్వనిధి విడత-3 ముందస్తు అర్హత (LOR ఆటోమేటెడ్)",
            "sthan_svanidhi_tier_ta": "பிஎம் ஸ்வநிதி தவணை-3 முன் தகுதி பெற்றது (LOR தானியங்கி)",
            "sthan_svanidhi_tier_kn": "ಪಿಎಂ ಸ್ವನಿಧಿ ಕಂತು-3 ಪೂರ್ವ-ಅರ್ಹತೆ (LOR ಸ್ವಯಂಚಾಲಿತ)",
            "sthan_peers": [
                {"name": "Raju Flower Stall", "role": "Adjacent Micro-Vendor", "tenure": "4 yrs", "status": "Verified"},
                {"name": "Sri Krishna Sweets & Bakery", "role": "Permanent Commercial Merchant", "tenure": "7 yrs", "status": "Verified"},
                {"name": "Koramangala Auto Drivers Union", "role": "Local Transport Stand", "tenure": "5 yrs", "status": "Verified"},
                {"name": "Ward 151 RWA Representative", "role": "Neighborhood Civic Watch", "tenure": "3 yrs", "status": "Verified"},
            ],
        }
    elif merchant_name == "Sharma Kirana":
        data = {
            "name": "Sharma Kirana Store",
            "name_hi": "शर्मा किराना स्टोर",
            "name_te": "శర్మ కిరాణా స్టోర్",
            "name_ta": "சர்மா மளிகைக் கடை",
            "name_kn": "ಶರ್ಮಾ ಕಿರಾಣಿ ಅಂಗಡಿ",
            "owner": "Vijay Sharma",
            "owner_hi": "विजय शर्मा",
            "owner_te": "విజయ్ శర్మ",
            "owner_ta": "விஜய் சர்மா",
            "owner_kn": "ವಿಜಯ್ ಶರ್ಮಾ",
            "phone_masked": "+91 99102 •••76",
            "location": "Lajpat Nagar, Delhi",
            "location_hi": "लाजपत नगर, दिल्ली",
            "location_te": "లజపత్ నగర్, ఢిల్లీ",
            "location_ta": "லஜ்பத் நகர், டெல்லி",
            "location_kn": "ಲಜಪತ್ ನಗರ, ದೆಹಲಿ",
            "type": "General Store",
            "type_hi": "जनरल स्टोर",
            "type_te": "జనరల్ స్టోర్",
            "type_ta": "பொது அங்காடி",
            "type_kn": "ಜನರಲ್ ಸ್ಟೋರ್",
            "credit_score": 681,
            "credit_label": "Fair",
            "credit_label_hi": "ठीक",
            "credit_label_te": "సాధారణం",
            "credit_label_ta": "பரவாயில்லை",
            "credit_label_kn": "ಸಾಧಾರಣ",
            "active_customers": 890,
            "max_loan": 300000,
            "gst_limit": 4000000,
            "eligible_scheme": "MUDRA Shishu Loan",
            "scheme_amount": 50000,
            "scheme_desc": "Micro Units Development & Refinance Agency loan for small businesses",
            "scheme_desc_hi": "छोटे व्यवसायों के लिए मुद्रा शिशु ऋण",
            "scheme_desc_te": "చిన్న వ్యాపారాల కోసం ముద్రా శిశు రుణం",
            "scheme_desc_ta": "சிறு தொழில்களுக்கான முத்ரா சிசு கடன்",
            "scheme_desc_kn": "ಸಣ್ಣ ಉದ್ಯಮಗಳಿಗೆ ಮುದ್ರಾ ಶಿಶು ಸಾಲ",
            "monthly_revenues": [
                380000, 395000, 410000, 405000, 390000, 350000,
                330000, 345000, 450000, 520000, 580000, 420000,
            ],
            "bahi_khata": {
                "Shop Rent / दुकान किराया": 35000,
                "Electricity / बिजली": 8500,
                "Inventory / माल खरीद": 180000,
                "Staff (2) / कर्मचारी": 30000,
                "Transport / परिवहन": 12000,
                "Packaging / पैकेजिंग": 5000,
                "Maintenance / रखरखाव": 3500,
                "Miscellaneous / विविध": 6000,
            },
            "anomalies": [
                {"time": "23:45", "amount": 25000, "from": "Unknown_UPI_789", "flag": "Midnight Spike: ₹25,000 at 11:45 PM", "risk": "High"},
                {"time": "10:15", "amount": 49, "from": "Multi_Acct_12", "flag": "Structuring: 50 micro-transactions in 10 mins", "risk": "Critical"},
                {"time": "15:30", "amount": 12000, "from": "Regular_Cust_45", "flag": "Normal: Regular bulk purchase", "risk": "Low"},
            ],
            "profit_delta": "+4.1%",
            "customer_delta": "+42",
            "sthan_spot": "Shop #14, Central Market Lane, Lajpat Nagar II, New Delhi",
            "sthan_spot_hi": "दुकान #14, सेंट्रल मार्केट लेन, लाजपत नगर II, नई दिल्ली",
            "sthan_spot_te": "షాప్ #14, సెంట్రల్ మార్కెట్ లేన్, లజపత్ నగర్ II, న్యూఢిల్లీ",
            "sthan_spot_ta": "கடை #14, சென்ட்ரல் மார்க்கெட் லேன், லஜ்பத் நகர் II, புது டெல்லி",
            "sthan_spot_kn": "ಅಂಗಡಿ #14, ಸೆಂಟ್ರಲ್ ಮಾರ್ಕೆಟ್ ಲೇನ್, ಲಜಪತ್ ನಗರ II, ನವದೆಹಲಿ",
            "sthan_ward": "Ward 58 (Lajpat Nagar II, MCD)",
            "sthan_ward_hi": "वार्ड 58 (लाजपत नगर II, एमसीडी)",
            "sthan_ward_te": "వార్డు 58 (లజపత్ నగర్ II, MCD)",
            "sthan_ward_ta": "வார்டு 58 (லஜ்பத் நகர் II, MCD)",
            "sthan_ward_kn": "ವಾರ್ಡ್ 58 (ಲಜಪತ್ ನಗರ II, ಎಂಸಿಡಿ)",
            "sthan_coords": (28.5678, 77.2433),
            "sthan_days": 1048,
            "sthan_start_date": "05 May 2021",
            "sthan_streak": 312,
            "sthan_geofence_adherence": 99.8,
            "sthan_tvc_status": "Permitted Commercial Zone / Municipal Trade License #DL-MCD-58-109",
            "sthan_tvc_status_hi": "अनुमति प्राप्त वाणिज्यिक क्षेत्र / नगर निगम लाइसेंस #DL-MCD-58-109",
            "sthan_tvc_status_te": "అనుమతించబడిన వాణిజ్య జోన్ / మునిసిపల్ ట్రేడ్ లైసెన్స్ #DL-MCD-58-109",
            "sthan_tvc_status_ta": "அனுமதிக்கப்பட்ட வணிக மண்டலம் / நகராட்சி வர்த்தக உரிமம் #DL-MCD-58-109",
            "sthan_tvc_status_kn": "ಅನುಮತಿಸಲಾದ ವಾಣಿಜ್ಯ ವಲಯ / ಮುನ್ಸಿಪಲ್ ವ್ಯಾಪಾರ ಪರವಾನಗಿ #DL-MCD-58-109",
            "sthan_legal_shield": "Maximum (Licensed Commercial Spot)",
            "sthan_legal_shield_hi": "सर्वोच्च (लाइसेंस प्राप्त व्यावसायिक स्थान)",
            "sthan_legal_shield_te": "అత్యధికం (లైసెన్స్ పొందిన వాణిజ్య స్థలం)",
            "sthan_legal_shield_ta": "அதிகபட்சம் (உரிமம் பெற்ற வணிக இடம்)",
            "sthan_legal_shield_kn": "ಗರಿಷ್ಠ ರಕ್ಷಣೆ (ಪರವಾನಗಿ ಪಡೆದ ವಾಣಿಜ್ಯ ಸ್ಥಳ)",
            "sthan_shield_score": 99,
            "sthan_svanidhi_tier": "MUDRA Scheme Active (Graduated from SVANidhi)",
            "sthan_svanidhi_tier_hi": "मुद्रा योजना सक्रिय (स्वनिधि से पदोन्नत)",
            "sthan_svanidhi_tier_te": "ముద్రా పథకం క్రియాశీలంగా ఉంది (స్వనిధి నుండి పదోన్నతి పొందింది)",
            "sthan_svanidhi_tier_ta": "முத்ரா திட்டம் செயல்பாட்டில் உள்ளது (ஸ்வநிதியிலிருந்து மேம்படுத்தப்பட்டது)",
            "sthan_svanidhi_tier_kn": "ಮುದ್ರಾ ಯೋಜನೆ ಸಕ್ರಿಯವಾಗಿದೆ (ಸ್ವನಿಧಿಯಿಂದ ತೇರ್ಗಡೆ ಹೊಂದಿದ್ದಾರೆ)",
            "sthan_peers": [
                {"name": "Gupta Medical Store", "role": "Neighboring Commercial Shop", "tenure": "9 yrs", "status": "Verified"},
                {"name": "Central Market Traders Assoc.", "role": "Market Merchant Guild", "tenure": "12 yrs", "status": "Verified"},
            ],
        }
    else:  # Suspicious Merchant
        data = {
            "name": "Quick Cash Trading",
            "name_hi": "क्विक कैश ट्रेडिंग",
            "name_te": "క్విక్ క్యాష్ ట్రేడింగ్",
            "name_ta": "குவிக் கேஷ் டிரேடிங்",
            "name_kn": "ಕ್ವಿಕ್ ಕ್ಯಾಶ್ ಟ್ರೇಡಿಂಗ್",
            "owner": "Anonymous Entity",
            "owner_hi": "अज्ञात इकाई",
            "owner_te": "అపరిచిత వ్యక్తి",
            "owner_ta": "அடையாளம் தெரியாத நபர்",
            "owner_kn": "ಅನಾಮಧೇಯ ವ್ಯಕ್ತಿ",
            "phone_masked": "+91 90041 •••09",
            "location": "Undisclosed, Mumbai",
            "location_hi": "अज्ञात, मुंबई",
            "location_te": "గుర్తించబడని ప్రదేశం, ముంబై",
            "location_ta": "குறிப்பிடப்படாத இடம், மும்பை",
            "location_kn": "ಗುರುತಿಸದ ಸ್ಥಳ, ಮುಂಬೈ",
            "type": "Trading",
            "type_hi": "ट्रेडिंग",
            "type_te": "ట్రేడింగ్",
            "type_ta": "வர்த்தகம்",
            "type_kn": "ಟ್ರೇಡಿಂಗ್",
            "credit_score": 385,
            "credit_label": "Poor - High Risk",
            "credit_label_hi": "खराब - उच्च जोखिम",
            "credit_label_te": "బలహీనమైనది - అధిక ప్రమాదం",
            "credit_label_ta": "மிக மோசமானது - அதிக ஆபத்து",
            "credit_label_kn": "ಕಳಪೆ - ಹೆಚ್ಚಿನ ಅಪಾಯ",
            "active_customers": 45,
            "max_loan": 0,
            "gst_limit": 4000000,
            "eligible_scheme": "None - Under Review",
            "scheme_amount": 0,
            "scheme_desc": "Account flagged for suspicious activity. No schemes available.",
            "scheme_desc_hi": "संदिग्ध गतिविधि के लिए खाता फ़्लैग किया गया। कोई योजना उपलब्ध नहीं।",
            "scheme_desc_te": "అనుమానాస్పద లావాదేవీల వల్ల ఖాతా నిలిపివేయబడింది. ఎటువంటి పథకాలు అందుబాటులో లేవు.",
            "scheme_desc_ta": "சந்தேகத்திற்கிடமான செயல்பாட்டிற்காக கணக்கு முடக்கப்பட்டுள்ளது. எந்த திட்டங்களும் இல்லை.",
            "scheme_desc_kn": "ಸಂದೇಹಾಸ್ಪದ ಚಟುವಟಿಕೆಗಾಗಿ ಖಾತೆಯನ್ನು ಫ್ಲ್ಯಾಗ್ ಮಾಡಲಾಗಿದೆ. ಯಾವುದೇ ಯೋಜನೆಗಳು ಲಭ್ಯವಿಲ್ಲ.",
            "monthly_revenues": [
                120000, 95000, 180000, 750000, 820000, 890000,
                950000, 1200000, 450000, 200000, 150000, 890000,
            ],
            "bahi_khata": {
                "Office Rent / कार्यालय किराया": 45000,
                "Electricity / बिजली": 5000,
                "Unknown Payments / अज्ञात भुगतान": 350000,
                "Cash Withdrawals / नकद निकासी": 280000,
                "Staff / कर्मचारी": 15000,
                "Commission / कमीशन": 125000,
                "Miscellaneous / विविध": 85000,
            },
            "anomalies": [
                {"time": "03:12", "amount": 49999, "from": "Shell_Corp_A", "flag": "Structuring: Amount just below ₹50K reporting threshold", "risk": "Critical"},
                {"time": "03:14", "amount": 49999, "from": "Shell_Corp_B", "flag": "Rapid Succession: Duplicate amount within 2 mins", "risk": "Critical"},
                {"time": "03:16", "amount": 49998, "from": "Shell_Corp_C", "flag": "Pattern Match: 3rd txn from linked entity", "risk": "Critical"},
                {"time": "04:30", "amount": 200000, "from": "Unknown_456", "flag": "Midnight Spike: ₹2L at 4:30 AM from unknown source", "risk": "High"},
                {"time": "12:00", "amount": 10, "from": "Micro_Burst", "flag": "Layering: 200 micro-txns of ₹10 in 30 mins", "risk": "Critical"},
            ],
            "profit_delta": "-102%",
            "customer_delta": "-12",
            "sthan_spot": "Nomadic Footprint / 7 Wards in 14 Days (Andheri, Kurla, Dadar, Thane)",
            "sthan_spot_hi": "अस्थिर पदचिह्न / 14 दिनों में 7 अलग-अलग वार्ड (मुंबई)",
            "sthan_spot_te": "సంచార గుర్తులు / 14 రోజుల్లో 7 విభిన్న వార్డులు (ముంబై)",
            "sthan_spot_ta": "நாடோடி தடம் / 14 நாட்களில் 7 வார்டுகள் (மும்பை)",
            "sthan_spot_kn": "ಅಲೆಮಾರಿ ಹೆಜ್ಜೆಗುರುತು / 14 ದಿನಗಳಲ್ಲಿ 7 ವಾರ್ಡ್‌ಗಳು (ಮುಂಬೈ)",
            "sthan_ward": "Unregistered / Multiple BMC Wards",
            "sthan_ward_hi": "अपंजीकृत / एकाधिक बीएमसी वार्ड",
            "sthan_ward_te": "నమోదుకానిది / బహుళ BMC వార్డులు",
            "sthan_ward_ta": "பதிவு செய்யப்படாதது / பல பிஎம்சி வார்டுகள்",
            "sthan_ward_kn": "ನೋಂದಾಯಿಸದ / ಬಹು ಬಿಎಂಸಿ ವಾರ್ಡ್‌ಗಳು",
            "sthan_coords": (19.0760, 72.8777),
            "sthan_days": 18,
            "sthan_start_date": "01 Sep 2026",
            "sthan_streak": 2,
            "sthan_geofence_adherence": 18.2,
            "sthan_tvc_status": "FLAGGED: Geo-Hopping Anomaly. No continuous vending presence found.",
            "sthan_tvc_status_hi": "फ्लैग किया गया: जियो-हॉपिंग विसंगति। कोई निरंतर वेंडिंग उपस्थिति नहीं मिली।",
            "sthan_tvc_status_te": "ఫ్లాగ్ చేయబడింది: జియో-హాపింగ్ విపత్తు. ఎటువంటి స్థిరమైన వ్యాపార ఉనికి కనుగొనబడలేదు.",
            "sthan_tvc_status_ta": "கண்டறியப்பட்டது: இருப்பிட விலகல் ஒழுங்கின்மை. நிலையான வியாபார இருப்பு எதுவும் இல்லை.",
            "sthan_tvc_status_kn": "ಫ್ಲ್ಯಾಗ್ ಮಾಡಲಾಗಿದೆ: ಜಿಯೋ-ಹಾಪಿಂಗ್ ಅಸಂಗತತೆ. ಯಾವುದೇ ನಿರಂತರ ಮಾರಾಟದ ಉಪಸ್ಥಿತಿ ಕಂಡುಬಂದಿಲ್ಲ.",
            "sthan_legal_shield": "Zero (Eviction Immunity Ineligible)",
            "sthan_legal_shield_hi": "शून्य (बेदखली सुरक्षा के लिए अयोग्य)",
            "sthan_legal_shield_te": "శూన్యం (తొలగింపు రక్షణకు అనర్హులు)",
            "sthan_legal_shield_ta": "பூஜ்ஜியம் (வெளியேற்ற எதிர்ப்பு தகுதியற்றது)",
            "sthan_legal_shield_kn": "ಶೂನ್ಯ ರಕ್ಷಣೆ (ಉಚ್ಚಾಟನೆ ವಿನಾಯಿತಿಗೆ ಅರ್ಹರಲ್ಲ)",
            "sthan_shield_score": 12,
            "sthan_svanidhi_tier": "Blocked / Shell Operation Risk",
            "sthan_svanidhi_tier_hi": "अवरुद्ध / शेल संचालन जोखिम",
            "sthan_svanidhi_tier_te": "బ్లాక్ చేయబడింది / షెల్ ఆపరేషన్ ప్రమాదం",
            "sthan_svanidhi_tier_ta": "முடக்கப்பட்டது / போலி நிறுவன ஆபத்து",
            "sthan_svanidhi_tier_kn": "ನಿರ್ಬಂಧಿಸಲಾಗಿದೆ / ಶೆಲ್ ಕಾರ್ಯಾಚರಣೆಯ ಅಪಾಯ",
            "sthan_peers": [],
        }

    return _finalize(data)


def get_credit_score_color(score):
    if score >= 750:
        return "#00c853"
    elif score >= 650:
        return "#ff9800"
    elif score >= 500:
        return "#ff5722"
    return "#f44336"


def get_credit_gauge(score):
    bar_color = get_credit_score_color(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"size": 56, "color": bar_color, "family": "Inter"}},
        gauge={
            "axis": {
                "range": [300, 900],
                "tickwidth": 2,
                "tickcolor": "#e0e0e0",
                "tickfont": {"size": 11, "color": "#999"},
                "dtick": 100,
            },
            "bar": {"color": bar_color, "thickness": 0.3},
            "bgcolor": "#f5f5f5",
            "borderwidth": 0,
            "steps": [
                {"range": [300, 500], "color": "#ffebee"},
                {"range": [500, 650], "color": "#fff3e0"},
                {"range": [650, 750], "color": "#fff8e1"},
                {"range": [750, 900], "color": "#e8f5e9"},
            ],
            "threshold": {"line": {"color": bar_color, "width": 4}, "thickness": 0.8, "value": score},
        },
    ))
    fig.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter"},
    )
    return fig


def delta_badge(pct_text, suffix, force_bad=False):
    negative = pct_text.strip().startswith("-")
    cls = "delta-negative" if (negative or force_bad) else "delta-positive"
    arrow = "&darr;" if negative else "&uarr;"
    return f'<span class="metric-delta {cls}">{arrow} {pct_text} {suffix}</span>'


def adjust_score(base, income, profit):
    ratio = profit / income if income > 0 else 0
    if ratio < 0:
        return max(300, base - 100)
    if ratio < 0.1:
        return max(300, base - 50)
    if ratio > 0.3:
        return min(900, base + 20)
    return base


def check_row(ok, label, detail):
    color = "#2e7d32" if ok else "#c62828"
    tag = "PASS" if ok else "FAIL"
    return (f'<div style="margin-bottom:6px;"><span style="color:{color};font-weight:700;">{tag}</span> '
            f'<b>{label}</b>: {detail}</div>')


def get_whatsapp_alert_html(owner, phone_masked, anomaly, lang):
    """Generates an official-looking, dark-themed mockup of an automated WhatsApp Business warning."""
    risk = anomaly["risk"]
    flag = anomaly["flag"]
    amt = inr(anomaly["amount"])
    time_str = anomaly["time"]
    
    if lang == "हिंदी":
        title = "🚨 *सुरक्षा चेतावनी: व्यापारस्कोर गार्ड*"
        greeting = f"नमस्ते {owner},"
        body = (
            f"आपके UPI खाते पर एक *{risk}* जोखिम विसंगति पाई गई है:\n\n"
            f"• *प्रकार:* {flag}\n"
            f"• *राशि:* {amt}\n"
            f"• *समय:* {time_str} (आज)\n\n"
            "यदि यह लेनदेन आपने अधिकृत नहीं किया है, तो तुरंत सुरक्षा सहायता और खाता सुरक्षित करने के लिए नीचे टैप करें।"
        )
        btn_text = "🔒 यूपीआई चैनल ब्लॉक करें"
    elif lang == "తెలుగు":
        title = "🚨 *భద్రతా హెచ్చరిక: వ్యాపారస్కోర్ గార్డ్*"
        greeting = f"నమస్తే {owner},"
        body = (
            f"మీ UPI ఖాతాలో ఒక *{risk}* ప్రమాదకర విపత్తు గుర్తించబడింది:\n\n"
            f"• *రకం:* {flag}\n"
            f"• *మొత్తం:* {amt}\n"
            f"• *సమయం:* {time_str} (ఈరోజు)\n\n"
            "ఈ లావాదేవీ మీ అనుమతి లేకుండా జరిగి ఉంటే, వెంటనే UPI ఛానెల్‌ను బ్లాక్ చేయడానికి క్రింద నొక్కండి."
        )
        btn_text = "🔒 UPI ఛానెల్‌ని బ్లాక్ చేయండి"
    elif lang == "தமிழ்":
        title = "🚨 *பாதுகாப்பு எச்சரிக்கை: வியாபார்ஸ்கோர் கார்டு*"
        greeting = f"வணக்கம் {owner},"
        body = (
            f"உங்கள் UPI கணக்கில் ஒரு *{risk}* ஆபத்துள்ள ஒழுங்கின்மை கண்டறியப்பட்டுள்ளது:\n\n"
            f"• *வகை:* {flag}\n"
            f"• *தொகை:* {amt}\n"
            f"• *நேரம்:* {time_str} (இன்று)\n\n"
            "இந்த பரிவர்த்தனை உங்களால் அங்கீகரிக்கப்படவில்லை எனில், உடனடியாக UPI சேனலை முடக்க கீழே தட்டவும்."
        )
        btn_text = "🔒 UPI சேனலை முடக்கு"
    elif lang == "ಕನ್ನಡ":
        title = "🚨 *ಭದ್ರತಾ ಎಚ್ಚರಿಕೆ: ವ್ಯಾಪಾರಸ್ಕೋರ್ ಗಾರ್ಡ್*"
        greeting = f"ನಮಸ್ಕಾರ {owner},"
        body = (
            f"ನಿಮ್ಮ UPI ಖಾತೆಯಲ್ಲಿ ಒಂದು *{risk}* ಅಪಾಯಕಾರಿ ಅಸಂಗತತೆ ಕಂಡುಬಂದಿದೆ:\n\n"
            f"• *ವಿಧ:* {flag}\n"
            f"• *ಮೊತ್ತ:* {amt}\n"
            f"• *ಸಮಯ:* {time_str} (ಇಂದು)\n\n"
            "ಈ ವಹಿವಾಟು ನಿಮ್ಮ ಅನುಮತಿಯಿಲ್ಲದೆ ನಡೆದಿದ್ದರೆ, ತಕ್ಷಣವೇ ನಿಮ್ಮ UPI ಚಾನಲ್ ಅನ್ನು ನಿರ್ಬಂಧಿಸಲು ಕೆಳಗೆ ಟ್ಯಾಪ್ ಮಾಡಿ."
        )
        btn_text = "🔒 UPI ಚಾನಲ್ ನಿರ್ಬಂಧಿಸಿ"
    else:
        title = "🚨 *VyaparScore Security Warning*"
        greeting = f"Dear {owner},"
        body = (
            f"We detected a *{risk}* risk anomaly on your registered UPI stream:\n\n"
            f"• *Alert:* {flag}\n"
            f"• *Amount:* {amt}\n"
            f"• *Time:* {time_str} (Today)\n\n"
            "If this was not authorized by you, please protect your account immediately."
        )
        btn_text = "🔒 Temporary Lock UPI Channel"

    return f"""
    <div style="background-color: #0b141a; border-radius: 12px; padding: 16px; border: 1px solid #202c33; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 450px; margin: 12px auto; box-shadow: 0 4px 16px rgba(0,0,0,0.3);">
        <!-- WhatsApp Header -->
        <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 10px; border-bottom: 1px solid #222d34; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 32px; height: 32px; background-color: #00a884; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.85rem;">VS</div>
                <div>
                    <div style="font-size: 0.85rem; font-weight: 700; color: #e9edef;">VyaparScore Guard ✓</div>
                    <div style="font-size: 0.68rem; color: #8696a0;">Official Business Account</div>
                </div>
            </div>
            <span style="font-size: 0.72rem; color: #8696a0;">{phone_masked}</span>
        </div>
        
        <!-- WhatsApp Chat Area -->
        <div style="display: flex; flex-direction: column; gap: 8px;">
            <div style="background-color: #005c4b; border-radius: 8px 8px 8px 0px; padding: 10px 12px; position: relative; max-width: 90%; align-self: flex-start; border: 1px solid #005c4b; box-shadow: 0 1px 2px rgba(0,0,0,0.15);">
                <div style="color: #e9edef; font-size: 0.85rem; font-weight: 700; margin-bottom: 4px;">{title}</div>
                <div style="color: #e9edef; font-size: 0.8rem; margin-bottom: 4px;">{greeting}</div>
                <div style="color: #e9edef; font-size: 0.8rem; white-space: pre-wrap; line-height: 1.45;">{body}</div>
                
                <!-- Quick Reply Button -->
                <div style="margin-top: 12px; background-color: rgba(255,255,255,0.08); border-radius: 6px; text-align: center; padding: 8px 0; border: 1px solid rgba(255,255,255,0.15); transition: background 0.2s;">
                    <span style="color: #53bdeb; font-size: 0.82rem; font-weight: 700;">{btn_text}</span>
                </div>
                
                <div style="text-align: right; font-size: 0.62rem; color: rgba(255,255,255,0.6); margin-top: 6px; display: flex; justify-content: flex-end; align-items: center; gap: 3px;">
                    <span>{time_str}</span>
                    <span style="color: #53bdeb; font-weight: bold; font-size: 0.7rem;">✓✓</span>
                </div>
            </div>
        </div>
    </div>
    """


# ============================================================
# SIDEBAR NAVIGATION & CONTROLS
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px 0;">
        <div style="font-size: 1.4rem; font-weight: 800; color: #69f0ae; letter-spacing: -0.5px;">VyaparScore</div>
        <div style="font-size: 0.7rem; font-weight: 400; color: #a8e6cf; letter-spacing: 1px; text-transform: uppercase; margin-top: 4px;">
            Bharat's Micro-Merchant Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    lang_selection = st.radio(
        "Language / ಭಾಷೆ / மொழி / భాష / भाषा",
        ["English", "हिंदी", "తెలుగు", "தமிழ்", "ಕನ್ನಡ"],
        horizontal=True,
        key="lang_toggle"
    )

    st.markdown("---")

    # Navigation Section
    st.markdown(f'<div class="sidebar-section-title">🧭 {t("Navigation", "नेविगेशन", "నావిగేషన్", "வழிசெலுத்தல்", "ನ್ಯಾವಿಗೇಷನ್")}</div>', unsafe_allow_html=True)

    nav_options = [
        "Overview",
        "Cash Flow",
        "Bahi-Khata OCR *",
        "Fraud Guard *",
        "Loan & Report",
        "Sthan Log 📍"
    ]

    nav_labels = {
        "Overview": t("Overview", "अवलोकन", "అవలోకనం", "கண்ணோட்டம்", "ಅವಲೋಕನ"),
        "Cash Flow": t("Cash Flow", "नकदी प्रवाह", "నగదు ప్రవాహం", "பணப்புழக்கம்", "ನಗದು ಹರಿವು"),
        "Bahi-Khata OCR *": t("Bahi-Khata OCR *", "बही-खाता OCR *", "బహి-ఖాతా OCR *", "பஹி-காதா OCR *", "ಬಹಿ-ಖಾತಾ OCR *"),
        "Fraud Guard *": t("Fraud Guard *", "फ्रॉड गार्ड *", "ఫ్రాడ్ గార్డ్ *", "மோசடி தடுப்பு *", "ಫ್ರಾಡ್ ಗಾರ್ಡ್ *"),
        "Loan & Report": t("Loan & Report", "लोन और रिपोर्ट", "రుణం & నివేదిక", "கடன் & அறிக்கை", "ಸಾಲ ಮತ್ತು ವರದಿ"),
        "Sthan Log 📍": t("Sthan Log 📍", "स्थान लॉग 📍", "స్థాన్ లాగ్ 📍", "ஸ்தான் லாக் 📍", "ಸ್ಥಾನ್ ಲಾಗ್ 📍")
    }

    selected_nav = st.radio(
        "Navigation Select",
        nav_options,
        format_func=lambda x: nav_labels[x],
        key="navigation_tabs",
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Merchant Selection
    st.markdown(f'**{t("Select Merchant", "व्यापारी चुनें", "వ్యాపారిని ఎంచుకోండి", "வணிகரைத் தேர்ந்தெடுக்கவும்", "ವ್ಯಾಪಾರಿಯನ್ನು ಆಯ್ಕೆಮಾಡಿ")}**')
    
    def merchant_formatter(key):
        m_item = get_merchant_data(key)
        selected_lang = st.session_state.get("lang_toggle", "English")
        if selected_lang == "हिंदी":
            return m_item["name_hi"]
        elif selected_lang == "తెలుగు":
            return m_item["name_te"]
        elif selected_lang == "தமிழ்":
            return m_item["name_ta"]
        elif selected_lang == "ಕನ್ನಡ":
            return m_item["name_kn"]
        return m_item["name"]

    merchant = st.selectbox(
        "Merchant",
        MERCHANT_KEYS,
        key="merchant_select",
        label_visibility="collapsed",
        format_func=merchant_formatter,
    )

    st.markdown("---")

    merchant_data = get_merchant_data(merchant)
    display_name = t(merchant_data["name"], merchant_data["name_hi"], merchant_data.get("name_te"), merchant_data.get("name_ta"), merchant_data.get("name_kn"))
    display_owner = t(merchant_data["owner"], merchant_data["owner_hi"], merchant_data.get("owner_te"), merchant_data.get("owner_ta"), merchant_data.get("owner_kn"))
    display_location = t(merchant_data["location"], merchant_data["location_hi"], merchant_data.get("location_te"), merchant_data.get("location_ta"), merchant_data.get("location_kn"))
    display_type = t(merchant_data["type"], merchant_data["type_hi"], merchant_data.get("type_te"), merchant_data.get("type_ta"), merchant_data.get("type_kn"))

    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.08); border-radius: 12px; padding: 16px; margin: 8px 0;">
        <div style="font-size: 1.1rem; font-weight: 700; color: #69f0ae; margin-bottom: 12px;">{display_name}</div>
        <div style="font-size: 0.8rem; color: #a8e6cf; margin-bottom: 6px;">{t("Owner", "मालिक", "యజమాని", "உரிமையாளர்", "ಮಾಲೀಕರು")}: {display_owner}</div>
        <div style="font-size: 0.8rem; color: #a8e6cf; margin-bottom: 6px;">{t("Location", "स्थान", "స్థలం", "இடம்", "ಸ್ಥಳ")}: {display_location}</div>
        <div style="font-size: 0.8rem; color: #a8e6cf;">{t("Type", "प्रकार", "రకం", "வகை", "ಪ್ರಕಾರ")}: {display_type}</div>
    </div>
    <div style="text-align: center; font-size: 0.7rem; color: #a8e6cf; margin-top: 20px;">
        {t("Last Updated", "अंतिम अपडेट", "చివరిగా నవీకరించబడింది", "கடைசியಾಗப் புதுப்பிக்கப்பட்டது", "ಕೊನೆಯದಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ")} (IST): {NOW.strftime('%d %b %Y, %I:%M %p')}
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# MAIN CONTENT
# ============================================================
md = merchant_data
is_suspicious = merchant == "Suspicious Merchant"

title_text = t(
    "VyaparScore: Bharat's Micro-Merchant Credit & Fraud Guard",
    "व्यापारस्कोर: भारत का माइक्रो-मर्चेंट क्रेडिट और फ्रॉड गार्ड",
    "వ్యాపారస్కోర్: భారతీయ సూక్ష్మ వ్యాపారుల క్రెడిట్ & ఫ్రాడ్ గార్డ్",
    "வியாபார்ஸ்கோர்: பாரதத்தின் மைக்ரோ-வணிகர் கடன் மற்றும் மோசடி தடுப்பு",
    "ವ್ಯಾಪಾರಸ್ಕೋರ್: ಭಾರತದ ಸೂಕ್ಷ್ಮ ಉದ್ಯಮಿಗಳ ಕ್ರೆಡಿಟ್ ಮತ್ತು ಫ್ರಾಡ್ ಗಾರ್ಡ್"
)
subtitle_text = t(
    "AI-Powered Credit Intelligence for India's Micro-Merchants",
    "सूक्ष्म व्यापारियों के लिए AI-संचालित क्रेडिट इंटेलिजेंस",
    "భారతీయ సూక్ష్మ వ్యాపారుల కోసం AI-ఆధారిత క్రెడిట్ ఇంటెలిజెన్స్",
    "இந்தியாவின் மைக்ரோ-வணிகர்களுக்கான AI-ஆற்றல் கடன் நுண்ணறிவு",
    "ಭಾರತದ ಸೂಕ್ಷ್ಮ ಉದ್ಯಮಿಗಳಿಗಾಗಿ AI-ಚಾಲಿತ ಕ್ರೆಡಿಟ್ ಇಂಟೆಲಿಜೆನ್ಸ್"
)

st.markdown(f'<div class="main-title">{title_text}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-subtitle">{subtitle_text}</div>', unsafe_allow_html=True)

# Elegant Active Tab Header Indicator Bar
st.markdown(f"""
<div class="top-nav-bar">
    <div class="active-tab-badge">
        <span class="active-tab-dot"></span>
        <span style="font-weight: 700; color: #0d3b28; font-size: 0.95rem;">{nav_labels[selected_nav]}</span>
    </div>
    <div style="font-size: 0.82rem; color: #6b7c74; font-weight: 500;">
        {display_name} • {display_owner} ({display_type})
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# CONDITIONAL VIEW RENDERING
# ============================================================

# --- TAB 1: OVERVIEW & CREDIT HEALTH ---
if selected_nav == "Overview":
    col_gauge, col_metrics = st.columns([1, 2])

    with col_gauge:
        score_label = t(md["credit_label"], md["credit_label_hi"], md.get("credit_label_te"), md.get("credit_label_ta"), md.get("credit_label_kn"))
        score_color = get_credit_score_color(md["credit_score"])

        st.markdown(
            f'<div class="gauge-title">{t("VyaparScore Credit Rating", "व्यापार क्रेडिट स्कोर", "వ్యాపారస్కోర్ క్రెడిట్ రేటింగ్", "வியாபார்ஸ்கோர் கடன் மதிப்பீடு", "ವ್ಯಾಪಾರಸ್ಕೋರ್ ಕ್ರೆಡಿಟ್ ರೇಟಿಂಗ್")}</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(get_credit_gauge(md["credit_score"]), key="credit_gauge", **STRETCH)
        st.markdown(f"""
        <div style="text-align: center; margin-top: -16px;">
            <span style="background: {score_color}20; color: {score_color}; padding: 6px 20px; border-radius: 8px;
                         font-weight: 700; font-size: 0.95rem; border: 2px solid {score_color}40;">{score_label}</span>
        </div>
        """, unsafe_allow_html=True)

    with col_metrics:
        rev_abnormal = abs(md["revenue_pct"]) > 100
        mc1, mc2 = st.columns(2)
        with mc1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{t("Monthly UPI Revenue", "मासिक UPI राजस्व", "నెలవారీ UPI ఆదాయం", "மாதாந்திர UPI வருவாய்", "ಮಾಸಿಕ UPI ಆದಾಯ")}</div>
                <div class="metric-value">{inr(md['monthly_revenue'])}</div>
                {delta_badge(md['revenue_delta'], t("vs last month", "पिछले माह से", "గత నెలతో పోలిస్తే", "கடந்த மாதத்துடன் ஒப்பிடுகையில்", "ಕಳೆದ ತಿಂಗಳಿಗೆ ಹೋಲಿಸಿದರೆ") + (t(" (abnormal jump)", " (असामान्य उछाल)", " (అసాధారణ పెరుగుదల)", " (அசாதாரண உயர்வு)", " (ಅಸಹಜ ಏರಿಕೆ)") if rev_abnormal else ""), force_bad=rev_abnormal)}
            </div>
            """, unsafe_allow_html=True)

        with mc2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{t("Net Profit", "शुद्ध लाभ", "నికర లాభం", "நிகர லாபம்", "ನಿವ್ವಳ ಲಾಭ")}</div>
                <div class="metric-value">{inr(md['net_profit'])}</div>
                {delta_badge(md['profit_delta'], t("vs last month", "पिछले माह से", "గత నెలతో పోలిస్తే", "கடந்த மாதத்துடன் ஒப்பிடுகையில்", "ಕಳೆದ ತಿಂಗಳಿಗೆ ಹೋಲಿಸಿದರೆ"))}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)

        mc3, mc4 = st.columns(2)
        with mc3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{t("Active Customers", "सक्रिय ग्राहक", "క్రియాశీల వినియోగదారులు", "செயலில் உள்ள வாடிக்கையாளர்கள்", "ಸಕ್ರಿಯ ಗ್ರಾಹಕರು")}</div>
                <div class="metric-value">{md['active_customers']:,}</div>
                {delta_badge(md['customer_delta'], t("this month", "इस माह", "ఈ నెల", "இந்த மாதம்", "ಈ ತಿಂಗಳು"))}
            </div>
            """, unsafe_allow_html=True)

        with mc4:
            has_loan = md["max_loan"] > 0
            loan_display = inr(md["max_loan"]) if has_loan else t("₹0 (Blocked)", "₹0 (अवरुद्ध)", "₹0 (బ్లాక్ చేయబడింది)", "₹0 (முடக்கப்பட்டது)", "₹0 (ನಿರ್ಬಂಧಿಸಲಾಗಿದೆ)")
            loan_color = "#0d3b28" if has_loan else "#f44336"
            badge_cls = "delta-positive" if has_loan else "delta-negative"
            badge_txt = t("Pre-approved", "पूर्व-स्वीकृत", "ముందుగా ఆమోదించబడింది", "முன் அங்கீகரிக்கப்பட்டது", "ಪೂರ್ವ-ಅನುಮೋದಿತ") if has_loan else t("Under Review", "समीक्षा में", "పరిశీలనలో ఉంది", "மதிப்பாய்வில் உள்ளது", "ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{t("Max Loan Limit", "अधिकतम ऋण सीमा", "గరిష్ట రుణ పరిమితి", "அதிகபட்ச கடன் வரம்பு", "ಗರಿಷ್ಠ ಸಾಲದ मಿತಿ")}</div>
                <div class="metric-value" style="color: {loan_color}">{loan_display}</div>
                <span class="metric-delta {badge_cls}">{badge_txt}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    gst_col1, gst_col2 = st.columns([2, 1])

    with gst_col1:
        limit_lakh = md["gst_limit"] / 100000
        gst_title = t("GST Tax Safety Meter", "GST कर सुरक्षा मीटर", "GST పన్ను భద్రతా మీటర్", "ஜிஎஸ்டி வரி பாதுகாப்பு மீட்டர்", "ಜಿಎಸ್ಟಿ ತೆರಿಗೆ ಸುರಕ್ಷತಾ ಮೀಟರ್")
        gst_subtitle = t(
            f"Annual Turnover vs ₹{limit_lakh:.0f} Lakh GST Threshold",
            f"वार्षिक टर्नओवर बनाम ₹{limit_lakh:.0f} लाख GST सीमा",
            f"వార్షిక టర్నోవర్ vs ₹{limit_lakh:.0f} లక్షల GST పరిమితి",
            f"ஆண்டு விற்றுமுதல் vs ₹{limit_lakh:.0f} லட்சம் ஜிஎஸ்டி வரம்பு",
            f"ವಾರ್ಷಿಕ ವಹಿವಾಟು vs ₹{limit_lakh:.0f} ಲಕ್ಷ ಜಿಎಸ್ಟಿ ಮಿತಿ"
        )

        gst_pct_raw = md["gst_revenue_ytd"] / md["gst_limit"]
        gst_remaining = max(md["gst_limit"] - md["gst_revenue_ytd"], 0)
        gst_over = max(md["gst_revenue_ytd"] - md["gst_limit"], 0)

        if gst_pct_raw > 1:
            gst_status_color = "#f44336"
            gst_status = t("THRESHOLD EXCEEDED: GST registration required", "सीमा पार: GST पंजीकरण आवश्यक", "పరిమితి దాటింది: GST నమోదు అవసరం", "வரம்பு தாண்டியது: ஜிஎஸ்டி பதிவு தேவை", "ಮಿತಿ ಮೀರಿದೆ: ಜಿಎಸ್ಟಿ ನೋಂದಣಿ ಅಗತ್ಯವಿದೆ")
        elif gst_pct_raw >= 0.95:
            gst_status_color = "#f44336"
            gst_status = t("DANGER: Very close to GST threshold", "खतरा: GST सीमा के बहुत करीब", "ప్రమాదం: GST పరిమితికి చాలా దగ్గరగా ఉంది", "ஆபத்து: ஜிஎஸ்டி வரம்பிற்கு மிக அருகில் உள்ளது", "ಅಪಾಯ: ಜಿಎಸ್ಟಿ ಮಿತಿಗೆ ಅತ್ಯಂತ ಹತ್ತಿರದಲ್ಲಿದೆ")
        elif gst_pct_raw >= 0.75:
            gst_status_color = "#ff9800"
            gst_status = t("CAUTION: Approaching GST threshold", "सावधान: GST सीमा निकट आ रही है", "హెచ్చరిక: GST పరిమితికి చేరువలో ఉంది", "எச்சரிக்கை: ஜிஎஸ்டி வரம்பை நெருங்குகிறது", "ಎಚ್ಚರಿಕೆ: ಜಿಎಸ್ಟಿ ಮಿತಿಯನ್ನು ಸಮೀಪಿಸುತ್ತಿದೆ")
        else:
            gst_status_color = "#00a844"
            gst_status = t("SAFE: Well below GST threshold", "सुरक्षित: GST सीमा से काफी दूर", "సురక్షితం: GST పరిమితి కంటే చాలా తక్కువగా ఉంది", "பாதுகாப்பானது: ஜிஎஸ்டி வரம்பிற்கு மிகக் கீழே உள்ளது", "ಸುರಕ್ಷಿತ: ಜಿಎಸ್ಟಿ ಮಿತಿಗಿಂತ ಸಾಕಷ್ಟು ಕೆಳಗಿದೆ")

        st.markdown(f"""
        <div class="gst-meter-container">
            <div class="gst-title">{gst_title}</div>
            <div style="font-size: 0.85rem; color: #6b7c74; margin-bottom: 12px;">{gst_subtitle}</div>
        </div>
        """, unsafe_allow_html=True)

        st.progress(min(gst_pct_raw, 1.0))

        headroom_line = (
            f'{t("Exceeded by", "सीमा से अधिक", "మించిన మొత్తం", "கடந்த தொகை", "ಮೀರಿದ ಮೊತ್ತ")}: {inr(gst_over)}' if gst_over > 0
            else f'{t("Remaining Headroom", "शेष सीमा", "మిగిలిన పరిమితి", "மீதமுள்ள வரம்பு", "ಉಳಿದ ಮಿತಿ")}: {inr(gst_remaining)}'
        )
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.85rem;">
            <span style="color: #0d3b28; font-weight: 600;">{inr(md['gst_revenue_ytd'])} / {inr(md['gst_limit'])}</span>
            <span style="color: {gst_status_color}; font-weight: 700;">{gst_pct_raw*100:.1f}% {t("Used", "उपयोग", "ఉపయోగించబడింది", "பயன்படுத்தப்பட்டது", "ಬಳಸಲಾಗಿದೆ")}</span>
        </div>
        <div style="margin-top: 8px; font-size: 0.85rem; color: {gst_status_color}; font-weight: 600;">{gst_status}</div>
        <div style="margin-top: 4px; font-size: 0.8rem; color: #6b7c74;">{headroom_line}</div>
        """, unsafe_allow_html=True)

    with gst_col2:
        scheme_title = t("Govt Scheme Finder", "सरकारी योजना", "ప్రభుత్వ పథకాల అన్వేషణ", "அரசு திட்ட கண்டறிதல்", "ಸರ್ಕಾರಿ ಯೋಜನೆ ಶೋಧಕ")
        scheme_desc = t(md["scheme_desc"], md["scheme_desc_hi"], md.get("scheme_desc_te"), md.get("scheme_desc_ta"), md.get("scheme_desc_kn"))

        if md["scheme_amount"] > 0:
            st.markdown(f"""
            <div class="scheme-card">
                <div class="scheme-title">{scheme_title}</div>
                <div style="font-size: 0.85rem; color: #2e7d32; margin-bottom: 8px;">
                    {t("Based on your profile, you are eligible for:", "आपकी प्रोफाइल के आधार पर, आप पात्र हैं:", "మీ ప్రొఫైల్ ఆధారంగా, మీరు అర్హులు:", "உங்கள் சுயவிவரத்தின் அடிப்படையில், நீங்கள் தகுதியுடையவர்:", "ನಿಮ್ಮ ಪ್ರೊಫೈಲ್ ಆಧರಿಸಿ, ನೀವು ಅರ್ಹರಾಗಿದ್ದೀರಿ:")}
                </div>
                <div style="font-size: 1rem; font-weight: 700; color: #1b5e20; margin-bottom: 4px;">{md['eligible_scheme']}</div>
                <div class="scheme-amount">{inr(md['scheme_amount'])}</div>
                <div style="font-size: 0.8rem; color: #2e7d32; margin-top: 4px;">{scheme_desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(t("Apply Now", "आवेदन करें", "ఇప్పుడే దరఖాస్తు చేసుకోండి", "இப்போதே விண்ணப்பிக்கவும்", "ಈಗಲೇ ಅರ್ಜಿ ಹಾಕಿ"), key="scheme_apply"):
                st.success(t(
                    "Application submitted successfully! You'll receive an SMS update within 48 hours.",
                    "आवेदन सफलतापूर्वक जमा! 48 घंटे में SMS अपडेट मिलेगा।",
                    "దరఖాస్తు విజయవంతంగా సమర్పించబడింది! 48 గంటల్లో SMS అప్‌డేట్ వస్తుంది.",
                    "விண்ணப்பம் வெற்றிகரமாக சமர்ப்பிக்கப்பட்டது! 48 மணிநேரத்திற்குள் எஸ்எம்எஸ் தகவல் வரும்.",
                    "ಅರ್ಜಿಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಸಲ್ಲಿಸಲಾಗಿದೆ! 48 ಗಂಟೆಗಳ ಒಳಗೆ ಎಸ್‌ಎಂಎಸ್ ನವೀಕರಣವನ್ನು ಸ್ವೀಕರಿಸುತ್ತೀರಿ."
                ))
        else:
            st.markdown(f"""
            <div class="alert-danger">
                <div style="font-weight: 700; margin-bottom: 4px;">{scheme_title}</div>
                <div style="font-size: 0.85rem;">{scheme_desc}</div>
            </div>
            """, unsafe_allow_html=True)


# --- TAB 2: SEASONALITY & CASH FLOW ---
elif selected_nav == "Cash Flow":
    st.markdown(f'<div class="section-header">{t("Seasonal Revenue Analysis", "मौसमी राजस्व विश्लेषण", "ఋతువుల ఆదాయ విశ్లేషణ", "பருவகால வருவாய் பகுப்பாய்வு", "ಋತುಮಾನದ ಆದಾಯ ವಿಶ್ಲೇಷಣೆ")}</div>',
                unsafe_allow_html=True)

    revs = md["monthly_revenues"]
    
    selected_lang = st.session_state.get("lang_toggle", "English")
    if selected_lang == "हिंदी":
        display_months = MONTHS_HI
    elif selected_lang == "తెలుగు":
        display_months = MONTHS_TE
    elif selected_lang == "தமிழ்":
        display_months = MONTHS_TA
    elif selected_lang == "ಕನ್ನಡ":
        display_months = MONTHS_KN
    else:
        display_months = MONTHS

    max_idx = int(np.argmax(revs))
    min_idx = int(np.argmin(revs))
    peak_is_festive = max_idx in FESTIVE_IDX
    low_is_monsoon = min_idx in MONSOON_IDX

    colors = []
    for i in range(len(revs)):
        if i in FESTIVE_IDX:
            colors.append("#00c853")
        elif i in MONSOON_IDX:
            colors.append("#ff9800")
        else:
            colors.append("#1de9b6")
    if not peak_is_festive:
        colors[max_idx] = "#f44336"  # peak outside festive months is a red flag, not seasonality

    fig_rev = go.Figure()
    fig_rev.add_trace(go.Bar(
        x=display_months,
        y=revs,
        marker_color=colors,
        marker_line_width=0,
        text=[f"₹{r/1000:.0f}K" for r in revs],
        textposition="outside",
        textfont=dict(size=11, color="#0d3b28", family="Inter"),
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
    ))

    if peak_is_festive:
        peak_label, peak_color, peak_bg = t("Festive Peak (Diwali)", "त्योहारी चरम (दिवाली)", "పండుగ సీజన్ గరిష్టం (దీపావళి)", "பண்டிகை கால உச்சம் (தீபாவளி)", "ಹಬ್ಬದ ಗರಿಷ್ಠ ಆದಾಯ (ದೀಪಾವಳಿ)"), "#00c853", "#e8f5e9"
    else:
        peak_label, peak_color, peak_bg = t("Abnormal Spike", "असामान्य उछाल", "అసాధారణ పెరుగుదల", "அசாதாரண உயர்வு", "ಅಸಹಜ ಏರಿಕೆ"), "#f44336", "#ffebee"
    if low_is_monsoon:
        low_label = t("Monsoon Slump", "मानसून मंदी", "వర్షాకాలం తగ్గుదల", "மழைக்கால மந்தநிலை", "ಮಳೆಗಾಲದ ಕುಸಿತ")
    else:
        low_label = t("Lowest Month", "सबसे कम माह", "అతి తక్కువ ఆదాయం ఉన్న నెల", "மிகக் குறைந்த மாதாந்திர வருவாய்", "ಅತಿ ಕಡಿಮೆ ಆದಾಯದ ತಿಂಗಳು")

    for idx, label, color, bg in [
        (max_idx, peak_label, peak_color, peak_bg),
        (min_idx, low_label, "#ff9800", "#fff3e0"),
    ]:
        fig_rev.add_annotation(
            x=display_months[idx], y=revs[idx], text=label,
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor=color,
            font=dict(size=12, color="#0d3b28", family="Inter"),
            bgcolor=bg, bordercolor=color, borderwidth=2, borderpad=6,
            ax=0, ay=-50,
        )

    fig_rev.update_layout(
        xaxis_title=t("Month", "महीना", "నెల", "மாதம்", "ತಿಂಗಳು"),
        yaxis_title=t("Revenue (₹)", "राजस्व (₹)", "ఆదాయం (₹)", "வருவாய் (₹)", "ಆದಾಯ (₹)"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#0d3b28"),
        height=450,
        margin=dict(l=60, r=20, t=60, b=60),
        yaxis=dict(gridcolor="#f0f0f0", gridwidth=1),
        xaxis=dict(showgrid=False),
        showlegend=False,
    )
    st.plotly_chart(fig_rev, key="revenue_chart", **STRETCH)

    legend_items = [
        ("#00c853", t("Festive Season", "त्योहारी सीज़न", "పండుగ కాలం", "பண்டிகை காலம்", "ಹಬ್ಬದ ಸೀಸನ್")),
        ("#ff9800", t("Monsoon Period", "मानसून काल", "వర్షాకాలం", "மழைக்காலம்", "ಮಳೆಗಾಲದ ಅವಧಿ")),
        ("#1de9b6", t("Normal", "सामान्य", "సాధారణం", "சாதாரண", "ಸಾಮಾನ್ಯ")),
    ]
    if not peak_is_festive:
        legend_items.append(("#f44336", t("Abnormal Spike", "असामान्य उछाल", "అసాధారణ పెరుగుదల", "அசாதாரண உயர்வு", "ಅಸಹಜ ಏರಿಕೆ")))
    legend_html = "".join(
        f'<span style="font-size: 0.8rem; color: #666;">'
        f'<span style="display: inline-block; width: 12px; height: 12px; background: {c}; border-radius: 3px; margin-right: 4px;"></span>{label}</span>'
        for c, label in legend_items
    )
    st.markdown(
        f'<div style="display: flex; gap: 24px; justify-content: center; margin-top: -8px; margin-bottom: 16px;">{legend_html}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">{t("Cash Flow Forecast", "नकदी प्रवाह पूर्वानुमान", "నగదు ప్రవాహం అంచనా", "பணப்புழக்க முன்னறிவிப்பு", "ನಗದು ಹರಿವಿನ ಮುನ್ಸೂಚನೆ")}</div>',
                unsafe_allow_html=True)

    fc1, fc2 = st.columns(2)

    with fc1:
        if is_suspicious:
            st.markdown(f"""
            <div class="alert-danger">
                <div style="font-weight: 700; font-size: 1rem; margin-bottom: 8px;">{t("CRITICAL WARNING", "गंभीर चेतावनी", "తీव्रమైన హెచ్చరిక", "முக்கிய எச்சரிக்கை", "ಗಂಭೀರ ಎಚ್ಚರಿಕೆ")}</div>
                <div style="font-size: 0.9rem;">
                    {t(
                        "High probability of negative cash flow in the next 7 days. Account under review due to irregular transaction patterns.",
                        "अगले 7 दिनों में नकारात्मक नकदी प्रवाह की उच्च संभावना। अनियमित लेनदेन पैटर्न के कारण खाता समीक्षा में।",
                        "రాబోయే 7 రోజుల్లో ప్రతికూల నగదు ప్రవాహం వచ్చే అవకాశం ఉంది. లావాదేవీల క్రమరాహిత్యం కారణంగా ఖాతా పరిశీలనలో ఉంది.",
                        "அடுத்த 7 நாட்களில் எதிர்மறையான பணப்புழக்கத்திற்கு அதிக வாய்ப்பு உள்ளது. ஒழுங்கற்ற பரிவர்த்தனை காரணமாக கணக்கு மதிப்பாய்வில் உள்ளது.",
                        "ಮುಂದಿನ 7 ದಿನಗಳಲ್ಲಿ ಋಣಾತ್ಮಕ ನಗದು ಹರಿವಿನ ಹೆಚ್ಚಿನ ಸಂಭವನೀಯತೆ ಇದೆ. ಅನಿಯಮಿತ ವಹಿವಾಟು ಮಾದರಿಯಿಂದಾಗಿ ಖಾತೆಯು ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ."
                    )}
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif merchant == "Sharma Kirana":
            st.markdown(f"""
            <div class="alert-warning">
                <div style="font-weight: 700; font-size: 1rem; margin-bottom: 8px;">{t("CAUTION", "सावधान", "జాగ్రత్త", "எச்சரிக்கை", "ಎಚ್ಚರಿಕೆ")}</div>
                <div style="font-size: 0.9rem;">
                    {t(
                        "Warning: High probability of negative cash flow in the next 14 days based on inventory cycle. Consider a ₹50,000 working capital loan for festive stocking.",
                        "चेतावनी: इन्वेंट्री चक्र के आधार पर अगले 14 दिनों में नकारात्मक नकदी प्रवाह की उच्च संभावना। त्योहारी स्टॉक के लिए ₹50,000 कार्यशील पूंजी ऋण पर विचार करें।",
                        "హెచ్చరిక: ఇన్వెంటరీ సైకిల్ ఆధారంగా రాబోయే 14 రోజుల్లో ప్రతికూల నగదు ప్రవాహం వచ్చే అవకాశం ఉంది. పండుగ స్టాక్ కోసం ₹50,000 వర్కింగ్ క్యాపిటల్ లోన్ తీసుకోండి.",
                        "எச்சரிக்கை: இருப்பு சுழற்சியின் அடிப்படையில் அடுத்த 14 நாட்களில் எதிர்மறையான பணப்புழக்கத்திற்கு அதிக வாய்ப்பு உள்ளது. பண்டிகை கால இருப்புக்கு ₹50,000 மூலதன கடனை பரிசீலிக்கவும்.",
                        "ಎಚ್ಚರಿಕೆ: ದಾಸ್ತಾನು ಚಕ್ರದ ಆಧಾರದ ಮೇಲೆ ಮುಂದಿನ 14 ದಿನಗಳಲ್ಲಿ ಋಣಾತ್ಮಕ ನಗದು ಹರಿವಿನ ಹೆಚ್ಚಿನ ಸಂಭವನೀಯತೆ ಇದೆ. ಹಬ್ಬದ ಸ್ಟಾಕಿಂಗ್ಗಾಗಿ ₹50,000 ಕಾರ್ಯಶೀಲ ಬಂಡವಾಳ ಸಾಲವನ್ನು ಪರಿಗಣಿಸಿ."
                    )}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert-success">
                <div style="font-weight: 700; font-size: 1rem; margin-bottom: 8px;">{t("HEALTHY CASH FLOW", "स्वस्थ नकदी प्रवाह", "ఆరోగ్యకరమైన నగదు ప్రవాహం", "ஆரோக்கியமான பணப்புழக்கம்", "ಆರೋಗ್ಯಕರ ನಗದು ಹರಿವು")}</div>
                <div style="font-size: 0.9rem;">
                    {t(
                        "Positive cash flow projected for the next 30 days. Your tea sales have shown a 35% increase during 4-7 PM evening window.",
                        "अगले 30 दिनों के लिए सकारात्मक नकदी प्रवाह अनुमानित। आपकी चाय की बिक्री में शाम 4-7 बजे के बीच 35% वृद्धि हुई है।",
                        "రాబోయే 30 రోజుల్లో సానుకూల నగదు ప్రవాహం అంచనా వేయబడింది. సాయంత్రం 4-7 గంటల సమయంలో మీ టీ అమ్మకాలు 35% పెరిగాయి.",
                        "அடுத்த 30 நாட்களுக்கு நேர்மறையான பணப்புழக்கம் கணிக்கப்பட்டுள்ளது. மாலை 4-7 மணி வரை உங்கள் தேநீர் விற்பனை 35% அதிகரித்துள்ளது.",
                        "ಮುಂದಿನ 30 ದಿನಗಳವರೆಗೆ ಧನಾತ್ಮಕ ನಗದು ಹರಿವು ಅಂದಾಜಿಸಲಾಗಿದೆ. ಸಂಜೆ 4-7 ರ ನಡುವೆ ನಿಮ್ಮ ಚಹಾ ಮಾರಾಟದಲ್ಲಿ 35% ಹೆಚ್ಚಳ ಕಂಡುಬಂದಿದೆ."
                    )}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with fc2:
        rng = np.random.default_rng(zlib.crc32(merchant.encode()))
        if is_suspicious:
            daily_flow = rng.integers(-15000, 5000, size=14).tolist()
        elif merchant == "Sharma Kirana":
            daily_flow = rng.integers(-5000, 12000, size=14).tolist()
        else:
            daily_flow = rng.integers(1000, 8000, size=14).tolist()

        fig_flow = go.Figure()
        fig_flow.add_trace(go.Bar(
            x=[f"{t('Day', 'दिन', 'రోజు', 'நாள்', 'ದಿನ')} {d}" for d in range(1, 15)],
            y=daily_flow,
            marker_color=["#00c853" if v >= 0 else "#f44336" for v in daily_flow],
            hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
        ))
        fig_flow.update_layout(
            title=dict(text=t("14-Day Forecast (₹)", "14-दिन पूर्वानुमान (₹)", "14 రోజుల అంచనా (₹)", "14-நாள் முன்னறிவிப்பு (₹)", "14-ದಿನಗಳ ಮುನ್ಸೂಚನೆ (₹)"), font=dict(size=14, color="#0d3b28")),
            height=250,
            margin=dict(l=40, r=10, t=40, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#f0f0f0"),
            xaxis=dict(tickfont=dict(size=9)),
            showlegend=False,
        )
        st.plotly_chart(fig_flow, key="flow_chart", **STRETCH)


# --- TAB 3: BAHI-KHATA OCR * ---
elif selected_nav == "Bahi-Khata OCR *":
    st.markdown(f'<div class="section-header">{t("Bahi-Khata OCR: Handwritten Register Scanner", "बही-खाता OCR: हस्तलिखित रजिस्टर स्कैनर", "బహి-ఖాతా OCR: చేతితో రాసిన రిజిస్టర్ స్కానర్", "பஹி-காதா OCR: கையால் எழுதப்பட்ட பதிவேடு ஸ்கேனர்", "ಬಹಿ-ಖಾತಾ OCR: ಕೈಬರಹದ ರಿಜಿಸ್ಟರ್ ಸ್ಕ್ಯಾನರ್")}</div>',
                unsafe_allow_html=True)

    st.markdown(f"""
    <div class="alert-info">
        <div style="font-weight: 600; margin-bottom: 4px;">
            {t(
                "Upload a photo of your physical Bahi-Khata notebook",
                "अपनी भौतिक बही-खाता नोटबुक की तस्वीर अपलोड करें",
                "మీ భౌతిక బహి-ఖాతా పుస్తకం ఫోటోను అప్‌లోడ్ చేయండి",
                "உங்கள் பஹி-காதா நோட்டுப் புத்தகத்தின் புகைப்படத்தைப் பதிவேற்றவும்",
                "ನಿಮ್ಮ ಭೌತಿಕ ಬಹಿ-ಖಾತಾ ಪುಸ್ತಕದ ಫೋಟೋವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ"
            )}
        </div>
        <div style="font-size: 0.85rem;">
            {t(
                "Our AI will read handwritten Hindi/English entries and convert them to digital format.",
                "हमारा AI हस्तलिखित हिंदी/अंग्रेजी प्रविष्टियों को पढ़ेगा और उन्हें डिजिटल प्रारूप में बदलेगा।",
                "మా AI చేతితో రాసిన హిందీ/ఇంగ్లీష్ ఎంట్రీలను చదివి డిజిటల్ ఫార్మాట్‌లోకి మారుస్తుంది.",
                "எங்கள் AI கையால் எழுதப்பட்ட இந்தி/ஆங்கில பதிவுகளைப் படித்து டிஜிட்டல் வடிவத்திற்கு மாற்றும்.",
                "ನಮ್ಮ AI ಕೈಬರಹದ ಹಿಂದಿ/ಇಂಗ್ಲಿಷ್ ನಮೂದುಗಳನ್ನು ಓದುತ್ತದೆ ಮತ್ತು ಅವುಗಳನ್ನು ಡಿಜಿಟಲ್ ರೂಪಕ್ಕೆ ಪರಿವರ್ತಿಸುತ್ತದೆ."
            )}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"**{t('Upload Bahi-Khata Photo', 'बही-खाता की फोटो अपलोड करें', 'బహి-ఖాతా ఫోటోను అప్‌లోడ్ చేయండి', 'பஹி-காதா புகைப்படத்தைப் பதிவேற்றவும்', 'ಬಹಿ-ಖಾತಾ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ')}**")
    uploaded_file = st.file_uploader(
        "Bahi-Khata photo",
        type=["jpg", "jpeg", "png", "pdf"],
        key="bahi_khata_upload",
        label_visibility="collapsed",
    )

    if st.button(t("Scan Register", "रजिस्टर स्कैन करें", "రిజిస్టర్ స్కాన్ చేయండి", "பதிவேட்டை ஸ்கேன் செய்யவும்", "ರಿಜಿಸ್ಟರ್ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ"), key="scan_btn"):
        with st.spinner(t("Extracting handwritten text...", "हस्तलिखित पाठ निकाला जा रहा है...", "చేతివ్రాత పాఠాన్ని సంగ్రహిస్తోంది...", "கையெழுத்து உரையை பிரித்தெடுக்கிறது...", "ಕೈಬರಹದ ಪಠ್ಯವನ್ನು ಹೊರತೆಗೆಯಲಾಗುತ್ತಿದೆ...")):
            time.sleep(2)
        n_entries = len(md["bahi_khata"])
        if uploaded_file is not None:
            st.success(t(f"Scan complete! {n_entries} entries extracted.", f"स्कैन पूरा! {n_entries} प्रविष्टियाँ निकाली गईं।", f"స్కాన్ పూర్తయింది! {n_entries} ఎంట్రీలు తీయబడ్డాయి.", f"ஸ்கேன் முடிந்தது! {n_entries} பதிவுகள் பெறப்பட்டன.", f"ಸ್ಕ್ಯಾನ್ ಪೂರ್ಣಗೊಂಡಿದೆ! {n_entries} ನಮೂದುಗಳನ್ನು ಹೊರತೆಗೆಯಲಾಗಿದೆ."))
        else:
            st.success(t(
                "Demo scan complete! Mock entries displayed.",
                "डेमो स्कैन पूरा! मॉक प्रविष्टियाँ दिखाई गई हैं।",
                "డెమో స్కాన్ పూర్తయింది! మాక్ ఎంట్రీలు చూపించబడ్డాయి.",
                "டெமோ ஸ்கேன் முடிந்தது! மாதிரி பதிவுகள் காட்டப்பட்டுள்ளன.",
                "ಡೆಮೊ ಸ್ಕ್ಯಾನ್ ಪೂರ್ಣಗೊಂಡಿದೆ! ಮಾಕ್ ನಮೂದುಗಳನ್ನು ಪ್ರದರ್ಶಿಸಲಾಗಿದೆ."
            ))

    st.markdown(f"**{t('Extracted Expenses (Editable)', 'निकाले गए खर्चे (संपादन योग्य)', 'సంగ్రహించిన ఖర్చులు (సవరించదగినవి)', 'பிரித்தெடுக்கப்பட்ட செலவுகள் (தொகுக்கக்கூடியவை)', 'ಹೊರತೆಗೆಯಲಾದ ವೆಚ್ಚಗಳು (ಬದಲಾಯಿಸಬಹುದಾದ)')}**")

    expense_df = pd.DataFrame({
        "Item": list(md["bahi_khata"].keys()),
        "Amount": list(md["bahi_khata"].values()),
        "Verified": [True] * len(md["bahi_khata"]),
    })

    edited_df = st.data_editor(
        expense_df,
        num_rows="dynamic",
        hide_index=True,
        key=f"expense_editor_{merchant}",
        column_config={
            "Item": st.column_config.TextColumn("Expense Item / खर्च मद"),
            "Amount": st.column_config.NumberColumn(
                "Amount (₹) / राशि", min_value=0, max_value=1000000, step=100, format="₹%d"
            ),
            "Verified": st.column_config.CheckboxColumn("Verified / सत्यापित", default=True),
        },
        **STRETCH,
    )
    st.caption(t(
        "Only rows marked Verified are counted in the totals below.",
        "नीचे के कुल में केवल सत्यापित पंक्तियाँ गिनी जाती हैं।",
        "ధృవీకరించబడిన వరుసలు మాత్రమే క్రింది మొత్తంలో లెక్కించబడతాయి.",
        "சரிபார்க்கப்பட்ட வரிசைகள் மட்டுமே கீழே உள்ள மொத்தத்தில் கணக்கிடப்படும்.",
        "ಪರಿಶೀಲಿಸಿದ ಸಾಲುಗಳನ್ನು ಮಾತ್ರ ಕೆಳಗಿನ ಒಟ್ಟು ವೆಚ್ಚದಲ್ಲಿ ಲೆಕ್ಕಹಾಕಲಾಗುತ್ತದೆ."
    ))

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    amounts = pd.to_numeric(edited_df["Amount"], errors="coerce").fillna(0)
    verified = edited_df["Verified"].fillna(True).astype(bool)
    total_expenses = float(amounts[verified].sum())
    upi_income = md["monthly_revenue"]
    calculated_profit = upi_income - total_expenses
    adjusted_score = adjust_score(md["credit_score"], upi_income, calculated_profit)

    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div class="metric-label">{t("UPI Income", "UPI आय", "UPI ఆదాయం", "UPI வருமானம்", "UPI ಆದಾಯ")}</div>
            <div class="metric-value" style="color: #00a844; font-size: 1.5rem;">{inr(upi_income)}</div>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div class="metric-label">{t("Bahi-Khata Expenses", "बही-खाता खर्चे", "బహి-ఖాతా ఖర్చులు", "பஹி-காதா செலவுகள்", "ಬಹಿ-ಖಾತಾ ವೆಚ್ಚಗಳು")}</div>
            <div class="metric-value" style="color: #f44336; font-size: 1.5rem;">- {inr(total_expenses)}</div>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        profit_color = "#00a844" if calculated_profit >= 0 else "#f44336"
        st.markdown(f"""
        <div class="metric-card" style="text-align: center; border-color: {profit_color}40;">
            <div class="metric-label">{t("Net Profit", "शुद्ध लाभ", "నికర లాభం", "நிகர லாபம்", "ನಿವ್ವಳ ಲಾಭ")}</div>
            <div class="metric-value" style="color: {profit_color}; font-size: 1.5rem;">= {inr(calculated_profit)}</div>
        </div>
        """, unsafe_allow_html=True)

    score_change = adjusted_score - md["credit_score"]
    change_text = f"+{score_change}" if score_change >= 0 else str(score_change)
    change_color = "#00a844" if score_change >= 0 else "#f44336"
    st.markdown(f"""
    <div style="text-align: center; margin-top: 16px; padding: 16px; background: #f8fffe; border-radius: 12px; border: 1px solid #e0f2ec;">
        <span style="font-size: 0.85rem; color: #6b7c74;">{t("Adjusted Credit Score", "समायोजित क्रेडिट स्कोर", "ಸవరించిన క్రెడిట్ స్కోరు", "சரிசெய்யப்பட்ட கடன் மதிப்பெண்", "ಹೊಂದಿಸಲಾದ ಕ್ರೆಡಿಟ್ ಸ್ಕೋರ್")}:</span>
        <span style="font-size: 1.5rem; font-weight: 800; color: {get_credit_score_color(adjusted_score)}; margin-left: 12px;">{adjusted_score}</span>
        <span style="font-size: 0.85rem; color: {change_color}; font-weight: 600; margin-left: 8px;">({change_text} {t("pts", "अंक", "పాయింట్లు", "புள்ளிகள்", "ಅಂಕಗಳು")})</span>
    </div>
    """, unsafe_allow_html=True)


# --- TAB 4: FRAUD GUARD * ---
elif selected_nav == "Fraud Guard *":
    st.markdown(f'<div class="section-header">{t("Fraud Guard & Anomaly Detector", "फ्रॉड गार्ड और विसंगति डिटेक्टर", "ఫ్రాడ్ గార్డ్ & అనోమలి డిటెక్టర్", "மோசடி தடுப்பு & ஒழுங்கற்ற தன்மை கண்டறிதல்", "ಫ್ರಾಡ್ ಗಾರ್ಡ್ ಮತ್ತು ಅಸಂಗತತೆ ಶೋಧಕ")}</div>',
                unsafe_allow_html=True)

    fraud_a, fraud_b = st.columns(2)

    with fraud_a:
        st.markdown(f"""
        <div style="font-size: 1.1rem; font-weight: 700; color: #0d3b28; margin-bottom: 12px;">
            {t("Fake Screenshot Detector", "नकली स्क्रीनशॉट डिटेक्टर", "నకిలీ స్క్రీన్‌షాట్ డిటెక్టర్", "போலி ஸ்கிரீன்ஷாட் கண்டறிதல்", "ನಕಲಿ ಸ್ಕ್ರೀನ್‌ಶಾಟ್ ಶೋಧಕ")}
        </div>
        <div class="alert-info">
            <div style="font-size: 0.85rem;">
                {t(
                    "Upload a customer's UPI payment screenshot to verify. AI will check font, metadata, and SMS confirmation.",
                    "कस्टमर के UPI भुगतान स्क्रीनशॉट को सत्यापित करने के लिए अपलोड करें। AI फॉन्ट, मटैडेटा और SMS पुष्टि की जांच करेगा।",
                    "ధృవీకరించడానికి కస్టమర్ UPI చెల్లింపు స్క్రీన్‌షాట్‌ను అప్‌లోడ్ చేయండి. AI ఫాంట్, మెటాడేటా మరియు SMS నిర్ధారణను తనిఖీ చేస్తుంది.",
                    "சரிபார்க்க வாடிக்கையாளரின் UPI கட்டண ஸ்கிரீன்ஷாட்டைப் பதிவேற்றவும். AI எழுத்துரு, மெட்டாடேட்டா மற்றும் எஸ்எம்எஸ் சரிபார்ப்பைச் சோதிக்கும்.",
                    "ಪರಿಶೀಲಿಸಲು ಗ್ರಾಹಕರ UPI ಪಾವತಿ ಸ್ಕ್ರೀನ್‌ಶಾಟ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ. AI ಫಾಂಟ್, ಮೆಟಾಡೇಟಾ ಮತ್ತು SMS ದೃಢೀಕರಣವನ್ನು ಪರಿಶೀಲಿಸುತ್ತದೆ."
                )}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**{t('Upload Payment Screenshot', 'भुगतान स्क्रीनशॉट अपलोड करें', 'చెల్లింపు స్క్రీన్‌షాట్‌ను అప్‌లోడ్ చేయండి', 'கட்டண ஸ்கிரீன்ஷாட்டைப் பதிவேற்றவும்', 'ಪಾವತಿ ಸ್ಕ್ರೀನ್‌ಶಾಟ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ')}**")
        screenshot_file = st.file_uploader(
            "Payment screenshot",
            type=["jpg", "jpeg", "png"],
            key="fraud_screenshot",
            label_visibility="collapsed",
        )

        if st.button(t("Run AI Scan", "AI स्कैन शुरू करें", "AI స్కాన్ రన్ చేయండి", "AI ஸ்கேன் இயக்கவும்", "AI ಸ್ಕ್ಯಾನ್ ಚಲಾಯಿಸಿ"), key="verify_screenshot"):
            if screenshot_file is None:
                st.warning(t("Upload a screenshot first.", "पहले स्क्रीनशॉट अपलोड करें।", "ముందుగా స్క్రీన్‌షాట్‌ను అప్‌లోడ్ చేయండి.", "முதலில் ஸ்கிரீன்ஷாட்டைப் பதிவேற்றவும்.", "ಮೊದಲು ಸ್ಕ್ರೀನ್‌ಶಾಟ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ."))
            else:
                with st.spinner(t("Running AI forensic analysis...", "AI विश्लेषण चल रहा है...", "AI ఫోరెన్సిక్ విశ్లేషణను రన్ చేస్తోంది...", "AI தடயவியல் பகுப்பாய்வு இயங்குகிறது...", "AI ವಿಶ್ಲೇಷಣೆ ನಡೆಸಲಾಗುತ್ತಿದೆ...")):
                    time.sleep(2.5)

                is_fake = is_suspicious or (zlib.crc32(screenshot_file.getvalue()) % 2 == 0)

                if is_fake:
                    rows = check_row(False, t("Font Mismatch", "फॉन्ट विसंगति", "ఫాంట్ సరిపోలడం లేదు", "எழுத்துரு பொருந்தவில்லை", "ಫಾಂಟ್ ಹೊಂದಾಣಿಕೆಯಿಲ್ಲ"),
                                     t("3 different fonts detected in screenshot", "स्क्रीनशॉट में 3 अलग-अलग फॉन्ट पाए गए", "స్క్రీన్‌షాట్‌లో 3 విభిన్న ఫాంట్‌లు కనుగొనబడ్డాయి", "ஸ்கிரீன்ஷாட்டில் 3 வெவ்வேறு எழுத்துருக்கள் கண்டறியப்பட்டுள்ளன", "ಸ್ಕ್ರೀನ್‌ಶಾಟ್‌ನಲ್ಲಿ 3 ವಿಭಿನ್ನ ಫಾಂಟ್‌ಗಳನ್ನು ಗುರುತಿಸಲಾಗಿದೆ"))
                    rows += check_row(False, t("Missing Bank SMS", "SMS पुष्टि गायब", "బ్యాంక్ SMS లేదు", "வங்கி எஸ்எம்எஸ் இல்லை", "ಬ್ಯಾಂಕ್ ಎಸ್‌ಎಂಎಸ್ ಇಲ್ಲ"),
                                      t("No corresponding bank SMS confirmation found", "कोई संबंधित बैंक SMS पुष्टि नहीं मिली", "ఎటువంటి బ్యాంక్ SMS నిర్ధారణ కనుగొనబడలేదు", "தொடர்புடைய வங்கி எஸ்எம்எஸ் சரிபார்ப்பு எதுவும் இல்லை", "ಯಾವುದೇ ಬ್ಯಾಂಕ್ ಎಸ್‌ಎಂಎಸ್ ದೃಢೀಕರಣ ಕಂಡುಬಂದಿಲ್ಲ"))
                    rows += check_row(False, t("Metadata", "मेटाडेटा", "మెటాడేటా", "மெட்டாடேட்டா", "ಮೆಟಾಡೇಟಾ"),
                                      t("Image editing software signature detected", "छवि संपादन सॉफ्टवेयर हस्ताक्षर पाया गया", "ఇమేజ్ ఎడిటింగ్ సాఫ్ట్‌వేర్ సంతకం గుర్తించబడింది", "படம் திருத்தும் மென்பொருள் கையொப்பம் கண்டறியப்பட்டுள்ளது", "ಚಿತ್ರ ಸಂಪಾದನೆ ಸಾಫ್ಟ್‌ವೇರ್ ಸಿಗ್ನೇಚರ್ ಕಂಡುಬಂದಿದೆ"))
                    rows += check_row(False, "UPI Ref",
                                      t("Reference number doesn't match bank records", "संदर्भ संख्या बैंक रिकॉर्ड से मेल नहीं खाती", "రెఫరెన్స్ నంబర్ బ్యాంక్ రికార్డులతో సరిపోలడం లేదు", "குறிப்பு எண் வங்கி பதிவுகளுடன் பொருந்தவில்லை", "ಉಲ್ಲೇಖ ಸಂಖ್ಯೆ ಬ್ಯಾಂಕ್ ದಾಖಲೆಗಳೊಂದಿಗೆ ಹೊಂದಾಣಿಕೆಯಾಗುತ್ತಿಲ್ಲ"))
                    st.markdown(f"""
                    <div class="alert-danger">
                        <span class="fraud-badge">{t("FAKE SCREENSHOT DETECTED", "नकली स्क्रीनशॉट पाया गया", "నకిలీ స్క్రీన్‌షాట్ గుర్తించబడింది", "போலி ஸ்கிரீன்ஷாட் கண்டறியப்பட்டது", "ನಕಲಿ ಸ್ಕ್ರೀನ್‌ಶಾಟ್ ಪತ್ತೆಯಾಗಿದೆ")}</span>
                        <div style="font-size: 0.9rem; margin-top: 12px;">{rows}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    rows = check_row(True, t("Font analysis", "फॉन्ट विश्लेषण", "ఫాంట్ విశ్లేషణ", "எழுத்துரு பகுப்பாய்வு", "ಫಾಂಟ್ ವಿಶ್ಲೇಷಣೆ"), t("Normal", "सामान्य", "సాధారణం", "சாதாரண", "ಸಾಮಾನ್ಯ"))
                    rows += check_row(True, t("SMS confirmation", "SMS पुष्टि", "SMS నిర్ధారణ", "ಎಸ್எம்எஸ் சரிபார்ப்பு", "ಎಸ್‌ಎಂಎಸ್ ದೃಢೀಕರಣ"), t("Found", "मिली", "కనుగొనబడింది", "கண்டறியப்பட்டது", "ಕಂಡುಬಂದಿದೆ"))
                    rows += check_row(True, "UPI Ref", t("Valid", "मान्य", "చెల్లుబాటు అయ్యేది", "செல்லுபடியாகும்", "ಮಾನ್ಯವಾಗಿದೆ"))
                    st.markdown(f"""
                    <div class="alert-success">
                        <span class="safe-badge">{t("VERIFIED GENUINE", "सत्यापित", "నిజమైనదిగా ధృవీకరించబడింది", "உண்மையானது என சரிபார்க்கப்பட்டது", "ನೈಜವೆಂದು ಪರಿಶೀಲಿಸಲಾಗಿದೆ")}</span>
                        <div style="font-size: 0.9rem; margin-top: 12px;">{rows}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.caption(t(
                    "Demo mode: this verdict is simulated, no forensic model is running.",
                    "डेमो मोड: यह परिणाम सिम्युलेटेड है, कोई फोरेंसिक मॉडल नहीं चल रहा।",
                    "డెమో మోడ్: ఈ ఫలితం కేవలం అనుకరణ మాత్రమే, ఎటువంటి ఫోరెన్సిక్ మోడల్ రన్ అవ్వడం లేదు.",
                    "டெமோ பயன்முறை: இந்த முடிவு உருவகப்படுத்தப்பட்டது, தடயவியல் மாதிரி எதுவும் இயங்கவில்லை.",
                    "ಡೆಮೊ ಮೋಡ್: ಈ ತೀರ್ಪು ಸಿಮ್ಯುಲೇಟೆಡ್ ಆಗಿದೆ, ಯಾವುದೇ ಫೋರೆನ್ಸಿಕ್ ಮಾದರಿ ಚಾಲನೆಯಲ್ಲಿಲ್ಲ."
                ))

    anomalies = md["anomalies"]

    with fraud_b:
        st.markdown(f"""
        <div style="font-size: 1.1rem; font-weight: 700; color: #0d3b28; margin-bottom: 12px;">
            {t("UPI Anomaly Monitor", "UPI विसंगति निगरानी", "UPI అనోమలి మానిటర్", "UPI ஒழுங்கற்ற கண்காணிப்பு", "UPI ಅಸಂಗತತೆ ಮಾನಿಟರ್")}
        </div>
        """, unsafe_allow_html=True)

        for anomaly in anomalies:
            risk = anomaly["risk"]
            if risk == "Critical":
                badge_html = '<span class="fraud-badge">CRITICAL</span>'
                alert_class = "alert-danger"
            elif risk == "High":
                badge_html = '<span style="background: #ff9800; color: white; padding: 3px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 700;">HIGH</span>'
                alert_class = "alert-warning"
            elif risk == "Medium":
                badge_html = '<span style="background: #ffc107; color: #333; padding: 3px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 700;">MEDIUM</span>'
                alert_class = "alert-warning"
            else:
                badge_html = '<span class="safe-badge">LOW</span>'
                alert_class = "alert-success"

            st.markdown(f"""
            <div class="{alert_class}" style="padding: 14px 18px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 0.8rem; color: #666;">{anomaly['time']} | ₹{anomaly['amount']:,.0f} | {anomaly['from']}</span>
                    {badge_html}
                </div>
                <div style="font-size: 0.85rem; font-weight: 600;">{anomaly['flag']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    # ============================================================
    # AUTOMATED WHATSAPP ALERTS FOR UPI ANOMALIES
    # ============================================================
    st.markdown(f'<div class="section-header">{t("Automated WhatsApp Alert Dispatcher", "स्वचालित व्हाट्सएप अलर्ट डिस्पैचर", "స్వయంచాలక వాట్సాప్ అలర్ట్ డిస్పాచర్", "தானியங்கி வாட்ஸ்அப் எச்சரிக்கை அனுப்புநர்", "ಸ್ವಯಂಚಾಲಿತ ವಾಟ್ಸಾಪ್ ಅಲರ್ಟ್ ಡಿಸ್ಪಾಚರ್")}</div>',
                unsafe_allow_html=True)

    w_col_info, w_col_sim = st.columns([1, 1])

    with w_col_info:
        st.markdown(f"""
        <div style="font-size: 1rem; font-weight: 700; color: #0d3b28; margin-bottom: 8px;">
            📲 {t("Real-Time WhatsApp Warning System", "रीयल-टाइम व्हाट्सएप चेतावनी प्रणाली", "రియల్ టైమ్ వాట్సాప్ హెచ్చరిక వ్యవస్థ", "நிகழ்நேர வாட்ஸ்அப் எச்சரிக்கை அமைப்பு", "ನೈಜ-ಸಮಯದ ವಾಟ್ಸಾಪ್ ಎಚ್ಚರಿಕೆ ವ್ಯವಸ್ಥೆ")}
        </div>
        <p style="font-size: 0.88rem; color: #4b6358; line-height: 1.5;">
            {t(
                "When our background engine flags a critical or high-risk transaction anomaly (e.g. rapid structuring, metadata tampering, or midnight velocity spikes), it immediately dispatches an interactive WhatsApp notification. This allows the merchant to temporarily freeze their UPI channel directly from within the chat interface, protecting against losses.",
                "जब हमारा बैकग्राउंड इंजन किसी गंभीर या उच्च जोखिम वाले लेनदेन विसंगति को फ़्लैग करता है, तो यह तुरंत एक इंटरैक्टिव व्हाट्सएप संदेश भेजता है। इसके ज़रिये व्यापारी सीधे चैट इंटरफ़ेस से अपने यूपीआई चैनल को तुरंत फ्रीज कर सकते हैं।",
                "మా బ్యాక్‌గ్రౌండ్ ఇంజన్ అధిక ప్రమాదం గల లావాదేవీల విसंगతిని గుర్తించినప్పుడు, ఇది వెంటనే వాట్సాప్ నోటిఫికేషన్‌ను పంపుతుంది. దీని ద్వారా వ్యాపారి చాట్ ఇంటర్‌ఫేస్ నుండి నేరుగా తమ UPI ఛానెల్‌ను తాత్కాలికంగా ఫ్రీజ్ చేయవచ్చు.",
                "எங்கள் பின்னணி இயந்திரம் அதிக ஆபத்துள்ள பரிவர்த்தனை ஒழுங்கற்ற தன்மையைக் கண்டறியும்போது, அது உடனடியாக வாட்ஸ்அப் அறிவிப்பை அனுப்புகிறது. இதன் மூலம் வணிகர் அரட்டை இடைமுகத்திலிருந்தே தங்கள் யுபிஐ சேனலை தற்காலிகமாக முடக்கலாம்.",
                "ನಮ್ಮ ಹಿನ್ನೆಲೆ ಎಂಜಿನ್ ಹೆಚ್ಚಿನ ಅಪಾಯದ ವಹಿವಾಟಿನ ಅಸಂಗತತೆಯನ್ನು ಗುರುತಿಸಿದಾಗ, ಅದು ತಕ್ಷಣವೇ ವಾಟ್ಸಾಪ್ ಅಧಿಸೂಚನೆಯನ್ನು ಕಳುಹಿಸುತ್ತದೆ. ಇದರಿಂದ ವ್ಯಾಪಾರಿ ಚಾಟ್ ಇಂಟರ್ಫೇಸ್‌ನಿಂದಲೇ ತಮ್ಮ ಯುಪಿಐ ಚಾನಲ್ ಅನ್ನು ತಾತ್ಕಾಲಿಕವಾಗಿ ಫ್ರೀಜ್ ಮಾಡಬಹುದು."
            )}
        </p>
        """, unsafe_allow_html=True)

        wa_enabled = st.toggle(
            t("Enable Instant WhatsApp Alerts for Anomalies", "विसंगतियों के लिए तत्काल व्हाट्सएप अलर्ट सक्षम करें", "విపత్తుల కోసం తక్షణ వాట్సాప్ అలర్ట్‌లను ప్రారంభించండి", "ஒழுங்கற்ற தன்மைகளுக்கான உடனடி வாட்ஸ்அப் எச்சரிக்கைகளை இயக்கவும்", "ಅಸಂಗತತೆಗಳಿಗಾಗಿ ತತ್ಕ್ಷಣದ ವಾಟ್ಸಾಪ್ ಅಲರ್ಟ್‌ಗಳನ್ನು ಸಕ್ರಿಯಗೊಳಿಸಿ"),
            value=True,
            key="wa_alert_toggle"
        )
        
        st.markdown(f"""
        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px 16px; font-size: 0.82rem; color: #166534; margin-top: 12px;">
            <b>{t("Active Profile Link:", "सक्रिय प्रोफ़ाइल लिंक:", "క్రియాశీల ప్రొఫైల్ లింక్:", "செயலில் உள்ள சுயவிவர இணைப்பு:", "ಸಕ್ರಿಯ ಪ್ರೊಫೈಲ್ ಲಿಂಕ್:")}</b> {display_owner} ({md["phone_masked"]}) <br/>
            <b>{t("Alert Status:", "अलर्ट स्थिति:", "అలర్ట్ స్థితి:", "எச்சரிக்கை நிலை:", "ಅಲರ್ಟ್ ಸ್ಥಿತಿ:")}</b> {t("🟢 Active and Ready to Dispatch", "🟢 सक्रिय और प्रेषण के लिए तैयार", "🟢 సక్రియంగా ఉంది మరియు పంపడానికి సిద్ధంగా ఉంది", "🟢 செயலில் உள்ளது ಮತ್ತು அனுப்ப தயாராக உள்ளது", "🟢 ಸಕ್ರಿಯವಾಗಿದೆ ಮತ್ತು ರವಾನಿಸಲು ಸಿದ್ಧವಾಗಿದೆ")}
        </div>
        """, unsafe_allow_html=True)

    with w_col_sim:
        st.markdown(f"**{t('Interactive Simulation Sandbox', 'इंटरएक्टिव सिमुलेशन सैंडबॉक्स', 'ఇంటరాక్టివ్ సిమ్యులేషన్ శాండ్‌బాక్స్', 'ஊடாடும் உருவகப்படுத்துதல் சாண்ட்பாக்ஸ்', 'ಸಂವಾದಾತ್ಮಕ ಸಿಮ್ಯುಲೇಶನ್ ಸ್ಯಾಂಡ್‌ಬಾಕ್ಸ್')}**")
        
        anomaly_options = {
            f"Anomaly {i+1}: ₹{a['amount']} ({a['risk']})": a 
            for i, a in enumerate(anomalies)
        }
        
        selected_anomaly_label = st.selectbox(
            t("Select Anomaly to Simulate Alert", "सिमुलेशन के लिए विसंगति चुनें", "అలర్ట్ అనుకరించడానికి విसंगతిని ఎంచుకోండి", "எச்சரிக்கையை உருவகப்படுத்த ஒழுங்கற்ற தன்மையைத் தேர்ந்தெடுக்கவும்", "ಅಲರ್ಟ್ ಸಿಮ್ಯುಲೇಟ್ ಮಾಡಲು ಅಸಂಗತತೆಯನ್ನು ಆರಿಸಿ"),
            options=list(anomaly_options.keys()),
            key="wa_sim_anomaly_select"
        )
        
        sim_anomaly = anomaly_options[selected_anomaly_label]
        
        if st.button(t("⚡ Simulate Immediate WhatsApp Dispatch", "⚡ व्हाट्सएप अलर्ट सिमुलेशन ट्रिगर करें", "⚡ తక్షణ వాట్సాప్ అలర్ట్ రన్ చేయండి", "⚡ உடனடி வாட்ஸ்அப் அறிவிப்பை உருவகப்படுத்தவும்", "⚡ ತತ್ಕ್ಷಣದ ವಾಟ್ಸಾಪ್ ರವಾನೆಯನ್ನು ಸಿಮ್ಯುಲೇಟ್ ಮಾಡಿ"), key="trigger_wa_sim", **STRETCH):
            with st.spinner(t("Routing via WhatsApp Business Cloud API Gateway...", "व्हाट्सएप बिजनेस क्लाउड एपीआई गेटवे द्वारा रूट किया जा रहा है...", "వాట్సాప్ బిజినెస్ క్లౌడ్ API గేట్‌వే ద్వారా రూట్ చేయబడుతోంది...", "வாட்ஸ்அப் பிசினஸ் கிளவுட் ஏபிஐ நுழைவாயில் வழியாக அனுப்பப்படுகிறது...", "ವಾಟ್ಸಾಪ್ ಬಿಸಿನೆಸ್ ಕ್ಲೌಡ್ API ಗೇಟ್‌ವೇ ಮೂಲಕ ರೂಟ್ ಮಾಡಲಾಗುತ್ತಿದೆ...")):
                time.sleep(1.2)
            st.toast(t("WhatsApp alert successfully dispatched!", "व्हाट्सएप अलर्ट सफलतापूर्वक भेजा गया!", "వాట్సాప్ అలర్ట్ విజయవంతంగా పంపబడింది!", "வாட்ஸ்அப் எச்சரிக்கை வெற்றிகரமாக அனுப்பப்பட்டது!", "ವಾಟ್ಸಾಪ್ ಅಲರ್ಟ್ ಯಶಸ್ವಿಯಾಗಿ ರವಾನೆಯಾಗಿದೆ!"), icon="📲")
            
            wa_box_html = get_whatsapp_alert_html(
                owner=display_owner,
                phone_masked=md["phone_masked"],
                anomaly=sim_anomaly,
                lang=st.session_state.get("lang_toggle", "English")
            )
            st.markdown(wa_box_html, unsafe_allow_html=True)
            st.caption(f"""<div style="text-align: center; color: #8696a0; font-size: 0.75rem; margin-top: -6px;">
                {t("▲ Live Preview of WhatsApp message template dispatched", "▲ भेजे गए व्हाट्सएप संदेश टेम्प्लेट का रीयल-टाइम प्रीव्यू", "▲ పంపబడిన వాట్సాప్ సందేశ టెంప్లేట్ లైవ్ ప్రివ్యూ", "▲ அனுப்பப்பட்ட வாட்ஸ்அப் செய்தி வார்ப்புருவின் நேரடி முன்னோட்டம்", "▲ ರವಾನಿಸಲಾದ ವಾಟ್ಸಾಪ್ ಸಂದೇಶ ಟೆಂಪ್ಲೇಟ್‌ನ ಲೈವ್ ಪೂರ್ವವೀಕ್ಷಣೆ")}
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">{t("Detailed Transaction Anomaly Report", "विस्तृत लेनदेन विसंगति रिपोर्ट", "వివరమైన లావాదేవీల విसंगతి నివేదిక", "விரிவான பரிவர்த்தனை ஒழுங்கற்ற அறிக்கை", "ವಿವರವಾದ ವಹಿವಾಟು ಅಸಂಗತತೆ ವರದಿ")}</div>',
                unsafe_allow_html=True)

    base_date = NOW - timedelta(days=1)
    anomaly_records = []
    for i, a in enumerate(anomalies):
        hour, minute = map(int, a["time"].split(":"))
        txn_time = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        anomaly_records.append({
            "Txn ID": stable_id(merchant, i, a["time"], a["from"], prefix="TXN"),
            "Time": txn_time.strftime("%d-%b %H:%M"),
            "Amount (₹)": a["amount"],
            "From/To": a["from"],
            "Flag": a["flag"],
            "Risk Level": a["risk"],
        })
    anomaly_df = pd.DataFrame(anomaly_records)

    def highlight_risk(row):
        risk = row["Risk Level"]
        if risk == "Critical":
            style = "background-color: #ffcdd2; color: #b71c1c; font-weight: bold"
        elif risk == "High":
            style = "background-color: #ffe0b2; color: #e65100; font-weight: bold"
        elif risk == "Medium":
            style = "background-color: #fff9c4; color: #f57f17"
        else:
            style = "background-color: #c8e6c9; color: #1b5e20"
        return [style] * len(row)

    st.dataframe(anomaly_df.style.apply(highlight_risk, axis=1), hide_index=True, **STRETCH)


# --- TAB 5: INSTANT MICRO-LOAN & BANK REPORT ---
elif selected_nav == "Loan & Report":
    st.markdown(f'<div class="section-header">{t("Instant Micro-Loan & Bank Report", "तत्काल माइक्रो-लोन और बैंक रिपोर्ट", "తక్షణ మైక్రో-లోన్ & బ్యాంక్ నివేదిక", "உடனடி மைக்ரோ-கடன் & வங்கி அறிக்கை", "ತತ್ಕ್ಷಣದ ಮೈಕ್ರೋ-ಸಾಲ ಮತ್ತು ಬ್ಯಾಂಕ್ ವರದಿ")}</div>',
                unsafe_allow_html=True)

    loan_col1, loan_col2 = st.columns(2)
    loan_amount = 0

    with loan_col1:
        st.markdown(f"""
        <div style="font-size: 1.1rem; font-weight: 700; color: #0d3b28; margin-bottom: 16px;">
            {t("Loan Calculator", "ऋण कैलकुलेटर", "రుణ కాలిక్యులేటర్", "கடன் கால்குலேட்டர்", "ಸಾಲದ ಕ್ಯಾಲ್ಕುಲೇಟರ್")}
        </div>
        """, unsafe_allow_html=True)

        if md["max_loan"] == 0:
            st.markdown(f"""
            <div class="alert-danger">
                <div style="font-weight: 700;">{t("Loan Unavailable", "ऋण अनुपलब्ध", "రుణం అందుబాటులో లేదు", "கடன் கிடைக்கவில்லை", "ಸಾಲ ಲಭ್ಯವಿಲ್ಲ")}</div>
                <div style="font-size: 0.85rem; margin-top: 4px;">
                    {t(
                        "Your account is under review for suspicious activity. Loan facility is temporarily disabled.",
                        "आपका खाता संदिग्ध गतिविधि के लिए समीक्षा में है। ऋण सुविधा अस्थायी रूप से अक्षम है।",
                        "అనుమానాస్పద లావాదేవీల వల్ల మీ ఖాతా పరిశీలనలో ఉంది. రుణ సౌకర్యం తాత్కాలికంగా నిలిపివేయబడింది.",
                        "சந்தேகத்திற்கிடமான செயல்பாட்டிற்காக உங்கள் கணக்கு மதிப்பாய்வில் உள்ளது. கடன் வசதி தற்காலிகமாக முடக்கப்பட்டுள்ளது.",
                        "ಸಂದೇಹಾಸ್ಪದ ಚಟುವಟಿಕೆಗಾಗಿ ನಿಮ್ಮ ಖಾತೆಯು ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ. ಸಾಲದ ಸೌಲಭ್ಯವನ್ನು ತಾತ್ಕಾಲಿಕವಾಗಿ ನಿಷ್ಕ್ರಿಯಗೊಳಿಸಲಾಗಿದೆ."
                    )}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            max_val = md["max_loan"]
            slider_key = f"loan_slider_{merchant}"
            num_key = f"loan_num_{merchant}"
            default_val = min(50000, max_val)

            # Initialize states securely if they don't exist
            if slider_key not in st.session_state:
                st.session_state[slider_key] = default_val
            if num_key not in st.session_state:
                st.session_state[num_key] = default_val

            # Mutual sync callbacks to keep both controls perfectly aligned
            def sync_from_slider():
                st.session_state[num_key] = st.session_state[slider_key]

            def sync_from_num():
                val = st.session_state[num_key]
                # Clamp within limits and round to the step value
                clamped = max(5000, min(val, max_val))
                stepped = int(round(clamped / 5000.0)) * 5000
                stepped = max(5000, min(stepped, max_val))
                st.session_state[num_key] = stepped
                st.session_state[slider_key] = stepped

            st.markdown(f"**{t('Select Loan Amount (₹)', 'ऋण राशि चुनें (₹)', 'రుణ మొత్తాన్ని ఎంచుకోండి (₹)', 'கடன் தொகையைத் தேர்ந்தெடுக்கவும் (₹)', 'ಸಾಲದ ಮೊತ್ತವನ್ನು ಆಯ್ಕೆಮಾಡಿ (₹)')}**")
            
            # Synchronized Side-by-Side Dual Controls Layout
            col_slide, col_num = st.columns([3, 1])
            with col_slide:
                loan_amount = st.slider(
                    "Loan amount",
                    min_value=5000,
                    max_value=max_val,
                    step=5000,
                    key=slider_key,
                    on_change=sync_from_slider,
                    label_visibility="collapsed",
                )
            with col_num:
                loan_amount_num = st.number_input(
                    "Loan amount numeric input",
                    min_value=5000,
                    max_value=max_val,
                    step=5000,
                    key=num_key,
                    on_change=sync_from_num,
                    label_visibility="collapsed",
                )

            interest_rate = 12.5  # annual %
            tenure_months = 12
            r = interest_rate / 12 / 100
            emi = loan_amount * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)
            total_payable = emi * tenure_months
            total_interest = total_payable - loan_amount

            st.markdown(f"""
            <div class="metric-card" style="margin-top: 16px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                    <div>
                        <div class="metric-label">{t("Loan Amount", "ऋण राशि", "రుణ మొత్తం", "கடன் தொகை", "ಸಾಲದ ಮೊತ್ತ")}</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #0d3b28;">{inr(loan_amount)}</div>
                    </div>
                    <div>
                        <div class="metric-label">{t("Interest Rate", "ब्याज दर", "వడ్డీ రేటు", "வட்டி விகிதம்", "ಬಡ್ಡಿ ದರ")}</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #ff9800;">{interest_rate}% p.a.</div>
                    </div>
                    <div>
                        <div class="metric-label">{t("Monthly EMI", "मासिक EMI", "నెలవారీ ఈఎంఐ (EMI)", "மாதாந்திர இஎம்ஐ (EMI)", "ಮಾಸಿಕ ಇಎಂಐ (EMI)")}</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #2196f3;">{inr(emi)}</div>
                    </div>
                    <div>
                        <div class="metric-label">{t("Total Interest", "कुल ब्याज", "మొత్తం వడ్డీ", "மொத்த வட்டி", "ಒಟ್ಟು ಬಡ್ಡಿ")}</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #f44336;">{inr(total_interest)}</div>
                    </div>
                </div>
                <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #e0f2ec;">
                    <div class="metric-label">{t("Total Payable (12 months)", "कुल देय राशि (12 महीने)", "మొత్తం చెల్లించవలసినది (12 నెలలు)", "மொத்தம் செலுத்த வேண்டியது (12 மாதங்கள்)", "ಒಟ್ಟು ಪಾವತಿಸಬೇಕಾದ ಮೊತ್ತ (12 ತಿಂಗಳು)")}</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #0d3b28;">{inr(total_payable)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with loan_col2:
        st.markdown(f"""
        <div style="font-size: 1.1rem; font-weight: 700; color: #0d3b28; margin-bottom: 16px;">
            {t("Bank Report & Loan Application", "बैंक रिपोर्ट और ऋण आवेदन", "బ్యాంక్ నివేదిక & రుణ దరఖాస్తు", "வங்கி அறிக்கை & கடன் விண்ணப்பம்", "ಬ್ಯಾಂಕ್ ವರದಿ ಮತ್ತು ಸಾಲದ ಅರ್ಜಿ")}
        </div>
        """, unsafe_allow_html=True)

        report_id = stable_id(merchant, NOW.strftime("%Y%m%d"), prefix="VYS-").upper()
        sep_eq, sep_dash = "=" * 60, "-" * 60
        report_text = f"""{sep_eq}
  VYAPARSCORE - MERCHANT FINANCIAL REPORT
  Bank-Ready Credit Assessment Summary
{sep_eq}

  Generated: {NOW.strftime('%d %B %Y, %I:%M %p')} IST
  Report ID: {report_id}

{sep_dash}
  MERCHANT PROFILE
{sep_dash}
  Name:           {md['name']}
  Owner:          {md['owner']}
  Location:       {md['location']}
  Business Type:  {md['type']}

{sep_dash}
  CREDIT ASSESSMENT
{sep_dash}
  VyaparScore:    {md['credit_score']} / 900 ({md['credit_label']})
  Max Loan Limit: {inr(md['max_loan'])}

{sep_dash}
  FINANCIAL SUMMARY (Monthly)
{sep_dash}
  UPI Revenue:      {inr(md['monthly_revenue'])}
  Net Profit:       {inr(md['net_profit'])}
  Active Customers: {md['active_customers']}

{sep_dash}
  ANNUAL GST STATUS
{sep_dash}
  Annual Turnover: {inr(md['gst_revenue_ytd'])}
  GST Threshold:   {inr(md['gst_limit'])}
  Utilization:     {md['gst_revenue_ytd']/md['gst_limit']*100:.1f}%

{sep_dash}
  MONTHLY REVENUE (Jan to Dec)
{sep_dash}
"""
        peak = max(md["monthly_revenues"])
        for m, rv in zip(MONTHS, md["monthly_revenues"]):
            report_text += f"  {m}: ₹{rv:>10,.0f}  {'#' * int(rv / peak * 30)}\n"

        report_text += f"""
{sep_dash}
  EXPENSE BREAKDOWN (Bahi-Khata)
{sep_dash}
"""
        for item, val in md["bahi_khata"].items():
            report_text += f"  {item:<35} ₹{val:>10,.0f}\n"

        total_exp = sum(md["bahi_khata"].values())
        report_text += f"""  {'-'*45}
  {'TOTAL':<35} ₹{total_exp:>10,.0f}

{sep_dash}
  RISK FLAGS
{sep_dash}
"""
        for a in md["anomalies"]:
            report_text += f"  [{a['risk']:>8}] {a['flag']}\n"

        report_text += f"""
{sep_dash}
  STHAN LOG - RIGHT-TO-VEND TENURE AUDIT (Street Vendors Act 2014)
{sep_dash}
  Vending Spot:        {md.get('sthan_spot', 'N/A')}
  Jurisdiction:        {md.get('sthan_ward', 'N/A')}
  Verified Tenure:     {md.get('sthan_days', 0)} Continuous Days (Since {md.get('sthan_start_date', 'N/A')})
  Geofence Adherence:  {md.get('sthan_geofence_adherence', 0)}%
  TVC Legal Status:    {md.get('sthan_tvc_status', 'N/A')}
  Section 3(3) Shield: {md.get('sthan_legal_shield', 'N/A')} ({md.get('sthan_shield_score', 0)}/100)
  PM SVANidhi Tier:    {md.get('sthan_svanidhi_tier', 'N/A')}

{sep_dash}
  ELIGIBLE GOVERNMENT SCHEMES
{sep_dash}
  Scheme: {md['eligible_scheme']}
  Amount: {inr(md['scheme_amount'])}

{sep_eq}
  Auto-generated by VyaparScore. Mock data for demonstration.
  GSTIN Verification Portal: gst.gov.in
{sep_eq}
"""

        summary_df = pd.DataFrame({
            "Metric": ["Merchant Name", "Credit Score", "Credit Rating", "Monthly Revenue", "Net Profit",
                       "Active Customers", "Max Loan Limit", "Annual Turnover", "GST Threshold",
                       "Verified Vending Days", "Vending Spot", "TVC Legal Status", "Section 3(3) Shield"],
            "Value": [md["name"], str(md["credit_score"]), md["credit_label"], inr(md["monthly_revenue"]),
                      inr(md["net_profit"]), str(md["active_customers"]), inr(md["max_loan"]),
                      inr(md["gst_revenue_ytd"]), inr(md["gst_limit"]),
                      str(md.get("sthan_days", 0)), md.get("sthan_spot", "N/A"),
                      md.get("sthan_tvc_status", "N/A"), md.get("sthan_legal_shield", "N/A")],
        })
        csv_bytes = summary_df.to_csv(index=False).encode("utf-8-sig")

        safe_name = md["name"].replace(" ", "_")
        stamp = NOW.strftime("%Y%m%d")
        btn1, btn2 = st.columns(2)
        with btn1:
            st.download_button(
                label=t("Download Bank-Ready Report", "बैंक-रेडी रिपोर्ट डाउनलोड करें", "బ్యాంక్-సిద్ధంగా ఉన్న నివేదికను డౌన్‌లోడ్ చేయండి", "வங்கிக்கு சமர்ப்பிக்கக்கூடிய அறிக்கையைப் பதிவிறக்கவும்", "ಬ್ಯಾಂಕ್-ಸಿದ್ಧ ವರದಿಯನ್ನು ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ"),
                data=report_text.encode("utf-8"),
                file_name=f"VyaparScore_Report_{safe_name}_{stamp}.txt",
                mime="text/plain",
                key="download_report",
            )
        with btn2:
            st.download_button(
                label=t("Download CSV", "CSV डाउनलोड करें", "CSV డౌన్‌లోడ్ చేయండి", "CSV பதிவிறக்கவும்", "CSV ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ"),
                data=csv_bytes,
                file_name=f"VyaparScore_Data_{safe_name}_{stamp}.csv",
                mime="text/csv",
                key="download_csv",
            )

        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

        if md["max_loan"] > 0:
            loans = st.session_state.setdefault("loans", {})

            if st.button(t("Apply for 1-Click Loan", "1-क्लिक ऋण के लिए आवेदन करें", "1-క్లిక్ లోన్ కోసం దరఖాస్తు చేసుకోండి", "1-கிளிக் கடனுக்கு விண்ணப்பிக்கவும்", "1-ಕ್ಲಿಕ್ ಸಾಲಕ್ಕೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ"), key="apply_loan", **STRETCH):
                with st.spinner(t("Processing loan application...", "ऋण आवेदन संसाधित हो रहा है...", "రుణ దరఖాస్తును ప్రాసెస్ చేస్తోంది...", "கடன் விண்ணப்பம் செயலாக்கப்படுகிறது...", "ಸಾಲದ ಅರ್ಜಿಯನ್ನು ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲಾಗುತ್ತಿದೆ...")):
                    time.sleep(3)
                loans[merchant] = {
                    "amount": loan_amount,
                    "id": stable_id(merchant, loan_amount, time.time_ns(), prefix="VYS-LOAN-").upper(),
                }
                st.balloons()

            loan = loans.get(merchant)
            if loan:
                st.markdown(f"""
                <div class="approval-cert">
                    <div class="approval-title">{t("LOAN APPROVED", "ऋण स्वीकृत", "రుణం ఆమోదించబడింది", "கடன் அங்கீகரிக்கப்பட்டது", "ಸಾಲ ಮಂಜೂರಾಗಿದೆ")}</div>
                    <div class="approval-amount">{inr(loan['amount'])}</div>
                    <div style="font-size: 1rem; color: #2e7d32; margin-bottom: 16px;">
                        {t("Digital Loan Approval Certificate", "डिजिटल ऋण स्वीकृति प्रमाणपत्र", "డిజిటల్ రుణ ఆమోదం ధృవీకరణ పత్రం", "ಡಿಜಿಟಲ್ ಸಾಲ ಮಂಜೂರಾತಿ ಪ್ರಮಾಣಪತ್ರ", "டிஜிட்டல் கடன் அனுமதி சான்றிதழ்")}
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-top: 16px;">
                        <div>
                            <div style="font-size: 0.75rem; color: #2e7d32;">{t("Approval ID", "स्वीकृति ID", "ఆమోదం ID", "அனுமதி ஐடி", "ಮಂಜೂರಾತಿ ID")}</div>
                            <div style="font-weight: 700; color: #1b5e20;">{loan['id']}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: #2e7d32;">{t("Tenure", "अवधि", "వ్యవధి", "கால அளவு", "ಅವಧಿ")}</div>
                            <div style="font-weight: 700; color: #1b5e20;">12 {t("Months", "महीने", "నెలలు", "மாதங்கள்", "ತಿಂಗಳುಗಳು")}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: #2e7d32;">{t("Status", "स्थिति", "స్థితి", "நிலை", "ಸ್ಥಿತಿ")}</div>
                            <div style="font-weight: 700; color: #1b5e20;">{t("SANCTIONED", "स्वीकृत", "మంజూరయింది", "அனுமதிக்கப்பட்டது", "ಮಂಜೂರಾಗಿದೆ")}</div>
                        </div>
                    </div>
                    <div style="margin-top: 20px; font-size: 0.8rem; color: #2e7d32;">
                        {t(
                            "Amount will be credited to your UPI-linked bank account within 24 hours.",
                            "राशि 24 घंटे के भीतर आपके UPI-लिंक्ड बैंक खाते में जमा हो जाएगी।",
                            "ఈ మొత్తం 24 గంటల్లో మీ UPI-లింక్డ్ బ్యాంక్ ఖాతాలో జమ చేయబడుతుంది.",
                            "இந்தத் தொகை 24 மணி நேரத்திற்குள் உங்கள் யுபிஐ இணைக்கப்பட்ட வங்கி கணக்கில் வரவு வைக்கப்படும்.",
                            "ಮೊತ್ತವನ್ನು 24 ಗಂಟೆಗಳ ಒಳಗೆ ನಿಮ್ಮ UPI-ಲಿಂಕ್ ಮಾಡಿದ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ಜಮಾ ಮಾಡಲಾಗುತ್ತದೆ."
                        )}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert-danger">
                <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 8px;">{t("Loan Facility Blocked", "ऋण सुविधा अवरुद्ध", "రుణ సౌకర్యం బ్లాక్ చేయబడింది", "கடன் வசதி முடக்கப்பட்டுள்ளது", "ಸಾಲದ ಸೌಲಭ್ಯವನ್ನು ನಿರ್ಬಂಧಿಸಲಾಗಿದೆ")}</div>
                <div style="font-size: 0.9rem;">
                    {t(
                        "Account is under review. Please resolve all anomalies and try again after 30 days.",
                        "खाता समीक्षा में है। कृपया सभी विसंगतियों का समाधान करें और 30 दिनों के बाद पुनः प्रयास करें।",
                        "ఖాతా పరిశీలనలో ఉంది. దయచేసి అన్ని విసంగతులను పరిష్కరించి 30 రోజుల తర్వాత మళ్లీ ప్రయత్నించండి.",
                        "கணக்கு மதிப்பாய்வில் உள்ளது. தயவுசெய்து அனைத்து ஒழுங்கற்ற தன்மைகளையும் தீர்த்து 30 நாட்களுக்குப் பிறகு மீண்டும் முயற்சிக்கவும்.",
                        "ಖಾತೆಯು ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ. ದಯವಿಟ್ಟು ಎಲ್ಲಾ ಅಸಂಗತತೆಗಳನ್ನು ಬಗೆಹರಿಸಿ 30 ದಿನಗಳ ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
                    )}
                </div>
            </div>
            """, unsafe_allow_html=True)


# --- TAB 6: STHAN LOG — THE RIGHT-TO-VEND EVIDENCE TRAIL ---
elif selected_nav == "Sthan Log 📍":
    st.markdown(f'<div class="section-header">{t("Sthan Log: The Right-to-Vend Evidence Trail", "स्थान लॉग: वेंडिंग अधिकार साक्ष्य शृंखला", "స్థాన్ లాగ్: వీధి వ్యాపార హక్కుల సాక్ష్యాధారాల నివేదిక", "ஸ்தான் லாக்: தெரு வியாபார உரிமைகளுக்கான சான்று", "ಸ್ಥಾನ್ ಲಾಗ್: ಬೀದಿ ಬದಿ ವ್ಯಾಪಾರ ಹಕ್ಕುಗಳ ಸಾಕ್ಷ್ಯಚಿತ್ರ")}</div>',
                unsafe_allow_html=True)

    st.markdown(f"""
    <div class="legal-alert">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
            <div>
                <span style="font-size: 1.1rem; font-weight: 800; color: #065f46;">
                    ⚖️ {t(
                        "The Street Vendors Act (2014) — Section 3(3) Statutory Eviction Shield",
                        "स्ट्रीट वेंडर्स अधिनियम (2014) — धारा 3(3) वैधानिक बेदखली ढाल",
                        "వీధి వ్యాపారుల చట్టం (2014) — సెక్షన్ 3(3) చట్టబద్ధమైన తొలగింపు నిరోధక రక్షణ",
                        "தெரு வியாபாரிகள் சட்டம் (2014) — பிரிவு 3(3) சட்டப்பூர்வ வெளியேற்ற எதிர்ப்பு அரண்",
                        "ಬೀದಿ ಬದಿ ವ್ಯಾಪಾರಿಗಳ ಕಾಯ್ದೆ (2014) — ಸೆಕ್ಷನ್ 3(3) ಶಾಸನಬದ್ಧ ಉಚ್ಚಾಟನೆ ರಕ್ಷಣೆ"
                    )}
                </span>
                <div style="font-size: 0.8rem; color: #047857; font-weight: 600; margin-top: 2px;">
                    {t(
                        "Central Act No. 7 of 2014 | Urban Livelihoods & Street Vending Protection Guarantee",
                        "केंद्रीय अधिनियम सं. 7 (2014) | शहरी आजीविका एवं स्ट्रीट वेंडिंग संरक्षण गारंटी",
                        "కేంద్ర చట్టం సంఖ్య 7 (2014) | పట్టణ జీవనోపాధి & వీధి వ్యాపార రక్షణ హామీ",
                        "மத்திய சட்டம் எண் 7 (2014) | நகர்ப்புற જીવનோபாயங்கள் & தெரு வியாபார பாதுகாப்பு உத்தரவாதம்",
                        "ಕೇಂದ್ರ ಕಾಯ್ದೆ ಸಂಖ್ಯೆ 7 (2014) | ನಗರ ಜೀವನೋಪಾಯ ಮತ್ತು ಬೀದಿ ಬದಿ ವ್ಯಾಪಾರ ರಕ್ಷಣೆ ಗ್ಯಾರಂಟಿ"
                    )}
                </div>
            </div>
            <span class="sthan-badge">
                📍 {t("CIVIC-LEGAL TENURE LEDGER", "सिविक-कानूनी कार्यकाल लेजर", "పౌర-చట్టబద్ధమైన వృత్తి నివేదిక", "குடிமைச் சட்டப்பூர்வ தொழில் பதிவேடு", "ನಾಗರಿಕ-ಕಾನೂನು ಅಧಿಕಾರಾವಧಿ ಲೆಡ್ಜರ್")}
            </span>
        </div>
        <div style="font-size: 0.88rem; color: #064e3b; line-height: 1.6;">
            <b>{t("The Legal Guarantee", "वैधानिक अधिकार", "చట్టపరమైన హామీ", "சட்டப்பூர்வ உத்தரவாதம்", "ಕಾನೂನು ಗ್ಯಾರಂಟಿ")}:</b> {t(
                "Section 3(3) of The Street Vendors Act, 2014 explicitly mandates: <i>'No street vendor who was carrying on vending activities prior to the survey shall be evicted or relocated until the Town Vending Committee (TVC) survey has been completed and certificate of vending granted.'</i>",
                "स्ट्रीट वेंडर्स अधिनियम, 2014 की धारा 3(3) स्पष्ट निर्देश देती है: <i>'टाउन वेंडिंग कमेटी (TVC) सर्वेक्षण पूरा होने और वेंडिंग प्रमाणपत्र दिए जाने तक सर्वेक्षण से पहले वेंडिंग करने वाले किसी भी स्ट्रीट वेंडर को बेदखल या स्थानांतरित नहीं किया जाएगा।'</i>",
                "వీధి వ్యాపారుల చట్టం, 2014 లోని సెక్షన్ 3(3) స్పష్టంగా ఆదేశిస్తుంది: <i>'టౌన్ వెండింగ్ కమిటీ (TVC) సర్వే పూర్తయి వీధి వ్యాపార ధృవీకరణ పత్రం మంజూరు చేసే వరకు, సర్వే కంటే ముందు నుండి వ్యాపారం చేస్తున్న ఏ వీధి వ్యాపారిని బలవంతంగా తొలగించడం లేదా వేరే చోటికి మార్చడం చేయరాదు.'</i>",
                "தெரு வியாபாரிகள் சட்டம், 2014 இன் பிரிவு 3(3) தெளிவாகக் குறிப்பிடுகிறது: <i>'நகர வியாபாரக் குழு (TVC) கணக்கெடுப்பு முடிந்து வியாபாரச் சான்றிதழ் வழங்கப்படும் வரை, கணக்கெடுப்பிற்கு முன்னர் வியாபாரம் செய்து வந்த எந்தவொரு தெரு வியாபாரியும் வெளியேற்றப்படவோ அல்லது இடமாற்றம் செய்யப்படவோ கூடாது.'</i>",
                "ಬೀದಿ ಬದಿ ವ್ಯಾಪಾರಿಗಳ ಕಾಯ್ದೆ, 2014 ರ ವಿಭಾಗ 3(3) ಸ್ಪಷ್ಟವಾಗಿ ಆದೇಶಿಸುತ್ತದೆ: <i>'ಟೌನ್ ವೆಂಡಿಂಗ್ ಕಮಿಟಿ (TVC) ಸಮೀಕ್ಷೆ ಪೂರ್ಣಗೊಂಡು ಮಾರಾಟ ಪ್ರಮಾಣಪತ್ರವನ್ನು ನೀಡುವವರೆಗೆ ಸಮೀಕ್ಷೆಯ ಮೊದಲು ವ್ಯಾಪಾರ ಚಟುವಟಿಕೆಗಳನ್ನು ನಡೆಸುತ್ತಿದ್ದ ಯಾವುದೇ ಬೀದಿ ಬದಿ ವ್ಯಾಪಾರಿಯನ್ನು ಉಚ್ಚಾಟಿಸಲು ಅಥವಾ ಸ್ಥಳಾಂತರಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ.'</i>"
            )}
            <br>
            <b>{t("The Unsolved Reality", "अनसुलझी वास्तविकता", "పరిష్కారం కాని వాస్తవం", "தீர்வு காணப்படாத உண்மை", "ಬಗೆಹರಿಯದ ವಾಸ್ತವ")}:</b> {t(
                "Vendors with 10–15 years of uninterrupted presence are arbitrarily displaced during municipal 'anti-encroachment' clearances or spot-stealing by newcomers because they have zero timestamped, tamper-evident proof. Legal tech is boring and doesn't sell.",
                "10-15 साल से उसी जगह पर दुकान लगाने वाले विक्रेताओं को नगर निगम के 'अतिक्रमण हटाओ' अभियानों या नए कब्जाधारियों द्वारा बेदखल कर दिया जाता है, क्योंकि उनके पास निरंतर वेंडिंग का कोई दस्तावेजी साक्ष्य नहीं होता। लीगल टेक जटिल है और कोई इसे लागू नहीं करता।",
                "పదేళ్లుగా ఒకే చోట వ్యాపారం చేస్తున్న వారిని కూడా మునిసిపల్ అధికారులు హఠాత్తుగా తొలగిస్తుంటారు, ఎందుకంటే వారి వద్ద నిరంతర వ్యాపారానికి సంబంధించిన ఎటువంటి ఆధారాలు ఉండవు.",
                "10-15 ஆண்டுகள் தொடர்ந்து வியாபாரம் செய்யும் வியாபாரிகள் கூட, அவர்களிடம் முறையான ஆவணச் சான்று இல்லாததால், நகராட்சி ஆக்கிரமிப்பு அகற்றும் பணிகளின் போது தன்னிச்சையாக வெளியேற்றப்படுகிறார்கள்.",
                "10-15 ವರ್ಷಗಳಿಂದ ನಿರಂತರವಾಗಿ ವ್ಯಾಪಾರ ಮಾಡುತ್ತಿರುವ ಮಾರಾಟಗಾರರನ್ನು ಸಹ ಪುರಸಭೆಯ ಒತ್ತುವರಿ ತೆರವು ಕಾರ್ಯಾಚರಣೆಯ ಸಮಯದಲ್ಲಿ ಉಚ್ಚಾಟಿಸಲಾಗುತ್ತದೆ, ಏಕೆಂದರೆ ಅವರ ಬಳಿ ನಿರಂತರ ವ್ಯಾಪಾರದ ಯಾವುದೇ ಪುರಾವೆಗಳಿರುವುದಿಲ್ಲ."
            )}
            <br>
            <b>{t("The VyaparScore Fintech Bridge", "व्यापारस्कोर का फिनटेक समाधान", "వ్యాపారస్కోర్ ఫిన్‌టెక్ వారధి", "வியாபார்ஸ்கோர் ஃபின்டெக் பாலம்", "ವ್ಯಾಪಾರಸ್ಕೋರ್ ಫಿನ್ಟೆಕ್ ಬ್ರಿಡ್ಜ್")}:</b> {t(
                "By anchoring routine daily UPI transactions and a 1-tap morning check-in to a cryptographic geo-stamp (Dual-band GPS + Cell Tower ID + Timestamp), VyaparScore silently compiles a court-admissible tenure ledger under Section 65B of the Indian Evidence Act. Your everyday payment app becomes a legal defense instrument and accelerates PM SVANidhi LOR verification.",
                "दैनिक UPI लेन-देन और 1-टैप मॉर्निंग चेक-इन को एक सुरक्षित भू-मुहर (GPS + सेल टॉवर + समय) से जोड़कर, व्यापारस्कोर भारतीय साक्ष्य अधिनियम की धारा 65B के तहत अदालत-मान्य कार्यकाल लेजर तैयार करता है। आपका रोज़मर्रा का ऐप कानूनी ढाल बन जाता है और पीएम स्वनिधि सत्यापन को गति देता है।",
                "రోజువారీ UPI లావాదేవీలను మరియు ఉదయం పూట చేసే 1-టాప్ చెక్-ఇన్‌ను ఒక క్రిప్టోగ్రాఫిక్ జియో-స్టాంప్ (GPS + సెల్ టవర్ ఐడీ) తో అనుసంధానించడం ద్వారా, ఇండియన్ ఎవిడెన్స్ యాక్ట్ లోని సెక్షన్ 65B కింద కోర్టులో ఆమోదయోగ్యమైన నివేదికను వ్యాపారస్కోర్ సిద్ధం చేస్తుంది. దీనివల్ల మీ రోజువారీ పేమెంట్ యాప్ ఒక రక్షణ కవచంగా మారుతుంది.",
                "தினசரி யுபிஐ பரிவர்த்தனைகள் மற்றும் ஒரு தட்டல் காலை சரிபார்ப்பை இருப்பிடப்பதிவுடன் (GPS) இணைப்பதன் மூலம், இந்திய சான்றுச் சட்டத்தின் பிரிவு 65B இன் கீழ் நீதிமன்றத்தால் ஏற்றுக்கொள்ளக்கூடிய சான்றை வியாபார்ஸ்கோர் உருவாக்குகிறது. உங்கள் தினசரி கட்டண செயலி சட்டப்பூர்வ பாதுகாப்பு கருவியாக மாறுகிறது.",
                "ದೈನಂದಿನ ಯುಪಿಐ ವಹಿವಾಟುಗಳು ಮತ್ತು ಬೆಳಗಿನ 1-ಟ್ಯಾಪ್ ಚೆಕ್-ಇನ್ ಅನ್ನು ಕ್ರಿಪ್ಟೋಗ್ರಾಫಿಕ್ ಜಿಯೋ-ಸ್ಟಾಂಪ್ (GPS) ನೊಂದಿಗೆ ಜೋಡಿಸುವ ಮೂಲಕ, ಭಾರತೀಯ ಸಾಕ್ಷ್ಯ ಕಾಯ್ದೆಯ ಸೆಕ್ಷನ್ 65B ಅಡಿಯಲ್ಲಿ ನ್ಯಾಯಾಲಯಕ್ಕೆ ಮಾನ್ಯವಿರುವ ದಾಖಲೆಯನ್ನು ವ್ಯಾಪಾರಸ್ಕೋರ್ ಸಿದ್ಧಪಡಿಸುತ್ತದೆ."
            )}
        </div>
    </div>
    """, unsafe_allow_html=True)

    sthan_records = st.session_state.setdefault("sthan_records", {})
    live_records = sthan_records.setdefault(merchant, [])
    active_tenure_days = md["sthan_days"] + len(live_records)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t("Verified Vending Tenure", "सत्यापित वेंडिंग कार्यकाल", "ధృవీకరించబడిన వ్యాపార కాలం", "சரிபார்க்கப்பட்ட தெரு வியாபார காலம்", "ಪರಿಶೀಲಿಸಿದ ವ್ಯಾಪಾರಾವಧಿ")}</div>
            <div class="metric-value">{active_tenure_days} {t("Days", "दिन", "రోజులు", "நாட்கள்", "ದಿನಗಳು")}</div>
            {delta_badge(f"{active_tenure_days}d", t(f"Since {md['sthan_start_date']}", f"{md['sthan_start_date']} से", f"{md['sthan_start_date']} నుండి", f"{md['sthan_start_date']} முதல்", f"{md['sthan_start_date']} ಇಂದ"))}
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        acc_text = f"{md['sthan_geofence_adherence']}%"
        delta_label = t("±2.8m GNSS Lock", "±2.8मी GNSS लॉक", "±2.8మీ GNSS లాక్", "±2.8மீ GNSS பூட்டு", "±2.8ಮೀ GNSS ಲಾಕ್") if not is_suspicious else t("Severe Geo-Drift", "गंभीर भू-उछाल", "తీవ్రమైన జియో-డ్రిఫ్ట్", "கடுமையான இருப்பிட விலகல்", "ಗಂಭೀರ ಜಿಯೋ-ಡ್ರಿಫ್ಟ್")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t("Micro-Geofence Accuracy", "स्थान निर्धारण शुद्धता", "మైక్రో-జియోఫెన్స్ ఖచ్చితత్వం", "மைக்ரோ-ஜியோஃபென்ஸ் துல்லியம்", "ಮೈಕ್ರೋ-ಜಿಯೋಫೆನ್ಸ್ ನಿಖರತೆ")}</div>
            <div class="metric-value">{acc_text}</div>
            {delta_badge(acc_text, delta_label, force_bad=is_suspicious)}
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        shield_txt = f"{md['sthan_shield_score']}/100"
        shield_label = t(md["sthan_legal_shield"], md["sthan_legal_shield_hi"], md.get("sthan_legal_shield_te"), md.get("sthan_legal_shield_ta"), md.get("sthan_legal_shield_kn"))
        shield_color = "#00c853" if md["sthan_shield_score"] >= 80 else ("#ff9800" if md["sthan_shield_score"] >= 50 else "#f44336")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t("Section 3(3) Legal Shield", "धारा 3(3) कानूनी ढाल", "సెక్షన్ 3(3) చట్టపరమైన రక్షణ", "பிரிவு 3(3) சட்டப்பூர்வ அரண்", "ಸೆಕ್ಷನ್ 3(3) ಕಾನೂನು ರಕ್ಷಣೆ")}</div>
            <div class="metric-value" style="color: {shield_color};">{shield_txt}</div>
            {delta_badge(f"{md['sthan_shield_score']}%", shield_label, force_bad=is_suspicious)}
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        svanidhi_status = t("PRE-QUALIFIED", "पूर्व-योग्य", "ముందుగా అర్హత పొందింది", "முன் தகுதி பெற்றது", "ಪೂರ್ವ-ಅರ್ಹತೆ") if not is_suspicious else t("UNDER REVIEW", "समीक्षा में", "పరిశీలనలో ఉంది", "மதிப்பாய்வில் உள்ளது", "ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ")
        svanidhi_color = "#00a844" if not is_suspicious else "#f44336"
        svanidhi_badge = t(md["sthan_svanidhi_tier"], md["sthan_svanidhi_tier_hi"], md.get("sthan_svanidhi_tier_te"), md.get("sthan_svanidhi_tier_ta"), md.get("sthan_svanidhi_tier_kn"))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t("PM SVANidhi Verification", "पीएम स्वनिधि सत्यापन", "పీఎం స్వనిధి ధృవీకరణ", "பிஎம் ஸ்வநிதி சரிபார்ப்பு", "ಪಿಎಂ ಸ್ವನಿಧಿ ಪರಿಶೀಲನೆ")}</div>
            <div class="metric-value" style="color: {svanidhi_color}; font-size: 1.4rem;">{svanidhi_status}</div>
            <span class="metric-delta {'delta-positive' if not is_suspicious else 'delta-negative'}">{svanidhi_badge}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.markdown(f"""
        <div style="font-size: 1.15rem; font-weight: 700; color: #0d3b28; margin-bottom: 12px;">
            {t("1-Tap Daily Check-in & Geo-Anchor", "1-टैप दैनिक चेक-इन एवं भू-मुहर", "1-టాప్ రోజువారీ చెక్-ఇన్ & జియో-యాంకర్", "1-தட்டல் தினசரி சரிபார்ப்பு & இருப்பிடப்பதிவு", "1-ಟ್ಯಾಪ್ ದೈನಂದಿನ ಚೆಕ್-ಇನ್ ಮತ್ತು ಜಿಯೋ-ಆಂಕರ್")}
        </div>
        """, unsafe_allow_html=True)

        display_spot = t(md["sthan_spot"], md["sthan_spot_hi"], md.get("sthan_spot_te"), md.get("sthan_spot_ta"), md.get("sthan_spot_kn"))
        display_ward = t(md["sthan_ward"], md["sthan_ward_hi"], md.get("sthan_ward_te"), md.get("sthan_ward_ta"), md.get("sthan_ward_kn"))

        st.markdown(f"""
        <div style="background: #f8fffe; border: 1px solid #c8e6c9; border-radius: 14px; padding: 18px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; color: #1b5e20; font-size: 0.95rem;">
                    📍 {t("Registered Vending Location", "पंजीकृत वेंडिंग स्थल", "నమోదిత వీధి వ్యాపార స్థలం", "பதிவுசெய்யப்பட்ட தெரு வியாபார இடம்", "ನೋಂದಾಯಿತ ವ್ಯಾಪಾರ ಸ್ಥಳ")}
                </span>
                <span style="background: #e8f5e9; color: #2e7d32; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">
                    {t("GPS LOCKED", "GPS लॉक", "GPS లాక్ చేయబడింది", "ஜிபிஎஸ் பூட்டப்பட்டது", "GPS ಲಾಕ್ ಆಗಿದೆ")}
                </span>
            </div>
            <div style="font-size: 0.9rem; font-weight: 600; color: #0d3b28; margin-bottom: 4px;">{display_spot}</div>
            <div style="font-size: 0.8rem; color: #4b6358;">
                <b>{t("Municipal Ward", "नगर निगम वार्ड", "మున్సిపల్ వార్డు", "நகராட்சி வார்டு", "ಮುನ್ಸಿಪಲ್ ವಾರ್ಡ್")}:</b> {display_ward}<br>
                <b>{t("Anchor Coordinates", "निर्धारित निर्देशांक", "యాంకర్ కోఆర్డినేట్స్", "இருப்பிட ஆயத்தொலைவுகள்", "ಆಂಕರ್ ನಿರ್ದೇಶಾಂಕಗಳು")}:</b> {md['sthan_coords'][0]:.4f}° N, {md['sthan_coords'][1]:.4f}° E<br>
                <b>{t("Current Time (IST)", "वर्तमान समय", "ప్రస్తుత సమయం (IST)", "தற்போதைய நேரம் (IST)", "ಪ್ರಸ್ತುತ ಸಮಯ (IST)")}:</b> {NOW.strftime('%d %b %Y, %I:%M %p')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**{t('Optional: Stall Verification Photo / QR Scan', 'वैकल्पिक: दुकान का फोटो / QR स्कैन', 'ఐచ్ఛికం: స్టాల్ ధృవీకరణ ఫోటో / QR స్కాన్', 'ವಿದೇಶಿ: ಅಂಗಡಿ ಪರಿಶೀಲನೆ ಫೋಟೋ / ಕ್ಯೂಆರ್ ಸ್ಕ್ಯಾನ್', 'விருப்பத்தேர்வு: கடை சரிபார்ப்பு புகைப்படம் / கியூஆர் ஸ்கேன்')}**")
        sthan_photo = st.file_uploader(
            "Stall Photo",
            type=["jpg", "jpeg", "png"],
            key=f"sthan_photo_upload_{merchant}",
            label_visibility="collapsed",
        )

        checkin_clicked = st.button(
            t("📍 Tap to Check-in Today (आज की उपस्थिति दर्ज करें)", "📍 आज की उपस्थिति दर्ज करें", "📍 ఈరోజు చెక్-ఇన్ చేయడానికి ఇక్కడ నొక్కండి", "📍 இன்று சரிபார்க்க இங்கே தட்டவும்", "📍 ಇಂದಿನ ಚೆಕ್-ಇನ್ ಮಾಡಲು ಇಲ್ಲಿ ಟ್ಯಾಪ್ ಮಾಡಿ"),
            key=f"btn_checkin_{merchant}",
            **STRETCH,
        )

        if checkin_clicked:
            with st.spinner(t("Acquiring dual-band GNSS lock & generating cryptographic block...", "GNSS उपग्रह लॉक एवं ब्लॉकचेन-ग्रेड हैश जनरेट हो रहा है...", "ద్వి-బ్యాండ్ GNSS లాక్ పొందుతోంది & క్రిప్టోగ్రాఫిక్ బ్లాక్‌ను సృష్టిస్తోంది...", "இரட்டை அலைவரிசை GNSS பூட்டைப் பெறுகிறது ಮತ್ತು குறியாக்கத் தொகுதியை உருவாக்குகிறது...", "ದ್ವಿ-ಬ್ಯಾಂಡ್ ಜಿಎನ್‌ಎಸ್ಎಸ್ ಲಾಕ್ ಪಡೆದುಕೊಳ್ಳಲಾಗುತ್ತಿದೆ ಮತ್ತು ಕ್ರಿಪ್ಟೋಗ್ರಾಫಿಕ್ ಬ್ಲಾಕ್ ರಚಿಸಲಾಗುತ್ತಿದೆ...")):
                time.sleep(1.8)

            checkin_time_str = NOW.strftime("%Y-%m-%d %H:%M:%S")
            block_hash = stable_id(merchant, checkin_time_str, time.time_ns(), prefix="0xSHA256-", digits=16).upper()
            new_entry = {
                "date": NOW.strftime("%d-%b-%Y"),
                "time": NOW.strftime("%I:%M %p"),
                "coords": f"{md['sthan_coords'][0]:.4f}, {md['sthan_coords'][1]:.4f}",
                "distance": "1.4m" if not is_suspicious else "6.8 km",
                "accuracy": "±2.2m" if not is_suspicious else "±650m",
                "hash": block_hash,
                "status": "Verified (Inside Geofence)" if not is_suspicious else "FAIL (Geofence Breach)",
            }
            live_records.append(new_entry)
            st.balloons()
            st.success(t(
                f"✅ Check-in Recorded! Day #{active_tenure_days} added to permanent statutory ledger. Cryptographic Proof: {block_hash[:18]}...",
                f"✅ चेक-इन सफल! दिन #{active_tenure_days} वैधानिक लेजर में दर्ज। क्रिप्टोग्राफ़िक साक्ष्य: {block_hash[:18]}...",
                f"✅ చెక్-ఇన్ విజయవంతంగా పూర్తయింది! శాశ్వత నివేదికలో రోజు #{active_tenure_days} చేర్చబడింది.",
                f"✅ வருகை பதிவு செய்யப்பட்டது! நிரந்தர சட்டப்பூர்வ பதிவேட்டில் நாள் #{active_tenure_days} சேர்க்கப்பட்டது.",
                f"✅ ಚೆಕ್-ಇನ್ ದಾಖಲಾಗಿದೆ! ಶಾಶ್ವತ ಶಾಸನಬದ್ಧ ಲೆಡ್ಜರ್‌ನಲ್ಲಿ ದಿನ #{active_tenure_days} ಸೇರಿಸಲಾಗಿದೆ."
            ))

        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-size: 1.05rem; font-weight: 700; color: #0d3b28; margin-bottom: 8px;">
            {t("Peer Vendor Endorsements (Local Panchnama)", "सह-व्यापारी प्रमाणन (स्थानीय पंचनामा)", "సహచర వ్యాపారుల ధృవీకరణ (స్థానిక పంచనామా)", "சக தெரு வியாபாரிகளின் சான்றளிப்பு (உள்ளூர் பஞ்சநாமா)", "ಸಹವರ್ತಿ ವ್ಯಾಪಾರಿಗಳ ದೃಢೀಕರಣ (ಸ್ಥಳೀಯ ಪಂಚನಾಮ)")}
        </div>
        <div style="font-size: 0.8rem; color: #6b7c74; margin-bottom: 12px;">
            {t("Neighboring merchants & market associations who have digitally attested to this vendor's daily presence.", "पड़ोसी दुकानदार और बाजार संघ जिन्होंने इस विक्रेता की दैनिक उपस्थिति का डिजिटल सत्यापन किया है।", "ఈ వ్యాపారి రోజువారీ ఉనికిని డిజిటల్‌గా ధృవీకరించిన పొరుగు వ్యాపారులు & మార్కెట్ సంఘాలు.", "இந்த வணிகரின் தினசரி வருகையை டிஜிட்டல் முறையில் சான்றளித்த அண்டை வணிகர்கள் மற்றும் சந்தை சங்கங்கள்.", "ಈ ವ್ಯಾಪಾರಿಯ ದೈನಂದಿನ ಉಪಸ್ಥಿತಿಯನ್ನು ಡಿಜಿಟಲ್ ರೂಪದಲ್ಲಿ ದೃಢೀಕರಿಸಿದ ನೆರೆಯ ವ್ಯಾಪಾರಿಗಳು ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಸಂಘಗಳು.")}
        </div>
        """, unsafe_allow_html=True)

        peers = md.get("sthan_peers", [])
        if peers:
            for p in peers:
                st.markdown(f"""
                <div class="peer-card">
                    <div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #0d3b28;">{p['name']}</div>
                        <div style="font-size: 0.75rem; color: #6b7c74;">{p['role']} • {p['tenure']} {t('presence', 'उपस्थिति', 'ఉనికి', 'வருகை', 'ಉಪಸ್ಥಿತಿ')}</div>
                    </div>
                    <span class="safe-badge" style="font-size: 0.65rem; padding: 2px 8px;">{p['status']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert-danger" style="padding: 12px 16px;">
                <div style="font-size: 0.85rem; font-weight: 600;">
                    {t("No Peer Endorsements Found", "कोई सह-व्यापारी प्रमाणन नहीं मिला", "ఎటువంటి సహచర వ్యాపారుల ధృవీకరణలు లభించలేదు", "சக வியாபாரிகளின் சான்றுகள் எதுவும் இல்லை", "ಯಾವುದೇ ಸಹವರ್ತಿ ವ್ಯಾಪಾರಿಗಳ ದೃಢೀಕರಣ ಕಂಡುಬಂದಿಲ್ಲ")}
                </div>
                <div style="font-size: 0.8rem; color: #7f1d1d;">
                    {t("This account has zero local merchant vouchers, indicating a fly-by-night or shell entity.", "इस खाते के पास कोई स्थानीय सत्यापनकर्ता नहीं है, जो एक अस्थिर या फर्जी इकाई का संकेत है।", "ఈ ఖాతాకు ఎటువంటి స్థానిక వ్యాపారుల మద్దతు లేదు, ఇది ఒక తాత్కాలిక లేదా నకిలీ సంస్థను సూచిస్తుంది.", "இந்த கணக்கிற்கு உள்ளூர் வியாபாரிகளின் சான்றுகள் எதுவும் இல்லை, இது ஒரு தற்காலிக நிறுவனத்தைக் குறிக்கிறது.", "ಈ ಖಾತೆಗೆ ಯಾವುದೇ ಸ್ಥಳೀಯ ವ್ಯಾಪಾರಿಗಳ ದೃಢೀಕರಣವಿಲ್ಲ, ಇದು ಒಂದು ಅಸ್ಥಿರ ಅಥವಾ ಶೆಲ್ ಘಟಕವನ್ನು ಸೂಚಿಸುತ್ತದೆ.")}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with c_right:
        st.markdown(f"""
        <div style="font-size: 1.15rem; font-weight: 700; color: #0d3b28; margin-bottom: 12px;">
            {t("Emergency Enforcement Shield", "आपातकालीन प्रवर्तन ढाल", "అత్యవసర తొలగింపు నిరోధక రక్షణ", "அவசரகால வெளியேற்ற தடுப்பு அரண்", "ತುರ್ತು ಜಾರಿ ರಕ್ಷಣೆ")}
        </div>
        """, unsafe_allow_html=True)

        squad_toggle = st.toggle(
            t("🚨 Activate 'Municipal Squad Mode' (Emergency Defense Shield)", "🚨 'नगर निगम दस्ता मोड' चालू करें (आपातकालीन ढाल)", "🚨 'మున్సిపల్ స్క్వాడ్ మోడ్' ఆన్ చేయండి (అత్యవసర రక్షణ)", "🚨 'நகராட்சி படைப் பிரிவு பயன்முறையை' இயக்கு (அவசரகால பாதுகாப்பு)", "🚨 'ಮುನ್ಸಿಪಲ್ ಸ್ಕ್ವಾಡ್ ಮೋಡ್' ಸಕ್ರಿಯಗೊಳಿಸಿ (ತುರ್ತು ರಕ್ಷಣಾ ಕವಚ)"),
            key=f"squad_mode_{merchant}",
            value=False,
        )

        if squad_toggle:
            if is_suspicious:
                st.markdown(f"""
                <div class="alert-danger">
                    <div style="font-weight: 800; font-size: 1rem; margin-bottom: 6px;">
                        ⚠️ {t("DISPLACEMENT DEFENSE INELIGIBLE", "बेदखली सुरक्षा के लिए अयोग्य", "తొలగింపు రక్షణకు అనర్హులు", "வெளியேற்ற பாதுகாப்பு தகுதியற்றது", "ಸ್ಥಳಾಂತರ ರಕ್ಷಣೆಗೆ ಅರ್ಹರಲ್ಲ")}
                    </div>
                    <div style="font-size: 0.85rem;">
                        {t("This account has only 18 recorded days and an 18.2% geofence adherence rate across 7 wards. Statutory Section 3(3) protection cannot be invoked.", "इस खाते के केवल 18 दिन दर्ज हैं और 7 अलग-अलग वार्डों में भू-उल्लंघन पाया गया है। धारा 3(3) की सुरक्षा लागू नहीं की जा सकती।", "ఈ ఖాతాలో కేవలం 18 రోజులు మాత్రమే నమోదయ్యాయి మరియు 7 వార్డులలో జియో-ఉల్లంఘనలు జరిగాయి. చట్టబద్ధమైన సెక్షన్ 3(3) రక్షణ వర్తించదు.", "இந்த கணக்கில் 18 நாட்கள் மட்டுமே பதிவாகியுள்ளன மற்றும் 7 வார்டுகளில் இருப்பிட மீறல்கள் உள்ளன. சட்டப்பூர்வ பிரிவு 3(3) பாதுகாப்பைப் பயன்படுத்த முடியாது.", "ಈ ಖಾತೆಯಲ್ಲಿ ಕೇವಲ 18 ದಿನಗಳು ದಾಖಲಾಗಿವೆ ಮತ್ತು 7 ವಾರ್ಡ್‌ಗಳಲ್ಲಿ ಜಿಯೋ-ಉಲ್ಲಂಘನೆ ಕಂಡುಬಂದಿದೆ. ಶಾಸನಬದ್ಧ ವಿಭಾಗ 3(3) ರಕ್ಷಣೆಯನ್ನು ಅನ್ವಯಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ.")}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                squad_hash = stable_id(merchant, "SQUAD-PROOF", prefix="SHA256-", digits=12).upper()
                st.markdown(f"""
                <div class="squad-mode-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eab308; padding-bottom: 8px; margin-bottom: 12px;">
                        <span style="font-size: 1.05rem; font-weight: 800; color: #fde047; letter-spacing: 0.5px;">
                            ⚠️ {t("STATUTORY NOTICE TO SQUAD / TVC OFFICER", "नगर निगम दस्ते / TVC अधिकारी को वैधानिक सूचना", "మున్సిపల్ అధికారికి చట్టబద్ధమైన నోటీసు", "நகராட்சி படை அதிகாரிக்கு சட்டப்பூர்வ அறிவிப்பு", "ಪುರಸಭೆಯ ದಳದ ಅಧಿಕಾರಿಗೆ ಶಾಸನಬದ್ಧ ನೋಟಿಸ್")}
                        </span>
                        <span style="background: #eab308; color: #1e293b; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 800;">
                            {t("SEC 3(3) IMMUNITY ACTIVE", "धारा 3(3) सुरक्षा सक्रिय", "సెక్షన్ 3(3) రక్షణ క్రియాశీలంగా ఉంది", "பிரிவு 3(3) பாதுகாப்பு செயல்பாட்டில் உள்ளது", "ಸೆಕ್ಷನ್ 3(3) ವಿನಾಯಿತಿ ಸಕ್ರಿಯವಾಗಿದೆ")}
                        </span>
                    </div>
                    <div style="font-size: 0.9rem; line-height: 1.6;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px;">
                            <div><b>{t("VENDOR NAME", "विक्रेता का नाम", "విక్రేత పేరు", "வியாபாரி பெயர்", "ಮಾರಾಟಗಾರನ ಹೆಸರು")}:</b> {display_name}</div>
                            <div><b>{t("ESTABLISHED SPOT", "निर्धारित स्थल", "స్థలం", "இடம்", "ಸ್ಥಳ")}:</b> {display_ward}</div>
                            <div><b>{t("VERIFIED TENURE", "कार्यकाल", "కాలపరిమితి", "சரிபார்க்கப்பட்ட காலம்", "ಪರಿಶೀಲಿಸಿದ ಅವಧಿ")}:</b> <span style="color: #4ade80; font-weight: 800;">{active_tenure_days} {t("DAYS", "दिन", "రోజులు", "நாட்கள்", "ದಿನಗಳು")}</span></div>
                            <div><b>{t("GEOFENCE SCORE", "जियोफेंस", "జియోఫెన్స్ స్కోరు", "இருப்பிட மதிப்பெண்", "ಜಿಯೋಫೆನ್ಸ್ ಸ್ಕೋರ್")}:</b> <span style="color: #4ade80; font-weight: 800;">{md['sthan_geofence_adherence']}%</span></div>
                        </div>
                        <div style="background: rgba(234, 179, 8, 0.12); border-left: 4px solid #eab308; padding: 10px 14px; border-radius: 4px; font-size: 0.82rem; color: #fef08a; margin-bottom: 10px;">
                            <b>{t("LEGAL WARNING TO INSPECTION TEAM", "निरीक्षण दल को कानूनी चेतावनी", "నిరీక్షణ బృందానికి చట్టపరమైన హెచ్చరిక", "ஆய்வுக் குழுவிற்கு சட்டப்பூர்வ எச்சரிக்கை", "ಪರಿಶೀಲನಾ ತಂಡಕ್ಕೆ ಕಾನೂನು ಎಚ್ಚರಿಕೆ")}:</b><br>
                            {t(
                                "Pursuant to Section 3(3) of Central Act No. 7 of 2014 and the landmark Supreme Court ruling in <i>Maharashtra Ekta Hawkers Union v. BMC (2014) 1 SCC 490</i>, this vendor holds verified continuous vending status. <b>Arbitrary eviction, spot reallocation, or seizure of goods prior to TVC survey conclusion is strictly prohibited and constitutes contempt of statutory mandate.</b>",
                                "केंद्रीय अधिनियम संख्या 7 (2014) की धारा 3(3) और सर्वोच्च न्यायालय के फैसले <i>(महाराष्ट्र एकता हॉकर्स यूनियन बनाम बीएमसी, 2014)</i> के अनुसार, यह विक्रेता निरंतर वेंडिंग का सत्यापित दर्जा रखता है। <b>TVC सर्वेक्षण पूरा होने से पहले बेदखली या सामान जब्ती कानूनन वर्जित है।</b>",
                                "కేంద్ర చట్టం సంఖ్య 7 (2014) లోని సెక్షన్ 3(3) మరియు సుప్రీం కోర్ట్ తీర్పు ప్రకారం, ఈ విక్రేత ధృవీకరించబడిన నిరంతర వ్యాపార స్థితిని కలిగి ఉన్నాడు. <b>TVC సర్వే పూర్తికాకముందే ఇతనిని తొలగించడం లేదా సరుకులు జప్తు చేయడం చట్టవిరుద్ధం.</b>",
                                "மத்திய சட்டம் எண் 7 (2014) இன் பிரிவு 3(3) மற்றும் உச்ச நீதிமன்றத் தீர்ப்பின்படி, இந்த வியாபாரி சரிபார்க்கப்பட்ட தொடர்ச்சியான வியாபார நிலையை கொண்டுள்ளார். <b>TVC கணக்கெடுப்பு முடிவதற்கு முன்னர் தன்னிச்சையாக வெளியேற்றுவது அல்லது பொருட்களைப் பறிமுதல் செய்வது சட்டம் மீறிய செயலாகும்.</b>",
                                "ಕೇಂದ್ರ ಕಾಯ್ದೆ ಸಂಖ್ಯೆ 7 (2014) ರ ವಿಭಾಗ 3(3) ಮತ್ತು ಸುಪ್ರೀಂ ಕೋರ್ಟ್‌ನ ಮಹತ್ವದ ತೀರ್ಪಿನ ಪ್ರಕಾರ, ಈ ಮಾರಾಟಗಾರನು ಪರಿಶೀಲಿಸಿದ ನಿರಂತರ ಮಾರಾಟದ ಸ್ಥಿತಿಯನ್ನು ಹೊಂದಿದ್ದಾನೆ. <b>ಟಿವಿಸಿ ಸಮೀಕ್ಷೆಯ ಮುಕ್ತಾಯಕ್ಕೆ ಮುನ್ನ ಮಾರಾಟಗಾರನನ್ನು ಉಚ್ಚಾಟಿಸುವುದು ಅಥವಾ ವಸ್ತುಗಳನ್ನು ಜಪ್ತಿ ಮಾಡುವುದು ಶಾಸನಬದ್ಧ ಆದೇಶದ ಉಲ್ಲಂಘನೆಯಾಗುತ್ತದೆ.</b>"
                            )}
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #94a3b8; border-top: 1px solid #334155; padding-top: 8px;">
                            <span>{t("Ledger Hash", "लेजर हैश", "లెడ్జర్ హాష్", "பதிவேடு குறியீடு", "ಲೆಡ್ಜರ್ ಹ್ಯಾಶ್")}: {squad_hash}</span>
                            <span>{t("Verification Authority", "सत्यापन", "ధృవీకరణ అధికారం", "சரிபார்ப்பு அதிகாரம்", "ಪರಿಶೀಲನಾ ಪ್ರಾಧಿಕಾರ")}: Urban TVC Grievance Portal</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">{t("Statutory Proof-of-Vending Certificate", "वैधानिक वेंडिंग प्रमाणपत्र", "చట్టబద్ధమైన వీధి వ్యాపార ధృవీకరణ పత్రం", "சட்டப்பூர்வ தெரு வியாபார சான்றிதழ்", "ಶಾಸನಬದ್ಧ ವ್ಯಾಪಾರ ಪ್ರಮಾಣಪತ್ರ")}</div>',
                unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size: 0.9rem; color: #4b6358; margin-bottom: 16px;">
        {t(
            "Generate an official, tamper-evident certificate of continuous vending occupancy under Section 65B of the Indian Evidence Act, 1872 / Bhartiya Sakshya Adhiniyam, 2023 for Town Vending Committee (TVC) hearings, municipal licensing, and PM SVANidhi LOR applications.",
            "टाउन वेंडिंग कमेटी (TVC) सुनवाई, नगर निगम लाइसेंसिंग और पीएम स्वनिधि LOR आवेदन के लिए भारतीय साक्ष्य अधिनियम की धारा 65B के तहत निरंतर वेंडिंग अधिभोग का आधिकारिक, डिजिटल प्रमाणपत्र जनरेट करें।",
            "టౌన్ వెండింగ్ కమిటీ (TVC) విచారణలు, మున్సిపల్ లైసెన్సింగ్ మరియు పీఎం స్వనిధి LOR దరఖాస్తుల కొరకు ఇండియన్ ఎవిడెన్స్ యాక్ట్ లోని సెక్షన్ 65B కింద నిరంతర వీధి వ్యాపారానికి సంబంధించిన అధికారిక డిజిటల్ ధృవీకరణ పత్రాన్ని సృష్టించండి.",
            "நகர வியாபாரக் குழு (TVC) விசாரணைகள், நகராட்சி உரிமம் மற்றும் பிஎம் ஸ்வநிதி எல்ஓஆர் விண்ணப்பங்களுக்காக இந்திய சான்றுச் சட்டத்தின் பிரிவு 65B இன் கீழ் அதிகாரப்பூர்வ டிஜிட்டல் சான்றிதழை உருவாக்கவும்.",
            "ಟೌನ್ ವೆಂಡಿಂಗ್ ಕಮಿಟಿ (TVC) ವಿಚಾರಣೆಗಳು, ಮುನ್ಸಿಪಲ್ ಪರವಾನಗಿ ಮತ್ತು ಪಿಎಂ ಸ್ವನಿಧಿ ಎಲ್‌ಒಆರ್ ಅರ್ಜಿಗಳಿಗಾಗಿ ಭಾರತೀಯ ಸಾಕ್ಷ್ಯ ಕಾಯ್ದೆಯ ಸೆಕ್ಷನ್ 65B ಅಡಿಯಲ್ಲಿ ಅಧಿಕೃತ ಡಿಜಿಟಲ್ ಪ್ರಮಾಣಪತ್ರವನ್ನು ರಚಿಸಿ."
        )}
    </div>
    """, unsafe_allow_html=True)

    cert_id = stable_id(merchant, active_tenure_days, prefix="STHAN-CERT-", digits=8).upper()
    merkle_hash = stable_id(merchant, active_tenure_days, "MERKLE-ROOT", prefix="0xSHA256-", digits=16).upper()

    st.markdown(f"""
    <div class="cert-official">
        <div style="text-align: center; border-bottom: 2px solid #0d3b28; padding-bottom: 16px; margin-bottom: 20px;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #6b7c74; letter-spacing: 2px; text-transform: uppercase;">
                {t(
                    "MUNICIPAL CORPORATION / TOWN VENDING COMMITTEE EVIDENCE DOSSIER",
                    "नगर निगम / टाउन वेंडिंग कमेटी साक्ष्य डोजियर",
                    "మునిసిపల్ కార్పొరేషన్ / టౌన్ వెండింగ్ కమిటీ సాక్ష్యాల పత్రం",
                    "மாநகராட்சி / நகர வியாபாரக் குழு சான்று கோப்பு",
                    "ಮಹಾನಗರ ಪಾಲಿಕೆ / ಟೌನ್ ವೆಂಡಿಂಗ್ ಕಮಿಟಿ ಸಾಕ್ಷ್ಯ ದಾಖಲೆ"
                )}
            </div>
            <div style="font-size: 1.4rem; font-weight: 800; color: #0d3b28; margin: 6px 0;">
                {t(
                    "CERTIFICATE OF CONTINUOUS STREET VENDING TENURE",
                    "निरन्तर स्ट्रीट वेंडिंग कार्यकाल प्रमाणपत्र",
                    "నిరంతర వీధి వ్యాపార కాలపరిమితి ధృవీకరణ పత్రం",
                    "தொடர்ச்சியான தெரு வியாபார சான்றிதழ்",
                    "ನಿರಂತರ ಬೀದಿ ಬದಿ ವ್ಯಾಪಾರ ಪ್ರಮಾಣಪತ್ರ"
                )}
            </div>
            <div style="font-size: 0.85rem; color: #1b5e20; font-weight: 600;">
                {t(
                    "Issued pursuant to Section 3(3) & Section 4 of The Street Vendors (Protection of Livelihood and Regulation of Street Vending) Act, 2014",
                    "स्ट्रीट वेंडर्स (आजीविका संरक्षण और स्ट्रीट वेंडिंग का विनियमन) अधिनियम, 2014 की धारा 3(3) एवं धारा 4 के तहत जारी",
                    "వీధి వ్యాపారుల (జీవనోపాధి రక్షణ మరియు వీధి వ్యాపార నియంత్రణ) చట్టం, 2014 లోని సెక్షన్ 3(3) & సెక్షన్ 4 ప్రకారం జారీ చేయబడింది",
                    "தெரு வியாபாரிகள் (ஜீவனோபாய பாதுகாப்பு மற்றும் தெரு வியாபார ஒழுங்குமுறை) சட்டம், 2014 இன் பிரிவு 3(3) மற்றும் பிரிவு 4 இன் படி வழங்கப்பட்டது",
                    "ಬೀದಿ ಬದಿ ವ್ಯಾಪಾರಿಗಳ (ಜೀವನೋಪಾಯ ರಕ್ಷಣೆ ಮತ್ತು ಬೀದಿ ವ್ಯಾಪಾರದ ನಿಯಂತ್ರಣ) ಕಾಯ್ದೆ, 2014 ರ ವಿಭಾಗ 3(3) ಮತ್ತು ವಿಭಾಗ 4 ರ ಅನ್ವಯ ನೀಡಲಾಗಿದೆ"
                )}
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; font-size: 0.88rem; line-height: 1.6; margin-bottom: 20px;">
            <div>
                <b>{t("Certificate ID", "प्रमाणपत्र ID", "ధృవీకరణ పత్రం ID", "சான்றிதழ் ஐடி", "ಪ್ರಮಾಣಪತ್ರ ID")}:</b> <span style="color: #0d3b28; font-weight: 700;">{cert_id}</span><br>
                <b>{t("Vendor Name", "विक्रेता का नाम", "విక్రేత పేరు", "வியாபாரி பெயர்", "ಮಾರಾಟಗಾರನ ಹೆಸರು")}:</b> {display_name} ({display_owner})<br>
                <b>{t("Designated Spot", "निर्धारित स्थल", "నిర్దేశిత స్థలం", "குறிப்பிடப்பட்ட இடம்", "ನಿಗದಿಪಡಿಸಿದ ಸ್ಥಳ")}:</b> {display_spot}<br>
                <b>{t("Jurisdiction / Ward", "क्षेत्राधिकार / वार्ड", "వార్డు", "வார்டு", "ವಾರ್ಡ್")}:</b> {display_ward}
            </div>
            <div>
                <b>{t("Verified Continuous Tenure", "सत्यापित निरंतर कार्यकाल", "ధృవీకరించబడిన నిరంతర వ్యాపార కాలం", "சரிபார்க்கப்பட்ட தொடர்ச்சியான காலம்", "ಪರಿಶೀಲಿಸಿದ ನಿರಂತರ ಅವಧಿ")}:</b> <span style="color: #00a844; font-weight: 800; font-size: 1.05rem;">{active_tenure_days} {t("Days", "दिन", "రోజులు", "நாட்கள்", "ದಿನಗಳು")}</span><br>
                <b>{t("Tenure Commenced", "कार्यकाल प्रारंभ", "వ్యాపారం ప్రారంభమైన తేదీ", "தொடங்கிய தேதி", "ಆರಂಭವಾದ ದಿನಾಂಕ")}:</b> {md['sthan_start_date']}<br>
                <b>{t("Geofence Compliance", "स्थान अनुपालन", "జియోఫెన్స్ అనుకూలత", "இருப்பிட இணக்கம்", "ಜಿಯೋಫೆನ್ಸ್ ಅನುಸರಣೆ")}:</b> {md['sthan_geofence_adherence']}% (GNSS dual-band anchor)<br>
                <b>{t("Peer Corroboration", "स्थानीय पंचनामा", "సహచర వ్యాపారుల మద్దతు", "சக வியாபாரிகளின் சான்றுகள்", "ಸಹವರ್ತಿಗಳ ದೃಢೀಕರಣ")}:</b> {len(md.get('sthan_peers', []))} {t("Independent Merchants Verified", "स्वतंत्र व्यापारियों द्वारा सत्यापित", "స్వతంత్ర వ్యాపారులు ధృవీకరించారు", "சுயாதீன வணிகர்களால் சரிபார்க்கப்பட்டது", "ಸ್ವತಂತ್ರ ವ್ಯಾಪಾರಿಗಳಿಂದ ದೃಢೀಕರಿಸಲ್ಪಟ್ಟಿದೆ")}
            </div>
        </div>

        <div style="background: #f8fffe; border: 1px dashed #00c853; border-radius: 8px; padding: 14px 18px; font-size: 0.82rem; color: #1b5e20; line-height: 1.5; margin-bottom: 20px;">
            <b>{t("STATUTORY ATTESTATION", "वैधानिक सत्यापन", "చట్టబద్ధమైన ధృవీకరణ", "சட்டப்பூர்வ சான்றளிப்பு", "ಶಾಸನಬದ್ಧ ದೃಢೀಕರಣ")}:</b><br>
            {t(
                "This electronic record is cryptographically signed and stored in compliance with Section 65B of the Indian Evidence Act, 1872 / Bhartiya Sakshya Adhiniyam, 2023. The data establishes uninterrupted vending presence at the recorded geographical anchor. As stipulated in Section 3(3) of Central Act No. 7 of 2014, the holder of this certificate is statutorily protected against eviction, relocation, or seizure of vending paraphernalia pending the conclusion of the Town Vending Committee survey.",
                "यह इलेक्ट्रॉनिक रिकॉर्ड भारतीय साक्ष्य अधिनियम, 1872 / भारतीय साक्ष्य अधिनियम, 2023 की धारा 65B के अनुपालन में क्रिप्टोग्राफ़िक रूप से सुरक्षित है। यह डेटा दर्ज भौगोलिक केंद्र पर निर्बाध वेंडिंग उपस्थिति स्थापित करता है। अधिनियम की धारा 3(3) के अनुसार, इस धारक को टीवीसी सर्वेक्षण पूरा होने तक किसी भी बेदखली या जब्ती से कानूनी संरक्षण प्राप्त है।",
                "ఈ ఎలక్ట్రానిక్ రికార్డ్ ఇండియన్ ఎవిడెన్స్ యాక్ట్ లోని సెక్షన్ 65B కింద క్రిప్టోగ్రాఫిక్ పద్ధతిలో భద్రపరచబడింది. నమోదైన భౌగోళిక స్థలంలో ఈ విక్రేత నిరంతర వ్యాపార ఉనికిని కలిగి ఉన్నాడని ఈ డేటా ధృవీకరిస్తోంది. కేంద్ర చట్టం సంఖ్య 7 (2014) లోని సెక్షన్ 3(3) ప్రకారం, టౌన్ వెండింగ్ కమిటీ సర్వే ముగిసే వరకు ఇతనిని తొలగించడం గానీ, వేరే చోటికి మార్చడం గానీ చట్టవిరుద్ధం.",
                "இந்த மின்னணு பதிவு இந்திய சான்றுச் சட்டத்தின் பிரிவு 65B இன் படி குறியாக்க முறையில் பாதுகாக்கப்பட்டுள்ளது. பதிவு செய்யப்பட்ட புவியியல் இடத்தில் இந்த வியாபாரி தொடர்ச்சியாக வியாபாரம் செய்து வருவதை இந்த தரவு உறுதிப்படுத்துகிறது. மத்திய சட்டம் எண் 7 (2014) இன் பிரிவு 3(3) இன் படி, நகர வியாபாரக் குழு கணக்கெடுப்பு முடியும் வரை இந்த சான்றிதழ் வைத்திருப்பவர் வெளியேற்றத்திற்கு எதிராக சட்டப்பூர்வ பாதுகாப்பு பெறுகிறார்.",
                "ಈ ಎಲೆಕ್ಟ್ರಾನಿಕ್ ದಾಖಲೆಯನ್ನು ಭಾರತೀಯ ಸಾಕ್ಷ್ಯ ಕಾಯ್ದೆಯ ಸೆಕ್ಷನ್ 65B ಅನ್ವಯ ಕ್ರಿಪ್ಟೋಗ್ರಾಫಿಕ್ ರೂಪದಲ್ಲಿ ಸುರಕ್ಷಿತವಾಗಿರಿಸಲಾಗಿದೆ. ದಾಖಲಾದ ಭೌಗೋಳಿಕ ಸ್ಥಳದಲ್ಲಿ ವ್ಯಾಪಾರಿಯ ನಿರಂತರ ಉಪಸ್ಥಿತಿಯನ್ನು ಈ ಡೇಟಾ ದೃಢೀಕರಿಸುತ್ತದೆ. ಕೇಂದ್ರ ಕಾಯ್ದೆಯ ವಿಭಾಗ 3(3) ರ ಪ್ರಕಾರ, ಟಿವಿಸಿ ಸಮೀಕ್ಷೆಯ ಮುಕ್ತಾಯದವರೆಗೆ ಈ ಪ್ರಮಾಣಪತ್ರ ಹೊಂದಿರುವವರಿಗೆ ಕಾನೂನು ರಕ್ಷಣೆ ಇರುತ್ತದೆ."
            )}
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: #6b7c74; border-top: 1px solid #e0f2ec; padding-top: 12px;">
            <div>
                <b>{t("Cryptographic Merkle Root", "क्रिप्टोग्राफ़िक रूट", "క్రిప్టోగ్రాఫిక్ రూట్", "குறியாக்க மெர்கಲ್ ரூட்", "ಕ್ರಿಪ್ಟೋಗ್ರಾಫಿಕ್ ಮೆರ್ಕಲ್ ರೂಟ್")}:</b> {merkle_hash}<br>
                <b>{t("Timestamp", "समय-मुहर", "సమయం", "நேர முத்திரை", "ಸಮಯ-ಮುದ್ರೆ")}:</b> {NOW.strftime('%d %B %Y, %I:%M:%S %p')} IST
            </div>
            <div style="text-align: right;">
                <span class="safe-badge" style="font-size: 0.75rem; padding: 4px 12px;">{t("TVC AUDIT READY", "TVC ऑडिट हेतु मान्य", "TVC పరిశీలనకు సిద్ధంగా ఉంది", "TVC தணிக்கைக்கு தயார்", "ಟಿವಿಸಿ ಆಡಿಟ್‌ಗೆ ಸಿದ್ಧವಾಗಿದೆ")}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sep_eq, sep_dash = "=" * 64, "-" * 64
    cert_text = {sep_eq}
  