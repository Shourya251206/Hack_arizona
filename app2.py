import streamlit as st
import requests

# Page config
st.set_page_config(page_title="Product Search", layout="wide")

# Custom JavaScript for Speech-to-Text
st.markdown("""
<script>
function startDictation() {
    if (window.hasOwnProperty('webkitSpeechRecognition')) {
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";
        recognition.start();

        recognition.onresult = function(event) {
            var result = event.results[0][0].transcript;
            document.getElementById("search_input").value = result;
            document.getElementById("hidden_input").value = result;
            document.getElementById("submit_button").click();
        };

        recognition.onerror = function(event) {
            console.log("Speech recognition error:", event);
        };
    }
}
</script>
""", unsafe_allow_html=True)

# Custom CSS for styling the microphone button
st.markdown("""
<style>
    .mic-button {
        background-color: #ff5733; /* Bright orange */
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.3s;
    }
    .mic-button:hover {
        background-color: #e74c3c; /* Slightly darker on hover */
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center; color: #1e3d59;'>Smart Product Search</h1>", unsafe_allow_html=True)

# Search Input and Mic Button
col1, col2 = st.columns([4, 1])

with col1:
    search_input = st.text_input("Enter a product name", key="search_input")

with col2:
    # Microphone Button (Uses Web Speech API)
    st.markdown('<button class="mic-button" onclick="startDictation()">🎤 Speak</button>', unsafe_allow_html=True)

# Hidden input to pass speech results
st.text_input("", key="hidden_input", label_visibility="collapsed")

# Sorting filter
sort_order = st.selectbox("Sort by Price", ["None", "Low to High", "High to Low"])

# API Call Function
def get_recommendations(query_params):
    try:
        response = requests.post("http://127.0.0.1:8000/recommend", json=query_params)
        return response.json()
    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
        return {"recommendations": []}

# Fetch Recommendations
if st.button("Get Recommendations", key="submit_button"):
    query_params = {"keywords": search_input}

    if sort_order == "Low to High":
        query_params["sort"] = "asc"
    elif sort_order == "High to Low":
        query_params["sort"] = "desc"

    with st.spinner("Finding the best products for you..."):
        result = get_recommendations(query_params)

    if result.get("recommendations"):
        for product in result["recommendations"]:
            st.write(f"**{product['title']}** - ${product['price']} - ⭐ {product['rating']}")
            st.markdown(f"[View on Amazon](https://www.amazon.com/s?k={product['title'].replace(' ', '+')})")

    else:
        st.info("No recommendations found. Try different criteria.")
