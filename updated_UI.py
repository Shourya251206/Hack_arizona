import streamlit as st
import requests
import json
from PIL import Image
import io
import base64

# Set page configuration
st.set_page_config(
    page_title="Smart Product Recommender",
    page_icon="🛍️",
    layout="wide"
)

# Custom CSS for styling
def add_bg_from_color(color_value):
    custom_css = f"""
    <style>
    .stApp {{
        background-color: {color_value};
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# Custom styling for components
def local_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 40px !important;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .subheader {
        color: #1E3A8A;
        font-size: 24px;
        padding: 10px;
        border-radius: 5px;
        background-color: white;
        margin-top: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .product-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    .cart-item {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #DC2626;
    }
    .search-bar {
        background-color: #DC2626 !important;
        color: white !important;
        padding: 10px !important;
        border-radius: 10px !important;
    }
    .category-filter {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .btn-add {
        background-color: #10B981;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .btn-add:hover {
        background-color: #059669;
    }
    .btn-remove {
        background-color: #DC2626;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state if not already set
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

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
    st.toast(f"✅ {product['name']} added to cart!")

# Function to remove item from cart
def remove_from_cart(index):
    removed_item = st.session_state.cart.pop(index)
    st.toast(f"🗑️ Removed {removed_item['name']} from cart")

# Function to clear cart
def clear_cart():
    st.session_state.cart = []
    st.success("Cart cleared!")

# Apply styling
local_css()

# Set background color based on search status
if st.session_state.search_performed:
    add_bg_from_color("#87CEEB")  # Sky blue background after search
else:
    add_bg_from_color("white")  # White background initially

# App Header
st.markdown("<h1 class='main-header'>🛍️ Smart Product Recommender</h1>", unsafe_allow_html=True)

# Create layout
left_col, right_col = st.columns([3, 1])

with right_col:
    # Shopping Cart
    st.markdown("<h3 style='color:#1E3A8A;'>🛒 Your Cart</h3>", unsafe_allow_html=True)
    cart_container = st.container()
    with cart_container:
        if st.session_state.cart:
            total_price = sum(float(item.get('price', 0)) for item in st.session_state.cart)
            for i, item in enumerate(st.session_state.cart):
                st.markdown(f"""
                <div class='cart-item'>
                    <strong>{item['name']}</strong><br>
                    💲{item.get('price', 0)}
                </div>
                """, unsafe_allow_html=True)
                st.button("Remove", key=f"remove_{i}", on_click=remove_from_cart, args=(i,))
            
            st.markdown(f"<h4>Total: 💲{total_price:.2f}</h4>", unsafe_allow_html=True)
            st.button("Clear Cart", on_click=clear_cart)
        else:
            st.info("Your cart is empty.")
    
    # Search History
    st.markdown("<h3 style='color:#1E3A8A; margin-top:20px;'>🔍 Recent Searches</h3>", unsafe_allow_html=True)
    history_container = st.container()
    with history_container:
        if st.session_state.search_history:
            for hist in st.session_state.search_history[-5:]:
                st.markdown(f"• {hist}")
        else:
            st.info("No search history yet.")

with left_col:
    # Search and Filter Section
    st.markdown("<div class='search-bar'>", unsafe_allow_html=True)
    query = st.text_input("Enter a product name or keyword:", "", key="search_input")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='category-filter'>", unsafe_allow_html=True)
        category = st.selectbox("Filter by Category:", 
                              ["All", "Electronics", "Fashion", "Books", "Home Appliances"])
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='category-filter'>", unsafe_allow_html=True)
        price_range = st.slider("Filter by Price Range ($):", 0, 500, (0, 500))
        st.markdown("</div>", unsafe_allow_html=True)
    
    search_btn = st.button("Search Products", use_container_width=True)
    
    # Process search
    if search_btn and query:
        st.session_state.search_history.append(query)
        st.session_state.search_performed = True
        recommendations = get_recommendations(query)
        
        # Refresh to apply background change
        st.experimental_rerun()
    
    # Display search results
    if st.session_state.search_performed:
        recommendations = get_recommendations(st.session_state.search_history[-1]) if st.session_state.search_history else []
        
        if recommendations:
            st.markdown("<h2 class='subheader'>Recommended Products</h2>", unsafe_allow_html=True)
            
            # Create responsive grid layout
            cols = st.columns(2)
            
            filtered_products = [
                product for product in recommendations
                if (category == "All" or product.get('category') == category) and
                (price_range[0] <= float(product.get('price', 0)) <= price_range[1])
            ]
            
            if filtered_products:
                for index, product in enumerate(filtered_products):
                    with cols[index % 2]:
                        st.markdown(f"""
                        <div class='product-card'>
                            <h3>{product['name']}</h3>
                            <p>Category: {product.get('category', 'Unknown')}</p>
                            <p>💲{product.get('price', 0)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display product image
                        st.image(product.get('image_url', 'https://via.placeholder.com/150'), 
                               width=150, 
                               caption=f"{product.get('category', '')}")
                        
                        # Add to cart button
                        st.button("Add to Cart", key=f"cart_{index}", on_click=add_to_cart, args=(product,))
            else:
                st.warning("No products match your filters. Try adjusting your search criteria.")
        else:
            st.warning("No recommendations found! Try a different search term.")
