# VyaparPulse — Inclusive Credit Intelligence for Bharat

A single-file, offline Streamlit demo that scores micro-merchants and street vendors with an
explainable, behaviour-based credit model — and protects them from the two frauds they meet most
often: fake payment screenshots and swapped QR codes.

```bash
pip install -r requirements.txt
streamlit run main.py
```

The app opens on the merchant workspace. Everything is synthetic and local: no uploaded document is
parsed, stored or sent anywhere, and no external API is called.

---

## What is in the box

| Workspace | What it does |
|---|---|
| **Overview** | Hero credit score, four KPI cards, cash-flow intelligence, AI insights, risk signals and an indicative credit eligibility envelope |
| **Credit Score** | Radial gauge, factor cards, live-vs-base radar, profit waterfall, month-filtered cash-flow chart, score trend, and the expense / revenue ledger that re-scores in real time |
| **Intelligence Layer** | Integrity verification (wash trading, payer concentration, VPA, velocity, geo-match) with the decision snapshot |
| **Fraud Guard** | Screenshot verification, QR health checks and a batch transaction audit |
| **Risk Analytics** | Composite risk index, revenue-volatility chart and five transparent monitoring signals |
| **Sthan Log** | Physical-presence log, check-ins, daily notes and the PM SVANidhi-ready Proof of Vending certificate |
| **Lender Report** | Credit Passport with factor breakdown, financial summary, attachments and officer notes |
| **Privacy / Terms** | DPDP-aligned policy pages and platform terms |

## The model

* **Live score (300–900):** margin shift × 300, capped at ±150, with expense-ratio penalties,
  revenue-growth credit, +2 per present check-in and +3 per attached expense page — clamped to 300–900.
* **Factors:** consistency, growth, liquidity buffer, payer diversity, reliability, longevity.
  Each factor is re-derived from the merchant's own additions, exactly as before.
* **Eligibility envelope:** `recommended credit × 1.0 … × 1.5`, rounded to an Indian rupee band, with a
  confidence score built from factor strength, ledger depth, documentation and risk signals.
* **Risk signals:** five rule-based monitors (UPI anomaly, transaction frequency, revenue volatility,
  payer concentration, suspicious patterns) rolled into a weighted index.

> All scores, integrity findings, risk signals and eligibility envelopes are **simulated demo output**
> for a hackathon. They are not credit bureau scores and not lending decisions.

## Design notes

* Deep navy ink on an off-white canvas, emerald as the positive/finance accent, amber reserved for
  warnings — no decorative colour.
* A small design-token layer (`--vp-*`) plus `.st-key-*` hooks restyle Streamlit's own widgets, so
  forms, uploaders, tabs and alerts match the bespoke cards instead of fighting them.
* Inter is **self-hosted** (`static/inter-latin-variable.woff2` via `[[theme.fontFaces]]`) and Material
  Symbols ship inside Streamlit, so the product keeps its typography with no CDN access.
* Motion is deliberately restrained: card lift on hover, ring draw, progress fill, count-up animations
  and a short card entrance — all disabled under `prefers-reduced-motion`.
* Layouts are tuned for a laptop demo and degrade to tablet and mobile through fluid grids,
  Streamlit's column wrapping and container queries at 1200/980/760 px.

## Repository layout

```
main.py                        # the VyaparPulse app (UI + scoring + charts + reports)
vyaparscore_app.py             # earlier VyaparScore prototype, kept for reference
.streamlit/config.toml         # theme tokens, self-hosted font, static serving
static/inter-latin-variable.woff2
requirements.txt
```

Deploying behind a proxy or an iframe preview? Streamlit needs:

```bash
streamlit run main.py --server.enableCORS false --server.enableXsrfProtection false
```
