import streamlit as st
import pandas as pd

st.title("Ozon AI选品系统 V1（稳定版）")

uploaded_file = st.file_uploader("上传Ozon CSV文件", type=["csv"])

if uploaded_file:

    # ========================
    # 1. 读取数据
    # ========================
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()

    st.write("原始字段：", df.columns.tolist())

    # ========================
    # 2. 自动数据清洗
    # ========================
    def to_num(col):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    def find_col(keywords):
        for col in df.columns:
            for k in keywords:
                if k in col:
                    return col
        return None

    price_col = find_col(["price", "价格", "цена"])
    rating_col = find_col(["rating", "评分"])
    review_col = find_col(["review", "评论"])
    sales_col = find_col(["sales", "销量"])
    seller_col = find_col(["seller", "卖家"])
    weight_col = find_col(["weight", "重量"])
    time_col = find_col(["created", "date", "时间"])
    brand_col = find_col(["brand", "品牌"])
    ship_col = find_col(["delivery", "logistics", "配送"])

    result = df.copy()

    for col in [price_col, rating_col, review_col, sales_col, seller_col, weight_col]:
        to_num(col)

    if time_col:
        result[time_col] = pd.to_datetime(result[time_col], errors="coerce")

    # ========================
    # 3. 筛选规则（你的条件）
    # ========================
    if price_col:
        result = result[result[price_col] <= 135]

    if rating_col:
        result = result[result[rating_col] >= 4.7]

    if review_col:
        result = result[result[review_col] > 1]

    if sales_col:
        result = result[result[sales_col] > 3]

    if seller_col:
        result = result[result[seller_col] < 50]

    if weight_col:
        result = result[result[weight_col] < 500]

    if brand_col:
        result = result[
            result[brand_col].fillna("").str.lower().str.contains("без бренда|no brand|无品牌")
        ]

    if ship_col:
        result = result[result[ship_col] == "FBS"]

    if time_col:
        result = result[result[time_col] >= pd.to_datetime("2026-04-01")]

    # ========================
    # 4. AI评分系统
    # ========================
    def safe(col):
        return result[col] if col in result.columns else 0

    result["score"] = (
        safe(rating_col) * 25 +
        safe(sales_col) * 10 +
        safe(review_col) * 2 -
        safe(price_col) * 0.3 -
        safe(weight_col) * 0.05 -
        safe(seller_col) * 0.8
    )

    result = result.sort_values("score", ascending=False)

    # ========================
    # 5. 输出
    # ========================
    st.success(f"筛选完成：{len(result)} 个商品")

    st.dataframe(result.head(100))

    # ========================
    # 6. 下载
    # ========================
    csv = result.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "下载选品结果CSV",
        csv,
        "ozon_ai_result.csv",
        "text/csv"
    )
