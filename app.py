import os
import io
import pandas as pd
import numpy as np
import streamlit as st

# Optional: use env var or Streamlit secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)

st.set_page_config(page_title="AI KPI Dashboard", page_icon="📊", layout="wide")

@st.cache_data(show_spinner=False)
def load_data(uploaded_file: io.BytesIO | None, path: str | None):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv(path or "data/sample_kpis.csv")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
    return df

def compute_kpis(df: pd.DataFrame) -> dict:
    last30 = df[df["date"] >= (df["date"].max() - pd.Timedelta(days=30))]
    kpis = {}
    kpis["uptime_avg"] = df["uptime_pct"].mean()
    kpis["tickets_resolved_sum"] = last30["tickets_resolved"].sum()
    kpis["tickets_opened_sum"] = last30["tickets_opened"].sum()
    kpis["avg_resolution_hrs"] = df["avg_resolution_hrs"].mean()

    df = df.copy()
    df["month"] = df["date"].dt.to_period("M")
    mo = df.groupby("month")["it_cost_usd"].mean().reset_index()
    if len(mo) >= 2:
        kpis["cost_mom_change"] = (mo.iloc[-1, 1] - mo.iloc[-2, 1]) / mo.iloc[-2, 1] * 100
        kpis["cost_last"] = mo.iloc[-1, 1]
    else:
        kpis["cost_mom_change"] = np.nan
        kpis["cost_last"] = mo.iloc[-1, 1] if len(mo) else np.nan
    return kpis

def kpi_card(label: str, value: float, suffix: str = "", help_text: str = ""):
    col = st.container(border=True)
    with col:
        st.markdown(f"**{label}**")
        st.markdown(
            f"<span style='font-size:28px;font-weight:700'>{value:,.2f}{suffix}</span>",
            unsafe_allow_html=True,
        )
        if help_text:
            st.caption(help_text)

def describe_dataframe(df: pd.DataFrame) -> str:
    lines = []
    lines.append("Columns: " + ", ".join(df.columns))
    if "date" in df.columns:
        lines.append(f"Date coverage: {df['date'].min().date()} to {df['date'].max().date()}")
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            lines.append(f"{c}: mean={df[c].mean():.2f}, min={df[c].min():.2f}, max={df[c].max():.2f}")
    return "\n".join(lines)

def ask_gpt(question: str, df: pd.DataFrame, kpis: dict) -> str:
    if not OPENAI_API_KEY:
        return "Set your OpenAI API key to use the conversational analysis. See README for instructions."
    try:
        # Lazy import so the app runs even if openai isn't installed yet
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        synopsis = describe_dataframe(df)

        system = (
            "You are an analyst assisting an IT manager. "
            "Use the provided KPI synopsis to answer questions about performance in clear, plain English. "
            "Be concise, cite numbers when relevant, and explain trends."
        )

        user = f"""KPI SYNOPSIS
{synopsis}

QUESTION
{question}
"""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            max_tokens=300,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling OpenAI API: {e}"

st.title("📊 AI KPI Dashboard for IT Managers")
st.caption("Conversational business intelligence for IT performance metrics.")

with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Upload CSV (optional)", type=["csv"], help="Must include a 'date' column and numeric KPI columns.")
    st.markdown("Or use the sample dataset bundled with this app.")
    st.divider()
    st.header("Settings")
    st.text_input("OpenAI API Key", type="password", key="api_key_input", help="Leave blank to rely on environment or secrets.")
    if st.session_state.get("api_key_input"):
        os.environ["OPENAI_API_KEY"] = st.session_state["api_key_input"]

df = load_data(uploaded, "data/sample_kpis.csv")
kpis = compute_kpis(df)

# KPI row
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Avg Uptime", kpis["uptime_avg"], suffix="%")
with c2:
    kpi_card("Tickets Resolved (30d)", kpis["tickets_resolved_sum"], help_text="Total in the last 30 days")
with c3:
    kpi_card("Avg Resolution Time", kpis["avg_resolution_hrs"], suffix=" hrs")
with c4:
    mom = kpis["cost_mom_change"]
    if pd.notna(mom):
        kpi_card("IT Cost (MoM)", mom, suffix=" %", help_text=f"Last month avg: ${kpis['cost_last']:,.0f}")
    else:
        kpi_card("IT Cost (MoM)", np.nan, suffix=" %", help_text="Need at least 2 months of data")

st.subheader("Trends")
t1, t2 = st.columns(2)
with t1:
    st.line_chart(df.set_index("date")[["tickets_opened", "tickets_resolved"]])
with t2:
    st.line_chart(df.set_index("date")[["it_cost_usd", "avg_resolution_hrs"]])

st.subheader("Ask the data")
q = st.text_input("Ask a question (e.g., 'What's our average resolution time over the last month?')")
if st.button("Analyze with GPT"):
    if q.strip():
        with st.spinner("Thinking..."):
            answer = ask_gpt(q, df, kpis)
        st.markdown("**Answer:**")
        st.write(answer)
    else:
        st.info("Type a question first.")

st.divider()
st.caption("Tip: Upload your own CSV to replace the sample data. Ensure a 'date' column (YYYY-MM-DD).")
