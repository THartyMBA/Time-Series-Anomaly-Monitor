# Time-Series-Anomaly-Monitor

🚨 Time-Series Anomaly Monitor
A Streamlit proof-of-concept that detects outliers in your time-series data using STL decomposition or Prophet forecasts, and optionally emails you an alert.

💡 What it does
Upload a CSV with one date column and one numeric column.

Choose a residual method:

STL decomposition (fast)

Prophet forecast (slower)

Specify a z-score threshold (e.g. |z| > 3) to flag anomalies.

View an interactive Plotly chart with outliers marked in red.

Inspect and download the table of anomalies.

(Optional) Send yourself an email alert listing anomalies via Gmail.

Demo only—no streaming ingestion, SLA monitoring, or enterprise alerting.
For production-grade monitoring pipelines, contact me → drtomharty.com/bio

✨ Key Features
Dual methods: STL or Prophet residuals

Interactive visualization: Plotly line chart with anomaly markers

Parametric control: Frequency, period, and z-score threshold sliders

Downloadable results: CSV export of detected anomalies

Email alerts: (Gmail + App Password) triggered from the app

🔑 Email Alert Setup (Optional)
To enable the “📧 Email me the anomaly list” feature, you’ll need a Gmail App Password:

Create a Gmail account (or use an existing one).

Generate an App Password under Google Account → Security → App passwords.

Add these secrets to Streamlit Cloud Secrets (or ~/.streamlit/secrets.toml locally):

toml
Copy
Edit
MONITOR_EMAIL_USER = "yourgmail@gmail.com"
MONITOR_EMAIL_PWD  = "16-character-app-password"
If these aren’t set or yagmail isn’t installed, the email UI will show a helpful error.

🛠️ Requirements
bash
Copy
Edit
streamlit>=1.32
pandas
numpy
plotly
statsmodels
prophet
yagmail      # optional for email alerts
🚀 Quick Start (Local)
bash
Copy
Edit
git clone https://github.com/THartyMBA/time-series-anomaly-monitor.git
cd time-series-anomaly-monitor
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run anomaly_monitor_app.py
Open http://localhost:8501 to upload your data and detect anomalies.

☁️ Deploy on Streamlit Cloud (Free)
Push this folder to GitHub under THartyMBA.

Go to streamlit.io/cloud ➜ New app and select your repo/branch.

(Optional) Add MONITOR_EMAIL_USER and MONITOR_EMAIL_PWD to Secrets.

Click Deploy.

🗂️ Repo Structure
vbnet
Copy
Edit
anomaly_monitor_app.py    ← single-file Streamlit app
requirements.txt
README.md                 ← you’re reading it
📜 License
CC0 1.0 – public-domain dedication. Attribution appreciated but not required.

🙏 Acknowledgements
Streamlit – rapid Python UIs

statsmodels STL – robust seasonal decomposition

Prophet – time-series forecasting

Plotly – interactive charts

yagmail – simple Gmail alerts

Flag anomalies, send alerts, and keep your data in check! 🚀
