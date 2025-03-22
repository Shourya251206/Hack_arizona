import streamlit as st
import requests

# Page Configuration
st.set_page_config(page_title="Product Recommendation System", page_icon="🛒", layout="centered")

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .title {
        color: #2c3e50;
        text-align: center;
        font-size: 32px;
        font-weight: bold;
    }
    .product-card {
        background-color: #ffffff;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .add-cart-btn {
        background-color: #ff7f50;
        color: white;
        border-radius: 5px;
        padding: 8px 15px;
        cursor: pointer;
        text-align: center;
    }
    .add-cart-btn:hover {
        background-color: #e67e22;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown('<div class="title">🛍️ Product Recommendation System</div>', unsafe_allow_html=True)

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
                    
                    for product in data["recommendations"]:
                        with st.container():
                            st.markdown(
                                f"""
                                <div class='product-card'>
                                    <h4>{product['name']}</h4>
                                    <p><strong>Price:</strong> ${product['price']}</p>
                                    <button class='add-cart-btn' onclick='alert("{product['name']} added to cart!")'>Add to Cart</button>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                else:
                    st.warning("No recommendations found. Try another query.")
            else:
                st.error("Error fetching recommendations from the backend.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query before submitting.")