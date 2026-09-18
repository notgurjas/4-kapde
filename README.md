# 🛡️ VyaparScore — Micro-Merchant Credit Score & UPI Anomaly Detector

A single-file Streamlit app built for a FinTech hackathon. It turns two things every
Indian micro-merchant already has — **UPI payment history** and a **photographed paper
bahi-khata (ledger)** — into a credit score, a fraud screen, and an instant micro-loan
decision.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app works out of the box: three mock merchant profiles are generated on the fly, so
nothing has to be uploaded to see every feature.

> `main.py` in this repository is an earlier, unrelated five-tab prototype. The
> hackathon build described here lives entirely in **`app.py`**.

---

## What is in the box

| Tab | What it does |
| --- | --- |
| 💳 **Digital UPI & Credit Score** | 300–900 score on a hero card + gauge, 8 KPI cards, daily income trend with a 7-day moving average, hour-of-day and weekday charts, most-loyal-customer ranking, and an expandable factor-by-factor score breakdown. |
| 📒 **Physical Register Scanner** | Upload a photo of a handwritten register page, run the simulated OCR pass, and get an itemised **editable** expense grid (`st.data_editor`). Totals, category mix and settlement-mode donut update live, and net profit flows back into tab 1. |
| 🚨 **UPI Anomaly & Fraud Detector** | A five-rule engine screens every credit, colour-codes them on a timeline, lists the top verdicts as warning cards, and exports the full flagged register with reason codes. |
| 🏦 **Micro-Loan Instant Approval** | Loan slider capped at the approved limit, live EMI/amortisation preview, and an "Apply Now" button that prints a sanction certificate (amount in words, application ID, repayment schedule, CSV export). |

The sidebar switches between the three mock profiles and a **UPI CSV upload**, and also
accepts the register image. Uploaded CSVs are mapped automatically — column aliases
(`Txn Date`, `Customer Name`, `Amount (INR)`, `Txn Status`, …) are resolved without any
configuration, and ₹/`Rs`/comma-formatted amounts are parsed.

## Mock merchants

| Profile | Story | Score band | Fraud verdict |
| --- | --- | --- | --- |
| Ramesh Tea Stall | ₹80k/month street vendor, 41 months on UPI | ~770 · Good | Guarded — one late-night credit worth reviewing |
| Sharma Kirana Store | ₹12L/month grocery, 6 years on UPI | ~810 · Excellent | Clean — one low-severity round-amount cluster |
| Suspicious Merchant | 5 months old, KYC pending, sudden growth | ~630 · Needs work | Critical — structuring, midnight whales, velocity bursts |

Use **🎲 Re-roll synthetic transactions** in the sidebar to regenerate the 60-day ledger
with a new seed, and **⬇️ Download sample UPI CSV** to grab a file you can feed back
through the upload path.

## How the credit score is built

`300 + 600 × Σ(weight × sub-score)`, clamped to 300–900:

| Factor | Weight | Sub-score |
| --- | --- | --- |
| Cash-flow consistency | 28% | `1 − volatility` (coefficient of variation of daily revenue) |
| Digital footprint | 22% | `log₁₀(monthly credits) ÷ log₁₀(900)` |
| Customer loyalty | 18% | `retention ÷ 70%` |
| Growth momentum | 14% | `0.5 + median-day growth ÷ 40` (median, so one whale credit can't fake growth) |
| Business tenure | 10% | `months on UPI ÷ 36` |
| Trust & safety | 8% | `1 − fraud risk index ÷ 100` |

**Loan limit** = `min(3 × net monthly profit × score multiplier, product cap)`, floored to
₹1,000; zero below a score of 500. Instant sanction needs **score > 650 _and_ a fraud risk
index below 60** — a CRITICAL-risk ledger is never auto-approved, even when the score
clears the bar (the UI shows a `FRAUD HOLD` badge instead).

## Anomaly rules

| Code | Anomaly | Severity | Trigger |
| --- | --- | --- | --- |
| STR-01 | Micro-transaction structuring | High | ≥ 6 credits of ≤ `max(₹20, 0.5 × median)` inside 5 minutes |
| MID-02 | Midnight high-value credit | High | Credit between 00:00–04:59 worth ≥ `max(₹5,000, 6 × 75th pct)` |
| VEL-03 | Transaction velocity spike | Medium | ≥ `max(25, 8 × median busy hour)` credits in a rolling hour |
| SPL-05 | Same payer burst | Medium | ≥ 5 credits from one payer inside 10 minutes |
| RND-04 | Round-amount clustering | Low | ≥ 4 exact ₹1,000-multiple credits on the same day |

Thresholds are derived from each merchant's own baseline, so a ₹20 chai sale is not
"structuring" for a tea stall and a Friday evening rush is not a "velocity spike" for a
busy kirana store. Risk index = `12 × high + 6 × medium + 2 × low` **events** (one event =
one rule firing within an hour), capped at 100. Date-only CSVs automatically disable the
intra-day rules instead of inventing midnight anomalies.

## Tests

```bash
.venv/bin/python -m pytest tests/ -q     # 29 tests
```

`tests/test_app.py` drives the real script through Streamlit's own `AppTest` harness —
profile switching, CSV upload, the OCR scan, ledger edits, the loan application and the
disabled-apply path — plus unit tests for the scoring, rule engine, amortisation and CSV
parsers.

## Honest limitations

* OCR is **simulated**: the parser is seeded from a hash of the uploaded image, so it is
  deterministic and demo-friendly but reads no actual pixels.
* All merchant data is synthetic, and no file is written to disk or sent anywhere.
* Scores, flags and sanctions are illustrative — not financial, lending or tax advice.
