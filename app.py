# anomaly_monitor_app.py
"""
Time-Series Anomaly Monitor  📈🚨
────────────────────────────────────────────────────────────────────────────
POC workflow

1. Upload a CSV that has **one date column** and **one numeric column**.  
2. The app runs **STL decomposition** + optional Prophet forecast to compute
   residuals.  
3. Data points whose residual z-score > threshold are flagged as anomalies.  
4. An interactive chart highlights anomalies; a table lists them.  
5. Optionally send yourself an **email alert** (Gmail) with the anomaly list.

Demo-level only — for production monitoring pipelines (streaming ingestion,
Airflow/Pandora scheduling, Grafana alerting), contact me → drtomharty.com/bio
"""
# ───────────────────────────────────────── imports ────────────────────────
import os, io
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from statsmodels.tsa.seasonal import STL
from prophet import Prophet

# optional email (Gmail only, POC)
try:
    import yagmail
    HAS_YAG = True
except ImportError:
    HAS_YAG = False

# ─────────────────────────────── helpers ──────────────────────────────────
def stl_residuals(series, period):
    """Return STL residuals given a pandas Series indexed by DatetimeIndex."""
    stl = STL(series, period=period, robust=True)
    res = stl.fit()
    return res.resid

def prophet_forecast(df, date_col, val_col, periods, freq):
    tmp = df[[date_col, val_col]].rename(columns={date_col:"ds", val_col:"y"})
    tmp["ds"] = pd.to_datetime(tmp["ds"], errors="coerce")
    m = Prophet()
    m.fit(tmp)
    future = m.make_future_dataframe(periods=periods, freq=freq)
    fc = m.predict(future)[["ds","yhat"]]
    fc = fc.set_index("ds")["yhat"]
    fc = fc.loc[tmp["ds"].min():tmp["ds"].max()]  # align to history range only
    return tmp.set_index("ds")["y"] - fc  # residuals

def zscore(series):
    return (series - series.mean()) / series.std(ddof=0)

def send_email(anomaly_df, to_email):
    sender = os.getenv("MONITOR_EMAIL_USER")
    pw     = os.getenv("MONITOR_EMAIL_PWD")
    if not (sender and pw):
        st.error("Set MONITOR_EMAIL_USER and MONITOR_EMAIL_PWD env vars for email.")
        return False
    if not HAS_YAG:
        st.error("Install `yagmail` to enable emailing.")
        return False
    yag = yagmail.SMTP(user=sender, password=pw)
    body = "Anomalies detected:\n\n" + anomaly_df.to_csv(index=False)
    yag.send(to=to_email, subject="Time-Series Anomaly Alert", contents=body)
    return True

# ─────────────────────────────── UI  ──────────────────────────────────────
st.set_page_config(page_title="Time-Series Anomaly Monitor", layout="wide")
st.title("🚨 Time-Series Anomaly Monitor")

st.info(
    "🔔 **Demo Notice**  \n"
    "This is a lightweight POC. For enterprise-grade alerting (streaming, SLA, SSO), "
    "[contact me](https://drtomharty.com/bio).",
    icon="💡"
)

csv_file = st.file_uploader("📂 Upload CSV (date + numeric column)", type="csv")
if not csv_file:
    st.stop()

df = pd.read_csv(csv_file)
st.subheader("Preview")
st.dataframe(df.head())

date_col = st.selectbox("Date column", df.columns)
val_col  = st.selectbox("Value column", df.select_dtypes(include="number").columns)
freq     = st.selectbox("Frequency", ["D","W","M","H"], index=0)
period_guess = {"D":7, "W":52, "M":12, "H":24}[freq]

method   = st.radio("Residual method", ["STL (fast)","Prophet (slower)"], index=0)
z_thresh = st.slider("Anomaly threshold (|z| >)", 2.0, 5.0, 3.0, 0.2)

if st.button("🚀 Detect anomalies"):
    ts = df.copy()
    ts[date_col] = pd.to_datetime(ts[date_col], errors="coerce")
    ts = ts.dropna(subset=[date_col, val_col]).set_index(date_col).sort_index()

    if method.startswith("STL"):
        resid = stl_residuals(ts[val_col], period_guess)
    else:
        with st.spinner("Running Prophet…"):
            resid = prophet_forecast(ts.reset_index(), date_col, val_col, 0, freq)

    ts["resid"] = resid
    ts["z"]     = zscore(resid)
    ts["anomaly"] = ts["z"].abs() > z_thresh

    # ─── Chart ──────────────────────────────────────────
    fig = px.line(ts, x=ts.index, y=val_col, title="Time-Series with Anomalies")
    fig.add_scatter(x=ts[ts.anomaly].index,
                    y=ts[ts.anomaly][val_col],
                    mode="markers", marker=dict(size=8, color="red"),
                    name="Anomaly")
    st.plotly_chart(fig, use_container_width=True)

    # ─── Table & downloads ─────────────────────────────
    anomalies = ts[ts.anomaly].reset_index().rename(columns={date_col:"timestamp"})
    st.subheader(f"Anomalies detected: {anomalies.shape[0]}")
    st.dataframe(anomalies)

    st.download_button("⬇️ Download anomalies CSV",
                       data=anomalies.to_csv(index=False).encode(),
                       file_name="anomalies.csv",
                       mime="text/csv")

    # ─── Optional email alert ──────────────────────────
    with st.expander("📧 Email me the anomaly list"):
        to_email = st.text_input("Recipient email (Gmail recommended)")
        if st.button("Send email"):
            if send_email(anomalies, to_email):
                st.success("Email sent!")
