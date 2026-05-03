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

# Custom CSS for Sakura theme
st.markdown("""
    <style>
    .main { background-color: #fff5f7; }
    .stMetric { background-color: #ffe0e9; padding: 15px; border-radius: 10px; }
    .invoice-box { border: 1px solid #eee; padding: 20px; border-radius: 10px; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌸 Sakura Sushi: Manager & Invoicing")

# --- DATA INITIALIZATION ---
base_prices = {
    "Salmon": 6.0, "Sugar": 2.0, "Rice": 2.0, "Tea": 2.0, "Wasabi": 4.0,
    "Broth": 5.0, "Sakura": 4.0, "Noodles": 5.0, "Chicken": 6.5,
    "Milk": 3.0, "Anchovy": 3.0
}

# Crafting Logic: 1 Milk ($3) = 3 Butter ($1 each)
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

# --- SIDEBAR: COSTS ---
st.sidebar.header("📁 Inventory Costs")
ing_prices = {}
all_ingredients = sorted(list(set(item for meal in menu.values() for item in meal["ingredients"])))

for ing in all_ingredients:
    if ing == "Butter":
        ing_prices[ing] = butter_cost
        st.sidebar.write(f"🧈 Butter: ${butter_cost:.2f} (Auto)")
    else:
        default_p = base_prices.get(ing, 1.0)
        ing_prices[ing] = st.sidebar.number_input(f"Price: {ing}", min_value=0.0, value=float(default_p), step=0.1)

# --- MAIN INTERFACE ---
tab1, tab2, tab3 = st.tabs(["🚀 Production Plan", "📊 Profit Analysis", "🧾 Facturation (Invoicing)"])

# OPTION 1: PRODUCTION
with tab1:
    st.header("Daily Production Order")
    cols = st.columns(2)
    order = {meal: cols[i % 2].number_input(f"{meal}", min_value=0, step=1, key=f"p_{meal}") for i, meal in enumerate(menu.keys())}
    
    if st.button("Calculate Shopping List"):
        totals = {}
        for meal, qty in order.items():
            if qty > 0:
                for ing, amt in menu[meal]["ingredients"].items():
                    totals[ing] = totals.get(ing, 0) + (amt * qty)
        if totals:
            shop_df = pd.DataFrame([{"Ingredient": k, "Qty": v, "Total Cost": f"${v*ing_prices[k]:.2f}"} for k, v in totals.items()])
            st.table(shop_df)
            st.metric("Total Order Cost", f"${sum(v*ing_prices[k] for k, v in totals.items()):.2f}")

# OPTION 2: PROFIT ANALYSIS
with tab2:
    st.header("Financial Performance")
    fin_list = []
    for meal, data in menu.items():
        cost = sum(ing_prices[ing] * amt for ing, amt in data["ingredients"].items())
        fin_list.append({"Meal": meal, "Price": f"${data['price']}", "Cost": f"${cost:.2f}", "Profit": f"${(data['price']-cost):.2f}"})
    st.dataframe(pd.DataFrame(fin_list), use_container_width=True)

# NEW OPTION 3: FACTURATION
with tab3:
    st.header("Create New Invoice")
    c_name = st.text_input("Customer Name", "Guest")
    inv_cols = st.columns(2)
    items_ordered = {}
    
    for i, meal in enumerate(menu.keys()):
        col = inv_cols[i % 2]
        items_ordered[meal] = col.number_input(f"Add {meal}", min_value=0, step=1, key=f"inv_{meal}")
    
    if st.button("Generate Facture"):
        st.markdown("---")
        st.subheader(f"Receipt: Sakura Sushi")
        st.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.write(f"**Customer:** {c_name}")
        
        invoice_data = []
        total_bill = 0.0
        total_cost = 0.0
        
        for meal, qty in items_ordered.items():
            if qty > 0:
                price = menu[meal]['price']
                cost = sum(ing_prices[ing] * amt for ing, amt in menu[meal]["ingredients"].items())
                subtotal = price * qty
                invoice_data.append({"Item": meal, "Qty": qty, "Unit Price": f"${price:.2f}", "Total": f"${subtotal:.2f}"})
                total_bill += subtotal
                total_cost += (cost * qty)
        
        if invoice_data:
            st.table(pd.DataFrame(invoice_data))
            c1, c2 = st.columns(2)
            c1.metric("Total to Pay", f"${total_bill:.2f}")
            c2.metric("Net Profit on Order", f"${total_bill - total_cost:.2f}", delta_color="normal")
            st.button("Print Invoice (Ctrl+P)")
        else:
            st.warning("Please add at least one item to the invoice.")
