import streamlit as st
import requests
import json

# Set page configuration
st.set_page_config(
    page_title="Smart Product Recommender",
    page_icon="🛍️",
    layout="wide"
)

# Custom CSS for the fixed color scheme: sky blue, red, and white
def apply_custom_css():
    st.markdown("""
    <style>
    /* Main background color - Sky Blue */
    .stApp {
        background-color: #87CEEB !important;
    }
    
    /* Header styling - White */
    .main-header {
        font-size: 40px !important;
        font-weight: bold;
        color: #000000;
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Search bar - Red */
    .search-section {
        background-color: #FF0000;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    
    /* Input fields within red section */
    .search-section .stTextInput input {
        border-color: white !important;
        color: black !important;
        background-color: white !important;
    }
    
    /* Product cards - White */
    .product-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar content - White */
    .sidebar-content {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    
    /* Section headers - White with border */
    .section-header {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 15px;
        font-weight: bold;
    }
    
    /* Filter section - White */
    .filter-section {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    /* Buttons - Red */
    .stButton button {
        background-color: #FF0000 !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton button:hover {
        background-color: #CC0000 !important;
    }
    
    /* Cart items - White */
    .cart-item {
        background-color: white;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #FF0000;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply the custom CSS
apply_custom_css()

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
    st.success(f"✅ {product['name']} added to cart!")

# Function to remove item from cart
def remove_from_cart(index):
    removed_item = st.session_state.cart.pop(index)
    st.success(f"🗑️ Removed {removed_item['name']} from cart")

# Function to clear cart
def clear_cart():
    st.session_state.cart = []
    st.success("Cart cleared!")

# Main app header
st.markdown("<h1 class='main-header'>🛍️ Smart Product Recommender</h1>", unsafe_allow_html=True)

# Create columns for layout
main_col, sidebar_col = st.columns([3, 1])

with main_col:
    # Search section - Red background
    st.markdown("<div class='search-section'>", unsafe_allow_html=True)
    query = st.text_input("Enter a product name or keyword:", "")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Filters section - White background
    st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
    st.markdown("<h3>Filter Products</h3>", unsafe_allow_html=True)
    
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        category = st.selectbox("Filter by Category:", ["All", "Electronics", "Fashion", "Books", "Home Appliances"])
    
    with filter_col2:
        price_range = st.slider("Filter by Price Range ($):", 0, 500, (0, 500))
    
    search_button = st.button("Search Products", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Process search
    if search_button and query:
        st.session_state.search_history.append(query)
        recommendations = get_recommendations(query)
        
        if recommendations:
            st.markdown("<div class='section-header'>Recommended Products</div>", unsafe_allow_html=True)
            
            # Filter products based on criteria
            filtered_products = []
            for product in recommendations:
                try:
                    price = float(product.get('price', 0))
                except ValueError:
                    price = 0
                
                # Apply filters
                if (category == "All" or product.get('category') == category) and (price_range[0] <= price <= price_range[1]):
                    filtered_products.append(product)
            
            if filtered_products:
                # Create two-column layout for products
                cols = st.columns(2)
                
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
                        st.image(product.get('image_url', 'https://via.placeholder.com/150'), width=150)
                        
                        # Add to cart button
                        st.button("Add to Cart", key=f"cart_{index}", on_click=add_to_cart, args=(product,))
            else:
                st.warning("No products match your filters. Try adjusting your criteria.")
        else:
            st.warning("No recommendations found! Try a different search term.")

with sidebar_col:
    # Shopping Cart section - White background
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    st.markdown("<h3>🛒 Your Shopping Cart</h3>", unsafe_allow_html=True)
    
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
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Search History section - White background
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    st.markdown("<h3>🔍 Recent Searches</h3>", unsafe_allow_html=True)
    
    if st.session_state.search_history:
        for hist in st.session_state.search_history[-5:]:
            st.markdown(f"• {hist}")
    else:
        st.info("No search history yet.")
    st.markdown("</div>", unsafe_allow_html=True)
