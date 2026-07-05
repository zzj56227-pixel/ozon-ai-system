import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ozon AI选品云系统", layout="wide")

st.title("🧠 Ozon AI选品系统（云端版）")

def score(row):
    score = 0

    sales = row.get("sales", 0)
    price = row.get("price", 0)
    weight = row.get("weight", 0)
    size = row.get("size", 0)
    days = row.get("days_on_shelf", 999)

    score += sales * 0.5

    if 10 <= price <= 50:
        score += 80
    elif price < 10:
        score += 40

    if weight < 0.5:
        score += 60
    elif weight < 1:
        score += 30

    if size < 20:
        score += 60
    elif size < 35:
        score += 30

    if days < 30:
        score += 50
    elif days < 90:
        score += 20

    return score


uploaded_file = st.file_uploader("📂 上传Ozon CSV文件", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)
    df = df.fillna(0)

    st.write("### 原始数据")
    st.dataframe(df.head())

    df["score"] = df.apply(score, axis=1)

    df = df.sort_values(by="score", ascending=False)

    st.write("### AI筛选结果")
    st.dataframe(df.head(50))

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button("下载结果CSV", csv, "result.csv", "text/csv")