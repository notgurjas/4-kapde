"""VyaparScore — Micro-Merchant Credit Score & UPI Anomaly Detector.

A single-file Streamlit hackathon demo that turns raw UPI payment history and a
photographed paper "bahi-khata" (ledger) into:

    Tab 1  Digital UPI & Credit Score      -> 300-900 score, KPIs, income trends
    Tab 2  Physical Register Scanner (OCR) -> simulated OCR into an editable ledger
    Tab 3  UPI Anomaly & Fraud Detector    -> rule engine with reason codes
    Tab 4  Micro-Loan Instant Approval     -> EMI calculator + sanction certificate

Run:
    pip install -r requirements.txt
    streamlit run app.py

Everything is synthetic/simulated: no external OCR or credit-bureau API is
called, no uploaded file is written to disk, and nothing leaves the process.
"""

from __future__ import annotations

import hashlib
import inspect
import io
import math
import re
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# 0. Environment compatibility
# ---------------------------------------------------------------------------
# Streamlit 1.49+ replaced `use_container_width=True` with `width="stretch"`.
# Detect it per element so the app is clean on old and new releases alike.


def _stretch(element) -> dict:
    try:
        params = inspect.signature(element).parameters
    except (TypeError, ValueError):  # pragma: no cover - builtins without signature
        return {"use_container_width": True}
    return {"width": "stretch"} if "width" in params else {"use_container_width": True}


BTN = _stretch(st.button)
IMG = _stretch(st.image)
FRAME = _stretch(st.dataframe)
EDITOR = _stretch(st.data_editor)
CHART = _stretch(st.plotly_chart)


def render_chart(fig: go.Figure, height: int | None = None) -> None:
    """Render a Plotly figure full-width on every supported Streamlit version."""
    if height is not None:
        fig.update_layout(height=height)
    st.plotly_chart(fig, config={"displayModeBar": False}, **CHART)


# ---------------------------------------------------------------------------
# 1. Theme & static copy
# ---------------------------------------------------------------------------

PALETTE = {
    "ink": "#0B1220",
    "primary": "#4F46E5",
    "primary_deep": "#3730A3",
    "accent": "#0EA5E9",
    "success": "#059669",
    "warning": "#D97706",
    "danger": "#DC2626",
    "muted": "#64748B",
    "border": "#E4E8F0",
    "canvas": "#F5F7FB",
}

CSS = f"""
<style>
:root {{ color-scheme: light; }}

html, body, [class*="css"] {{
    font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto,
                 "Helvetica Neue", Arial, sans-serif;
}}
.stApp {{ background: {PALETTE['canvas']}; color: {PALETTE['ink']}; }}
.block-container {{ padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1400px; }}

/* ---- sidebar ---- */
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%); }}
section[data-testid="stSidebar"] * {{ color: #E2E8F0; }}
section[data-testid="stSidebar"] .vs-side-note b {{ color: #F8FAFC; }}
.vs-side-brand {{ font-size: 1.35rem; font-weight: 800; letter-spacing: -.02em; margin: 0 0 .1rem 0; }}
.vs-side-sub {{ color: #94A3B8; font-size: .78rem; margin: 0 0 .4rem 0; line-height: 1.45; }}
.vs-side-note {{
    background: rgba(148,163,184,.12); border: 1px solid rgba(148,163,184,.25);
    border-radius: 10px; padding: .55rem .7rem; font-size: .72rem; color: #CBD5E1; line-height: 1.5;
}}

/* ---- masthead ---- */
.vs-masthead {{
    background: linear-gradient(115deg, #0F172A 0%, #312E81 55%, #4F46E5 100%);
    border-radius: 18px; padding: 1.3rem 1.55rem; color: #fff;
    box-shadow: 0 18px 40px -22px rgba(15,23,42,.75); margin-bottom: 1.1rem;
}}
.vs-masthead h1 {{ font-size: 1.6rem; font-weight: 800; margin: 0; letter-spacing: -.025em; }}
.vs-masthead .vs-sub {{ color: #C7D2FE; font-size: .87rem; margin: .3rem 0 .8rem 0; }}
.vs-chip {{
    display: inline-block; padding: .26rem .68rem; border-radius: 999px;
    background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.22);
    font-size: .73rem; font-weight: 600; margin: 0 .32rem .22rem 0;
}}

/* ---- metric cards ---- */
.vs-card {{
    background: #fff; border: 1px solid {PALETTE['border']}; border-radius: 14px;
    padding: .9rem 1.05rem; height: 100%; box-shadow: 0 8px 22px -20px rgba(15,23,42,.55);
}}
.vs-card-label {{
    font-size: .67rem; font-weight: 700; letter-spacing: .085em; text-transform: uppercase;
    color: {PALETTE['muted']}; margin-bottom: .32rem;
}}
.vs-card-value {{ font-size: 1.5rem; font-weight: 800; letter-spacing: -.02em; color: {PALETTE['ink']}; }}
.vs-card-foot {{ font-size: .73rem; color: {PALETTE['muted']}; margin-top: .28rem; }}
.vs-up {{ color: {PALETTE['success']}; font-weight: 700; }}
.vs-down {{ color: {PALETTE['danger']}; font-weight: 700; }}
.vs-flat {{ color: {PALETTE['muted']}; font-weight: 700; }}

/* ---- score hero ---- */
.vs-hero {{
    border-radius: 16px; padding: 1.1rem 1.3rem; color: #fff;
    box-shadow: 0 18px 34px -22px rgba(15,23,42,.8);
}}
.vs-hero-label {{ font-size: .68rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; opacity: .85; }}
.vs-hero-score {{ font-size: 3.3rem; font-weight: 800; line-height: 1.05; letter-spacing: -.04em; }}
.vs-hero-scale {{ font-size: .73rem; opacity: .82; }}
.vs-hero-grade {{
    display: inline-block; margin-top: .45rem; padding: .28rem .8rem; border-radius: 999px;
    background: rgba(255,255,255,.2); border: 1px solid rgba(255,255,255,.32);
    font-size: .8rem; font-weight: 700;
}}

/* ---- panels & badges ---- */
.vs-panel {{
    background: #fff; border: 1px solid {PALETTE['border']}; border-radius: 14px;
    padding: .85rem 1.1rem; margin-bottom: .7rem; box-shadow: 0 8px 22px -22px rgba(15,23,42,.5);
}}
.vs-panel h4 {{ margin: 0 0 .12rem 0; font-size: 1rem; font-weight: 750; letter-spacing: -.01em; }}
.vs-panel p.vs-hint {{ margin: 0; color: {PALETTE['muted']}; font-size: .79rem; line-height: 1.5; }}
.vs-bar {{
    background: #fff; border: 1px solid {PALETTE['border']}; border-radius: 14px;
    padding: .85rem 1.1rem; margin-bottom: .9rem; display: flex; justify-content: space-between;
    align-items: center; flex-wrap: wrap; gap: .6rem; box-shadow: 0 8px 22px -22px rgba(15,23,42,.5);
}}
.vs-bar h4 {{ margin: 0 0 .12rem 0; font-size: 1rem; font-weight: 750; }}
.vs-bar p.vs-hint {{ margin: 0; color: {PALETTE['muted']}; font-size: .79rem; line-height: 1.5; }}

.vs-badge {{
    display: inline-block; padding: .22rem .6rem; border-radius: 999px;
    font-size: .7rem; font-weight: 750; letter-spacing: .03em; white-space: nowrap;
}}
.vs-badge-high {{ background: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }}
.vs-badge-med  {{ background: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }}
.vs-badge-low  {{ background: #E0F2FE; color: #075985; border: 1px solid #7DD3FC; }}
.vs-badge-ok   {{ background: #D1FAE5; color: #065F46; border: 1px solid #6EE7B7; }}

.vs-flagcard {{
    border-left: 4px solid {PALETTE['danger']}; background: #fff; border-radius: 10px;
    padding: .65rem .85rem; border-top: 1px solid {PALETTE['border']};
    border-right: 1px solid {PALETTE['border']}; border-bottom: 1px solid {PALETTE['border']};
    margin-bottom: .5rem;
}}
.vs-flagcard.med {{ border-left-color: {PALETTE['warning']}; }}
.vs-flagcard.low {{ border-left-color: {PALETTE['accent']}; }}
.vs-flagcard.ok {{ border-left-color: {PALETTE['success']}; }}
.vs-flagcard .t {{ font-weight: 750; font-size: .88rem; }}
.vs-flagcard .d {{ color: {PALETTE['muted']}; font-size: .77rem; line-height: 1.45; margin-top: .15rem; }}

/* ---- certificate ---- */
.vs-cert {{
    border: 2px solid {PALETTE['primary']}; border-radius: 18px;
    background: radial-gradient(120% 140% at 0% 0%, #EEF2FF 0%, #FFFFFF 45%);
    padding: 1.5rem 1.65rem; position: relative; overflow: hidden;
    box-shadow: 0 24px 50px -30px rgba(49,46,129,.7);
}}
.vs-cert:after {{
    content: ""; position: absolute; inset: 8px; border: 1px dashed #C7D2FE; border-radius: 12px;
}}
.vs-cert-head {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }}
.vs-cert-title {{ font-size: 1.45rem; font-weight: 800; color: {PALETTE['primary_deep']}; letter-spacing: -.02em; }}
.vs-cert-sub {{ color: {PALETTE['muted']}; font-size: .8rem; margin-top: .15rem; }}
.vs-cert-amount {{ font-size: 2.4rem; font-weight: 800; color: {PALETTE['ink']}; letter-spacing: -.03em; }}
.vs-cert-words {{ color: {PALETTE['muted']}; font-size: .8rem; font-style: italic; }}
.vs-cert-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: .75rem 1.1rem; margin: 1rem 0; }}
.vs-cert-grid div span {{
    display: block; font-size: .64rem; letter-spacing: .08em; text-transform: uppercase;
    color: {PALETTE['muted']}; font-weight: 700;
}}
.vs-cert-grid div b {{ font-size: .95rem; font-weight: 700; color: {PALETTE['ink']}; }}
.vs-cert-foot {{
    border-top: 1px solid {PALETTE['border']}; padding-top: .75rem;
    color: {PALETTE['muted']}; font-size: .71rem; line-height: 1.5;
}}
.vs-seal {{
    width: 72px; height: 72px; border-radius: 50%; flex: 0 0 72px;
    background: linear-gradient(140deg, #4F46E5, #0EA5E9); color: #fff;
    display: flex; align-items: center; justify-content: center; font-size: 1.85rem;
    box-shadow: 0 10px 22px -10px rgba(79,70,229,.9);
}}

[data-testid="stDataFrame"] {{ border-radius: 10px; }}
.vs-sep {{ height: 1px; background: {PALETTE['border']}; margin: .95rem 0; border: 0; }}
.vs-step {{
    display: flex; gap: .55rem; align-items: flex-start; margin-bottom: .45rem;
    font-size: .84rem; color: {PALETTE['muted']};
}}
.vs-step b {{ color: {PALETTE['ink']}; }}
.vs-empty {{
    background: #fff; border: 1px dashed {PALETTE['border']}; border-radius: 14px;
    padding: 1.6rem 1rem; text-align: center;
}}
</style>
"""

INDIAN_ONES = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
    "Seventeen", "Eighteen", "Nineteen",
]
INDIAN_TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

EXPENSE_CATEGORIES = [
    "Inventory Purchase", "Shop Rent", "Staff Wages", "Electricity & Utilities",
    "Packaging & Supplies", "Transport & Logistics", "Equipment Repair",
    "Marketing", "Miscellaneous",
]

PAYMENT_MODES = ["Cash", "UPI", "Bank Transfer", "Credit (Udhaar)"]

RULE_LOGIC = {
    "STR-01": ("Micro-transaction structuring", "High",
               "≥ 6 credits of ≤ max(₹20, 0.5 × median amount) inside any 5-minute window."),
    "MID-02": ("Midnight high-value credit", "High",
               "Credit between 00:00-04:59 worth ≥ max(₹5,000, 6 × 75th-percentile amount)."),
    "VEL-03": ("Transaction velocity spike", "Medium",
               "≥ max(25, 8 × median busy hour) successful credits inside any rolling 60 minutes."),
    "SPL-05": ("Same payer burst", "Medium", "≥ 5 credits from one payer inside 10 minutes."),
    "RND-04": ("Round-amount clustering", "Low",
               "≥ 4 exact round-figure (₹1,000 multiple) credits on the same day."),
}
REASON_CODES = {code: (label, severity) for code, (label, severity, _) in RULE_LOGIC.items()}

SOURCE_CHOICES = ["🧪 Mock merchant profile", "📤 Upload UPI CSV"]


# ---------------------------------------------------------------------------
# 2. Formatting helpers
# ---------------------------------------------------------------------------

def _indian_group(digits: str) -> str:
    """Group an integer string the Indian way: 1234567 -> 12,34,567."""
    if len(digits) <= 3:
        return digits
    head, tail = digits[:-3], digits[-3:]
    chunks: list[str] = []
    while len(head) > 2:
        chunks.insert(0, head[-2:])
        head = head[:-2]
    if head:
        chunks.insert(0, head)
    return ",".join(chunks) + "," + tail


def inr(value: float, decimals: int = 0) -> str:
    """Format a number in Indian Rupees: inr(1234567) -> '₹12,34,567'."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "₹0"
    sign = "-" if number < 0 else ""
    text = f"{abs(number):,.{decimals}f}".replace(",", "")
    if "." in text:
        int_part, frac = text.split(".", 1)
        return f"{sign}₹{_indian_group(int_part)}.{frac}"
    return f"{sign}₹{_indian_group(text)}"


def inr_words(value: float) -> str:
    """Indian-system number to words: 125000 -> 'One Lakh Twenty Five Thousand Rupees Only'."""
    number = int(round(abs(float(value))))
    if number == 0:
        return "Zero Rupees Only"

    def two_digits(n: int) -> str:
        if n < 20:
            return INDIAN_ONES[n]
        tens, ones = divmod(n, 10)
        return f"{INDIAN_TENS[tens]}{' ' + INDIAN_ONES[ones] if ones else ''}".strip()

    def three_digits(n: int) -> str:
        hundreds, rest = divmod(n, 100)
        parts = []
        if hundreds:
            parts.append(f"{INDIAN_ONES[hundreds]} Hundred")
        if rest:
            parts.append(two_digits(rest))
        return " ".join(parts)

    crore, remainder = divmod(number, 10_000_000)
    lakh, remainder = divmod(remainder, 100_000)
    thousand, remainder = divmod(remainder, 1_000)

    chunks = []
    if crore:
        chunks.append(f"{three_digits(crore)} Crore")
    if lakh:
        chunks.append(f"{two_digits(lakh)} Lakh")
    if thousand:
        chunks.append(f"{two_digits(thousand)} Thousand")
    if remainder:
        chunks.append(three_digits(remainder))
    return " ".join(chunks).strip() + " Rupees Only"


def pct(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}%"


def signed_pct(value: float) -> str:
    return f"{'+' if value >= 0 else ''}{value:.1f}%"


# ---------------------------------------------------------------------------
# 3. Mock merchant profiles & synthetic data generation
# ---------------------------------------------------------------------------

PROFILES: dict[str, dict] = {
    "Ramesh Tea Stall": {
        "owner": "Ramesh Kumar", "city": "Bengaluru, Karnataka",
        "segment": "Street food & beverages", "tenure_months": 41,
        "upi_id": "ramesh.tea@okhdfc", "daily_txn_target": 42, "avg_ticket": 48,
        "weekend_lift": 1.45, "noise": 0.30, "loyal_pool": 210, "loan_cap": 150_000, "growth": 4.0,
        "risk_profile": "light", "expense_ratio": 0.62, "seed": 101,
    },
    "Sharma Kirana Store": {
        "owner": "Anita Sharma", "city": "Mysuru, Karnataka",
        "segment": "Neighbourhood grocery", "tenure_months": 74,
        "upi_id": "sharmakirana@ybl", "daily_txn_target": 118, "avg_ticket": 265,
        "weekend_lift": 1.18, "noise": 0.22, "loyal_pool": 640, "loan_cap": 600_000, "growth": 9.0,
        "risk_profile": "minimal", "expense_ratio": 0.74, "seed": 202,
    },
    "Suspicious Merchant": {
        "owner": "Unverified Retail Account", "city": "Bengaluru, Karnataka",
        "segment": "General trading (KYC pending)", "tenure_months": 5,
        "upi_id": "quicktrade99@ptsbi", "daily_txn_target": 65, "avg_ticket": 190,
        "weekend_lift": 1.02, "noise": 0.68, "loyal_pool": 48, "loan_cap": 120_000, "growth": 8.0,
        "risk_profile": "heavy", "expense_ratio": 0.88, "seed": 303,
    },
}

HOUR_WEIGHTS = np.array(
    [0.05, 0.03, 0.02, 0.02, 0.02, 0.05, 0.25, 0.75, 1.60, 1.85, 1.70, 1.20,
     1.35, 1.05, 0.95, 1.00, 1.15, 1.70, 2.05, 1.95, 1.50, 1.05, 0.55, 0.22],
    dtype=float,
)
HOUR_PROBS = HOUR_WEIGHTS / HOUR_WEIGHTS.sum()

FIRST_NAMES = [
    "Arun", "Divya", "Sanjay", "Fatima", "Rahul", "Lakshmi", "Imran", "Pooja", "Vikram",
    "Meena", "Karthik", "Nisha", "Suresh", "Anjali", "Ravi", "Deepa", "Manoj", "Kavya",
    "Ganesh", "Rekha", "Tarun", "Sneha", "Ajay", "Bhavana", "Prakash", "Swati", "Naveen",
    "Harini", "Yogesh", "Shreya", "Mahesh", "Indu", "Farhan", "Neha", "Gopal", "Ashwini",
]
LAST_INITIALS = ["K", "R", "S", "M", "N", "B", "G", "T", "V", "P", "J", "L"]

ANOMALY_PLANS = {
    "minimal": {"structuring": 0, "midnight": 0, "velocity": 0, "rounds": 1},
    "light": {"structuring": 0, "midnight": 1, "velocity": 1, "rounds": 0},
    "heavy": {"structuring": 4, "midnight": 5, "velocity": 3, "rounds": 2},
}


def _payer_pool(loyal_pool: int, seed: int) -> list[str]:
    rng = np.random.default_rng(seed + 7_777)
    names = {f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_INITIALS)}" for _ in range(loyal_pool * 5)}
    while len(names) < loyal_pool:
        names.add(f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_INITIALS)} {rng.integers(2, 99)}")
    return sorted(names)[:loyal_pool]


def _zipf_weights(size: int) -> np.ndarray:
    weights = 1.0 / np.arange(1, size + 1) ** 0.85
    return weights / weights.sum()


@st.cache_data(show_spinner=False)
def build_mock_transactions(profile_name: str, days: int = 60, seed_bump: int = 0) -> pd.DataFrame:
    """Deterministic, realistic 60-day UPI credit ledger for a mock merchant."""
    profile = PROFILES[profile_name]
    rng = np.random.default_rng(profile["seed"] + seed_bump * 13)
    pool = _payer_pool(profile["loyal_pool"], profile["seed"])
    weights = _zipf_weights(len(pool))

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=days - 1)
    drift = 1.0 + profile["growth"] / 100 / 30  # month-on-month growth spread over days
    rows: list[dict] = []

    for offset in range(days):
        day = start + timedelta(days=offset)
        weekend = profile["weekend_lift"] if day.weekday() >= 5 else 1.0
        season = 1.0 + 0.08 * math.sin(offset / 6.0)
        expected = profile["daily_txn_target"] * weekend * season * (drift ** offset)
        expected *= max(0.15, 1.0 + rng.normal(0, profile["noise"]))
        count = int(rng.poisson(expected))
        for hour in rng.choice(24, size=count, p=HOUR_PROBS):
            amount = float(np.clip(rng.lognormal(math.log(profile["avg_ticket"]), 0.55),
                                   5, profile["avg_ticket"] * 9))
            payer = str(rng.choice(pool, p=weights))
            rows.append({
                "timestamp": day.replace(hour=int(hour), minute=int(rng.integers(0, 60)),
                                         second=int(rng.integers(0, 60))),
                "payer": payer,
                "payer_upi": f"{payer.split()[0].lower()}{int(rng.integers(10, 99))}@"
                             f"{'okaxis' if rng.random() > 0.5 else 'ybl'}",
                "amount": round(amount, 2),
                "mode": "QR Scan" if rng.random() > 0.28 else "Collect Request",
                "note": "",
                "status": "SUCCESS" if rng.random() > 0.035 else str(rng.choice(["FAILED", "PENDING"])),
            })

    frame = pd.DataFrame(rows, columns=["timestamp", "payer", "payer_upi", "amount", "mode", "note", "status"])
    if frame.empty:
        frame = pd.DataFrame([{
            "timestamp": today.replace(hour=9, minute=12), "payer": pool[0],
            "payer_upi": "walkin@ybl", "amount": 50.0, "mode": "QR Scan", "note": "", "status": "SUCCESS",
        }])
    frame = _inject_anomalies(frame, profile, rng)
    return frame.sort_values("timestamp", kind="stable").reset_index(drop=True)


def _inject_anomalies(frame: pd.DataFrame, profile: dict, rng: np.random.Generator) -> pd.DataFrame:
    """Seed clearly-labelled suspicious patterns so the detector has signal."""
    plan = ANOMALY_PLANS[profile["risk_profile"]]
    days = sorted(pd.Timestamp(day) for day in frame["timestamp"].dt.normalize().unique())
    if not days:
        return frame
    late_days = days[-25:]
    pool = _payer_pool(profile["loyal_pool"], profile["seed"])
    ticket = profile["avg_ticket"]
    extra: list[dict] = []

    def pick_day() -> datetime:
        return pd.Timestamp(rng.choice(late_days)).to_pydatetime()

    def row(ts, payer, upi, amount, mode="QR Scan"):
        return {"timestamp": ts, "payer": payer, "payer_upi": upi, "amount": round(float(amount), 2),
                "mode": mode, "note": "", "status": "SUCCESS"}

    for _ in range(plan["structuring"]):
        base = pick_day().replace(hour=int(rng.integers(11, 21)), minute=int(rng.integers(0, 50)))
        for _ in range(int(rng.integers(8, 15))):
            idx = int(rng.integers(1, 9))
            extra.append(row(base + timedelta(seconds=int(rng.integers(0, 240))),
                             f"Split Payer {idx}", f"splitter{idx}@ptsbi",
                             rng.uniform(0.08, 0.35) * ticket))

    for _ in range(plan["midnight"]):
        base = pick_day().replace(hour=int(rng.integers(0, 4)), minute=int(rng.integers(0, 59)))
        extra.append(row(base + timedelta(minutes=int(rng.integers(0, 40))), "Unknown Wallet",
                         f"wallet{int(rng.integers(100, 999))}@paytm",
                         rng.uniform(max(6_000, ticket * 25), max(12_000, ticket * 90)), mode="P2P"))

    for _ in range(plan["velocity"]):
        base = pick_day().replace(hour=int(rng.integers(9, 20)), minute=0)
        for _ in range(int(rng.integers(32, 43))):
            extra.append(row(base + timedelta(minutes=int(rng.integers(0, 58))),
                             str(rng.choice(pool)), "burst@upi", rng.uniform(ticket * 0.4, ticket * 1.4)))

    for _ in range(plan["rounds"]):
        base = pick_day().replace(hour=int(rng.integers(10, 18)), minute=0)
        for i in range(int(rng.integers(5, 8))):
            extra.append(row(base + timedelta(minutes=45 * i + int(rng.integers(0, 25))),
                             f"Round Payer {i + 1}", f"round{i}@okicici",
                             int(rng.choice([5_000, 10_000, 20_000, 25_000])), mode="P2P"))

    if extra:
        frame = pd.concat([frame, pd.DataFrame(extra)], ignore_index=True)
    return frame


LEDGER_MIX = {
    "Inventory Purchase": 0.46, "Shop Rent": 0.17, "Staff Wages": 0.14,
    "Electricity & Utilities": 0.05, "Packaging & Supplies": 0.06,
    "Transport & Logistics": 0.05, "Equipment Repair": 0.02,
    "Marketing": 0.02, "Miscellaneous": 0.03,
}

VOUCHER_NOTES = {
    "Inventory Purchase": "Wholesale stock refill - mandi / distributor",
    "Shop Rent": "Monthly shop rent paid to landlord",
    "Staff Wages": "Helper wages - monthly",
    "Electricity & Utilities": "Electricity bill + water charges",
    "Packaging & Supplies": "Carry bags, cups, packaging rolls",
    "Transport & Logistics": "Auto / mini-truck freight",
    "Equipment Repair": "Equipment servicing & spares",
    "Marketing": "Signboard & local pamphlets",
    "Miscellaneous": "Tea, cleaning & sundry shop expenses",
}


def _ledger_frame(profile_name: str, monthly_revenue: float, variant: int) -> pd.DataFrame:
    """Build an itemised physical (offline) expense sheet for a merchant."""
    profile = PROFILES[profile_name]
    rng = np.random.default_rng(profile["seed"] + 555 + int(variant))
    budget = max(monthly_revenue * profile["expense_ratio"], 8_000)
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    rows: list[dict] = []
    voucher = 1
    for category, share in LEDGER_MIX.items():
        splits = 1 if category in {"Shop Rent", "Staff Wages", "Electricity & Utilities"} else int(rng.integers(2, 4))
        for portion in rng.dirichlet(np.ones(splits) * 2.0):
            amount = round(float(budget * share * portion))
            if amount < 50:
                continue
            rows.append({
                "Date": pd.Timestamp(month_start + timedelta(days=int(rng.integers(0, 27)))),
                "Voucher No.": f"BKH-{voucher:04d}",
                "Particulars": VOUCHER_NOTES[category],
                "Category": category,
                "Amount (₹)": float(amount),
                "Payment Mode": str(rng.choice(["Cash", "UPI", "Bank Transfer", "Credit (Udhaar)"],
                                               p=[0.45, 0.30, 0.15, 0.10])),
            })
            voucher += 1
    return pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_mock_ledger(profile_name: str, monthly_revenue: float) -> pd.DataFrame:
    """Default register contents, used when no image has been scanned."""
    return _ledger_frame(profile_name, round(monthly_revenue, -2), 0)


@st.cache_data(show_spinner=False)
def build_ocr_ledger(profile_name: str, monthly_revenue: float, image_hash: str) -> pd.DataFrame:
    """Deterministic 'OCR result' for one specific uploaded image."""
    variant = int(image_hash[:8], 16) % 997
    return _ledger_frame(profile_name, round(monthly_revenue, -2), variant)


# ---------------------------------------------------------------------------
# 4. Upload parsing / normalisation
# ---------------------------------------------------------------------------

COLUMN_ALIASES = {
    "timestamp": ["timestamp", "datetime", "date_time", "txn_datetime", "txn_time", "txn_date",
                  "date", "time", "payment_time", "payment_date", "created_at", "upi_time", "when"],
    "payer": ["payer_name", "payer", "customer_name", "customer", "payer_vpa", "payer_upi",
              "from", "sender", "sender_name", "name", "paid_by"],
    "amount": ["amount", "txn_amount", "amt", "credit_amount", "credited_amount",
               "payment_amount", "value", "inr", "rs"],
    "mode": ["mode", "payment_mode", "txn_type", "type", "channel", "instrument"],
    "note": ["note", "remarks", "narration", "description", "upi_ref", "txn_ref", "ref", "utr"],
    "status": ["status", "txn_status", "state", "result", "payment_status"],
}
SUCCESS_WORDS = {"SUCCESS", "SUCCESSFUL", "COMPLETED", "CAPTURED", "CREDIT", "C", "CR",
                 "PAID", "OK", "Y", "TRUE"}

# Fallback tokens used when a header is not an exact alias, e.g. "Amount (INR)".
FUZZY_TOKENS = {
    "timestamp": ["timestamp", "datetime", "date_time", "date", "time", "when"],
    "amount": ["amount", "amt", "value", "inr", "rupee"],
    "payer": ["payer", "customer", "sender", "paid_by", "from", "name"],
    "status": ["status", "state", "result"],
    "mode": ["mode", "type", "channel", "instrument"],
    "note": ["note", "remark", "narration", "description", "ref", "utr"],
}


def _resolve_columns(raw_columns) -> dict[str, str | None]:
    """Map arbitrary CSV headers onto the canonical schema (exact alias, then token match)."""
    normalised: dict[str, str] = {}
    for column in raw_columns:
        key = re.sub(r"[^a-z0-9]+", "_", str(column).strip().lower()).strip("_")
        normalised.setdefault(key, column)

    resolved: dict[str, str | None] = {}
    used: set[str] = set()
    for canonical, aliases in COLUMN_ALIASES.items():
        match = next((normalised[alias] for alias in aliases
                      if alias in normalised and normalised[alias] not in used), None)
        if match is not None:
            used.add(match)
        resolved[canonical] = match

    for canonical, tokens in FUZZY_TOKENS.items():
        if resolved[canonical] is not None:
            continue
        match = next((original for key, original in normalised.items()
                      if original not in used and any(token in key for token in tokens)), None)
        if match is not None:
            used.add(match)
            resolved[canonical] = match
    return resolved
CANONICAL_COLUMNS = ["timestamp", "payer", "payer_upi", "amount", "mode", "note", "status"]


def _parse_amounts(series: pd.Series) -> pd.Series:
    text = (
        series.astype("string")
        .str.strip()
        .str.replace(r"(?i)^(rs\.?|inr|₹)\s*", "", regex=True)
        .str.replace(r"[₹,\s]", "", regex=True)
        .str.replace(r"(?i)cr$", "", regex=True)
    )
    return pd.to_numeric(text, errors="coerce")


def _parse_timestamps(series: pd.Series) -> pd.Series:
    """Parse a timestamp column without mangling ISO dates.

    `dayfirst=True` silently turns `2026-08-01` into 8 January, so ISO-looking
    columns are parsed as ISO first; everything else is read day-first, which is
    the convention Indian bank/PSP exports use (`01/08/2026`).
    """
    text = series.astype("string").str.strip()
    iso_like = text.str.match(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}").fillna(False)
    if iso_like.mean() > 0.5:
        parsed = pd.to_datetime(text, errors="coerce", format="ISO8601")
        if parsed.notna().mean() > 0.5:
            return parsed

    try:
        parsed = pd.to_datetime(text, errors="coerce", format="mixed", dayfirst=True)
    except (ValueError, TypeError):
        parsed = pd.to_datetime(text, errors="coerce", dayfirst=True)
    if parsed.notna().sum() == 0:
        parsed = pd.to_datetime(text, errors="coerce")
    return parsed


def normalize_transactions(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Map an arbitrary merchant CSV onto the canonical VyaparScore schema."""
    meta: dict = {"warnings": [], "has_time": True, "mapped": {}, "dropped_rows": 0}
    mapping = _resolve_columns(list(raw.columns))
    meta["mapped"] = mapping

    if not mapping["timestamp"] or not mapping["amount"]:
        meta["warnings"].append("No timestamp/date column or no amount column found in the upload.")
        return pd.DataFrame(columns=CANONICAL_COLUMNS), meta

    frame = pd.DataFrame({
        "timestamp": _parse_timestamps(raw[mapping["timestamp"]]),
        "amount": _parse_amounts(raw[mapping["amount"]]),
    })
    before = len(frame)
    frame = frame.dropna(subset=["timestamp", "amount"])
    meta["dropped_rows"] = int(before - len(frame))
    if meta["dropped_rows"]:
        meta["warnings"].append(f"{meta['dropped_rows']} row(s) had an unreadable date or amount and were skipped.")

    for canonical, default in (("payer", "Unknown Payer"), ("mode", "UPI"), ("note", ""), ("status", "SUCCESS")):
        source = mapping[canonical]
        frame[canonical] = (raw[source].astype("string").fillna(default)
                            if source is not None else default)

    frame["payer"] = frame["payer"].replace({"": "Unknown Payer", "nan": "Unknown Payer"}).astype(str)
    frame["payer_upi"] = (frame["payer"].str.lower().str.replace(r"\W+", "", regex=True) + "@uploaded")
    status = frame["status"].astype(str).str.upper().str.strip()
    frame["status"] = status.where(status.isin(SUCCESS_WORDS | {"FAILED", "PENDING"}), "SUCCESS")
    frame["amount"] = frame["amount"].astype(float).round(2)

    # A date-only export would otherwise fabricate a wave of "midnight" anomalies.
    if len(frame) and bool(((frame["timestamp"].dt.hour == 0) & (frame["timestamp"].dt.minute == 0)).all()):
        meta["has_time"] = False
        meta["warnings"].append(
            "The file carries dates but no clock times, so intra-day rules "
            "(structuring / midnight / velocity / payer bursts) are disabled for this dataset."
        )

    frame = frame[CANONICAL_COLUMNS].sort_values("timestamp", kind="stable").reset_index(drop=True)
    return frame, meta


# ---------------------------------------------------------------------------
# 5. Analytics: KPIs, credit score, anomaly engine
# ---------------------------------------------------------------------------

def compute_metrics(txns: pd.DataFrame, meta: dict, tenure_months: int) -> dict:
    """Business KPIs plus the daily / hourly series used by the charts."""
    # A *stable* sort keeps the row order identical to detect_anomalies(), which
    # re-sorts the same frame; flag indices therefore always address the same row.
    credits = (txns[txns["status"] == "SUCCESS"]
               .sort_values("timestamp", kind="stable")
               .reset_index(drop=True)[CANONICAL_COLUMNS])
    span_days = max(int((txns["timestamp"].max() - txns["timestamp"].min()).days) + 1, 1) if len(txns) else 1
    scale = 30.0 / span_days

    if credits.empty:
        return {
            "credits": credits, "daily": pd.DataFrame({"revenue": [], "txns": []}),
            "monthly_revenue": 0.0, "monthly_txns": 0.0, "avg_daily_txns": 0.0, "avg_ticket": 0.0,
            "active_days": 0, "span_days": span_days, "unique_payers": 0, "retention": 0.0,
            "momentum": 0.0, "volatility": 1.0, "hourly": pd.DataFrame({"sum": [0] * 24, "count": [0] * 24}),
            "weekday": pd.Series(0.0, index=["Monday", "Tuesday", "Wednesday", "Thursday",
                                             "Friday", "Saturday", "Sunday"]),
            "top_payers": pd.Series(dtype="int64"), "peak_amount": 0.0, "p75_amount": 0.0,
            "median_amount": 0.0, "has_time": meta.get("has_time", True), "tenure_months": tenure_months,
        }

    daily = (
        credits.groupby(credits["timestamp"].dt.normalize())["amount"]
        .agg(revenue="sum", txns="count")
        .reindex(pd.date_range(credits["timestamp"].min().normalize(),
                               credits["timestamp"].max().normalize(), freq="D"), fill_value=0)
    )

    monthly_revenue = float(daily["revenue"].sum() * scale)
    monthly_txns = float(daily["txns"].sum() * scale)

    # Median (not mean) so one whale credit cannot masquerade as business growth.
    split = max(len(daily) // 2, 1)
    prev_half, last_half = daily["revenue"].iloc[:split], daily["revenue"].iloc[split:]
    prev_median, last_median = float(prev_half.median()), float(last_half.median())
    momentum = (last_median - prev_median) / prev_median * 100 if prev_median > 0 else 0.0

    payer_counts = credits.groupby("payer").size()
    retention = float((payer_counts >= 2).mean() * 100) if len(payer_counts) else 0.0

    daily_values = daily["revenue"].to_numpy(float)
    volatility = float(np.std(daily_values) / np.mean(daily_values)) if daily_values.mean() > 0 else 1.0

    return {
        "credits": credits,
        "daily": daily,
        "monthly_revenue": monthly_revenue,
        "monthly_txns": monthly_txns,
        "avg_daily_txns": monthly_txns / 30.0,
        "avg_ticket": monthly_revenue / monthly_txns if monthly_txns else 0.0,
        "active_days": int((daily["txns"] > 0).sum()),
        "span_days": span_days,
        "unique_payers": int(len(payer_counts)),
        "retention": retention,
        "momentum": momentum,
        "volatility": volatility,
        "hourly": credits.groupby(credits["timestamp"].dt.hour)["amount"]
                 .agg(["sum", "count"]).reindex(range(24), fill_value=0),
        "weekday": credits.groupby(credits["timestamp"].dt.day_name())["amount"].sum()
                   .reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                             "Saturday", "Sunday"], fill_value=0),
        "top_payers": payer_counts.sort_values(ascending=False).head(8).sort_values(),
        "peak_amount": float(credits["amount"].max()),
        "p75_amount": float(credits["amount"].quantile(0.75)),
        "median_amount": float(credits["amount"].median()),
        "has_time": meta.get("has_time", True),
        "tenure_months": tenure_months,
    }


def _window_sum(values: np.ndarray, secs: np.ndarray, window: float) -> np.ndarray:
    """For each index i, the sum of `values` inside the half-open window (secs[i]-window, secs[i]]."""
    cumulative = np.concatenate(([0.0], np.cumsum(values)))
    left = np.searchsorted(secs, secs - window, side="right")
    return cumulative[np.arange(len(secs)) + 1] - cumulative[left]


def _seconds(series: pd.Series) -> np.ndarray:
    return ((series.to_numpy() - np.datetime64("1970-01-01T00:00:00")) / np.timedelta64(1, "s")).astype(float)


def detect_anomalies(credits: pd.DataFrame, has_time: bool = True) -> tuple[pd.DataFrame, float, dict]:
    """Rule-based UPI anomaly engine -> (flag rows, risk index 0-100, severity counts)."""
    if credits.empty:
        return pd.DataFrame(), 0.0, {"High": 0, "Medium": 0, "Low": 0}

    frame = credits.sort_values("timestamp", kind="stable").reset_index(drop=True)
    secs = _seconds(frame["timestamp"])
    amounts = frame["amount"].to_numpy(float)
    # Thresholds are relative to this shop's own baseline, so a ₹20 chai sale is
    # not "structuring" for a tea stall and a Friday evening rush is not a
    # "velocity spike" for a busy kirana store.
    micro_cap = max(20.0, float(np.median(amounts)) * 0.5)
    hourly_counts = frame.groupby([frame["timestamp"].dt.normalize(),
                                   frame["timestamp"].dt.hour]).size()
    median_hourly = float(hourly_counts.median()) if len(hourly_counts) else 0.0
    velocity_threshold = max(25.0, median_hourly * 8)
    flags: list[dict] = []

    def push(positions: np.ndarray, code: str, reason_fn) -> None:
        label, severity = REASON_CODES[code]
        for position in positions:
            row = frame.iloc[int(position)]
            flags.append({
                "index": int(position),
                "Time": row["timestamp"],
                "Payer": row["payer"],
                "Amount (₹)": float(row["amount"]),
                "Mode": row["mode"],
                "Rule Code": code,
                "Anomaly": label,
                "Severity": severity,
                "Reason": reason_fn(row, int(position)),
            })

    if has_time:
        # STR-01 — micro-transaction structuring.
        micro_in_5min = _window_sum((amounts <= micro_cap).astype(float), secs, 300.0)
        push(np.where(micro_in_5min >= 6)[0], "STR-01",
             lambda row, pos: f"{int(micro_in_5min[pos])} payments of ≤ {inr(micro_cap)} inside one "
                              f"5-minute window — split-payment structuring pattern.")

        # VEL-03 — velocity spike.
        per_hour = _window_sum(np.ones_like(amounts), secs, 3600.0)
        push(np.where(per_hour >= velocity_threshold)[0], "VEL-03",
             lambda row, pos: f"{int(per_hour[pos])} credits in the trailing 60 minutes against a "
                              f"median busy hour of {median_hourly:.0f} for this shop.")

        # SPL-05 — same payer bursting.
        for payer, group in frame.groupby("payer", sort=False):
            if len(group) < 4:
                continue
            counts = _window_sum(np.ones(len(group)), _seconds(group["timestamp"]), 600.0)
            hits = np.where(counts >= 5)[0]
            if hits.size:
                positions = np.array([group.index[position] for position in hits])
                label, severity = REASON_CODES["SPL-05"]
                for position in positions:
                    row = frame.iloc[int(position)]
                    flags.append({
                        "index": int(position), "Time": row["timestamp"], "Payer": row["payer"],
                        "Amount (₹)": float(row["amount"]), "Mode": row["mode"], "Rule Code": "SPL-05",
                        "Anomaly": label, "Severity": severity,
                        "Reason": f"{int(max(counts[hits]))} payments from the same payer '{payer}' inside 10 minutes.",
                    })

    # MID-02 — midnight high-value credit.
    threshold = max(5_000.0, float(np.quantile(amounts, 0.75)) * 6)
    push(np.where((frame["timestamp"].dt.hour.to_numpy() < 5) & (amounts >= threshold))[0], "MID-02",
         lambda row, pos: f"{inr(amounts[pos])} credited at {row['timestamp']:%I:%M %p}, far above the "
                          f"{inr(threshold)} late-night threshold for this shop.")

    # RND-04 — round-amount clustering.
    round_mask = (amounts % 1000 == 0) & (amounts >= 1000)
    round_days = frame.loc[round_mask, "timestamp"].dt.normalize()
    if len(round_days):
        heavy = set(round_days.value_counts().loc[lambda s: s >= 4].index)
        push(np.where(round_mask & frame["timestamp"].dt.normalize().isin(heavy))[0], "RND-04",
             lambda row, pos: f"Exact round figure of {inr(amounts[pos])} — {len(heavy)} same-day "
                              f"round-amount cluster(s) detected in this ledger.")

    if not flags:
        return pd.DataFrame(), 0.0, {"High": 0, "Medium": 0, "Low": 0}

    result = (pd.DataFrame(flags)
              .drop_duplicates(subset=["index", "Rule Code"])
              .sort_values(["Time", "index"])
              .reset_index(drop=True))

    # One "event" per rule per hour, so a single burst is not counted dozens of times.
    result["Event"] = result["Rule Code"] + "|" + result["Time"].dt.floor("h").astype(str)
    events = result.groupby("Event")["Severity"].first()
    counts = result["Severity"].value_counts().to_dict()
    summary = {level: int(counts.get(level, 0)) for level in ("High", "Medium", "Low")}
    raw = (12 * int((events == "High").sum())
           + 6 * int((events == "Medium").sum())
           + 2 * int((events == "Low").sum()))
    risk = float(min(100.0, raw))
    return result, risk, summary


def score_grade(score: int) -> tuple[str, str]:
    if score >= 800:
        return "Excellent", "excellent"
    if score >= 720:
        return "Good", "good"
    if score >= 650:
        return "Fair", "fair"
    if score >= 550:
        return "Needs work", "weak"
    return "High risk", "bad"


def compute_credit_score(metrics: dict, risk_score: float) -> dict:
    """Transparent 300-900 score built from six weighted, explainable factors."""
    components = {
        "Cash-flow consistency": (0.28, max(0.0, 1.0 - min(metrics["volatility"], 1.0))),
        "Digital footprint": (0.22, min(1.0, math.log10(max(metrics["monthly_txns"], 1.0)) / math.log10(900))),
        "Customer loyalty": (0.18, min(metrics["retention"] / 70.0, 1.0)),
        "Growth momentum": (0.14, min(max(0.5 + metrics["momentum"] / 40.0, 0.0), 1.0)),
        "Business tenure": (0.10, min(metrics["tenure_months"] / 36.0, 1.0)),
        "Trust & safety": (0.08, 1.0 - min(risk_score / 100.0, 1.0)),
    }
    weighted = sum(weight * sub for weight, sub in components.values())
    score = int(round(max(300.0, min(900.0, 300 + 600 * weighted))))
    grade, tone = score_grade(score)
    return {
        "score": score,
        "grade": grade,
        "tone": tone,
        "weighted": weighted,
        "components": {name: {"weight": weight, "sub": sub, "points": 600 * weight * sub}
                       for name, (weight, sub) in components.items()},
    }


def approved_loan_limit(score: int, net_profit: float, profile_cap: float) -> int:
    """Loan ceiling: 3x sustainable monthly profit, scaled by score band, capped by product limit."""
    if score < 500:
        return 0
    multiplier = 1.0 if score >= 750 else 0.8 if score >= 650 else 0.5
    limit = min(max(net_profit, 0.0) * 3 * multiplier, profile_cap)
    return int(max(0, math.floor(limit / 1000) * 1000))


def risk_rate(score: int) -> float:
    """Score-based pricing, kept on a 0.5 grid so it can seed the rate slider."""
    if score >= 800:
        return 11.5
    if score >= 720:
        return 14.0
    if score >= 650:
        return 17.5
    return 23.0


# ---------------------------------------------------------------------------
# 6. Loan maths
# ---------------------------------------------------------------------------

def amortisation(principal: float, annual_rate: float, months: int) -> tuple[float, pd.DataFrame]:
    """Standard reducing-balance EMI schedule."""
    months = max(int(months), 1)
    rate = annual_rate / 12 / 100
    emi = principal / months if rate == 0 else (
        principal * rate * (1 + rate) ** months / ((1 + rate) ** months - 1)
    )
    rows, balance = [], float(principal)
    start = datetime.now().replace(day=1)
    for month in range(1, months + 1):
        interest = balance * rate
        principal_part = emi - interest
        balance = max(balance - principal_part, 0.0)
        due = (start + timedelta(days=32 * month)).replace(day=5)
        rows.append({
            "Instalment": month,
            "Due date": due.date(),
            "EMI (₹)": round(emi),
            "Interest (₹)": round(interest),
            "Principal (₹)": round(principal_part),
            "Closing balance (₹)": round(balance),
        })
    return round(emi), pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 7. UI primitives
# ---------------------------------------------------------------------------

def hero_css(tone: str) -> str:
    return {
        "excellent": "background: linear-gradient(135deg,#047857 0%,#059669 55%,#10B981 100%);",
        "good": "background: linear-gradient(135deg,#1D4ED8 0%,#4F46E5 55%,#6366F1 100%);",
        "fair": "background: linear-gradient(135deg,#B45309 0%,#D97706 55%,#F59E0B 100%);",
        "weak": "background: linear-gradient(135deg,#9A3412 0%,#C2410C 60%,#EA580C 100%);",
        "bad": "background: linear-gradient(135deg,#7F1D1D 0%,#B91C1C 55%,#DC2626 100%);",
    }[tone]


def metric_card(label: str, value: str, footer: str = "", tone: str = "flat") -> str:
    css_class = {"up": "vs-up", "down": "vs-down"}.get(tone, "vs-flat")
    footer_html = f'<div class="vs-card-foot"><span class="{css_class}">{footer}</span></div>' if footer else ""
    return (f'<div class="vs-card"><div class="vs-card-label">{label}</div>'
            f'<div class="vs-card-value">{value}</div>{footer_html}</div>')


def panel(title: str, hint: str = "") -> None:
    hint_html = f'<p class="vs-hint">{hint}</p>' if hint else ""
    st.markdown(f'<div class="vs-panel"><h4>{title}</h4>{hint_html}</div>', unsafe_allow_html=True)


def bar(title: str, hint: str, badges: str) -> None:
    st.markdown(
        f'<div class="vs-bar"><div><h4>{title}</h4><p class="vs-hint">{hint}</p></div>'
        f'<div>{badges}</div></div>',
        unsafe_allow_html=True,
    )


def badge(text: str, kind: str = "ok") -> str:
    return f'<span class="vs-badge vs-badge-{kind}">{text}</span>'


def severity_badge(severity: str) -> str:
    return badge(severity.upper(), {"High": "high", "Medium": "med", "Low": "low"}.get(severity, "ok"))


def style_figure(fig: go.Figure, height: int = 320) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=30, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", size=12, color="#334155"),
        hoverlabel=dict(bgcolor="#0F172A", font_color="white", bordercolor="#0F172A"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=False, showline=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#EEF2F7", showline=False, zeroline=False)
    return fig


def gauge_figure(score: int, grade: str) -> go.Figure:
    color = {"excellent": "#059669", "good": "#4F46E5", "fair": "#D97706",
             "weak": "#EA580C", "bad": "#DC2626"}[score_grade(score)[1]]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"size": 38, "color": "#0B1220", "family": "Inter, sans-serif"}},
        title={"text": f"<b>{grade}</b><br><span style='font-size:.72rem;color:#64748B'>scale 300 - 900</span>",
               "font": {"size": 13, "color": "#334155"}},
        gauge={
            "axis": {"range": [300, 900], "tickwidth": 1, "tickcolor": "#94A3B8", "tickfont": {"size": 10}},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [300, 550], "color": "#FEE2E2"},
                {"range": [550, 650], "color": "#FFEDD5"},
                {"range": [650, 720], "color": "#FEF3C7"},
                {"range": [720, 800], "color": "#E0E7FF"},
                {"range": [800, 900], "color": "#D1FAE5"},
            ],
            "threshold": {"line": {"color": "#0B1220", "width": 3}, "thickness": 0.8, "value": score},
        },
    ))
    fig.update_layout(height=265, margin=dict(l=22, r=22, t=38, b=4), paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Inter, Segoe UI, sans-serif"))
    return fig


# ---------------------------------------------------------------------------
# 8. Sidebar / data source resolution
# ---------------------------------------------------------------------------

def signature(source: str, merchant: str, payload: bytes | None, bump: int) -> str:
    digest = hashlib.sha256(payload or b"").hexdigest()[:12]
    return hashlib.sha256(f"{source}|{merchant}|{digest}|{bump}".encode()).hexdigest()[:12]


def sidebar() -> dict:
    st.sidebar.markdown('<div class="vs-side-brand">🛡️ VyaparScore</div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        '<p class="vs-side-sub">Micro-merchant credit score &amp; UPI anomaly detector.<br>'
        "Hackathon demo — 100% simulated.</p>",
        unsafe_allow_html=True,
    )
    st.sidebar.divider()

    st.sidebar.markdown("**1 · Data source**")
    source = st.sidebar.radio("Load merchant data from", SOURCE_CHOICES,
                              label_visibility="collapsed", key="source_choice")

    state: dict = {"csv": None, "csv_name": None,
                   "seed_bump": int(st.session_state.get("seed_bump", 0))}

    if source == SOURCE_CHOICES[0]:
        st.sidebar.markdown("**2 · Merchant profile**")
        state["merchant"] = st.sidebar.selectbox(
            "Mock merchant profile", list(PROFILES.keys()), index=0, key="profile_choice",
            help="Ramesh and Sharma are healthy businesses; the Suspicious Merchant is seeded with fraud patterns.",
        )
        profile = PROFILES[state["merchant"]]
        st.sidebar.caption(f"{profile['owner']} · {profile['segment']}  \n"
                           f"{profile['city']} · {profile['tenure_months']} months on UPI")
        if st.sidebar.button("🎲 Re-roll synthetic transactions", key="reroll", **BTN):
            st.session_state["seed_bump"] = state["seed_bump"] + 1
            st.rerun()
        if st.sidebar.button("⬇️ Download sample UPI CSV", key="sample_csv", **BTN):
            sample = build_mock_transactions(state["merchant"], days=30, seed_bump=state["seed_bump"])
            st.session_state["sample_csv_payload"] = sample.to_csv(index=False).encode("utf-8")
        if st.session_state.get("sample_csv_payload"):
            st.sidebar.download_button(
                "Save sample_u.csv", data=st.session_state["sample_csv_payload"],
                file_name="vyaparscore_sample_upi.csv", mime="text/csv", key="sample_csv_dl",
            )
    else:
        st.sidebar.markdown("**2 · UPI history**")
        upload = st.sidebar.file_uploader(
            "UPI transaction CSV", type=["csv"], key="csv_uploader",
            help="Expected columns: timestamp, payer, amount, status — aliases are auto-detected.",
        )
        if upload is not None:
            state["csv"] = upload.getvalue()
            state["csv_name"] = upload.name
            st.sidebar.success(f"Loaded `{upload.name}` · {len(state['csv']) / 1024:.0f} KB")
        else:
            st.sidebar.info("No file selected yet — the mock merchant below is used as a fallback.")
        st.sidebar.markdown("**3 · Fallback merchant**")
        state["merchant"] = st.sidebar.selectbox(
            "Used when the upload is empty or unreadable", list(PROFILES.keys()),
            index=0, key="fallback_profile",
        )

    st.sidebar.divider()
    st.sidebar.markdown("**· Physical register (bahi-khata)**")
    state["image"] = st.sidebar.file_uploader(
        "Register page photo", type=["png", "jpg", "jpeg", "webp"], key="side_image_uploader",
        help="The same upload is available inside the Physical Register Scanner tab.",
    )

    st.sidebar.divider()
    st.sidebar.markdown(
        '<div class="vs-side-note"><b>Demo disclaimer.</b> Credit scores, OCR output, fraud flags and loan '
        "sanctions here are simulated for a hackathon. Nothing on this screen is real financial, lending or "
        "tax advice.</div>",
        unsafe_allow_html=True,
    )
    return state


def load_dataset(state: dict) -> tuple[pd.DataFrame, dict, bool]:
    """Return (transactions, meta, using_mock) for the active source."""
    if state["csv"]:
        raw = None
        try:
            raw = pd.read_csv(io.BytesIO(state["csv"]))
        except Exception as exc:  # noqa: BLE001 - surfaced to the user as a warning
            st.sidebar.warning(f"Could not read that CSV ({exc}). Falling back to mock data.")
        if raw is not None and not raw.empty:
            frame, meta = normalize_transactions(raw)
            if not frame.empty:
                return frame, meta, False
            for warning in meta["warnings"]:
                st.sidebar.warning(warning)
            st.sidebar.warning("No usable rows found — falling back to the mock merchant profile.")

    return (build_mock_transactions(state["merchant"], days=60, seed_bump=state["seed_bump"]),
            {"warnings": [], "has_time": True, "mapped": {}, "dropped_rows": 0}, True)


def ledger_amount_total(ledger: pd.DataFrame) -> float:
    series = ledger.get("Amount (₹)")
    if series is None:
        return 0.0
    return float(pd.to_numeric(series, errors="coerce").fillna(0).sum())


# ---------------------------------------------------------------------------
# 9. Tab 1 — Digital UPI & Credit Score
# ---------------------------------------------------------------------------

def tab_credit(metrics: dict, credit: dict, limit: int, net_profit: float, merchant: str,
               using_mock: bool, risk_score: float, flag_count: int) -> None:
    risk_kind = "high" if risk_score >= 50 else "med" if risk_score >= 20 else "ok"
    bar(
        f"Credit health · {merchant}",
        f"Scored from {metrics['span_days']} days of UPI history "
        f"({len(metrics['credits']):,} successful credits).",
        badge("MOCK DATA" if using_mock else "UPLOADED CSV", "low") + "&nbsp;"
        + badge(f"RISK INDEX {risk_score:.0f}/100", risk_kind),
    )

    left, right = st.columns([1.02, 2.2], gap="large")
    with left:
        st.markdown(
            f'<div class="vs-hero" style="{hero_css(credit["tone"])}">'
            f'<div class="vs-hero-label">VyaparScore credit rating</div>'
            f'<div class="vs-hero-score">{credit["score"]}</div>'
            f'<div class="vs-hero-scale">out of 900 · micro-merchant scale</div>'
            f'<div class="vs-hero-grade">{credit["grade"]}</div></div>',
            unsafe_allow_html=True,
        )
        render_chart(gauge_figure(credit["score"], credit["grade"]), height=265)

    with right:
        momentum_tone = "up" if metrics["momentum"] >= 0 else "down"
        row1 = st.columns(4, gap="medium")
        row1[0].markdown(metric_card("Total monthly UPI revenue", inr(metrics["monthly_revenue"]),
                                     f"{signed_pct(metrics['momentum'])} vs previous period", momentum_tone),
                         unsafe_allow_html=True)
        row1[1].markdown(metric_card("Average daily transactions", f"{metrics['avg_daily_txns']:.0f}",
                                     f"{inr(metrics['avg_ticket'])} average ticket"), unsafe_allow_html=True)
        row1[2].markdown(metric_card("Customer retention rate", pct(metrics["retention"]),
                                     f"{metrics['unique_payers']:,} unique payers"), unsafe_allow_html=True)
        row1[3].markdown(metric_card("Max loan approved", inr(limit),
                                     f"From {inr(net_profit)} net monthly profit",
                                     "up" if limit > 0 else "down"), unsafe_allow_html=True)

        row2 = st.columns(4, gap="medium")
        row2[0].markdown(metric_card("Successful credits", f"{len(metrics['credits']):,}",
                                     f"{metrics['active_days']} active days"), unsafe_allow_html=True)
        row2[1].markdown(metric_card("Largest single credit", inr(metrics["peak_amount"]),
                                     f"75th percentile {inr(metrics['p75_amount'])}"), unsafe_allow_html=True)
        row2[2].markdown(metric_card("Cash-flow volatility", f"{metrics['volatility']:.2f}",
                                     "Coefficient of variation — lower is better"), unsafe_allow_html=True)
        row2[3].markdown(metric_card("Fraud flags raised", str(flag_count),
                                     "See the anomaly tab for reason codes",
                                     "down" if flag_count else "up"), unsafe_allow_html=True)

    st.markdown('<hr class="vs-sep">', unsafe_allow_html=True)

    col_a, col_b = st.columns([1.6, 1], gap="large")
    with col_a:
        panel("Daily UPI income trend", "Bars are credited amount per day; the line is a 7-day moving average.")
        daily = metrics["daily"]
        trend = px.bar(daily, x=daily.index, y="revenue",
                       labels={"revenue": "Revenue (₹)", "index": ""},
                       color_discrete_sequence=["#C7D2FE"])
        trend.add_scatter(x=daily.index, y=daily["revenue"].rolling(7, min_periods=1).mean(),
                          mode="lines", name="7-day average",
                          line=dict(color=PALETTE["primary"], width=3))
        trend.update_traces(hovertemplate="%{x|%d %b}<br>₹%{y:,.0f}<extra></extra>", selector=dict(type="bar"))
        render_chart(style_figure(trend, 330))

    with col_b:
        panel("When the shop earns", "Hour-of-day revenue concentration.")
        hourly = metrics["hourly"]
        hours = px.bar(x=hourly.index, y=hourly["sum"], labels={"x": "Hour of day", "y": "Revenue (₹)"},
                       color=hourly["sum"], color_continuous_scale="Blues")
        hours.update_layout(coloraxis_showscale=False)
        hours.update_traces(hovertemplate="%{x}:00 hrs<br>₹%{y:,.0f}<extra></extra>")
        render_chart(style_figure(hours, 330))

    col_c, col_d = st.columns(2, gap="large")
    with col_c:
        panel("Weekday rhythm", "Which days carry the business.")
        weekday = metrics["weekday"]
        week_fig = px.bar(x=weekday.index, y=weekday.values, labels={"x": "", "y": "Revenue (₹)"},
                          color_discrete_sequence=["#0EA5E9"])
        week_fig.update_traces(hovertemplate="%{x}<br>₹%{y:,.0f}<extra></extra>")
        render_chart(style_figure(week_fig, 300))

    with col_d:
        panel("Most loyal customers", "Repeat payers are the strongest retention signal in the score.")
        top = metrics["top_payers"]
        if top.empty:
            st.info("Not enough payer history to rank customers yet.")
        else:
            payer_fig = px.bar(x=top.values, y=top.index, orientation="h",
                               labels={"x": "Transactions", "y": ""},
                               color_discrete_sequence=["#059669"])
            payer_fig.update_traces(hovertemplate="%{y}<br>%{x} transactions<extra></extra>")
            render_chart(style_figure(payer_fig, 300))

    with st.expander("🧮 How this score was calculated"):
        breakdown = pd.DataFrame([
            {"Factor": name, "Weight": pct(details["weight"] * 100, 0),
             "Sub-score": pct(details["sub"] * 100, 0), "Points earned": round(details["points"], 1)}
            for name, details in credit["components"].items()
        ])
        st.dataframe(breakdown, hide_index=True, **FRAME)
        fig = px.bar(breakdown, x="Points earned", y="Factor", orientation="h",
                     labels={"Points earned": "Points contributed", "Factor": ""},
                     color_discrete_sequence=[PALETTE["primary"]])
        render_chart(style_figure(fig, 250))
        st.caption(
            "Formula: 300 + 600 × Σ(weight × sub-score), clamped to 300-900. "
            "Sub-scores — consistency = 1 − volatility · footprint = log₁₀(monthly credits) ÷ log₁₀(900) · "
            "loyalty = retention ÷ 70% · momentum = 0.5 + median-day growth ÷ 40 · tenure = months ÷ 36 · "
            "safety = 1 − risk index ÷ 100."
        )

    if not metrics["has_time"]:
        st.info("This dataset has no clock times, so intra-day rules were skipped when scoring safety.")


# ---------------------------------------------------------------------------
# 10. Tab 2 — Physical register scanner (simulated OCR)
# ---------------------------------------------------------------------------

def tab_ocr(merchant: str, metrics: dict, sig: str, sidebar_image) -> dict:
    bar("Bahi-Khata OCR scanner",
        "Upload a photo of a handwritten register page. The simulated parser reads every line into an "
        "itemised, editable expense sheet that feeds straight into net profit.",
        badge("SIMULATED OCR", "low"))

    upload_col, preview_col = st.columns([1.15, 1], gap="large")
    with upload_col:
        tab_image = st.file_uploader("Register page photo (JPG / PNG / WEBP)",
                                     type=["png", "jpg", "jpeg", "webp"], key="tab_image_uploader")
        image = tab_image or sidebar_image
        if image is not None:
            st.caption(f"Selected file: `{image.name}`")
        if st.button("🔍 Run AI OCR scan", type="primary", key=f"run_ocr::{sig}",
                     disabled=image is None, **BTN):
            image_hash = hashlib.sha256(image.getvalue()).hexdigest()
            with st.status("Reading the register page…", expanded=True) as status:
                st.write("① De-skewing and enhancing contrast…")
                time.sleep(0.3)
                st.write("② Detecting handwritten rows…")
                time.sleep(0.3)
                st.write("③ Recognising Devanagari &amp; Latin numerals…")
                time.sleep(0.3)
                st.write("④ Mapping lines to expense categories…")
                time.sleep(0.25)
                status.update(label="OCR complete — line items extracted", state="complete")
            st.session_state[f"ledger::{sig}"] = build_ocr_ledger(merchant, metrics["monthly_revenue"], image_hash)
            st.session_state[f"ledger_gen::{sig}"] = int(st.session_state.get(f"ledger_gen::{sig}", 0)) + 1
            st.toast("Register page parsed successfully", icon="✅")
            st.rerun()
    with preview_col:
        if image is not None:
            st.image(image, caption="Uploaded register page", **IMG)
        else:
            st.markdown(
                '<div class="vs-empty"><div style="font-size:2.1rem">📒</div>'
                '<div class="vs-card-label" style="margin-top:.4rem">No image uploaded</div>'
                f'<div class="vs-card-foot">Showing a simulated parse of {merchant}&#39;s register so the '
                'dashboard works out of the box.</div></div>',
                unsafe_allow_html=True,
            )

    ledger_key = f"ledger::{sig}"
    generation = int(st.session_state.get(f"ledger_gen::{sig}", 0))
    editor_key = f"ledger_editor::{sig}::v{generation}"
    if ledger_key not in st.session_state:
        st.session_state[ledger_key] = build_mock_ledger(merchant, metrics["monthly_revenue"])

    st.markdown('<hr class="vs-sep">', unsafe_allow_html=True)
    head, reset = st.columns([4, 1], gap="medium")
    with head:
        panel("Extracted expense lines (editable)",
              "Edit an amount, re-categorise a line or add rows — the credit tab and loan limit update instantly.")
    with reset:
        st.markdown("<div style='height:2.1rem'></div>", unsafe_allow_html=True)
        if st.button("↺ Reset ledger", key=f"reset_ledger::{sig}", **BTN):
            st.session_state[ledger_key] = build_mock_ledger(merchant, metrics["monthly_revenue"])
            st.session_state[f"ledger_gen::{sig}"] = generation + 1
            st.rerun()

    def persist_ledger() -> None:
        """on_change runs before the script body, so tab 1 sees the edit in the same rerun."""
        st.session_state[ledger_key] = st.session_state[editor_key].copy()

    edited = st.data_editor(
        st.session_state[ledger_key],
        key=editor_key,
        num_rows="dynamic",
        hide_index=True,
        height=330,
        on_change=persist_ledger,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY", width="small"),
            "Voucher No.": st.column_config.TextColumn("Voucher No.", width="small"),
            "Particulars": st.column_config.TextColumn("Particulars", width="large"),
            "Category": st.column_config.SelectboxColumn("Category", options=EXPENSE_CATEGORIES, width="medium"),
            "Amount (₹)": st.column_config.NumberColumn("Amount (₹)", min_value=0, step=50,
                                                        format="₹ %d", width="small"),
            "Payment Mode": st.column_config.SelectboxColumn("Payment Mode", options=PAYMENT_MODES, width="medium"),
        },
        **EDITOR,
    )

    clean = edited.copy()
    if "Amount (₹)" in clean.columns:
        clean["Amount (₹)"] = pd.to_numeric(clean["Amount (₹)"], errors="coerce").fillna(0)
    else:
        clean["Amount (₹)"] = 0.0
    if "Category" not in clean.columns:
        clean["Category"] = "Miscellaneous"
    if "Payment Mode" not in clean.columns:
        clean["Payment Mode"] = "Cash"

    total_expenses = float(clean["Amount (₹)"].sum())
    net_profit = metrics["monthly_revenue"] - total_expenses
    margin = (net_profit / metrics["monthly_revenue"] * 100) if metrics["monthly_revenue"] else 0.0

    c1, c2, c3 = st.columns(3, gap="medium")
    c1.markdown(metric_card("Total physical expenses", inr(total_expenses),
                            f"{len(clean)} itemised line(s)"), unsafe_allow_html=True)
    c2.markdown(metric_card("Monthly UPI revenue", inr(metrics["monthly_revenue"]),
                            "Digital inflow from tab 1"), unsafe_allow_html=True)
    c3.markdown(metric_card("Net monthly profit", inr(net_profit), f"Margin {pct(margin)}",
                            "up" if net_profit >= 0 else "down"), unsafe_allow_html=True)

    by_cat, by_mode = st.columns([1.5, 1], gap="large")
    with by_cat:
        panel("Where the money goes", "Expense mix by category.")
        grouped = clean.groupby("Category")["Amount (₹)"].sum().sort_values()
        if grouped.sum() > 0:
            fig = px.bar(x=grouped.values, y=grouped.index, orientation="h",
                         labels={"x": "Amount (₹)", "y": ""}, color=grouped.values,
                         color_continuous_scale="Sunset")
            fig.update_layout(coloraxis_showscale=False)
            fig.update_traces(hovertemplate="%{y}<br>₹%{x:,.0f}<extra></extra>")
            render_chart(style_figure(fig, 320))
        else:
            st.info("Add at least one expense line above.")
    with by_mode:
        panel("Settlement mode", "Cash vs digital outflow.")
        modes = clean.groupby("Payment Mode")["Amount (₹)"].sum()
        if modes.sum() > 0:
            fig = px.pie(names=modes.index, values=modes.values, hole=0.55,
                         color_discrete_sequence=["#4F46E5", "#0EA5E9", "#059669", "#D97706"])
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(height=320, margin=dict(l=8, r=8, t=30, b=8), showlegend=False)
            render_chart(fig)
        else:
            st.info("No settlement data yet.")

    st.download_button("⬇️ Download expense ledger (CSV)", data=clean.to_csv(index=False).encode("utf-8"),
                       file_name=f"VyaparScore_{merchant.replace(' ', '_')}_expenses.csv",
                       mime="text/csv", key=f"dl_ledger::{sig}")

    return {"total_expenses": total_expenses, "net_profit": net_profit, "margin": margin, "lines": len(clean)}


# ---------------------------------------------------------------------------
# 11. Tab 3 — Anomaly & fraud detector
# ---------------------------------------------------------------------------

def tab_fraud(flags: pd.DataFrame, risk_score: float, summary: dict, metrics: dict,
              sig: str, has_time: bool) -> None:
    verdict = ("CRITICAL" if risk_score >= 60 else "ELEVATED" if risk_score >= 30
               else "GUARDED" if risk_score >= 10 else "CLEAN")
    verdict_kind = {"CRITICAL": "high", "ELEVATED": "high", "GUARDED": "med", "CLEAN": "ok"}[verdict]

    bar("UPI anomaly &amp; fraud scan",
        f"{len(metrics['credits']):,} successful credits screened against 5 rules — structuring, midnight "
        f"value, velocity, payer bursts and round-amount clustering.",
        badge(f"VERDICT: {verdict}", verdict_kind) + "&nbsp;" + badge(f"RISK INDEX {risk_score:.0f}/100", verdict_kind))

    if not has_time:
        st.warning("Intra-day rules need clock times. Upload a CSV with full timestamps to enable the "
                   "complete rule set.")

    s1, s2, s3, s4 = st.columns(4, gap="medium")
    s1.markdown(metric_card("High severity flags", str(summary["High"]), "Manual review advised",
                            "down" if summary["High"] else "up"), unsafe_allow_html=True)
    s2.markdown(metric_card("Medium severity flags", str(summary["Medium"]), "Monitor over 7 days",
                            "down" if summary["Medium"] else "up"), unsafe_allow_html=True)
    s3.markdown(metric_card("Low severity flags", str(summary["Low"]), "Informational pattern noise",
                            "down" if summary["Low"] else "up"), unsafe_allow_html=True)
    flagged_value = float(flags.drop_duplicates("index")["Amount (₹)"].sum()) if len(flags) else 0.0
    s4.markdown(metric_card("Flagged transaction value", inr(flagged_value),
                            "Gross value of screened outliers"), unsafe_allow_html=True)

    col_a, col_b = st.columns([1.55, 1], gap="large")
    with col_a:
        panel("Transactions on the timeline", "Each dot is one successful credit; coloured dots carry a reason code.")
        credits = metrics["credits"].copy()
        if len(flags):
            severity_by_index = (flags.drop_duplicates("index").set_index("index")["Severity"].to_dict())
            order = {"High": 3, "Medium": 2, "Low": 1}
            worst: dict[int, str] = {}
            for _, row in flags.iterrows():
                current = worst.get(row["index"])
                if current is None or order[row["Severity"]] > order[current]:
                    worst[row["index"]] = row["Severity"]
            credits["Severity"] = [worst.get(i, "Normal") for i in credits.index]
        else:
            credits["Severity"] = "Normal"
            severity_by_index = {}

        scatter = px.scatter(credits, x="timestamp", y="amount", color="Severity",
                             category_orders={"Severity": ["Normal", "Low", "Medium", "High"]},
                             color_discrete_map={"Normal": "#CBD5E1", "Low": "#0EA5E9",
                                                 "Medium": "#F59E0B", "High": "#DC2626"},
                             labels={"timestamp": "", "amount": "Amount (₹)", "Severity": ""},
                             hover_data={"payer": True}, opacity=0.75)
        scatter.update_traces(marker=dict(size=6),
                              hovertemplate="%{x|%d %b %H:%M}<br>₹%{y:,.0f}<br>%{customdata[0]}<extra></extra>")
        render_chart(style_figure(scatter, 340))
        st.caption(f"{len(severity_by_index):,} of {len(credits):,} credits carry at least one flag.")

    with col_b:
        panel("Rule engine verdicts", "Highest-impact flags first.")
        if flags.empty:
            st.markdown(
                '<div class="vs-flagcard ok"><div class="t">✅ No anomalies detected</div>'
                '<div class="d">Every transaction sits inside this merchant&#39;s normal behavioural '
                "envelope.</div></div>",
                unsafe_allow_html=True,
            )
        else:
            ranked = flags.copy()
            ranked["rank"] = ranked["Severity"].map({"High": 0, "Medium": 1, "Low": 2})
            top = ranked.sort_values(["rank", "Amount (₹)"], ascending=[True, False]).head(7)
            for _, row in top.iterrows():
                kind = {"High": "", "Medium": "med", "Low": "low"}[row["Severity"]]
                st.markdown(
                    f'<div class="vs-flagcard {kind}">'
                    f'<div class="t">{row["Rule Code"]} · {row["Anomaly"]} '
                    f'{severity_badge(row["Severity"])}</div>'
                    f'<div class="d"><b>{inr(row["Amount (₹)"])}</b> from {row["Payer"]} · '
                    f'{row["Time"]:%d %b, %I:%M %p}<br>{row["Reason"]}</div></div>',
                    unsafe_allow_html=True,
                )

    st.markdown('<hr class="vs-sep">', unsafe_allow_html=True)
    panel("Flagged transaction register", "Export this list for the lender's risk team.")
    if flags.empty:
        st.success("Nothing to report — this ledger is clean.")
    else:
        display = flags[["Time", "Payer", "Amount (₹)", "Mode", "Rule Code", "Anomaly",
                         "Severity", "Reason"]].copy()
        display["Time"] = display["Time"].dt.strftime("%d %b %Y, %I:%M %p")
        st.dataframe(
            display, hide_index=True, height=360,
            column_config={
                "Severity": st.column_config.TextColumn("Severity", width="small"),
                "Amount (₹)": st.column_config.NumberColumn("Amount (₹)", format="₹ %.0f", width="small"),
                "Reason": st.column_config.TextColumn("Reason", width="large"),
            },
            **FRAME,
        )
        st.download_button("⬇️ Download flagged transactions (CSV)",
                           data=display.to_csv(index=False).encode("utf-8"),
                           file_name="VyaparScore_flagged_transactions.csv",
                           mime="text/csv", key=f"dl_flags::{sig}")

    with st.expander("📜 Rule definitions & reason codes"):
        st.dataframe(
            pd.DataFrame([{"Code": code, "Anomaly": label, "Severity": severity, "Trigger logic": logic}
                          for code, (label, severity, logic) in RULE_LOGIC.items()]),
            hide_index=True, **FRAME,
        )
        st.caption("Risk index = 12 × high-severity events + 6 × medium + 2 × low, capped at 100. "
                   "One 'event' is one rule firing within a single hour, so a burst is counted once.")


# ---------------------------------------------------------------------------
# 12. Tab 4 — Micro-loan instant approval
# ---------------------------------------------------------------------------

def rejection_reasons(score: int, amount: int, limit: int, risk_score: float,
                      high_flags: int) -> list[str]:
    reasons = []
    if score <= 650:
        reasons.append(f"Your VyaparScore is {score}; instant approval needs a score above 650.")
    if risk_score >= 60:
        reasons.append(f"An automatic fraud hold is in place: risk index {risk_score:.0f}/100 with "
                       f"{high_flags} high-severity anomaly flag(s) open on the detector tab.")
    if amount > limit:
        reasons.append(f"The requested {inr(amount)} exceeds your approved limit of {inr(limit)}.")
    if limit == 0 and score > 650:
        reasons.append("Net monthly profit is too thin to support an instalment right now.")
    return reasons or ["This request could not be auto-approved."]


def tab_loan(score: int, limit: int, net_profit: float, merchant: str, owner: str,
             upi_id: str, sig: str, risk_score: float, high_flags: int) -> None:
    offer_rate = risk_rate(score)
    fraud_hold = risk_score >= 60
    # Two gates: the score gate from the product brief, plus a fraud hold so a
    # CRITICAL-risk ledger can never be sanctioned instantly.
    eligible = score > 650 and limit > 0 and not fraud_hold

    status_badge = (badge("PRE-APPROVED", "ok") if eligible
                    else badge("FRAUD HOLD", "high") if score > 650 and fraud_hold
                    else badge("NOT ELIGIBLE YET", "high"))
    hint = (f"Pre-approved from your VyaparScore of <b>{score}</b> — unsecured, no collateral, "
            f"disbursal straight to {upi_id}.")
    if fraud_hold:
        hint = (f"Your score of <b>{score}</b> clears the 650 gate, but {high_flags} high-severity "
                f"anomaly flag(s) put an automatic hold on instant disbursal. Clear them on the "
                f"detector tab to unlock this offer.")
    bar("Instant micro-loan desk", hint, status_badge)

    k1, k2, k3, k4 = st.columns(4, gap="medium")
    k1.markdown(metric_card("Approved loan limit", inr(limit),
                            "3 × sustainable net profit, score-scaled", "up" if limit else "down"),
                unsafe_allow_html=True)
    k2.markdown(metric_card("Your interest rate", f"{offer_rate:.1f}% p.a.",
                            "Reducing balance, score-based pricing"), unsafe_allow_html=True)
    k3.markdown(metric_card("Net monthly profit", inr(net_profit), "Repayment capacity basis",
                            "up" if net_profit > 0 else "down"), unsafe_allow_html=True)
    k4.markdown(metric_card("Instant approval needs", "650+ & risk < 60",
                            f"Score {score} · risk {risk_score:.0f}/100",
                            "up" if eligible else "down"), unsafe_allow_html=True)

    st.markdown('<hr class="vs-sep">', unsafe_allow_html=True)

    form_col, summary_col = st.columns([1, 1.3], gap="large")
    safe_limit = max(limit, 2_000)
    default_amount = min(max(1_000, int(limit * 0.6 // 1000 * 1000)), safe_limit)
    with form_col:
        panel("Build your loan", "Move the slider — the EMI and schedule recalculate live.")
        amount = st.slider("Loan amount (₹)", min_value=1_000, max_value=safe_limit,
                           value=default_amount, step=1_000, key=f"loan_amount::{sig}",
                           disabled=not eligible,
                           help="Capped at your approved limit." if eligible
                           else "Qualify by raising your score above 650.")
        tenure = st.selectbox("Repayment tenure", [3, 6, 9, 12, 18, 24], index=2, key=f"loan_tenure::{sig}",
                              format_func=lambda months: f"{months} months", disabled=not eligible)
        rate = st.slider("Interest rate (% p.a.)", min_value=9.0, max_value=30.0, value=float(offer_rate),
                         step=0.5, key=f"loan_rate::{sig}", disabled=not eligible,
                         help=f"Best offer for your score band is {offer_rate:.1f}% p.a.")
        purpose = st.selectbox("Purpose of loan",
                               ["Inventory restock", "Equipment purchase", "Shop renovation",
                                "Working capital", "Festival season stock"],
                               key=f"loan_purpose::{sig}", disabled=not eligible)

        apply_clicked = st.button("⚡ Apply Now — instant decision", type="primary",
                                  key=f"apply::{sig}", disabled=not eligible, **BTN)
        clear_clicked = st.button("Clear application", key=f"clear::{sig}", **BTN)

    emi, schedule = amortisation(amount, rate, int(tenure))
    total_payable = emi * int(tenure)
    interest_total = max(total_payable - amount, 0.0)

    with summary_col:
        panel("Repayment snapshot", "Reducing-balance amortisation.")
        m1, m2, m3 = st.columns(3, gap="medium")
        m1.markdown(metric_card("Monthly EMI", inr(emi), "Fixed instalment"), unsafe_allow_html=True)
        m2.markdown(metric_card("Total interest", inr(interest_total),
                                f"{pct(interest_total / amount * 100) if amount else '0%'} of principal"),
                    unsafe_allow_html=True)
        m3.markdown(metric_card("Total payable", inr(total_payable), f"Over {tenure} months"),
                    unsafe_allow_html=True)
        render_chart(style_figure(
            px.area(schedule, x="Instalment", y=["Interest (₹)", "Principal (₹)"],
                    labels={"value": "₹", "variable": "", "Instalment": "Instalment #"},
                    color_discrete_sequence=["#F59E0B", "#4F46E5"]), 300))

    application_key = f"application::{sig}"
    rejection_key = f"rejection::{sig}"

    if clear_clicked:
        st.session_state[application_key] = None
        st.session_state[rejection_key] = None
    if apply_clicked:
        if eligible and amount <= limit:
            st.session_state[application_key] = {
                "id": "VS-" + datetime.now().strftime("%Y%m%d") + "-"
                      + hashlib.sha256(f"{sig}{amount}{tenure}{time.time()}".encode()).hexdigest()[:6].upper(),
                "amount": float(amount), "emi": float(emi), "tenure": int(tenure), "rate": float(rate),
                "purpose": purpose, "score": score, "owner": owner, "merchant": merchant, "upi": upi_id,
                "risk": risk_score,
                "sanctioned_on": datetime.now(), "schedule": schedule,
                "first_due": schedule.iloc[0]["Due date"],
            }
            st.session_state[rejection_key] = None
            st.toast("Loan approved instantly!", icon="🎉")
        else:
            st.session_state[application_key] = None
            st.session_state[rejection_key] = rejection_reasons(score, amount, limit,
                                                               risk_score, high_flags)

    application = st.session_state.get(application_key)
    if application:
        st.markdown('<hr class="vs-sep">', unsafe_allow_html=True)
        render_certificate(application)
    elif st.session_state.get(rejection_key):
        st.markdown('<hr class="vs-sep">', unsafe_allow_html=True)
        st.error("**Application declined.** " + " ".join(st.session_state[rejection_key]))
        st.markdown(
            '<div class="vs-panel"><h4>How to qualify in 30 days</h4>'
            '<div class="vs-step">1. <span>Accept more payments on UPI instead of cash — the digital '
            "footprint factor is worth 22% of the score.</span></div>"
            '<div class="vs-step">2. <span>Keep daily collections steady; cash-flow consistency is the '
            "heaviest factor at 28%.</span></div>"
            '<div class="vs-step">3. <span>Clear open fraud flags on the anomaly tab — safety is a hard '
            "gate for instant sanction.</span></div></div>",
            unsafe_allow_html=True,
        )


def render_certificate(app: dict) -> None:
    st.markdown(
        f"""
<div class="vs-cert">
  <div class="vs-cert-head">
    <div>
      <div class="vs-cert-title">🎉 Loan Approved!</div>
      <div class="vs-cert-sub">VyaparScore Instant Sanction · Application <b>{app['id']}</b></div>
    </div>
    <div class="vs-seal">✓</div>
  </div>
  <div style="margin-top:1rem">
    <div class="vs-cert-amount">{inr(app['amount'])}</div>
    <div class="vs-cert-words">{inr_words(app['amount'])}</div>
  </div>
  <div class="vs-cert-grid">
    <div><span>Sanctioned to</span><b>{app['owner']}</b></div>
    <div><span>Business</span><b>{app['merchant']}</b></div>
    <div><span>Disbursal UPI ID</span><b>{app['upi']}</b></div>
    <div><span>Tenure</span><b>{app['tenure']} months</b></div>
    <div><span>Interest rate</span><b>{app['rate']:.1f}% p.a. (reducing)</b></div>
    <div><span>Monthly EMI</span><b>{inr(app['emi'])}</b></div>
    <div><span>Purpose</span><b>{app['purpose']}</b></div>
    <div><span>Sanctioned on</span><b>{app['sanctioned_on']:%d %b %Y, %I:%M %p}</b></div>
    <div><span>First instalment</span><b>{app['first_due']:%d %b %Y}</b></div>
  </div>
  <div class="vs-cert-foot">
    Credit score at sanction: <b>{app['score']} / 900</b> · fraud risk index <b>{app['risk']:.0f} / 100</b>.
    Sanctioned under the VyaparScore micro-merchant
    programme — unsecured, no collateral, no processing fee. This is a simulated hackathon certificate and
    is not a binding credit offer.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div style="height:.7rem"></div>', unsafe_allow_html=True)
    panel("Repayment schedule", "Auto-debit from the linked account on the 5th of every month.")
    st.dataframe(
        app["schedule"], hide_index=True, height=280,
        column_config={
            "EMI (₹)": st.column_config.NumberColumn("EMI (₹)", format="₹ %.0f"),
            "Interest (₹)": st.column_config.NumberColumn("Interest (₹)", format="₹ %.0f"),
            "Principal (₹)": st.column_config.NumberColumn("Principal (₹)", format="₹ %.0f"),
            "Closing balance (₹)": st.column_config.NumberColumn("Closing balance (₹)", format="₹ %.0f"),
        },
        **FRAME,
    )
    st.download_button("⬇️ Download repayment schedule (CSV)",
                       data=app["schedule"].to_csv(index=False).encode("utf-8"),
                       file_name=f"VyaparScore_{app['id']}_schedule.csv",
                       mime="text/csv", key=f"dl_schedule::{app['id']}")


# ---------------------------------------------------------------------------
# 13. App shell
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="VyaparScore · Micro-Merchant Credit & UPI Anomaly Detector",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    state = sidebar()
    txns, meta, using_mock = load_dataset(state)
    profile = PROFILES[state["merchant"]]
    tenure = profile["tenure_months"] if using_mock else max(
        int((txns["timestamp"].max() - txns["timestamp"].min()).days / 30), 1)

    metrics = compute_metrics(txns, meta, tenure)
    flags, risk_score, summary = detect_anomalies(metrics["credits"], metrics["has_time"])
    sig = signature("mock" if using_mock else "csv", state["merchant"], state["csv"], state["seed_bump"])

    # Resolve the ledger before tab 1 so net profit and the loan limit reflect the latest edits.
    ledger_key = f"ledger::{sig}"
    if ledger_key not in st.session_state:
        st.session_state[ledger_key] = build_mock_ledger(state["merchant"], metrics["monthly_revenue"])
    net_profit = metrics["monthly_revenue"] - ledger_amount_total(st.session_state[ledger_key])

    credit = compute_credit_score(metrics, risk_score)
    limit = approved_loan_limit(credit["score"], net_profit, profile["loan_cap"])

    source_label = f"Mock · {state['merchant']}" if using_mock else f"Upload · {state['csv_name']}"
    st.markdown(
        f"""
<div class="vs-masthead">
  <h1>🛡️ VyaparScore</h1>
  <div class="vs-sub">Micro-merchant credit score &amp; UPI anomaly detector · built for Bharat's kirana economy</div>
  <span class="vs-chip">👤 {profile['owner']}</span>
  <span class="vs-chip">🏪 {state['merchant']}</span>
  <span class="vs-chip">📍 {profile['city']}</span>
  <span class="vs-chip">🔑 {profile['upi_id']}</span>
  <span class="vs-chip">📊 {source_label}</span>
  <span class="vs-chip">🗓️ {metrics['span_days']} days of history</span>
</div>
""",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "💳 Digital UPI & Credit Score",
        "📒 Physical Register Scanner",
        "🚨 UPI Anomaly & Fraud Detector",
        "🏦 Micro-Loan Instant Approval",
    ])

    with tab1:
        tab_credit(metrics, credit, limit, net_profit, state["merchant"], using_mock, risk_score, len(flags))
    with tab2:
        ocr_result = tab_ocr(state["merchant"], metrics, sig, state["image"])
    with tab3:
        tab_fraud(flags, risk_score, summary, metrics, sig, metrics["has_time"])
    with tab4:
        tab_loan(credit["score"], limit, ocr_result["net_profit"], state["merchant"],
                 profile["owner"], profile["upi_id"], sig, risk_score, summary["High"])

    st.markdown(
        '<hr class="vs-sep">'
        '<p style="color:#94A3B8;font-size:.75rem;line-height:1.6;text-align:center">'
        "VyaparScore · hackathon prototype · all merchant data, OCR output, fraud flags and loan sanctions "
        "are simulated. Not financial, lending or tax advice.</p>",
        unsafe_allow_html=True,
    )


main()
