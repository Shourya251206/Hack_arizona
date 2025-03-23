import streamlit as st
import requests
import speech_recognition as sr

# Configure page
st.set_page_config(page_title="Product Recommendations", layout="wide")

# Custom CSS (updated to make mic icon white)
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton button {
        background-color: #1e3d59 !important;
        color: white !important;
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > input {
        border: 2px solid #1e3d59;
    }
    h1, h2, h3 {
        color: #1e3d59;
    }
    .product-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-top: 4px solid #1e3d59;
        border-bottom: 4px solid #ff6b6b;
    }
    .recommendation-header {
        background-color: #1e3d59;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .mic-container {
        display: flex;
        align-items: center;
    }
    /* Specific styling for the mic button */
    button[kind="mic_button"] {
        background-color: #1e3d59 !important;  /* Matches your theme */
        color: white !important;              /* Makes the mic icon white */
        font-size: 24px !important;
        padding: 5px 10px !important;
        border: none !important;
        border-radius: 5px !important;
        margin-left: 10px !important;
        cursor: pointer !important;
    }
    button[kind="mic_button"]:hover {
        background-color: #355d82 !important; /* Slightly lighter on hover */
    }
    .sort-container {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 style='text-align: center; color: #1e3d59;'>Smart Product Recommendations</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #1e3d59;'>Find the perfect products based on your preferences</p>", unsafe_allow_html=True)

# Voice-to-text function
def voice_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak your keywords!")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.success("Heard: " + text)
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I couldn't understand that.")
            return ""
        except sr.RequestError:
            st.error("Speech recognition service unavailable.")
            return ""

# Inputs
col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
with col1:
    # Keywords input with mic icon in a container
    st.markdown('<div class="mic-container">', unsafe_allow_html=True)
    keywords = st.text_input("Enter keywords (e.g., 'running shoes')", key="keywords")
    if st.button("🎤", key="mic_button", type="primary"):  # Added type="primary" for consistency
        keywords = voice_to_text()
        st.session_state["keywords"] = keywords
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    price = st.number_input("Maximum price", min_value=0.0, value=0.0, step=5.0)
with col3:
    stars = st.slider("Minimum star rating", min_value=0.0, max_value=5.0, value=0.0, step=0.5)
with col4:
    search_button = st.button("Get Recommendations", use_container_width=True)

# Backend call
def get_recommendations(query_params):
    try:
        response = requests.post("http://127.0.0.1:8000/recommend", json=query_params)
        return response.json()
    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
        return {"recommendations": []}

# Display results
if search_button and keywords:
    query_params = {}
    if keywords:
        query_params["keywords"] = keywords
    if price > 0:
        query_params["price"] = price
    if stars > 0:
        query_params["stars"] = stars

    if price == 0:
        st.warning("You can't buy products for free! Please set a maximum price greater than 0.")
    else:
        with st.spinner("Finding the best products for you..."):
            result = get_recommendations(query_params)

        # Debug raw response
        with st.expander("Debug: Raw Backend Response"):
            st.json(result)

        if result.get("recommendations"):
            # Sorting options
            st.markdown('<div class="sort-container">', unsafe_allow_html=True)
            sort_option = st.selectbox(
                "Sort by price:",
                ["Default", "Low to High", "High to Low"],
                key="sort_select",
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            # Sort recommendations
            recommendations = result["recommendations"]
            if sort_option == "Low to High":
                recommendations = sorted(recommendations, key=lambda x: float(x["price"]))
            elif sort_option == "High to Low":
                recommendations = sorted(recommendations, key=lambda x: float(x["price"]), reverse=True)

            st.markdown("<div class='recommendation-header'><h2 style='text-align: center;'>Recommended Products</h2></div>", unsafe_allow_html=True)

            for product in recommendations:
                st.markdown("<div class='product-card'>", unsafe_allow_html=True)
                cols = st.columns([1, 3])

                with cols[0]:
                    img_url = product.get("imgURL", "")
                    try:
                        if img_url and img_url.startswith("http"):
                            st.image(img_url, width=140)
                        else:
                            raise Exception("Invalid or missing image URL")
                    except:
                        st.image("https://via.placeholder.com/150?text=No+Image", width=140)

                with cols[1]:
                    title = product.get("title", "Unnamed Product")
                    product_url = f"https://www.amazon.com/s?k={title.replace(' ', '+')}"

                    st.markdown(f"<h3><a href='{product_url}' target='_blank' style='text-decoration:none; color:#1e3d59;'>{title}</a></h3>", unsafe_allow_html=True)
                    
                    # Handle price with error checking
                    raw_price = product.get("price", "N/A")
                    try:
                        price_value = float(raw_price)
                        st.markdown(f"<p><strong>Price:</strong> ${price_value:.2f}</p>", unsafe_allow_html=True)
                    except (ValueError, TypeError):
                        st.markdown(f"<p><strong>Price:</strong> {raw_price} (Invalid format)</p>", unsafe_allow_html=True)
                    
                    # Handle rating
                    if "rating" in product:
                        try:
                            rating = float(product["rating"])
                            st.markdown(f"<p><strong>Rating:</strong> {'⭐' * int(rating)} ({rating:.1f})</p>", unsafe_allow_html=True)
                        except (ValueError, TypeError):
                            st.markdown(f"<p><strong>Rating:</strong> {product['rating']} (Invalid format)</p>", unsafe_allow_html=True)
                    
                    # Handle category
                    category = product.get("category", "Not specified")
                    st.markdown(f"<p><strong>Category:</strong> {category}</p>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No recommendations found. Try different criteria.")
else:
    st.info("Enter product keywords and click 'Get Recommendations'.")

# Footer
st.markdown("""
<div style='text-align: center; margin-top: 50px; padding: 20px; color: #666;'>
    <p>© 2025 Product Recommendation System | All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
