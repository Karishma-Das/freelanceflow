import os, tempfile
import pandas as pd
import streamlit as st

from src.pipeline import process_file
from src.validate import validate
from src.flags import unusual_spending
from src.forecast import monthly_totals, forecast_next

st.set_page_config(page_title="FreelanceFlow", layout="wide")
st.title("FreelanceFlow")
st.caption("Documents are read locally on your computer by an open-source model. "
           "This is not tax or accounting advice.")

COLS = ["filename", "date", "party", "amount", "currency", "category", "direction",
        "needs_review", "reasons"]

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=COLS)


def add_review_columns(df):
    df = df.astype(object).where(df.notna(), None)
    checks = [validate(r) for r in df.to_dict("records")]
    df["needs_review"] = [c["needs_review"] for c in checks]
    df["reasons"] = ["; ".join(c["reasons"]) for c in checks]
    return df


# ---------- Sidebar: get data in ----------
with st.sidebar:
    st.header("1. Add documents")
    files = st.file_uploader("PNG, JPG or PDF", type=["png", "jpg", "jpeg", "pdf"],
                             accept_multiple_files=True)
    if st.button("Process uploaded files") and files:
        rows = []
        bar = st.progress(0.0)
        for i, f in enumerate(files):
            with tempfile.TemporaryDirectory() as tmp:
                path = os.path.join(tmp, f.name)
                with open(path, "wb") as out:
                    out.write(f.getbuffer())
                try:
                    for name, rec in process_file(path):
                        d = rec.model_dump()
                        d["filename"] = name
                        rows.append(d)
                except Exception as e:
                    rows.append({"filename": f.name, "reasons": f"could not read: {str(e)[:80]}",
                                 "needs_review": True})
            bar.progress((i + 1) / len(files))
        if rows:
            new = add_review_columns(pd.DataFrame(rows))
            st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)
        st.success("Done")
        st.caption("Each receipt takes about 3 minutes on a laptop CPU.")

    st.header("Or load saved results")
    if st.button("Load data/real/results.csv"):
        path = "data/real/results.csv"
        if os.path.exists(path):
            saved = pd.read_csv(path)
            st.session_state.df = add_review_columns(saved)
        else:
            st.error("results.csv not found. Run python run_real.py first.")

df = st.session_state.df

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["Records", "Forecast", "Alerts"])

with tab1:
    if df.empty:
        st.info("Upload files or load saved results from the sidebar.")
    else:
        flagged = int(df["needs_review"].fillna(False).astype(bool).sum())
        st.write(f"{len(df)} records, {flagged} need review.")
        show = [c for c in COLS if c in df.columns]
        edited = st.data_editor(df[show], width="stretch", num_rows="dynamic")
        st.session_state.df = edited.reindex(columns=df.columns)
        st.download_button("Download CSV", edited.to_csv(index=False).encode("utf-8"),
                           file_name="freelanceflow_records.csv", mime="text/csv")

with tab2:
    st.subheader("Forecast")
    st.caption("Uses TabPFN if its license is set up on this computer, otherwise a 3-month average.")
    source = st.radio("Data source", ["Demo history (synthetic)", "My records"], horizontal=True)
    if source == "Demo history (synthetic)":
        if os.path.exists("data/sample/history.csv"):
            hist = pd.read_csv("data/sample/history.csv")
        else:
            hist = pd.DataFrame()
            st.error("Run python make_history.py first.")
    else:
        hist = monthly_totals(df) if not df.empty else pd.DataFrame()

    if hist.empty or len(hist) < 3:
        st.warning("Need at least 3 months of data to forecast.")
    else:
        st.line_chart(hist.set_index("month")[["income", "expense"]])
        months = hist["month"].tolist()
        for col in ["income", "expense"]:
            if st.button(f"Forecast next month {col}", key=col):
                with st.spinner("Forecasting..."):
                    p, low, high, method, warn = forecast_next(hist[col].tolist(), months)
                st.write(f"**{col.title()}:** about {p:,.0f} "
                         f"(likely between {low:,.0f} and {high:,.0f}). Method: {method}.")
                if warn:
                    st.warning(warn)

with tab3:
    st.subheader("Unusual spending")
    if df.empty:
        st.info("No records yet.")
    else:
        u = unusual_spending(df)
        if u.empty:
            st.write("Nothing unusual found (needs at least 3 expenses per category).")
        else:
            st.dataframe(u, width="stretch")
    st.subheader("Late payers")
    st.write("Not built yet. This is a planned next step.")