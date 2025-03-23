import streamlit as st
import requests

def get_product_recommendations(query):
    url = "https://your-backend-api.com/recommend"
    params = {"query": query}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("products", [])
    except requests.exceptions.RequestException:
        return []

st.set_page_config(page_title="Product Finder", layout="wide")
st.markdown("""
    <style>
        .stApp {
            background-color: #1C39BB; /* Persian Blue */
        }
        .search-bar {
            background-color: red;
            padding: 10px;
            border-radius: 5px;
        }
        .product-card {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar: Cart and Search History
with st.sidebar:
    st.title("🛒 Shopping Cart")
    cart = st.session_state.get("cart", [])
    for item in cart:
        st.write(f"- {item}")
    st.title("🔍 Search History")
    search_history = st.session_state.get("search_history", [])
    for query in search_history:
        st.write(f"- {query}")

# Main Content
st.markdown("<div class='search-bar'>", unsafe_allow_html=True)
query = st.text_input("Search for a product:", key="search_input")
st.markdown("</div>", unsafe_allow_html=True)

if st.button("Search"):
    if query:
        recommendations = get_product_recommendations(query)
        if "search_history" not in st.session_state:
            st.session_state["search_history"] = []
        st.session_state["search_history"].append(query)

        if recommendations:
            st.subheader("Recommended Products:")
            col1, col2 = st.columns(2)
            for index, product in enumerate(recommendations):
                with (col1 if index % 2 == 0 else col2):
                    st.markdown(f"""
                        <div class='product-card'>
                            <h4>{product['name']}</h4>
                            <p>Price: ${product['price']}</p>
                            <button onclick="st.session_state['cart'].append('{product['name']}')">Add to Cart</button>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("No products found. Try another search!")
