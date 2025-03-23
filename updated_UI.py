import streamlit as st
import requests
import json

# Initialize session state if not already set
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Function to fetch recommendations from backend API
def get_recommendations(query):
    api_url = f"http://127.0.0.1:8000/recommend?query={query}"
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch recommendations: {e}")
        return []

# Function to add item to cart
def add_to_cart(product):
    st.session_state.cart.append(product)
    st.success(f"{product['name']} added to cart!")

# Function to remove item from cart
def remove_from_cart(index):
    removed_item = st.session_state.cart.pop(index)
    st.success(f"Removed {removed_item['name']} from cart")

# UI Elements
st.title("🛍️ Smart Product Recommender")

# Search input
query = st.text_input("Enter a product name or keyword:", "")

# Filters
category = st.selectbox("Filter by Category:", ["All", "Electronics", "Fashion", "Books", "Home Appliances"])
price_range = st.slider("Filter by Price Range ($):", 0, 500, (0, 500))

if st.button("Search") and query:
    st.session_state.search_history.append(query)
    recommendations = get_recommendations(query)
    
    if recommendations:
        st.subheader("Recommended Products")
        cols = st.columns(2)  # Two-column layout
        
        for index, product in enumerate(recommendations):
            try:
                price = float(product.get('price', 0))
            except ValueError:
                price = 0
            
            # Apply filters
            if category != "All" and product.get('category') != category:
                continue
            if not (price_range[0] <= price <= price_range[1]):
                continue
            
            with cols[index % 2]:
                st.image(product.get('image_url', 'https://via.placeholder.com/150'), width=150)
                st.write(f"**{product['name']}**")
                st.write(f"💲{price}")
                st.button("Add to Cart", key=f"cart_{index}", on_click=add_to_cart, args=(product,))
    else:
        st.warning("No recommendations found!")

# Sidebar: Shopping Cart
st.sidebar.title("🛒 Your Cart")
if st.session_state.cart:
    for i, item in enumerate(st.session_state.cart):
        st.sidebar.write(f"- {item['name']} - 💲{item.get('price', 0)}")
        st.sidebar.button("Remove", key=f"remove_{i}", on_click=remove_from_cart, args=(i,))
else:
    st.sidebar.write("Your cart is empty.")

# Sidebar: Search History
st.sidebar.title("🔍 Search History")
for hist in st.session_state.search_history[-5:]:
    st.sidebar.write(f"- {hist}")
