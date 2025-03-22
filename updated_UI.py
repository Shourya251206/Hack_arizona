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
    .subtitle {
        color: #555;
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }
    .search-container {
        background-color: #fff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 30px;
    }
    .search-title {
        color: #4361ee;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 15px;
        text-align: center;
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
        padding: 12px 15px;
        font-weight: bold;
        width: 100%;
        transition: background-color 0.3s ease;
    }
    .search-btn:hover {
        background-color: #3a56d4;
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
    .zero-price-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #ffc107;
        margin: 15px 0;
        text-align: center;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for history & cart if not already set
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "cart" not in st.session_state:
    st.session_state.cart = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "price_range" not in st.session_state:
    st.session_state.price_range = (0, 1000)

# Dark Mode Toggle in sidebar
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
        .subtitle {
            color: #aaa;
        }
        .search-container {
            background-color: #1e1e1e;
            border: 1px solid #333;
        }
        .search-title {
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
        .zero-price-message {
            background-color: #332701;
            color: #ffda6a;
            border-left: 5px solid #ffda6a;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Display the main title
st.markdown('<div class="title">Smart Shop</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Find the perfect products for your needs</div>', unsafe_allow_html=True)

# Central search container instead of sidebar
st.markdown('<div class="search-container">', unsafe_allow_html=True)
st.markdown('<div class="search-title">🔍 Search for Products</div>', unsafe_allow_html=True)

# Three input elements in columns
col1, col2, col3 = st.columns([3, 2, 1])

with col1:
    # 1. Keywords search input
    query = st.text_input("Enter keywords (e.g., 'running shoes', 'laptop')", key="search_keywords")

with col2:
    # 2. Price range slider
    price_range = st.slider("Price Range ($)", 0, 1000, st.session_state.price_range, key="price_slider")
    st.session_state.price_range = price_range

with col3:
    # 3. Search button (with space above to align with other elements)
    st.write("")  # Add some space to align with the inputs
    search_clicked = st.button("🔍 Search", key="search_button", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close search container

# Process search when the button is clicked
if search_clicked:
    if query:
        try:
            # Modify API request to include price range
            min_price, max_price = price_range
            # Replace with actual API endpoint
            response = requests.get(f"http://127.0.0.1:8000/recommend?query={query}&min_price={min_price}&max_price={max_price}")
            
            if response.status_code == 200:
                data = response.json()
                if data["recommendations"]:
                    st.markdown('<div class="title">🛍️ Recommended Products</div>', unsafe_allow_html=True)
                    product_list = []
                    
                    # Filter out zero-priced items and check if any valid products remain
                    valid_products = [product for product in data["recommendations"] 
                                      if float(product['price']) > 0]
                    
                    # Show a message if all products are priced at $0
                    if not valid_products and data["recommendations"]:
                        st.markdown(
                            '<div class="zero-price-message">⚠️ No items found for $0. Try a different search query.</div>',
                            unsafe_allow_html=True
                        )
                    
                    # Display products in a grid layout - only non-zero priced items
                    if valid_products:
                        cols = st.columns(3)
                        for i, product in enumerate(valid_products):
                            product_list.append({"name": product['name'], "price": product['price'], 
                                              "image_url": product['image_url']})
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
                    
                    # Save search history (including the message about zero-priced items)
                    if product_list:
                        st.session_state.search_history.append({
                            "query": query, 
                            "price_range": price_range,
                            "products": product_list
                        })
                else:
                    st.warning("No recommendations found matching your criteria. Try adjusting your search or price range.")
            else:
                st.error("Error fetching recommendations from the backend.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter keywords before searching.")

# Display Cart in sidebar with improved styling and functionality
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
            price_info = f"Price range: ${entry.get('price_range', (0, 1000))[0]} - ${entry.get('price_range', (0, 1000))[1]}"
            st.write(f"**Search #{i+1}:** {entry['query']} ({price_info})")
            
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

# Display welcome message when no products are shown yet
if not search_clicked and not st.session_state.search_history:
    st.markdown("""
    <div style="text-align: center; padding: 30px; margin-top: 20px;">
        <h3>Ready to shop? Enter your search criteria above</h3>
        <p>Use the search box to find products, adjust the price range to fit your budget, and click search!</p>
        <p>Your product recommendations will appear here</p>
    </div>
    """, unsafe_allow_html=True)