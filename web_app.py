import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="iPhone Deal Analyzer",
    page_icon="📱",
    layout="centered"
)

st.title("📱 iPhone Deal Analyzer")
st.write("Paste a Facebook Marketplace listing below")

# -----------------------------
# LOAD CSV
# -----------------------------
df = pd.read_csv("iphone_prices.csv")

# -----------------------------
# CLEAN PRICE COLUMN
# -----------------------------
df["Price"] = (
    df["Price"]
    .astype(str)
    .str.replace("R", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.strip()
)

df["Price"] = pd.to_numeric(
    df["Price"],
    errors="coerce"
)

# -----------------------------
# USER INPUT
# -----------------------------
text = st.text_area(
    "Paste listing here",
    height=200
)

battery = st.slider(
    "Battery Health %",
    70,
    100,
    90
)

# -----------------------------
# SAVE DEAL FUNCTION
# -----------------------------
def save_deal(
    model,
    storage,
    condition,
    listing_price,
    expected,
    profit,
    decision,
    risk
):

    deal = pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Model": model,
        "Storage": storage,
        "Condition": condition,
        "Listing Price": listing_price,
        "Expected Value": expected,
        "Profit": profit,
        "Decision": decision,
        "Risk": risk
    }])

    file_name = "deal_history.csv"

    if os.path.exists(file_name):

        existing = pd.read_csv(file_name)

        updated = pd.concat(
            [existing, deal],
            ignore_index=True
        )

        updated.to_csv(file_name, index=False)

    else:

        deal.to_csv(file_name, index=False)

# -----------------------------
# EXTRACT INFO
# -----------------------------
def extract_info(text):

    text = text.lower()

    # -----------------------------
    # MODEL
    # -----------------------------
    model = None

    special_models = [
        "iphone xr",
        "iphone xs max",
        "iphone xs",
        "iphone x",
        "iphone se (2020)",
        "iphone se"
    ]

    for sm in special_models:

        if sm in text:
            model = sm.title()

    # Standard models
    if not model:

        for i in range(11, 18):

            if f"iphone {i}" in text:

                if "pro max" in text:
                    model = f"iPhone {i} Pro Max"

                elif "pro" in text:
                    model = f"iPhone {i} Pro"

                elif "plus" in text:
                    model = f"iPhone {i} Plus"

                else:
                    model = f"iPhone {i}"

    # -----------------------------
    # STORAGE
    # -----------------------------
    storage = None

    for s in ["64", "128", "256", "512", "1024"]:

        if s in text:
            storage = f"{s}GB"

    # -----------------------------
    # CONDITION
    # -----------------------------
    if any(x in text for x in ["sealed", "brand new"]):
        condition = "Sealed"

    elif any(x in text for x in ["mint", "excellent", "like new"]):
        condition = "Mint"

    elif any(x in text for x in ["good"]):
        condition = "Good"

    elif any(x in text for x in ["fair", "used"]):
        condition = "Fair"

    elif any(x in text for x in ["poor", "crack", "broken"]):
        condition = "Poor"

    else:
        condition = "Good"

    # -----------------------------
    # PRICE
    # -----------------------------
    price_match = re.search(
        r"\b\d{3,6}\b",
        text.replace(",", "")
    )

    price = int(price_match.group()) if price_match else None

    return model, storage, condition, price

# -----------------------------
# ANALYSE BUTTON
# -----------------------------
if st.button("Analyse Deal"):

    model, storage, condition, listing_price = extract_info(text)

    # -----------------------------
    # DISPLAY DETECTED INFO
    # -----------------------------
    st.subheader("Detected Listing Info")

    st.write(f"📱 Model: {model}")
    st.write(f"💾 Storage: {storage}")
    st.write(f"🔧 Condition: {condition}")
    st.write(f"💵 Listing Price: R{listing_price}")

    # -----------------------------
    # VALIDATION
    # -----------------------------
    if not model or not storage or not listing_price:

        st.error(
            "Could not detect model, storage or price. Try adding more detail."
        )

    else:

        # -----------------------------
        # FIND MATCHING PRICE
        # -----------------------------
        result = df[
            (df["Model"] == model)
            & (df["Storage"] == storage)
            & (df["Condition"] == condition)
        ]

        if result.empty:

            st.warning(
                "No matching pricing found in database."
            )

        else:

            expected = result.iloc[0]["Price"]

            # -----------------------------
            # BATTERY ADJUSTMENT
            # -----------------------------
            if battery < 80:
                expected -= 800

            elif battery < 85:
                expected -= 500

            elif battery < 90:
                expected -= 250

            # -----------------------------
            # CALCULATIONS
            # -----------------------------
            profit = expected - listing_price

            max_buy = int(expected * 0.75)

            offer_price = int(expected * 0.70)

            # -----------------------------
            # RISK DETECTION
            # -----------------------------
            risk = "Low"

            risky_words = [
                "icloud",
                "face id",
                "crack",
                "broken",
                "replacement screen",
                "battery issue",
                "no face id"
            ]

            if any(word in text.lower() for word in risky_words):
                risk = "High"

            # -----------------------------
            # DECISION
            # -----------------------------
            if profit >= 2000:
                decision = "🔥 BUY"

            elif profit >= 1000:
                decision = "🤔 MAYBE"

            else:
                decision = "❌ SKIP"

            # -----------------------------
            # RESULTS
            # -----------------------------
            st.subheader("Deal Analysis")

            st.success(
                f"Estimated Resell Value: R{expected:,.0f}"
            )

            st.info(
                f"Suggested Offer Price: R{offer_price:,.0f}"
            )

            st.warning(
                f"Maximum Buy Price: R{max_buy:,.0f}"
            )

            st.write(
                f"💰 Estimated Profit: R{profit:,.0f}"
            )

            st.write(
                f"⚠️ Risk Level: {risk}"
            )

            st.subheader(
                f"Decision: {decision}"
            )

            # -----------------------------
            # WHATSAPP MESSAGE
            # -----------------------------
            st.subheader("Quick Offer Message")

            whatsapp_message = f"""
Hi, is the {model} still available?

Would you accept around R{offer_price:,.0f} cash today?
"""

            st.code(whatsapp_message)

            # -----------------------------
            # SAVE DEAL
            # -----------------------------
            save_deal(
                model,
                storage,
                condition,
                listing_price,
                expected,
                profit,
                decision,
                risk
            )

            st.success("Deal saved to history")