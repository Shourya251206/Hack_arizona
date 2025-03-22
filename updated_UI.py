import streamlit as st
import requests

# Page Configuration
st.set_page_config(page_title="Product Recommendation System", page_icon="🛒", layout="wide")

# Custom CSS for styling - improved color scheme and visual design
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .title {
        color: #4361ee;
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 20px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .product-card {
        background-color: #ffffff;
        padding: 20px;
        margin: 15px 0;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid #e0e0e0;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    }
    .product-image {
        width: 180px;
        height: auto;
        border-radius: 8px;
        margin-bottom: 15px;
        object-fit: cover;
    }
    .product-price {
        font-size: 20px;
        font-weight: bold;
        color: #4361ee;
        margin: 10px 0;
    }
    .product-name {
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 10px;
        color: #2b2d42;
    }
    .add-cart-btn {
        background-color: #4361ee;
        color: white;
        border-radius: 8px;
        padding: 10px 18px;
        cursor: pointer;
        text-align: center;
        border: none;
        font-weight: bold;
        margin-top: 10px;
        transition: background-color 0.3s ease;
        width: 100%;
    }
    .add-cart-btn:hover {
        background-color: #3a56d4;
    }
    .history-section {
        margin-top: 25px;
        padding: 15px;
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
    }
    .sidebar-header {
        color: #4361ee;
        font-weight: bold;
        font-size: 20px;
        margin-bottom: 15px;
    }
    .cart-item {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        border-left: 4px solid #4361ee;
    }
    .search-btn {
        background-color: #4361ee;
        color: white;
        border-radius: 8px;
        padding: 8px 15px;
        width: 100%;
        margin-top: 10px;
    }
    .cart-total {
        font-weight: bold;
        margin-top: 15px;
        padding-top: 10px;
        border-top: 1px solid #e0e0e0;
    }
    .empty-state {
        text-align: center;
        color: #6c757d;
        padding: 30px;
        font-style: italic;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar for User Input with improved styling
st.sidebar.markdown('<div class="sidebar-header">🔍 Search for Products</div>', unsafe_allow_html=True)
query = st.sidebar.text_input("Enter your preference (e.g., 'running shoes under $100'):")

# Initialize session state for history & cart if not already set
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "cart" not in st.session_state:
    st.session_state.cart = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Dark Mode Toggle with better explanation
dark_mode_toggle = st.sidebar.checkbox("🌙 Enable Dark Mode", st.session_state.dark_mode)
if dark_mode_toggle != st.session_state.dark_mode:
    st.session_state.dark_mode = dark_mode_toggle
    st.experimental_rerun()

# Apply Dark Mode CSS if enabled - enhanced for better contrast and readability
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #121212;
            color: #e0e0e0;
        }
        .title {
            color: #738bff;
        }
        .product-card {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #333;
        }
        .product-name {
            color: #e0e0e0;
        }
        .product-price {
            color: #738bff;
        }
        .history-section {
            background-color: #1e1e1e;
        }
        .cart-item {
            background-color: #262626;
            border-left: 4px solid #738bff;
        }
        .empty-state {
            color: #adb5bd;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Get Recommendations - Enhanced button styling
if st.sidebar.button("🔍 Get Recommendations", key="recommend_btn", help="Click to find products matching your query"):
    if query:
        try:
            # Replace with actual API endpoint
            response = requests.get(f"http://127.0.0.1:8000/recommend?query={query}")
            if response.status_code == 200:
                data = response.json()
                if data["recommendations"]:
                    st.markdown('<div class="title">🛍️ Recommended Products</div>', unsafe_allow_html=True)
                    product_list = []
                    
                    # Display products in a grid layout
                    cols = st.columns(3)
                    for i, product in enumerate(data["recommendations"]):
                        product_list.append({"name": product['name'], "price": product['price'], "image_url": product['image_url']})
                        with cols[i % 3]:
                            st.markdown(f"""
                            <div class="product-card">
                                <img src="{product['image_url']}" class="product-image">
                                <div class="product-name">{product['name']}</div>
                                <div class="product-price">${product['price']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button(f"🛒 Add to Cart", key=f"add_{product['name']}"):
                                st.session_state.cart.append(product)
                                st.success(f"{product['name']} added to cart!")
                    
                    # Save search history
                    st.session_state.search_history.append({"query": query, "products": product_list})
                else:
                    st.sidebar.warning("No recommendations found. Try another query.")
            else:
                st.sidebar.error("Error fetching recommendations from the backend.")
        except Exception as e:
            st.sidebar.error(f"An error occurred: {e}")
    else:
        st.sidebar.warning("Please enter a query before submitting.")

# Display Cart with improved styling and functionality
st.sidebar.markdown('<div class="sidebar-header">🛒 Shopping Cart</div>', unsafe_allow_html=True)
if st.session_state.cart:
    total = 0
    for item in st.session_state.cart:
        price = float(item['price'])
        total += price
        st.sidebar.markdown(f"""
        <div class="cart-item">
            <strong>{item['name']}</strong><br>
            ${item['price']}
        </div>
        """, unsafe_allow_html=True)
    
    # Show cart total
    st.sidebar.markdown(f'<div class="cart-total">Total: ${total:.2f}</div>', unsafe_allow_html=True)
    
    # Checkout button
    if st.sidebar.button("✅ Proceed to Checkout", key="checkout"):
        st.sidebar.success("Checkout process initiated!")
        
    # Clear cart button
    if st.sidebar.button("🗑️ Clear Cart", key="clear_cart"):
        st.session_state.cart = []
        st.experimental_rerun()
else:
    st.sidebar.markdown('<div class="empty-state">Your cart is empty</div>', unsafe_allow_html=True)

# Display Search History with enhanced styling
if st.session_state.search_history:
    with st.expander("📜 View Search History"):
        for i, entry in enumerate(reversed(st.session_state.search_history)):
            st.write(f"**Search Query #{i+1}:** {entry['query']}")
            
            # Display products in a horizontal layout
            cols = st.columns(min(3, len(entry["products"])))
            for j, product in enumerate(entry["products"]):
                with cols[j % len(cols)]:
                    st.image(product['image_url'], width=100)
                    st.write(f"**{product['name']}**")
                    st.write(f"${product['price']}")
            st.markdown("---")
else:
    st.markdown('<div class="empty-state">Your search history will appear here</div>', unsafe_allow_html=True)

# Display welcome message when no products are shown
if not query:
    st.markdown('<div class="title">Welcome to Smart Shop</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 30px;">
        <h3>Start by searching for products you're interested in</h3>
        <p>Enter keywords, price ranges, or specific product types in the search box</p>
    </div>
    """, unsafe_allow_html=True)