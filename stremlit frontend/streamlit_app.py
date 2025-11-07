# streamlit_app.py — top imports
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
import os
from io import BytesIO
from typing import Optional, Dict
import xlsxwriter


# optional for PDF export (install reportlab if you want PDF)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# --------------- CONFIG ---------------
# --- Backend API endpoint (deployed) ---
BACKEND_URL = os.getenv("BACKEND_URL", "https://balance-sheet-analyst.onrender.com")

# --------------------------------------

# --------------------------------------

st.set_page_config(page_title="Balance Sheet Analyst (Streamlit)", layout="wide")

# ---------- Helpers ----------
def api_post(path: str, json=None, params=None):
    url = BACKEND_URL.rstrip("/") + path
    try:
        r = requests.post(url, json=json, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Request error: {e}")
        return None


def api_call(path: str, method="GET", params=None, json=None):
    """Generic API caller that supports GET and POST."""
    url = BACKEND_URL.rstrip("/") + path
    try:
        if method.upper() == "POST":
            r = requests.post(url, params=params, json=json, timeout=60)
        else:
            r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {e}")
        return None

def login_backend(email: str, password: str) -> Optional[Dict]:
    payload = {"email": email, "password": password}
    return api_post("/login", json=payload)

def fetch_balance_sheet(token: str, company: str | None = None):
    params = {"token": token}
    if company:
        params["company"] = company
    return api_call("/balance-sheet", params=params)


def call_analyze(token: str, question: str):
    return api_post("/analyze", json={"question": question}, params={"token": token})

# ---------- Session State ----------
if "user" not in st.session_state:
    st.session_state.user = None
if "token" not in st.session_state:
    st.session_state.token = None
if "balance" not in st.session_state:
    st.session_state.balance = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "companies" not in st.session_state:
    st.session_state.companies = []
if "selected_company" not in st.session_state:
    st.session_state.selected_company = None

# ---------- UI ----------
st.title("Balance Sheet Analyst — Streamlit UI")

# left column: login / user info
left, right = st.columns([1, 3])

with left:
    st.subheader("User")
    if not st.session_state.user:
        # prefilled demo user for speed
        email = st.text_input("Email", value="analyst@company.com")
        pwd = st.text_input("Password", value="analyst123", type="password")
        if st.button("Log in"):
            res = login_backend(email, pwd)
            if res:
                # backend returns { name, role, token, companies }
                st.session_state.user = {
                    "name": res.get("name", "Analyst"),
                    "role": res.get("role", "analyst"),
                }
                st.session_state.token = res.get("token") or email
                st.session_state.companies = res.get("companies", ["Reliance"])
                # default selected company
                st.session_state.selected_company = st.session_state.companies[0] if st.session_state.companies else None
                st.success(f"Logged in as {st.session_state.user['name']}")
                # fetch balance sheet immediately for selected company
                bs = fetch_balance_sheet(st.session_state.token, st.session_state.selected_company)
                if bs:
                    if isinstance(bs, dict) and "data" in bs and "figures_crore" in bs["data"]:
                        st.session_state.balance = bs["data"]["figures_crore"]
                        st.session_state.company = bs.get("company") or bs["data"].get("company")
                    elif isinstance(bs, dict) and "figures_crore" in bs:
                        st.session_state.balance = bs["figures_crore"]
                        st.session_state.company = bs.get("company")
                    else:
                        st.session_state.balance = bs
                        st.session_state.company = bs.get("company", "Company")
                else:
                    st.warning("Failed to fetch balance-sheet after login.")
    else:
        st.write(f"**{st.session_state.user['name']}**")
        st.write(f"Role: {st.session_state.user['role']}")
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.token = None
            st.session_state.balance = None
            st.session_state.chat_history = []
            st.experimental_rerun()

with right:
    if not st.session_state.user:
        st.info("Please login with the demo credentials (analyst@company.com / analyst123).")
        st.write("After login the app will fetch the Reliance balance sheet and show charts + chat.")
        st.stop()
        # Company selector (if user has multiple companies)
    if st.session_state.companies:
        sel = st.selectbox("Select company", st.session_state.companies, index=0)
        if sel != st.session_state.selected_company:
            st.session_state.selected_company = sel
            # fetch new company data
            bs = fetch_balance_sheet(st.session_state.token, st.session_state.selected_company)
            if bs:
                if isinstance(bs, dict) and "data" in bs and "figures_crore" in bs["data"]:
                    st.session_state.balance = bs["data"]["figures_crore"]
                    st.session_state.company = bs.get("company") or bs["data"].get("company")
                elif isinstance(bs, dict) and "figures_crore" in bs:
                    st.session_state.balance = bs["figures_crore"]
                    st.session_state.company = bs.get("company")
                else:
                    st.session_state.balance = bs
                    st.session_state.company = bs.get("company", "Company")

    # User is logged in, show company + KPIs
    st.subheader("Company Overview")
    balance = st.session_state.balance
    if not balance:
        st.info("Fetching balance-sheet data...")
        bs = fetch_balance_sheet(st.session_state.token)
        if bs:
            if isinstance(bs, dict) and "data" in bs and "figures_crore" in bs["data"]:
                st.session_state.balance = bs["data"]["figures_crore"]
                st.session_state.company = bs.get("company") or bs["data"].get("company")
            elif isinstance(bs, dict) and "figures_crore" in bs:
                st.session_state.balance = bs["figures_crore"]
                st.session_state.company = bs.get("company")
            else:
                st.session_state.balance = bs
                st.session_state.company = bs.get("company", "Company")
        balance = st.session_state.balance

    # show cards
    cols = st.columns(4)
    if balance:
                # ensure numeric
        def n(v):
            try:
                return float(v)
            except:
                return None

        assets = n(balance.get("total_assets"))
        liabilities = n(balance.get("total_liabilities"))
        equity = n(balance.get("total_equity"))
        revenue = n(balance.get("revenue_from_operations") or balance.get("Revenue") or balance.get("Revenue from Operations"))
        profit = n(balance.get("profit_for_the_year"))
        cash = n(balance.get("cash_and_cash_equivalents"))
        inventories = n(balance.get("inventories"))

        # Ratios
        profit_margin = (profit / revenue * 100) if profit and revenue else None
        debt_to_equity = (liabilities / equity) if liabilities and equity else None
        current_ratio = (assets / liabilities) if assets and liabilities else None

        cols = st.columns(4)
        cols[0].metric("Total Assets (₹ crore)", f"{assets:,.0f}" if assets else "—")
        cols[1].metric("Revenue (₹ crore)", f"{revenue:,.0f}" if revenue else "—")
        cols[2].metric("Net Profit (₹ crore)", f"{profit:,.0f}" if profit else "—")
        cols[3].metric("Cash (₹ crore)", f"{cash:,.0f}" if cash else "—")

        # Ratios display
        r1, r2, r3 = st.columns(3)
        r1.metric("Profit Margin (%)", f"{profit_margin:.2f}%" if profit_margin else "—")
        r2.metric("Debt-to-Equity", f"{debt_to_equity:.2f}" if debt_to_equity else "—")
        r3.metric("Assets/Liabilities", f"{current_ratio:.2f}" if current_ratio else "—")

        st.markdown("---")
        st.subheader(f"{st.session_state.company or 'Company'} — Financial snapshot")

        # prepare dataframe for bars & downloads
        chart_df = pd.DataFrame({
            "metric": ["Assets", "Liabilities", "Equity", "Revenue", "Profit"],
            "value": [
                assets or 0,
                liabilities or 0,
                equity or 0,
                revenue or 0,
                profit or 0
            ]
        })

        # Download buttons: CSV and Excel
        csv_bytes = chart_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV (metrics)", csv_bytes, file_name=f"{st.session_state.selected_company}_metrics.csv", mime="text/csv")
        # Excel
        towrite = BytesIO()
        with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
            chart_df.to_excel(writer, index=False, sheet_name="summary")
            writer.close()
        towrite.seek(0)
        st.download_button("📥 Download Excel (metrics)", towrite, file_name=f"{st.session_state.selected_company}_metrics.xlsx", mime="application/vnd.ms-excel")

        # Optional PDF report (simple) — requires reportlab installed
        if REPORTLAB_AVAILABLE:
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=letter)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(72, 720, f"{st.session_state.company or 'Company'} — Balance Sheet Summary")
            c.setFont("Helvetica", 10)
            y = 700
            for k, v in chart_df.values:
                c.drawString(72, y, f"{k}: ₹{v:,.0f}")
                y -= 18
            c.showPage()
            c.save()
            pdf_buffer.seek(0)
            st.download_button("📥 Download PDF summary", pdf_buffer, file_name=f"{st.session_state.selected_company}_summary.pdf", mime="application/pdf")

    
    
import pandas as pd
import plotly.express as px

# inside main_app() after login and data fetch
if st.session_state.get("token"):
    bs_data = api_call("/balance-sheet", params={"token": st.session_state.token})
    if bs_data:
        data = bs_data["data"]["figures_crore"]
        st.subheader(f"📊 {bs_data['company']} Balance Sheet Overview")

        df = pd.DataFrame(data.items(), columns=["Metric", "Value (₹ Crore)"])
        st.dataframe(df, use_container_width=True)

        # Visualize key indicators
        metrics = {
            "Total Assets": data["total_assets"],
            "Total Liabilities": data["total_liabilities"],
            "Total Equity": data["total_equity"],
            "Profit for the Year": data["profit_for_the_year"],
        }

        cols = st.columns(len(metrics))
        for i, (label, value) in enumerate(metrics.items()):
            cols[i].metric(label, f"₹{value:,}")

        st.markdown("### 💹 Financial Breakdown")
        fig = px.bar(df, x="Metric", y="Value (₹ Crore)",
                     color="Value (₹ Crore)", text="Value (₹ Crore)",
                     title="Company Financial Summary")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Balance-sheet data not available.")
        st.markdown("---")
        st.subheader("Trend Analysis (upload past balance sheets)")
        st.info("Upload multiple JSON files (each containing figures_crore) or a CSV with columns: year, revenue, profit, assets, liabilities, equity")

        uploaded = st.file_uploader("Upload JSON/CSV files (multiple)", accept_multiple_files=True, type=['json','csv'])
        trend_df = None
        if uploaded:
            rows = []
            for f in uploaded:
                name = f.name
                if f.name.lower().endswith(".json"):
                    obj = json.load(f)
                    # try to find figures_crore
                    if "figures_crore" in obj:
                        fr = obj["figures_crore"]
                    elif "data" in obj and "figures_crore" in obj["data"]:
                        fr = obj["data"]["figures_crore"]
                    else:
                        fr = obj
                    year = obj.get("fiscal_year_end") or obj.get("year") or name.replace(".json","")
                    rows.append({
                        "year": year,
                        "revenue": fr.get("revenue_from_operations"),
                        "profit": fr.get("profit_for_the_year"),
                        "assets": fr.get("total_assets"),
                        "liabilities": fr.get("total_liabilities"),
                        "equity": fr.get("total_equity")
                    })
                else:
                    df = pd.read_csv(f)
                    # user-supplied CSV must have columns year,revenue,profit,assets,liabilities,equity
                    rows.extend(df.to_dict(orient="records"))
            if rows:
                trend_df = pd.DataFrame(rows)
                # ensure numeric
                for col in ["revenue","profit","assets","liabilities","equity"]:
                    if col in trend_df.columns:
                        trend_df[col] = pd.to_numeric(trend_df[col], errors='coerce')
                trend_df = trend_df.sort_values("year")
                st.dataframe(trend_df)
                # plot revenue trend
                if "revenue" in trend_df.columns:
                    fig_tr = px.line(trend_df, x="year", y="revenue", markers=True, title="Revenue Trend")
                    st.plotly_chart(fig_tr, use_container_width=True)
                if "profit" in trend_df.columns:
                    fig_tr2 = px.line(trend_df, x="year", y="profit", markers=True, title="Profit Trend")
                    st.plotly_chart(fig_tr2, use_container_width=True)


# Chat / Analyst assistant
st.markdown("---")
# ---- Chatbot section ----
st.divider()
st.markdown("### 💬 Ask the Analyst (LLM)")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

question = st.text_input("Type a question about company performance (e.g. 'How was revenue growth?')")

if st.button("Ask"):
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        with st.spinner("Querying analyst model (with RAG)..."):
            ans = call_analyze(st.session_state.token, question)
            if ans:
                answer_text = ans.get("answer") or str(ans)
                retrieved = ans.get("retrieved", [])
                st.session_state.chat_history.append({
                    "q": question,
                    "a": answer_text,
                    "retrieved": retrieved
                })

                # 💬 Latest Response
                st.markdown("### 💬 Latest Response")
                st.markdown(f"**Q:** {question}")
                st.success(f"💡 {answer_text}")

                # 📘 Show RAG insights if available
                if retrieved:
                    # Filter out garbage / single-character fragments
                    cleaned = [
                        chunk.strip().replace("\n", " ").replace("  ", " ")
                        for chunk in retrieved
                        if chunk and len(chunk.strip()) > 30  # only meaningful text
                    ]

                    if cleaned:
                        st.markdown("### 📘 Insights used from Annual Report")
                        for i, chunk in enumerate(cleaned, start=1):
                            st.markdown(f"**Excerpt {i}:** {chunk[:500]}{'...' if len(chunk) > 500 else ''}")



                # Save chat persistently
                try:
                    chat_file = f"chats_{st.session_state.token.replace('@','_at_')}.json"
                    existing = []
                    if os.path.exists(chat_file):
                        with open(chat_file, "r", encoding="utf-8") as fh:
                            existing = json.load(fh)
                    existing.append({
                        "q": question,
                        "a": answer_text,
                        "retrieved": retrieved
                    })
                    with open(chat_file, "w", encoding="utf-8") as fh:
                        json.dump(existing, fh, ensure_ascii=False, indent=2)
                except Exception as e:
                    st.warning(f"Could not persist chat: {e}")
            else:
                st.error("No response from /analyze endpoint. Check backend logs.")


# ---------- Chat display: show latest Q&A + dropdown for previous ----------
st.markdown("---")

# Dropdown of PREVIOUS questions only (exclude latest)
prev_entries = [
    e for e in st.session_state.chat_history[:-1]
    if isinstance(e, dict) and "q" in e and "a" in e
]

if prev_entries:
    st.markdown("### 📜 Previous questions")
    prev_qs = [e["q"] for e in prev_entries]
    selected = st.selectbox("Select a previous question to view its answer:", ["-- choose --"] + prev_qs)

    if selected != "-- choose --":
        sel = next((e for e in prev_entries if e["q"] == selected), None)
        if sel:
            st.markdown(f"**Q:** {sel['q']}")
            st.info(f"💡 {sel['a']}")
