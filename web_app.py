import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="iPhone Deal Checker", layout="centered")

st.title("📱 iPhone Deal Analyser")
st.caption("Paste a Facebook Marketplace listing below")

# --- LOAD DATA (LOCAL FILE IN REPO) ---
@st.cache_data
def load_data():
    df = pd.read_csv("iphone_prices.csv")

    # Clean price column
    df["Price"] = (
        df["Price"]
        .astype(str)
        .str.replace("R", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df = df.dropna(subset=["Price"])

    df["key"] = df["Model"] + "_" + df["Storage"] + "_" + df["Condition"]
    return dict(zip(df["key"], df["Price"]))

price_lookup = load_data()

# --- SMART DETECTION ---
def extract_info(text):
    text = text.lower()

    # MODEL (handles Pro / Pro Max)
    model = None
    for i in range(11, 16):
        if f"iphone {i}" in text:
            if "pro max" in text:
                model = f"iPhone {i} Pro Max"
            elif "pro" in text:
                model = f"iPhone {i} Pro"
            else:
                model = f"iPhone {i}"

    # STORAGE
    storage = None
    for s in ["64", "128", "256", "512"]:
        if s in text:
            storage = f"{s}GB"

    # CONDITION
    if any(x in text for x in ["excellent", "like new", "mint"]):
        condition = "Excellent"
    elif any(x in text for x in ["fair", "used", "scratches", "crack"]):
        condition = "Fair"
    else:
        condition = "Good"

    # PRICE
    price_match = re.search(r"\d{3,6}", text.replace(",", ""))
    price = int(price_match.group()) if price_match else None

    return model, storage, condition, price

# --- UI ---
text = st.text_area("Paste listing here", height=150)

if st.button("Analyse Deal"):

    model, storage, condition, market_price = extract_info(text)

    if not model or not storage or not market_price:
        st.error("⚠️ Could not detect model, storage or price. Try adding more detail.")
    else:
        key = f"{model}_{storage}_{condition}"
        expected = price_lookup.get(key)

        # --- FALLBACK (ignore condition if not found)
        if not expected:
            for k in price_lookup:
                if model in k and storage in k:
                    expected = price_lookup[k]
                    break

        if expected:
            profit = expected - market_price
            margin = (profit / expected) * 100
            max_buy = int(expected * 0.75)

            # DEAL RATING
            if profit > 1000:
                rating = "🔥 GREAT DEAL"
                st.success("🔥 GREAT DEAL")
            elif profit > 500:
                rating = "⚡ DECENT DEAL"
                st.warning("⚡ DECENT DEAL")
            else:
                rating = "❌ NOT WORTH IT"
                st.error("❌ NOT WORTH IT")

            # DISPLAY RESULTS
            st.markdown(f"""
            ### 📱 {model} ({storage})
            **Condition:** {condition}

            **💰 Market Price:** R{market_price}  
            **📊 Expected Value:** R{int(expected)}  

            **💵 Profit:** R{int(profit)}  
            **📈 Margin:** {margin:.1f}%  

            **🎯 Max Buy Price:** R{max_buy}
            """)

        else:
            st.error("No pricing data found for this model")