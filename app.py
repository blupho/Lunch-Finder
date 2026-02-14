import streamlit as st
import googlemaps
import os
import random
from dotenv import load_dotenv
from streamlit_js_eval import get_geolocation

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Lunch Finder 🍽️",
    page_icon="🍽️",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
    }
    .restaurant-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-bottom: 20px;
    }
    .cuisine-header {
        color: #FF4B4B;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# List of cuisines to choose from
CUISINES = [
    "American", "Mexican", "Asian", "Italian", "BBQ", 
    "Indian", "Mediterranean", "Thai", "Burger", "Pizza", 
    "Seafood", "Chinese", "Japanese", "Vietnamese"
]

def get_recommendations(api_key, address, radius_miles, lat_lng=None):
    """
    Fetches recommendations based on address and radius.
    """
    gmaps = googlemaps.Client(key=api_key)
    
    # Geocode the address
    if lat_lng:
        location = lat_lng
    else:
        try:
            geocode_result = gmaps.geocode(address)
            if not geocode_result:
                return None, "Address not found."
            
            location = geocode_result[0]['geometry']['location']
        except Exception as e:
            return None, f"Error geocoding address: {str(e)}"

    # Convert radius to meters
    radius_meters = int(radius_miles * 1609.34)
    
    # Select 3 random unique cuisines
    selected_cuisines = random.sample(CUISINES, 3)
    
    recommendations = []
    
    for cuisine in selected_cuisines:
        try:
            # Search for restaurants of this cuisine
            # Note: server-side min_rating is not available in basic places_nearby, 
            # so we fetch results and filter. 
            # We use keyword to target the cuisine.
            places_result = gmaps.places_nearby(
                location=location,
                radius=radius_meters,
                keyword=cuisine,
                type='restaurant',
                open_now=True
            )
            
            if 'results' in places_result:
                # Filter for rating >= 4.5
                candidates = [
                    p for p in places_result['results'] 
                    if p.get('rating', 0) >= 4.5 and p.get('user_ratings_total', 0) > 10
                ]
                
                if candidates:
                    # Pick one random restaurant
                    choice = random.choice(candidates)
                    price_level = choice.get('price_level', None)
                    price_str = "💰" * price_level if price_level else "Price not available"
                    
                    recommendations.append({
                        "cuisine": cuisine,
                        "name": choice.get('name'),
                        "rating": choice.get('rating'),
                        "address": choice.get('vicinity'),
                        "place_id": choice.get('place_id'),
                        "price": price_str
                    })
                else:
                    recommendations.append({
                        "cuisine": cuisine,
                        "error": "No high-rated options found nearby."
                    })
            else:
                 recommendations.append({
                        "cuisine": cuisine,
                        "error": "No results found."
                    })
                    
        except Exception as e:
            recommendations.append({
                "cuisine": cuisine,
                "error": f"API Error: {str(e)}"
            })
            
    return recommendations, None

def main():
    st.sidebar.title("Configuration")
    
    # API Key Input
    # Try to load from environment variable first
    env_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if env_api_key:
        api_key = env_api_key
        st.sidebar.success("API Key loaded from environment")
    else:
        api_key = st.sidebar.text_input("Google Maps API Key", type="password", help="Enter your Google Maps API Key here.")
    
    # Address Input
    use_location = st.sidebar.checkbox("Use Current Location")
    
    lat_lng = None
    address = None
    
    if use_location:
         loc = get_geolocation()
         if loc:
             lat_lng = {"lat": loc['coords']['latitude'], "lng": loc['coords']['longitude']}
             st.sidebar.success(f"Location detected: {lat_lng['lat']:.4f}, {lat_lng['lng']:.4f}")
         else:
             st.sidebar.warning("Getting location... (Allow permissions in browser)")
    else:
        default_address = "300 Beltway Green Blvd. Pasadena, TX 77503"
        address = st.sidebar.text_input("Current Address", value=default_address)
    
    # Radius Slider
    radius = st.sidebar.slider("Search Radius (miles)", min_value=1, max_value=10, value=3)
    
    st.title("Lunch Finder 🍽️")
    st.write("Find top-rated lunch options near you!")
    
    if st.button("Find Lunch!") or st.session_state.get('rerun', False):
        st.session_state['rerun'] = False # Reset rerun trigger
        
        if not api_key:
            st.error("Please enter a Google Maps API Key in the sidebar.")
        elif not address and not lat_lng:
             if use_location:
                 st.error("Waiting for location... Please allow permissions or uncheck 'Use Current Location' to enter address manually.")
             else:
                st.error("Please enter an address.")
        else:
            with st.spinner("Finding the best spots..."):
                results, error = get_recommendations(api_key, address, radius, lat_lng)
                
                if error:
                    st.error(error)
                else:
                    cols = st.columns(3)
                    for i, res in enumerate(results):
                        with cols[i]:
                            st.markdown(f"### {res['cuisine']}")
                            if "error" in res:
                                st.warning(res['error'])
                            else:
                                st.success(f"**{res['name']}**")
                                st.write(f"⭐ {res['rating']}")
                                st.write(f"{res.get('price', 'Price not available')}")
                                st.write(f"📍 {res['address']}")
                                google_maps_link = f"https://www.google.com/maps/place/?q=place_id:{res['place_id']}"
                                st.markdown(f"[View on Maps]({google_maps_link})")
    
    if st.button("Try Again"):
         st.session_state['rerun'] = True
         st.rerun()

if __name__ == "__main__":
    main()
