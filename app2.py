import streamlit as st
import requests

# Page config
st.set_page_config(page_title="Product Search", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .mic-button {
        background-color: #ff5733;
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.3s;
    }
    .mic-button:hover {
        background-color: #e74c3c;
    }
    .stButton>button {
        background-color: #1e3d59;
        color: white;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center; color: #1e3d59;'>Smart Product Search</h1>", unsafe_allow_html=True)

# Layout for input, mic, and filters
col1, col2 = st.columns([4, 1])

with col1:
    # Search input with session state
    if "search_input" not in st.session_state:
        st.session_state.search_input = ""
    search_input = st.text_input("Enter a product name (e.g., 'running shoes')", 
                                value=st.session_state.search_input, 
                                key="search_input")

with col2:
    # Microphone button (simplified, triggers a placeholder action)
    if st.button("🎤 Speak", key="mic_button"):
        # Placeholder: Sets a dummy value; replace with actual speech logic if backend supports it
        st.session_state.search_input = "Speech input not fully implemented"
        st.warning("Mic functionality requires backend speech-to-text integration.")

# Filters
st.markdown("### Filters")
col3, col4 = st.columns(2)
with col3:
    sort_order = st.selectbox("Sort by Price", ["None", "Low to High", "High to Low"], key="sort_order")
with col4:
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1, key="min_rating")

# API Call Function
def get_recommendations(query_params):
    try:
        response = requests.post("http://127.0.0.1:8000/recommend", json=query_params, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
        return {"recommendations": []}

# Fetch Recommendations
if st.button("Get Recommendations", key="submit_button"):
    query_params = {"keywords": st.session_state.search_input}

    if sort_order == "Low to High":
        query_params["sort"] = "asc"
    elif sort_order == "High to Low":
        query_params["sort"] = "desc"
    if min_rating > 0:
        query_params["min_rating"] = min_rating

    with st.spinner("Finding the best products for you..."):
        result = get_recommendations(query_params)

    if result.get("recommendations"):
        st.subheader("Top Recommendations")
        for product in result["recommendations"][:10]:  # Top 10 results
            st.write(f"**{product['title']}** - ${product['price']} - ⭐ {product['rating']}")
            st.markdown(f"[View on Amazon](https://www.amazon.com/s?k={product['title'].replace(' ', '+')})")
    else:
        st.info("No recommendations found. Try different criteria.")

# Debug: Show current session state (optional, remove for final version)
# st.write("Debug - Current Search Input:", st.session_state.search_input)
