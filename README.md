# AI KPI Dashboard — Conversational BI for IT Managers

A minimal, portfolio-ready Streamlit app that shows IT KPIs (uptime, tickets, cost trends) and lets you ask natural-language questions powered by GPT.

**Tech stack:** Python, Streamlit, Pandas, OpenAI API

## ✨ Features
- KPI cards (uptime, tickets, resolution time, cost MoM)
- Trend charts (tickets opened/resolved, cost vs. resolution hours)
- Upload your own CSV (must include a `date` column)
- Ask questions like “What’s our average resolution time?” — GPT answers in plain English

## 🚀 Quickstart

```bash
# 1) Clone and enter
git clone https://github.com/your-username/ai-kpi-dashboard.git
cd ai-kpi-dashboard

# 2) Create a virtual env (optional, but recommended)
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3) Install
pip install -r requirements.txt

# 4) Set your OpenAI key (one-time per shell) 
export OPENAI_API_KEY=sk-...    # Windows PowerShell: $env:OPENAI_API_KEY="sk-..."

# 5) Run
streamlit run app.py
```

Then open the local URL shown by Streamlit.

### Using Streamlit Community Cloud (free deploy)
1. Push this repo to GitHub.
2. Go to Streamlit Community Cloud → New app → select repo/branch → `app.py`.
3. In **Secrets**, add:
   ```toml
   OPENAI_API_KEY="sk-..."
   ```
4. Deploy.

### Using Render/Railway
- Create a web service with `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
- Set `PORT` env var and `OPENAI_API_KEY` in the dashboard.
- Use the generated URL in your portfolio.

## 🧱 Data format
- CSV with columns like:
  - `date` (YYYY-MM-DD)
  - `uptime_pct` (0–100)
  - `tickets_opened`, `tickets_resolved` (ints)
  - `avg_resolution_hrs` (float)
  - `it_cost_usd` (float)

A sample dataset lives at `data/sample_kpis.csv`.

## 🧠 How GPT is used
We synthesize a compact KPI synopsis (means, ranges, coverage) and pass your question + synopsis to the OpenAI API (model: `gpt-4o-mini` by default). You can switch models in `app.py`.

## 📁 Repo structure
```
ai-kpi-dashboard/
├─ app.py
├─ data/
│  └─ sample_kpis.csv
├─ requirements.txt
├─ README.md
└─ .gitignore
```

## 🛡️ Security
- Your key is read from environment or Streamlit Secrets. Never hard-code it in the repo.
- For team use, prefer Secrets in deploy providers.

## 📜 License
MIT