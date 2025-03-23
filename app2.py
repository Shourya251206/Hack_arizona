import streamlit as st
import requests
import speech_recognition as sr

# Configure page
st.set_page_config(page_title="Product Recommendations", layout="wide")

# Custom CSS (kept minimal and adjusted for mic icon)
st.markdown("""
<style>
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
    /* Specific styling for the mic button */
    button[kind="mic_button"] {
        background-color: #1e3d59 !important;
        color: white !important;
        font-size: 24px !important;
        padding: 5px 10px !important;
        border: none !important;
        border-radius: 5px !important;
        margin-left: 10px !important;
        cursor: pointer !important;
    }
    button[kind="mic_button"]:hover {
        background-color: #355d82 !important;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("Product Recommendation System")

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

# User Input Fields
keywords = st.text_input("Enter keywords (e.g., 'running shoes')", "")
if st.button("🎤", key="mic_button", type="primary"):
    keywords = voice_to_text()
    st.session_state["keywords"] = keywords

price = st.number_input("Maximum price (optional)", min_value=0.0, value=0.0, step=10.0)
stars = st.slider("Minimum star rating (optional)", min_value=0.0, max_value=5.0, value=0.0, step=0.5)

# Submit Button
if st.button("Get Recommendations"):
    # Prepare query parameters (only include non-default values)
    query_params = {}
    if keywords:
        query_params["keywords"] = keywords
    if price > 0:  # Only include if user sets a value greater than 0
        query_params["price"] = price
    if stars > 0:  # Only include if user sets a minimum
        query_params["stars"] = stars

    # Check if price is 0 before proceeding
    if price == 0 and not keywords and not stars:
        st.warning("You can't buy products for free! Please set a maximum price greater than 0 or enter keywords/stars.")
    elif query_params:  # Proceed only if there are valid parameters
        try:
            # Send POST request to backend
            response = requests.post(
                "http://127.0.0.1:8000/recommend",
                json=query_params
            )
            if response.status_code == 200:
                data = response.json()

                # Debug raw response
                with st.expander("Debug: Raw Backend Response"):
                    st.json(data)

                if data["recommendations"]:
                    st.write("### Recommended Products:")
                    # Sorting options
                    sort_option = st.selectbox(
                        "Sort by price:",
                        ["Default", "Low to High", "High to Low"],
                        key="sort_select"
                    )
                    
                    # Sort recommendations
                    recommendations = data["recommendations"]
                    if sort_option == "Low to High":
                        recommendations = sorted(recommendations, key=lambda x: float(x["price"]))
                    elif sort_option == "High to Low":
                        recommendations = sorted(recommendations, key=lambda x: float(x["price"]), reverse=True)

                    for product in recommendations:
                        st.markdown("----")
                        cols = st.columns([1, 3])  # Left for image, right for details

                        with cols[0]:
                            if product.get("imgURL"):
                                st.image(product["imgURL"], width=120)

                        with cols[1]:
                            title = product.get("title", "Unnamed Product")
                            product_url = f"https://www.amazon.com/s?k={title.replace(' ', '+')}"

                            if product_url and product_url.startswith("http"):
                                st.markdown(f'<a href="{product_url}" target="_blank"><strong>{title}</strong></a>', unsafe_allow_html=True)
                            else:
                                st.markdown(f"**{title}**")

                            # Handle price with error checking
                            raw_price = product.get("price", "N/A")
                            try:
                                price_value = float(raw_price)
                                st.write(f"${price_value:.2f}")
                            except (ValueError, TypeError):
                                st.write(f"Price: {raw_price} (Invalid format)")

                            if "rating" in product:
                                try:
                                    rating = float(product["rating"])
                                    st.write(f"Rating: {rating} ★ ({product.get('review_count', 0)} reviews)")
                                except (ValueError, TypeError):
                                    st.write(f"Rating: {product['rating']} (Invalid format)")
                            if "category" in product:
                                st.write(f"Category: {product['category']}")
                else:
                    st.write("No recommendations found. Try adjusting your query.")
            else:
                st.error(f"Error fetching recommendations: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter at least one preference (keywords, price, or stars).")
