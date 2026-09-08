# 🚆 Railway Imprest Bill Automator

A Streamlit web app that automates generating the two monthly imprest-account
Word documents for **SETTIHALLI Station** (Indian Railways):

| Document | What it is |
|---|---|
| **Annexure I** | Master Bill — recoupment, balances, voucher summary, G.I. Ledger, certification |
| **Annexure II** | Labour Annexure — attendance & wage register for two cleaning workers |

Instead of manually filling Word templates every month, you enter the month,
expenses, vouchers, and worker attendance in a browser UI, and the app fills
the existing `.docx` templates and hands you both files to download.

---

## ✨ Features

- **Two voucher modes** — 3-voucher (single consumable bill) or 4-voucher
  (with/without stationery), each mapped to its own dedicated template.
- **Auto-carried opening balance** — after generating a month's documents,
  its closing balance is saved to a local file. The next month's Opening
  Balance field auto-fills from it (still editable).
- **Per-month input memory** — amounts, dates, and worked-days entered for
  one month never bleed into another; switching months shows that month's
  own saved values, or a clean default if untouched.
- **Stale-document protection** — changing any input after generating
  automatically clears the previous downloads, so you can never accidentally
  hand out an out-of-date document.
- **Template sanity check** — before generating, each template is scanned
  for the tables/text the fill logic expects, surfacing a specific warning
  if a template was edited and no longer matches.
- **Negative-balance / leave-overlap guard** — the Generate button is
  disabled if the closing balance would go negative or the two workers'
  leave days overlap.
- **Randomized, no-overlap leave assignment** for the Labour Annexure.

---

## 📁 Project structure

```
railway_imprest/
├── app.py                     # entrypoint — wires everything together
├── config.py                  # MONTHS, SANCTIONED_AMOUNT, DAILY_WAGE, template paths
├── requirements.txt
├── App.bat                    # Windows one-click launcher
├── imprest_balances.ini       # auto-generated at runtime — do not hand-edit
│
├── templates/                 # your 5 fixed .docx templates go here
│   ├── ANNEXURE 1 WITH 3 VOUCHERS.docx
│   ├── ANNEXURE 1 WITH 4 VOUCHERS With Stationery.docx
│   ├── ANNEXURE 1 WITH 4 VOUCHERS Without Stationery.docx
│   ├── ANNEXTURE II LABOUR 3 VOUCHERS.docx
│   └── ANNEXTURE II LABOUR 4 VOUCHERS.docx
│
├── core/
│   ├── dates.py                # get_days_in_month()
│   ├── num_to_words.py         # number → Indian-English words (lakh/thousand)
│   ├── state.py                 # shared session-state default-init helper
│   ├── validation.py            # template anchor-text sanity checks
│   └── balance_store.py         # month-to-month closing-balance persistence (INI)
│
├── docx_engine/
│   ├── xml_helpers.py           # raw OOXML run/cell formatting helpers
│   ├── annexure1.py              # generate_annexure_1()
│   └── labour.py                 # generate_labour_annexure()
│
└── ui/
    ├── styles.py                 # global CSS (inject_css())
    ├── sidebar.py                 # month/year selector
    ├── tab_expenses.py            # Tab 1 — Consumables
    ├── tab_labour.py              # Tab 2 — Labour
    └── tab_generate.py            # Tab 3 — balances, generate, download
```

Each module has one job — `core/` is pure logic with zero Streamlit
dependency (testable on its own), `docx_engine/` builds the actual Word
files, and `ui/` is the only layer that touches Streamlit.

---

## 🚀 Setup

### 1. Add your templates

Place your 5 real Word templates in `templates/`, with these **exact**
filenames (note: `ANNEXTURE`, not `ANNEXURE`, for the two labour files —
kept as-is to match the original naming):

```
templates/
├── ANNEXURE 1 WITH 3 VOUCHERS.docx
├── ANNEXURE 1 WITH 4 VOUCHERS With Stationery.docx
├── ANNEXURE 1 WITH 4 VOUCHERS Without Stationery.docx
├── ANNEXTURE II LABOUR 3 VOUCHERS.docx
└── ANNEXTURE II LABOUR 4 VOUCHERS.docx
```

> Templates are **not** included in this repo — they're specific to your
> station's official format and should be added locally.

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run

**Windows — one click:**
Double-click `App.bat`. It checks the app files and all 5 templates are
present, installs missing dependencies if needed, then launches the app.

**Manual (any OS):**
```bash
streamlit run app.py
```
Run this from *inside* the `railway_imprest/` folder — internal module
imports and the `templates/`/`imprest_balances.ini` paths are relative
to it.

The app opens at **http://localhost:8501**.

---

## 🗂️ How month-to-month balances work

`core/balance_store.py` writes a plain INI file (`imprest_balances.ini`)
with one section per month:

```ini
[2026-JULY]
closing_balance = 18450
```

Every time documents are generated for a month, its closing balance is
saved. When you open the **Generate & Download** tab for the *next* month,
the Opening Balance field auto-fills from that stored value — no manual
copy-paste required.

> ⚠️ **This file lives on whatever machine runs the app.** It's server-local
> state, not tied to your browser or login. If you deploy somewhere with an
> ephemeral filesystem (some free-tier hosts wipe disk on every redeploy),
> this file — and the balance history — gets wiped too.

---

## 🧯 Troubleshooting

| Symptom | Likely cause |
|---|---|
| `ModuleNotFoundError: No module named 'ui'` (or `core`/`docx_engine`) | You launched Streamlit from the wrong folder — `cd` into `railway_imprest/` first. |
| `❌ Template check failed: ... is missing expected text` | The anchor list in `core/validation.py` doesn't match your real template's exact wording — this is only a warning, generation still attempts to proceed. |
| `❌ Annexure I / Labour Annexure generation failed` | Check the **Details:** line shown under the error — it has the exact Python exception. Common causes: a template's table/paragraph structure differs from what the fill logic expects. |
| Sidebar won't reopen after collapsing | Already fixed — see `ui/styles.py`, the `[data-testid="collapsedControl"]` rule keeps the reopen button visible. |
| A generated document looks stale after changing inputs | Shouldn't happen — Tab 3 clears previous downloads automatically when inputs change (`generated_signature` check). If you see this, please report it. |

---

## ⚙️ Configuration

Edit `config.py` directly for:
- `SANCTIONED_AMOUNT` — monthly imprest ceiling (currently ₹25,000)
- `DAILY_WAGE` — per-day wage for both cleaning workers (currently ₹380)
- `TEMPLATES` — file paths, if you ever rename your template files

This app is built for a **single station** (SETTIHALLI) with these
constants hardcoded rather than exposed in the UI — edit them here if
either value changes.

---

## 📄 License / Notes

- Built for internal station use — not a general-purpose imprest tool.
- Station-specific static text (station name, division, officer name,
  contact numbers, ATM card number) lives directly in the `.docx`
  templates themselves and is left untouched by the generator — only
  month-to-month variable data (dates, amounts, voucher details) is filled
  in programmatically.

---

## Suggested `.gitignore`

```
venv/
__pycache__/
*.pyc
imprest_balances.ini
templates/*.docx
```
