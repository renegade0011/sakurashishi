import streamlit as st
import pandas as pd
import io
from datetime import datetime

# 1. Branding and Page Config
st.set_page_config(
    page_title="Sakura Sushi Manager", 
    page_icon="🌸", 
    layout="wide"
)

# 2. High-Contrast Deep Blue Theme
st.markdown("""
    <style>
    /* Main Background */
    .main { background-color: #f4f7f9; }
    
    /* Metric Card Styling - DEEP BLUE with WHITE TEXT */
    [data-testid="stMetric"] {
        background-color: #004080 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    
    /* Metric Value (The Price/Number) */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 2.8rem !important;
    }
    
    /* Metric Label (The Text) */
    [data-testid="stMetricLabel"] {
        color: #e0e0e0 !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
    }
    
    /* Styling for the Invoicing Box */
    .invoice-container {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #004080;
    }
    
    /* Headers */
    h1, h2, h3 { color: #004080; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌸 Sakura Sushi Manager")

# --- DATA INITIALIZATION ---
base_prices = {
    "Salmon": 6.0, "Sugar": 2.0, "Rice": 2.0, "Tea": 2.0, "Wasabi": 4.0,
    "Broth": 5.0, "Sakura": 4.0, "Noodles": 5.0, "Chicken": 6.5,
    "Milk": 3.0, "Anchovy": 3.0
}

# 1 Milk = 3 Butter
butter_cost = base_prices["Milk"] / 3

menu = {
    "🍣 Sushi Roll": {"price": 25.0, "ingredients": {"Salmon": 1, "Rice": 1, "Wasabi": 1}},
    "🍜 Chicken Ramen": {"price": 25.0, "ingredients": {"Noodles": 1, "Broth": 1, "Chicken": 1}},
    "🍛 Japanese Curry": {"price": 30.0, "ingredients": {"Rice": 2, "Chicken": 1, "Butter": 2}},
    "🥣 Miso Soup": {"price": 22.0, "ingredients": {"Broth": 1, "Salmon": 1}},
    "🐙 Takoyaki": {"price": 35.0, "ingredients": {"Anchovy": 1, "Butter": 4, "Sugar": 1}},
    "🥟 Chicken Gyoza": {"price": 35.0, "ingredients": {"Chicken": 1, "Noodles": 3, "Wasabi": 1}},
    "🌸 Sakura Tea": {"price": 35.0, "ingredients": {"Tea": 2, "Sakura": 3, "Sugar": 3}},
    "🍵 Ganmaicha": {"price": 20.0, "ingredients": {"Tea": 2, "Rice": 2}},
    "🍶 Amazake": {"price": 30.0, "ingredients": {"Rice": 1, "Milk": 2, "Sugar": 3}},
    "🌿 Matcha": {"price": 25.0, "ingredients": {"Tea": 3, "Milk": 2, "Sugar": 2}}
}

# --- SIDEBAR ---
st.sidebar.header("⚙️ Cost Inventory")
ing_prices = {}
all_ingredients = sorted(list(set(item for meal in menu.values() for item in meal["ingredients"])))
for ing in all_ingredients:
    if ing == "Butter":
        ing_prices[ing] = butter_cost
        st.sidebar.caption(f"🧈 Butter: ${butter_cost:.2f} (from Milk)")
    else:
        ing_prices[ing] = st.sidebar.number_input(f"{ing} ($)", min_value=0.0, value=float(base_prices.get(ing, 1.0)), step=0.1)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📋 Production", "📊 Analysis", "💰 Invoicing"])

# --- TAB 1: PRODUCTION ---
with tab1:
    st.subheader("Inventory Preparation")
    cols = st.columns(2)
    order = {meal: cols[i % 2].number_input(f"{meal}", min_value=0, step=1, key=f"p_{meal}") for i, meal in enumerate(menu.keys())}
    
    if st.button("Generate Shopping List"):
        totals = {}
        for meal, qty in order.items():
            if qty > 0:
                for ing, amt in menu[meal]["ingredients"].items():
                    totals[ing] = totals.get(ing, 0) + (amt * qty)
        if totals:
            shop_df = pd.DataFrame([{"Ingredient": k, "Qty": v, "Total Cost": f"${v*ing_prices[k]:.2f}"} for k, v in totals.items()])
            st.table(shop_df)
            st.metric("Required Budget", f"${sum(v*ing_prices[k] for k, v in totals.items()):.2f}")

# --- TAB 2: ANALYSIS ---
with tab2:
    st.subheader("Profit Breakdown per Item")
    fin_list = []
    for meal, data in menu.items():
        cost = sum(ing_prices[ing] * amt for ing, amt in data["ingredients"].items())
        fin_list.append({"Meal": meal, "Price": f"${data['price']}", "Cost": f"${cost:.2f}", "Profit": f"${(data['price']-cost):.2f}"})
    st.dataframe(pd.DataFrame(fin_list), use_container_width=True)

# --- TAB 3: INVOICING (Facturation) ---
with tab3:
    st.subheader("Customer Invoicing")
    c_name = st.text_input("Customer Name", "Guest")
    inv_cols = st.columns(2)
    items_ordered = {meal: inv_cols[i % 2].number_input(f"Add {meal}", min_value=0, step=1, key=f"inv_{meal}") for i, meal in enumerate(menu.keys())}
    
    if st.button("Process Order & Show Receipt"):
        st.markdown(f'<div class="invoice-container">', unsafe_allow_html=True)
        st.markdown(f"### RECEIPT: SAKURA SUSHI")
        st.markdown(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')} | **Client:** {c_name}")
        st.markdown("---")
        
        invoice_data = []
        total_bill = 0.0
        total_cost = 0.0
        
        for meal, qty in items_ordered.items():
            if qty > 0:
                price = menu[meal]['price']
                cost = sum(ing_prices[ing] * amt for ing, amt in menu[meal]["ingredients"].items())
                invoice_data.append({"Item": meal, "Qty": qty, "Price": f"${price:.2f}", "Total": f"${price * qty:.2f}"})
                total_bill += (price * qty)
                total_cost += (cost * qty)
        
        if invoice_data:
            st.table(pd.DataFrame(invoice_data))
            
            # THE HIGH-CONTRAST SECTION
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("TOTAL TO PAY", f"${total_bill:.2f}")
            m_col2.metric("NET PROFIT", f"${total_bill - total_cost:.2f}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please select at least one meal to generate an invoice.")
