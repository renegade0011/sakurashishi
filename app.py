import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="Restaurant Management Pro", layout="wide")

st.title("🍣 Restaurant Production & Profit Manager")

# --- DATA INITIALIZATION ---
menu = {
    "Sushi Roll": {"price": 25, "ingredients": {"Salmon": 1, "Rice": 1, "Wasabi": 1}},
    "Chicken Ramen": {"price": 25, "ingredients": {"Noodles": 1, "Broth": 1, "Chicken": 1}},
    "Japanese Curry": {"price": 30, "ingredients": {"Rice": 2, "Chicken": 1, "Butter": 2}},
    "Miso Soup": {"price": 22, "ingredients": {"Broth": 1, "Salmon": 1}},
    "Takoyaki": {"price": 35, "ingredients": {"Anchovy": 1, "Butter": 4, "Sugar": 1}},
    "Chicken Gyoza": {"price": 35, "ingredients": {"Chicken": 1, "Noodles": 3, "Wasabi": 1}},
    "Sakura Tea": {"price": 35, "ingredients": {"Tea": 2, "Sakura": 3, "Sugar": 3}},
    "Ganmaicha": {"price": 20, "ingredients": {"Tea": 2, "Rice": 2}},
    "Amazake": {"price": 30, "ingredients": {"Rice": 1, "Milk": 2, "Sugar": 3}},
    "Matcha": {"price": 25, "ingredients": {"Tea": 3, "Milk": 2, "Sugar": 2}}
}

# --- SIDEBAR: INGREDIENT PRICING (Option 2) ---
st.sidebar.header("💰 Step 1: Set Ingredient Costs")
ing_prices = {}
all_ingredients = sorted(list(set(item for meal in menu.values() for item in meal["ingredients"])))

for ing in all_ingredients:
    ing_prices[ing] = st.sidebar.number_input(f"Price of 1 unit of {ing}", min_value=0.0, value=1.0, step=0.1)

# --- MAIN INTERFACE ---
tab1, tab2 = st.tabs(["🚀 Option 1: Production Plan", "📊 Option 2: Financials"])

with tab1:
    st.header("Daily Production Order")
    st.info("Enter the number of meals you want to prepare today to see the total cost.")
    
    cols = st.columns(2)
    order = {}
    
    # Input how many of each meal
    for i, meal in enumerate(menu.keys()):
        col = cols[0] if i % 2 == 0 else cols[1]
        order[meal] = col.number_input(f"Quantity of {meal}", min_value=0, step=1, key=f"prod_{meal}")

    if st.button("Calculate Shopping List & Total Cost"):
        shopping_list = []
        grand_total = 0.0
        
        # Calculate totals for each ingredient needed
        temp_list = {}
        for meal, qty in order.items():
            if qty > 0:
                for ing, amt in menu[meal]["ingredients"].items():
                    temp_list[ing] = temp_list.get(ing, 0) + (amt * qty)
        
        # Build the final table with prices
        for ing, total_qty in temp_list.items():
            cost_for_this_item = total_qty * ing_prices[ing]
            shopping_list.append({
                "Ingredient": ing,
                "Total Quantity": total_qty,
                "Unit Price": f"${ing_prices[ing]:.2f}",
                "Subtotal": f"${cost_for_this_item:.2f}",
                "numeric_subtotal": cost_for_this_item
            })
            grand_total += cost_for_this_item
        
        if shopping_list:
            st.subheader("🛒 Total Ingredients Needed")
            df_shop = pd.DataFrame(shopping_list).drop(columns=["numeric_subtotal"])
            st.table(df_shop)
            
            # Grand Total Display
            st.metric(label="Estimated Total Cost for Production", value=f"${grand_total:.2f}")
        else:
            st.warning("Please enter at least one meal quantity.")

with tab2:
    st.header("Profitability Analysis")
    # ... (Rest of the financial logic remains the same)
    financial_data = []
    for meal, data in menu.items():
        m_price = data["price"]
        m_cost = sum(ing_prices[ing] * amt for ing, amt in data["ingredients"].items())
        m_profit = m_price - m_cost
        
        financial_data.append({
            "Meal": meal,
            "Selling Price": f"${m_price}",
            "Production Cost": f"${m_cost:.2f}",
            "Net Profit": f"${m_profit:.2f}"
        })
    
    df_fin = pd.DataFrame(financial_data)
    st.dataframe(df_fin, use_container_width=True)
