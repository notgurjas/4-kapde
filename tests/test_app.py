"""End-to-end and unit tests for the VyaparScore Streamlit app.

The end-to-end tests drive the real `app.py` script through Streamlit's own
`AppTest` harness, so every widget, callback and tab body actually executes.

Run from the repository root:
    .venv/bin/python -m pytest tests/ -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402  (importing executes the app once in bare mode)

APP_PATH = ROOT / "app.py"

# A minimal 1x1 PNG, enough for the uploader to hand back real bytes.
PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
    b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05"
    b"\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def run_app() -> AppTest:
    return AppTest.from_file(str(APP_PATH), default_timeout=180).run()


def find(seq, key):
    matches = [el for el in seq if el.key == key]
    assert matches, f"no element with key {key!r}; have {[el.key for el in seq]}"
    return matches[0]


def button(at: AppTest, key: str):
    return find(at.button, key)


def uploader(at: AppTest, key: str):
    return find(at.get("file_uploader"), key)


def ledger_editor(at: AppTest):
    """The editable bahi-khata grid (st.data_editor surfaces as a dataframe)."""
    matches = [d for d in at.get("dataframe") if (d.key or "").startswith("ledger_editor::")]
    assert matches, [d.key for d in at.get("dataframe")]
    return matches[0]


def all_markdown(at: AppTest) -> str:
    return "\n".join(m.value for m in at.markdown)


def alerts(at: AppTest) -> str:
    return "\n".join(
        el.value for kind in ("info", "warning", "error", "success") for el in at.get(kind)
    )


# ---------------------------------------------------------------------------
# Full-script runs
# ---------------------------------------------------------------------------

def test_app_renders_four_tabs_without_errors():
    at = run_app()
    assert not at.exception, at.exception
    assert [t.label for t in at.tabs] == [
        "💳 Digital UPI & Credit Score",
        "📒 Physical Register Scanner",
        "🚨 UPI Anomaly & Fraud Detector",
        "🏦 Micro-Loan Instant Approval",
    ]
    text = all_markdown(at)
    assert "VyaparScore" in text
    assert "Ramesh Tea Stall" in text          # default mock profile
    assert "MOCK DATA" in text                 # source badge on tab 1
    for kpi in ("Total monthly UPI revenue", "Average daily transactions",
                "Customer retention rate", "Max loan approved"):
        assert kpi in text, kpi


def test_default_merchant_has_editable_ledger_and_totals():
    at = run_app()
    assert not at.exception, at.exception
    ledger = ledger_editor(at).value
    assert {"Date", "Voucher No.", "Particulars", "Category", "Amount (₹)", "Payment Mode"} <= set(ledger.columns)
    assert len(ledger) >= 8
    assert float(ledger["Amount (₹)"].sum()) > 0
    text = all_markdown(at)
    assert "Total physical expenses" in text
    assert "Net monthly profit" in text
    assert "Bahi-Khata OCR scanner" in text


def test_suspicious_merchant_is_flagged_and_denied_credit():
    at = run_app()
    at.selectbox(key="profile_choice").set_value("Suspicious Merchant").run()
    assert not at.exception, at.exception
    text = all_markdown(at)
    assert "CRITICAL" in text or "ELEVATED" in text
    assert "STR-01" in text and "MID-02" in text
    assert "NOT ELIGIBLE YET" in text or "FRAUD HOLD" in text
    frames = [f.value for f in at.get("dataframe")]
    flagged = [f for f in frames if "Rule Code" in f.columns]
    assert flagged, "flagged transaction table missing"
    assert len(flagged[0]) > 0
    assert {"Rule Code", "Anomaly", "Severity", "Reason"} <= set(flagged[0].columns)


def test_flagged_rows_share_an_index_space_with_the_timeline():
    """Guards the regression where flag indices did not map onto chart points."""
    frame = app.build_mock_transactions("Suspicious Merchant", days=60, seed_bump=0)
    metrics = app.compute_metrics(frame, {"has_time": True}, 5)
    flags, risk, summary = app.detect_anomalies(metrics["credits"], True)
    assert not flags.empty
    assert set(flags["index"]).issubset(set(metrics["credits"].index))
    assert risk > 50 and summary["High"] > 0
    for _, row in flags.iterrows():
        original = metrics["credits"].loc[row["index"]]
        assert abs(float(original["amount"]) - row["Amount (₹)"]) < 0.01
        assert original["payer"] == row["Payer"]
        assert original["timestamp"] == row["Time"]


def test_uploaded_csv_replaces_the_mock_data():
    csv_bytes = (
        b"timestamp,payer,amount,status\n"
        b"2026-08-01 09:15:00,Arun K,120.50,SUCCESS\n"
        b"2026-08-01 18:22:00,Divya R,340.00,SUCCESS\n"
        b"2026-08-02 10:05:00,Arun K,90.00,SUCCESS\n"
        b"2026-08-02 20:41:00,Sanjay M,1500.00,SUCCESS\n"
        b"2026-08-03 11:00:00,Fatima S,75.25,FAILED\n"
    )

    at = run_app()
    at.radio(key="source_choice").set_value(app.SOURCE_CHOICES[1]).run()
    uploader(at, "csv_uploader").set_value(("upi.csv", csv_bytes, "text/csv")).run()
    assert not at.exception, at.exception
    text = all_markdown(at)
    assert "Upload · upi.csv" in text
    assert "3 days of history" in text  # 1-3 Aug inclusive
    assert "UPLOADED CSV" in text


def test_date_only_upload_disables_intraday_rules():
    csv_bytes = (
        b"date,customer,amt\n"
        b"01/08/2026,Arun K,500\n"
        b"02/08/2026,Divya R,700\n"
        b"03/08/2026,Arun K,900\n"
    )
    at = run_app()
    at.radio(key="source_choice").set_value(app.SOURCE_CHOICES[1]).run()
    uploader(at, "csv_uploader").set_value(("ledger.csv", csv_bytes, "text/csv")).run()
    assert not at.exception, at.exception
    assert "no clock times" in all_markdown(at) + alerts(at)


def test_ocr_scan_parses_the_uploaded_register_image():
    at = run_app()
    before = ledger_editor(at).value
    uploader(at, "side_image_uploader").set_value(("register.png", PNG_BYTES, "image/png")).run()
    assert not at.exception, at.exception

    sig = ledger_editor(at).key.split("::")[1]
    button(at, f"run_ocr::{sig}").click().run()
    assert not at.exception, at.exception

    editor = ledger_editor(at)
    after = editor.value
    assert len(after) >= 8
    assert float(after["Amount (₹)"].sum()) > 0
    assert editor.key != f"ledger_editor::{sig}::v0", "editor should be re-keyed after a fresh scan"
    assert not after["Amount (₹)"].round(2).equals(before["Amount (₹)"].round(2)), \
        "a scanned image should produce a different parse than the default ledger"


def test_loan_application_produces_a_certificate():
    at = run_app()
    at.selectbox(key="profile_choice").set_value("Sharma Kirana Store").run()
    assert not at.exception, at.exception
    assert "PRE-APPROVED" in all_markdown(at)

    slider = find(at.slider, f"loan_amount::{app.signature('mock', 'Sharma Kirana Store', None, 0)}")
    slider.set_value(20_000).run()
    assert not at.exception, at.exception

    sig = app.signature("mock", "Sharma Kirana Store", None, 0)
    button(at, f"apply::{sig}").click().run()
    assert not at.exception, at.exception

    text = all_markdown(at)
    assert "Loan Approved!" in text
    assert "Repayment schedule" in text
    assert "Rupees Only" in text                    # amount-in-words on the certificate
    assert "Twenty Thousand Rupees Only" in text

    schedules = [f.value for f in at.get("dataframe") if "Closing balance (₹)" in f.value.columns]
    assert schedules, "amortisation table missing"
    assert len(schedules[0]) == 9                   # default tenure is 9 months
    assert schedules[0].iloc[-1]["Closing balance (₹)"] == 0


def test_fraud_merchant_cannot_reach_the_apply_button():
    """Either the score gate or the fraud hold must block instant sanction."""
    at = run_app()
    at.selectbox(key="profile_choice").set_value("Suspicious Merchant").run()
    text = all_markdown(at)
    assert "NOT ELIGIBLE YET" in text or "FRAUD HOLD" in text
    assert "PRE-APPROVED" not in text
    sig = app.signature("mock", "Suspicious Merchant", None, 0)
    assert button(at, f"apply::{sig}").proto.disabled is True


def test_rejection_reasons_cover_both_gates():
    assert any("above 650" in r for r in app.rejection_reasons(620, 10_000, 50_000, 10.0, 0))
    fraud = app.rejection_reasons(700, 10_000, 50_000, 95.0, 12)
    assert any("fraud hold" in r for r in fraud), fraud
    assert app.rejection_reasons(700, 90_000, 50_000, 10.0, 0)[0].startswith("The requested")


def test_bigger_register_expenses_shrink_the_loan_limit():
    """Editing the ledger feeds tab 1 (net profit) and tab 4 (eligibility)."""
    merchant = "Sharma Kirana Store"
    sig = app.signature("mock", merchant, None, 0)
    ledger_key = f"ledger::{sig}"

    at = run_app()
    at.selectbox(key="profile_choice").set_value(merchant).run()
    assert "PRE-APPROVED" in all_markdown(at)
    baseline = at.session_state[ledger_key].copy()
    assert app.ledger_amount_total(baseline) > 0

    bloated = baseline.copy()
    bloated["Amount (₹)"] = bloated["Amount (₹)"] * 50
    at.session_state[ledger_key] = bloated
    at.run()
    assert not at.exception, at.exception
    assert "NOT ELIGIBLE YET" in all_markdown(at)
    assert at.session_state[ledger_key]["Amount (₹)"].sum() > baseline["Amount (₹)"].sum()


def test_reroll_changes_the_synthetic_transactions():
    at = run_app()
    try:
        first = at.session_state["seed_bump"]
    except Exception:
        first = 0
    button(at, "reroll").click().run()
    assert not at.exception, at.exception
    assert at.session_state["seed_bump"] == first + 1


def test_every_plotly_figure_serialises(monkeypatch):
    """Plotly only rejects bad properties at render time - the gauge once shipped broken."""
    import plotly.io as pio

    captured: list = []
    monkeypatch.setattr(app.st, "plotly_chart", lambda fig, **kwargs: captured.append(fig))

    at = run_app()
    assert not at.exception, at.exception
    assert len(captured) >= 8, f"expected the dashboard charts, captured {len(captured)}"
    for fig in captured:
        payload = pio.to_json(fig)      # raises ValueError on invalid properties
        assert len(payload) > 200


# ---------------------------------------------------------------------------
# Pure-function unit tests
# ---------------------------------------------------------------------------

def test_inr_uses_indian_grouping():
    assert app.inr(1234567) == "₹12,34,567"
    assert app.inr(1000) == "₹1,000"
    assert app.inr(999) == "₹999"
    assert app.inr(-2500.5, decimals=2) == "-₹2,500.50"
    assert app.inr(123456789) == "₹12,34,56,789"


def test_inr_words_uses_the_indian_system():
    assert app.inr_words(0) == "Zero Rupees Only"
    assert app.inr_words(125000) == "One Lakh Twenty Five Thousand Rupees Only"
    assert app.inr_words(1000) == "One Thousand Rupees Only"
    assert app.inr_words(20500) == "Twenty Thousand Five Hundred Rupees Only"
    assert app.inr_words(10000000) == "One Crore Rupees Only"


def test_credit_score_stays_within_300_900():
    floors = {"Ramesh Tea Stall": 650, "Sharma Kirana Store": 700, "Suspicious Merchant": 300}
    for profile, floor in floors.items():
        frame = app.build_mock_transactions(profile, days=60)
        metrics = app.compute_metrics(frame, {"has_time": True}, app.PROFILES[profile]["tenure_months"])
        _, risk, _ = app.detect_anomalies(metrics["credits"], True)
        credit = app.compute_credit_score(metrics, risk)
        assert 300 <= credit["score"] <= 900
        assert credit["score"] >= floor, profile
        assert sum(c["weight"] for c in credit["components"].values()) == pytest.approx(1.0)


def test_suspicious_merchant_is_never_instantly_approved():
    """Re-rolling the seed must not let a CRITICAL-risk ledger through, whatever the score."""
    profile = "Suspicious Merchant"
    for bump in range(6):
        frame = app.build_mock_transactions(profile, days=60, seed_bump=bump)
        metrics = app.compute_metrics(frame, {"has_time": True}, app.PROFILES[profile]["tenure_months"])
        _, risk, summary = app.detect_anomalies(metrics["credits"], True)
        credit = app.compute_credit_score(metrics, risk)
        limit = app.approved_loan_limit(credit["score"], 50_000, app.PROFILES[profile]["loan_cap"])
        eligible = credit["score"] > 650 and limit > 0 and risk < 60
        assert risk >= 60 and summary["High"] > 0, bump
        assert not eligible, (bump, credit["score"], risk)


def test_healthy_merchants_rank_above_the_fraud_profile():
    scores = {}
    for profile in app.PROFILES:
        frame = app.build_mock_transactions(profile, days=60)
        metrics = app.compute_metrics(frame, {"has_time": True}, app.PROFILES[profile]["tenure_months"])
        _, risk, _ = app.detect_anomalies(metrics["credits"], True)
        scores[profile] = app.compute_credit_score(metrics, risk)["score"]
    assert scores["Sharma Kirana Store"] > scores["Ramesh Tea Stall"] > scores["Suspicious Merchant"]
    assert scores["Sharma Kirana Store"] >= 800          # reaches the "Excellent" band
    assert scores["Suspicious Merchant"] < 700


def test_healthy_merchants_get_a_loan_limit():
    for profile in ("Ramesh Tea Stall", "Sharma Kirana Store"):
        frame = app.build_mock_transactions(profile, days=60)
        metrics = app.compute_metrics(frame, {"has_time": True}, app.PROFILES[profile]["tenure_months"])
        _, risk, _ = app.detect_anomalies(metrics["credits"], True)
        credit = app.compute_credit_score(metrics, risk)
        net_profit = metrics["monthly_revenue"] * (1 - app.PROFILES[profile]["expense_ratio"])
        limit = app.approved_loan_limit(credit["score"], net_profit, app.PROFILES[profile]["loan_cap"])
        assert credit["score"] > 650, profile
        assert limit > 0 and limit % 1000 == 0
        assert limit <= app.PROFILES[profile]["loan_cap"]

    assert app.approved_loan_limit(480, 50_000, 500_000) == 0
    assert app.approved_loan_limit(700, -5_000, 500_000) == 0


def test_risk_rate_values_land_on_the_slider_grid():
    for score in (300, 550, 651, 720, 800, 900):
        rate = app.risk_rate(score)
        assert 9.0 <= rate <= 30.0
        assert (rate - 9.0) % 0.5 == 0


def _normal_backdrop(count=40, amount=500.0):
    """Ordinary daily trade the anomaly rules must NOT react to."""
    return [
        {"timestamp": pd.Timestamp("2026-08-01 10:00:00") + pd.Timedelta(days=i, hours=i % 8),
         "payer": f"Regular {i % 12}", "payer_upi": "r@ybl", "amount": amount,
         "mode": "QR Scan", "note": "", "status": "SUCCESS"}
        for i in range(count)
    ]


def test_anomaly_rules_fire_on_synthetic_patterns():
    rows = _normal_backdrop()
    base = pd.Timestamp("2026-08-10 14:00:00")
    for i in range(8):  # 8 micro payments inside ~4.5 minutes -> STR-01
        rows.append({"timestamp": base + pd.Timedelta(seconds=40 * i), "payer": f"P{i % 3}",
                     "payer_upi": "x@ybl", "amount": 60.0, "mode": "QR Scan", "note": "", "status": "SUCCESS"})
    rows.append({"timestamp": pd.Timestamp("2026-08-11 02:15:00"), "payer": "Whale",
                 "payer_upi": "w@paytm", "amount": 150_000.0, "mode": "P2P", "note": "", "status": "SUCCESS"})
    for i in range(5):  # 5 round amounts on one day -> RND-04
        rows.append({"timestamp": pd.Timestamp("2026-08-12 12:00:00") + pd.Timedelta(minutes=50 * i),
                     "payer": f"Round{i}", "payer_upi": "r@upi", "amount": 10_000.0,
                     "mode": "P2P", "note": "", "status": "SUCCESS"})
    frame = pd.DataFrame(rows)

    flags, risk, summary = app.detect_anomalies(frame, has_time=True)
    assert {"STR-01", "MID-02", "RND-04"} <= set(flags["Rule Code"])
    assert risk > 0 and summary["High"] >= 2

    flags_no_time, _, _ = app.detect_anomalies(frame, has_time=False)
    assert "STR-01" not in set(flags_no_time["Rule Code"])
    assert "MID-02" in set(flags_no_time["Rule Code"])


def test_velocity_rule_uses_the_merchants_own_baseline():
    base = pd.Timestamp("2026-08-14 16:00:00")
    rows = _normal_backdrop() + [
        {"timestamp": base + pd.Timedelta(minutes=i * 2), "payer": f"Cust{i}",
         "payer_upi": "c@ybl", "amount": 320.0, "mode": "QR Scan", "note": "", "status": "SUCCESS"}
        for i in range(28)
    ]
    flags, _, summary = app.detect_anomalies(pd.DataFrame(rows), has_time=True)
    assert "VEL-03" in set(flags["Rule Code"])
    assert summary["Medium"] == 4  # only the tail of the burst has 25+ credits in its hour
    assert flags.loc[flags["Rule Code"] == "VEL-03", "Payer"].tolist() == [
        "Cust24", "Cust25", "Cust26", "Cust27"
    ]


def test_payer_burst_rule():
    base = pd.Timestamp("2026-08-14 16:00:00")
    rows = _normal_backdrop() + [
        {"timestamp": base + pd.Timedelta(minutes=i * 2), "payer": "Same Payer",
         "payer_upi": "s@ybl", "amount": 500.0, "mode": "QR Scan", "note": "", "status": "SUCCESS"}
        for i in range(6)
    ]
    flags, _, _ = app.detect_anomalies(pd.DataFrame(rows), has_time=True)
    assert "SPL-05" in set(flags["Rule Code"])
    assert (flags.loc[flags["Rule Code"] == "SPL-05", "Payer"] == "Same Payer").all()


def test_clean_ledger_produces_no_flags():
    frame = pd.DataFrame([
        {"timestamp": pd.Timestamp("2026-08-10 09:00:00") + pd.Timedelta(hours=i),
         "payer": f"Customer {i}", "payer_upi": "c@ybl", "amount": 250.0 + i,
         "mode": "QR Scan", "note": "", "status": "SUCCESS"}
        for i in range(30)
    ])
    flags, risk, summary = app.detect_anomalies(frame, has_time=True)
    assert flags.empty and risk == 0.0 and summary == {"High": 0, "Medium": 0, "Low": 0}


def test_detect_anomalies_handles_an_empty_ledger():
    flags, risk, summary = app.detect_anomalies(pd.DataFrame(columns=app.CANONICAL_COLUMNS), True)
    assert flags.empty and risk == 0.0 and summary == {"High": 0, "Medium": 0, "Low": 0}


def test_amortisation_schedule_is_internally_consistent():
    emi, schedule = app.amortisation(120_000, 12.0, 12)
    assert len(schedule) == 12
    assert schedule.iloc[-1]["Closing balance (₹)"] == 0
    assert abs(schedule["Principal (₹)"].sum() - 120_000) < 12
    assert abs(schedule["Interest (₹)"].sum() + schedule["Principal (₹)"].sum() - emi * 12) < 24
    assert emi > 120_000 / 12  # interest makes the instalment larger than a flat split
    assert list(schedule["Due date"]) == sorted(schedule["Due date"])


def test_normalize_transactions_maps_aliased_columns():
    raw = pd.DataFrame({
        "Txn Date": ["01/08/2026 09:15", "02/08/2026 21:30"],
        "Customer Name": ["Arun K", "Divya R"],
        "Amount (INR)": ["₹1,200.00", "Rs 450"],
        "Txn Status": ["Success", "Failed"],
        "Remarks": ["milk", "bread"],
    })
    frame, meta = app.normalize_transactions(raw)
    assert list(frame.columns) == app.CANONICAL_COLUMNS
    assert meta["has_time"] is True
    assert frame["amount"].tolist() == [1200.0, 450.0]
    assert frame["status"].tolist() == ["SUCCESS", "FAILED"]
    assert frame.loc[0, "payer"] == "Arun K"
    assert frame.loc[1, "payer_upi"] == "divyar@uploaded"


def test_timestamp_parsing_does_not_mangle_iso_dates():
    """`dayfirst=True` would read 2026-08-01 as 8 January; that broke the day span."""
    parsed = app._parse_timestamps(pd.Series(["2026-08-01 09:15:00", "2026-08-03 11:00:00"]))
    assert parsed.dt.month.tolist() == [8, 8]
    assert parsed.dt.day.tolist() == [1, 3]

    indian = app._parse_timestamps(pd.Series(["01/08/2026 09:15", "03/08/2026 11:00"]))
    assert indian.dt.month.tolist() == [8, 8]
    assert indian.dt.day.tolist() == [1, 3]

    frame, meta = app.normalize_transactions(
        pd.DataFrame({"timestamp": ["2026-08-01 09:15:00", "2026-08-03 11:00:00"], "amount": [10, 20]})
    )
    assert app.compute_metrics(frame, meta, 1)["span_days"] == 3


def test_normalize_transactions_rejects_unusable_files():
    frame, meta = app.normalize_transactions(pd.DataFrame({"foo": [1, 2], "bar": [3, 4]}))
    assert frame.empty
    assert meta["warnings"]


def test_metrics_scale_a_short_window_to_a_month():
    frame = pd.DataFrame([
        {"timestamp": pd.Timestamp("2026-08-01 10:00:00") + pd.Timedelta(days=i),
         "payer": "Regular" if i < 4 else f"OneOff{i}", "payer_upi": "c@ybl", "amount": 1000.0,
         "mode": "QR Scan", "note": "", "status": "SUCCESS"}
        for i in range(10)
    ])
    metrics = app.compute_metrics(frame, {"has_time": True}, 12)
    assert metrics["span_days"] == 10
    assert metrics["monthly_revenue"] == pytest.approx(30_000.0)   # 10 x 1000 scaled to 30 days
    assert metrics["avg_daily_txns"] == pytest.approx(1.0)         # 30 credits / 30 days
    assert metrics["retention"] == pytest.approx(100 / 7)          # only "Regular" repeats
    assert metrics["avg_ticket"] == pytest.approx(1000.0)
    assert metrics["daily"]["revenue"].sum() == pytest.approx(10_000.0)
