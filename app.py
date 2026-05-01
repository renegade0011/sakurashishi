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

# --- DATA INITIALIZATION ---
# Meal names updated with Emojis
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

all_ingredients = sorted(list(set(item for meal in menu.values() for item in meal["ingredients"])))

# --- SIDEBAR: DATA MANAGEMENT ---
st.sidebar.header("📁 Data Management")

# Upload existing prices
uploaded_file = st.sidebar.file_uploader("Upload your saved prices (CSV)", type="csv")
loaded_prices = {}

if uploaded_file is not None:
    df_upload = pd.read_csv(uploaded_file)
    loaded_prices = dict(zip(df_upload["Ingredient"], df_upload["Price"]))
    st.sidebar.success("Prices Loaded!")

# --- SIDEBAR: INGREDIENT PRICING ---
st.sidebar.header("💰 Step 1: Set Costs")
ing_prices = {}

for ing in all_ingredients:
    # Uses uploaded price if available, otherwise defaults to 1.0
    val = float(loaded_prices.get(ing, 1.0))
    ing_prices[ing] = st.sidebar.number_input(f"Price: {ing}", min_value=0.0, value=val, step=0.1, key=f"price_{ing}")

# Download button to save for next time
df_save = pd.DataFrame(list(ing_prices.items()), columns=["Ingredient", "Price"])
csv_buffer = io.StringIO()
df_save.to_csv(csv_buffer, index=False)
st.sidebar.download_button(
    label="💾 Download Prices to Save",
    data=csv_buffer.getvalue(),
    file_name="sakura_sushi_prices.csv",
    mime="text/csv",
)

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
