# 4-kapde

**VyaparScore** — a single-file, offline Streamlit hackathon demo for micro-merchant
credit health, seasonality, bahi-khata OCR (simulated), fraud guard and micro-loans.
All data is synthetic; no external API is called and no money moves.

## Run it

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run main.py --server.address 0.0.0.0
```

Then open http://localhost:8501.

## Navigation

The five sections live in the **sidebar as tabs** (no top tab strip), and only the
selected tab is rendered:

| Tab | Section |
| --- | --- |
| 📊 | Overview & Credit Health |
| 📈 | Seasonality & Cash Flow |
| 📒 | Bahi-Khata OCR |
| 🛡️ | Fraud Guard (badge shows the synthetic review-event count) |
| 💳 | Micro-Loan & Bank Report |

- The sidebar tab list is a real radio group, so ↑/↓ arrow keys switch tabs and the
  active tab keeps a persistent highlighted state.
- The main canvas shows an active-tab header with a `← Previous` / `Next →` pair, so
  tabs can also be stepped through when the sidebar is collapsed on a phone.
- Labels and hints are translated by the Language / भाषा switch.
- Bahi-khata edits are stored outside the widgets, so switching tabs never discards them.

## Notes

`main.py` is intentionally self-contained for a hackathon demo. Scores use an
illustrative profit-margin heuristic, OCR and screenshot scans return fixed mock
responses, and nothing here is financial, lending, legal or tax advice.
