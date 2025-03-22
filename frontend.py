import streamlit as st
import requests

# Page Configuration
st.set_page_config(page_title="Product Recommendation System", page_icon="🛒", layout="centered")

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffffff;
    }
    .title {
        color: #d32f2f;
        text-align: center;
        font-size: 32px;
        font-weight: bold;
    }
    .product-card {
        background-color: #ffffff;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 255, 0.2);
        text-align: center;
        border: 2px solid #d32f2f;
    }
    .product-image {
        width: 150px;
        height: auto;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 2px solid #0d47a1;
    }
    .add-cart-btn {
        background-color: #d32f2f;
        color: white;
        border-radius: 5px;
        padding: 8px 15px;
        cursor: pointer;
        text-align: center;
        border: none;
        font-weight: bold;
    }
    .add-cart-btn:hover {
        background-color: #b71c1c;
    }
    .history-section {
        margin-top: 20px;
        padding: 10px;
        background-color: #f5f5f5;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown('<div class="title">🛍️ Product Recommendation System</div>', unsafe_allow_html=True)

# Initialize session state for history if not already set
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# User Input Field
query = st.text_input("Enter your preference (e.g., 'running shoes under $100'):")

# Submit Button
if st.button("Get Recommendations", key="recommend_btn"):
    if query:
        try:
            # Replace with actual API endpoint
            response = requests.get(f"http://127.0.0.1:8000/recommend?query={query}")
            if response.status_code == 200:
                data = response.json()
                if data["recommendations"]:
                    st.write("### Recommended Products:")
                    product_list = []
                    for product in data["recommendations"]:
                        product_list.append({"name": product['name'], "price": product['price'], "image_url": product['image_url']})
                        with st.container():
                            st.markdown(
                                f"""
                                <div class='product-card'>
                                    <img src='{product['image_url']}' class='product-image' alt='Product Image'>
                                    <h4 style='color:#0d47a1'>{product['name']}</h4>
                                    <p><strong>Price:</strong> <span style='color:#d32f2f'>${product['price']}</span></p>
                                    <button class='add-cart-btn' onclick='alert("{product['name']} added to cart!")'>Add to Cart</button>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    
                    # Save search history
                    st.session_state.search_history.append({"query": query, "products": product_list})
                else:
                    st.warning("No recommendations found. Try another query.")
            else:
                st.error("Error fetching recommendations from the backend.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query before submitting.")

# Display Search History
if st.session_state.search_history:
    st.write("### Search History")
    for entry in st.session_state.search_history:
        st.write(f"**Search Query:** {entry['query']}")
        for product in entry["products"]:
            with st.container():
                st.markdown(
                    f"""
                    <div class='product-card'>
                        <img src='{product['image_url']}' class='product-image' alt='Product Image'>
                        <h4 style='color:#0d47a1'>{product['name']}</h4>
                        <p><strong>Price:</strong> <span style='color:#d32f2f'>${product['price']}</span></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        st.write("---")
