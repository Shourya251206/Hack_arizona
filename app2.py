import streamlit as st
import requests

# Page config
st.set_page_config(page_title="Product Search", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .mic-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 10px;
    }
    .mic-button {
        background-color: #ff5733;
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .mic-button:hover {
        background-color: #e74c3c;
    }
    .mic-button svg {
        margin-right: 8px;
    }
    .filter-container {
        margin-top: 20px;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    .product-card {
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        border: 1px solid #ddd;
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# JavaScript for Speech Recognition with proper Streamlit integration
st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Find the microphone button after the DOM is fully loaded
    setTimeout(function() {
        const micButton = document.querySelector('.mic-button');
        if (micButton) {
            micButton.addEventListener('click', startDictation);
        }
    }, 1000);

    function startDictation() {
        if ('webkitSpeechRecognition' in window) {
            const recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = "en-US";
            
            // Visual feedback that mic is active
            const micButton = document.querySelector('.mic-button');
            if (micButton) {
                const originalText = micButton.innerHTML;
                micButton.innerHTML = '🎤 Listening...';
                micButton.style.backgroundColor = '#27ae60';
            }
            
            recognition.start();
            
            recognition.onresult = function(event) {
                const result = event.results[0][0].transcript;
                
                // Find the search input field and update its value
                const searchInputs = document.querySelectorAll('input[type="text"]');
                if (searchInputs.length > 0) {
                    const searchInput = searchInputs[0];
                    searchInput.value = result;
                    
                    // Dispatch events to make Streamlit recognize the change
                    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                    searchInput.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    // Trigger search button click
                    setTimeout(function() {
                        const searchButton = document.querySelector('button[kind="primary"]');
                        if (searchButton) {
                            searchButton.click();
                        }
                    }, 500);
                }
                
                // Reset mic button
                if (micButton) {
                    micButton.innerHTML = originalText;
                    micButton.style.backgroundColor = '#ff5733';
                }
            };
            
            recognition.onerror = function(event) {
                console.error("Speech recognition error:", event.error);
                // Reset mic button on error
                if (micButton) {
                    micButton.innerHTML = originalText;
                    micButton.style.backgroundColor = '#ff5733';
                }
            };
            
            recognition.onend = function() {
                // Reset mic button when recognition ends
                if (micButton) {
                    micButton.innerHTML = originalText;
                    micButton.style.backgroundColor = '#ff5733';
                }
            };
        } else {
            alert("Your browser doesn't support speech recognition. Please try Chrome.");
        }
    }
});
</script>
""", unsafe_allow_html=True)

# Title with improved styling
st.markdown("<h1 style='text-align: center; color: #1e3d59; margin-bottom: 30px;'>Smart Product Search</h1>", unsafe_allow_html=True)

# Search Input with Mic Button
col1, col2 = st.columns([4, 1])

with col1:
    search_input = st.text_input("Enter a product name", key="search_input", placeholder="Type or click the microphone button...")

with col2:
    st.markdown('<div class="mic-container"><button class="mic-button"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M8 5a2 2 0 1 1 0 4 2 2 0 0 1 0-4zm0 5a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/><path d="M8 0a.5.5 0 0 1 .5.5v1.5a.5.5 0 0 1-1 0V.5A.5.5 0 0 1 8 0zm0 13a.5.5 0 0 1 .5.5v1.5a.5.5 0 0 1-1 0V13.5a.5.5 0 0 1 .5-.5z"/><path d="M2.75 5H2c-.276 0-.5.224-.5.5V8c0 1.664.626 3.184 1.655 4.333A5.981 5.981 0 0 0 8 14a5.981 5.981 0 0 0 4.846-1.667A6.981 6.981 0 0 0 14.5 8V5.5c0-.276-.224-.5-.5-.5h-.75a.75.75 0 0 1 0-1.5h.75c1.105 0 2 .895 2 2V8c0 1.993-.794 3.8-2.075 5.13A7.964 7.964 0 0 1 8 16a7.964 7.964 0 0 1-5.925-2.87A7.988 7.988 0 0 1 0 8V5.5c0-1.105.895-2 2-2h.75a.75.75 0 0 1 0 1.5z"/></svg>Speak</button></div>', unsafe_allow_html=True)

# Filter section with improved UI
st.markdown('<div class="filter-container">', unsafe_allow_html=True)
col3, col4 = st.columns([1, 1])
with col3:
    sort_order = st.selectbox("Sort by Price", ["None", "Low to High", "High to Low"], key="sort_filter")
with col4:
    max_results = st.slider("Number of results", min_value=5, max_value=20, value=10, step=5)
st.markdown('</div>', unsafe_allow_html=True)

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
    if not search_input:
        st.warning("Please enter a product name or use the microphone to speak.")
    else:
        query_params = {
            "keywords": search_input,
            "limit": max_results
        }
        
        if sort_order == "Low to High":
            query_params["sort"] = "asc"
        elif sort_order == "High to Low":
            query_params["sort"] = "desc"
        
        with st.spinner("Finding the best products for you..."):
            result = get_recommendations(query_params)
            
            if result.get("recommendations"):
                st.subheader(f"Found {len(result['recommendations'])} products matching '{search_input}'")
                
                for product in result["recommendations"]:
                    with st.container():
                        st.markdown(f'''
                        <div class="product-card">
                            <h3>{product['title']}</h3>
                            <p><strong>Price:</strong> ${product['price']}</p>
                            <p><strong>Rating:</strong> {"⭐" * int(float(product['rating']))} ({product['rating']})</p>
                            <a href="https://www.amazon.com/s?k={product['title'].replace(' ', '+')}" target="_blank">
                                <button style="background-color: #f90; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer;">
                                    View on Amazon
                                </button>
                            </a>
                        </div>
                        ''', unsafe_allow_html=True)
            else:
                st.info("No recommendations found. Try different search terms.")
