import streamlit as st
import requests

# Set page config first (must be the first Streamlit command)
st.set_page_config(
    page_title="Smart Product Recommender",
    page_icon="🛍️",
    layout="wide"
)

# Choose one of these light blue colors:
# LIGHT_BLUE = "#E3F2FD"  # Very light blue (Material UI)
# LIGHT_BLUE = "#BBDEFB"  # Light blue (Material UI)
LIGHT_BLUE = "#90CAF9"  # Medium light blue (Material UI)
# LIGHT_BLUE = "#64B5F6"  # Slightly darker light blue (Material UI)
# LIGHT_BLUE = "#B3E5FC"  # Light cyan blue (Material UI)
# LIGHT_BLUE = "#D4F1F9"  # Very soft light blue
# LIGHT_BLUE = "#CCE5FF"  # Soft blue (Bootstrap)

# Define the red color
RED_COLOR = "#FF0000"  # Pure red
# RED_COLOR = "#F44336"  # Material UI red (slightly softer)

# Apply base CSS for the color scheme
st.markdown(f"""
<style>
    /* Main background - Light Blue */
    .main {{
        background-color: {LIGHT_BLUE};
    }}
    
    /* Make the content area light blue */
    .block-container {{
        background-color: {LIGHT_BLUE};
        padding: 1rem;
    }}
    
    /* Make sure text is visible */
    p, h1, h2, h3, h4, h5, h6 {{
        color: black;
    }}
    
    /* Custom classes */
    .white-container {{
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }}
    
    .red-container {{
        background-color: {RED_COLOR};
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }}
    
    /* Make buttons red */
    .stButton > button {{
        background-color: {RED_COLOR} !important;
        color: white !important;
        border: none !important;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Function to fetch recommendations
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

# App title
st.title("🛍️ Smart Product Recommender")

# Create two columns for layout
col1, col2 = st.columns([3, 1])

with col1:
    # Search section - RED container
    st.markdown("<div class='red-container'>", unsafe_allow_html=True)
    query = st.text_input("Enter a product name or keyword:", "")
    search_button = st.button("Search Products", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Filters section - WHITE container
    st.markdown("<div class='white-container'>", unsafe_allow_html=True)
    st.subheader("Filter Products")
    
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        category = st.selectbox("Category:", ["All", "Electronics", "Fashion", "Books", "Home Appliances"])
    with filter_col2:
        price_range = st.slider("Price Range ($):", 0, 500, (0, 500))
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Process search
    if search_button and query:
        st.session_state.search_history.append(query)
        recommendations = get_recommendations(query)
        
        # Results section - WHITE container
        st.markdown("<div class='white-container'>", unsafe_allow_html=True)
        st.subheader("Recommended Products")
        
        if recommendations:
            # Filter products
            filtered_products = []
            for product in recommendations:
                try:
                    price = float(product.get('price', 0))
                except ValueError:
                    price = 0
                
                if (category == "All" or product.get('category') == category) and \
                   (price_range[0] <= price <= price_range[1]):
                    filtered_products.append(product)
            
            if filtered_products:
                # Create product grid
                product_cols = st.columns(2)
                for idx, product in enumerate(filtered_products):
                    with product_cols[idx % 2]:
                        st.write(f"**{product['name']}**")
                        st.write(f"Category: {product.get('category', 'Unknown')}")
                        st.write(f"Price: ${product.get('price', 0)}")
                        st.image(product.get('image_url', 'https://via.placeholder.com/150'), width=150)
                        st.button("Add to Cart", key=f"add_{idx}", on_click=add_to_cart, args=(product,))
                        st.write("---")
            else:
                st.write("No products match your filters. Try adjusting your criteria.")
        else:
            st.write("No recommendations found. Try a different search term.")
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # Cart section - WHITE container
    st.markdown("<div class='white-container'>", unsafe_allow_html=True)
    st.subheader("🛒 Your Cart")
    
    if st.session_state.cart:
        total = sum(float(item.get('price', 0)) for item in st.session_state.cart)
        
        for i, item in enumerate(st.session_state.cart):
            st.write(f"**{item['name']}** - ${item.get('price', 0)}")
            st.button("Remove", key=f"remove_{i}", on_click=remove_from_cart, args=(i,))
            st.write("---")
        
        st.write(f"**Total: ${total:.2f}**")
        if st.button("Clear Cart"):
            st.session_state.cart = []
            st.experimental_rerun()
    else:
        st.write("Your cart is empty.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Search history - WHITE container
    st.markdown("<div class='white-container'>", unsafe_allow_html=True)
    st.subheader("🔍 Recent Searches")
    
    if st.session_state.search_history:
        for search in st.session_state.search_history[-5:]:
            st.write(f"• {search}")
    else:
        st.write("No search history yet.")
    st.markdown("</div>", unsafe_allow_html=True)
