import streamlit as st
import pandas as pd
import io

# 1. Branding and Page Config
st.set_page_config(
    page_title="Sakura Sushi Manager", 
    page_icon="🌸", 
    layout="wide"
)

st.title("🌸 Sakura Sushi: Production & Profit Manager")

# --- FIXED DATA & CRAFTING LOGIC ---
# User defined prices
base_prices = {
    "Sugar": 2.0,
    "Rice": 2.0,
    "Tea": 2.0,
    "Wasabi": 4.0,
    "Broth": 5.0,
    "Sakura": 4.0,
    "Noodles": 5.0,
    "Chicken": 6.5,
    "Milk": 3.0,
    "Salmon": 5.0,   # Set to a default, can be adjusted in app
    "Anchovy": 3.0   # Set to a default, can be adjusted in app
}

# 1 Milk = 3 Butter logic
butter_cost = base_prices["Milk"] / 3

menu = {
    "🍣 Sushi Roll": {"price": 25, "ingredients": {"Salmon": 1, "Rice": 1, "Wasabi": 1}},
    "🍜 Chicken Ramen": {"price": 25, "ingredients": {"Noodles": 1, "Broth": 1, "Chicken": 1}},
    "🍛 Japanese Curry": {"price": 30, "ingredients": {"Rice": 2, "Chicken": 1, "Butter": 2}},
    "🥣 Miso Soup": {"price": 22, "ingredients": {"Broth": 1, "Salmon": 1}},
    "🐙 Takoyaki": {"price": 35, "ingredients": {"Anchovy": 1, "Butter": 4, "Sugar": 1}},
    "🥟 Chicken Gyoza": {"price": 35, "ingredients": {"Chicken": 1, "Noodles": 3, "Wasabi": 1}},
    "🌸 Sakura Tea": {"price": 35, "ingredients": {"Tea": 2, "Sakura": 3, "Sugar": 3}},
    "🍵 Ganmaicha": {"price": 20, "ingredients": {"Tea": 2, "Rice": 2}},
    "🍶 Amazake": {"price": 30, "ingredients": {"Rice": 1, "Milk": 2, "Sugar": 3}},
    "🌿 Matcha": {"price": 25, "ingredients": {"Tea": 3, "Milk": 2, "Sugar": 2}}
}

# --- SIDEBAR: PRICING ---
st.sidebar.header("📁 Inventory & Costs")
st.sidebar.info(f"💡 Crafting Info: 1 Milk (${base_prices['Milk']}) creates 3 Butter. Butter cost set to ${butter_cost:.2f}")

ing_prices = {}
all_ingredients = sorted(list(set(item for meal in menu.values() for item in meal["ingredients"])))

for ing in all_ingredients:
    if ing == "Butter":
        ing_prices[ing] = butter_cost
        st.sidebar.text(f"Butter: ${butter_cost:.2f} (from Milk)")
    else:
        default_p = base_prices.get(ing, 1.0)
        ing_prices[ing] = st.sidebar.number_input(f"Price: {ing}", min_value=0.0, value=float(default_p), step=0.1)

# --- MAIN INTERFACE ---
tab1, tab2 = st.tabs(["🚀 Production Plan", "📊 Profit Analysis"])

with tab1:
    st.header("Daily Production Order")
    cols = st.columns(2)
    order = {}
    
    for i, meal in enumerate(menu.keys()):
        col = cols[0] if i % 2 == 0 else cols[1]
        order[meal] = col.number_input(f"Quantity of {meal}", min_value=0, step=1, key=f"q_{meal}")

    if st.button("Calculate Shopping List"):
        temp_list = {}
        for meal, qty in order.items():
            if qty > 0:
                for ing, amt in menu[meal]["ingredients"].items():
                    temp_list[ing] = temp_list.get(ing, 0) + (amt * qty)
        
        if temp_list:
            shopping_data = []
            grand_total = 0.0
            for ing, total_qty in temp_list.items():
                cost = total_qty * ing_prices[ing]
                shopping_data.append({
                    "Ingredient": ing, 
                    "Qty Needed": total_qty, 
                    "Unit Cost": f"${ing_prices[ing]:.2f}", 
                    "Total Cost": f"${cost:.2f}"
                })
                grand_total += cost
            
            st.subheader("🛒 Shopping List")
            st.table(pd.DataFrame(shopping_data))
            st.metric("Total Order Cost", f"${grand_total:.2f}")
        else:
            st.warning("Please enter a quantity for at least one meal.")

with tab2:
    st.header("Financial Performance")
    financial_data = []
    for meal, data in menu.items():
        m_cost = sum(ing_prices[ing] * amt for ing, amt in data["ingredients"].items())
        financial_data.append({
            "Meal": meal,
            "Price": f"${data['price']}",
            "Cost": f"${m_cost:.2f}",
            "Profit": f"${(data['price'] - m_cost):.2f}"
        })
    st.dataframe(pd.DataFrame(financial_data), use_container_width=True)
