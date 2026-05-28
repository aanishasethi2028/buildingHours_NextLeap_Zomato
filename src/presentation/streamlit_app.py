import streamlit as st
import requests
import json

# Set premium page configuration
st.set_page_config(
    page_title="zomato",
    page_icon="🍔",
    layout="wide"
)

# Custom CSS for Zomato styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Force Zomato white/light background and dark text */
.stApp {
    background-color: #FFFFFF !important;
    color: #1C1C1C !important;
}

/* Hide Streamlit default header and sidebar completely */
[data-testid="stHeader"] {
    display: none !important;
}
[data-testid="stSidebar"] {
    display: none !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}
div.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px !important;
}
[data-testid="stSidebar"] * {
    color: #1C1C1C !important;
}

/* Zomato Header Navigation Bar */
.zomato-nav-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
    border-bottom: 1px solid #E8E8E8;
    background-color: #FFFFFF;
    margin-bottom: 30px;
    font-family: 'Outfit', sans-serif;
}
.zomato-logo-brand {
    font-size: 38px;
    font-weight: 800;
    color: #E23744;
    letter-spacing: -2px;
    font-style: italic;
    text-decoration: none;
}
.zomato-nav-links {
    display: flex;
    gap: 25px;
    font-size: 16px;
    color: #696969;
    font-weight: 500;
}
.zomato-nav-link:hover {
    color: #1C1C1C;
    cursor: pointer;
}

/* AI Summary Section */
.ai-summary-card {
    background: #FFF4F5;
    border: 1px solid #FFE4E6;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 30px;
    font-family: 'Outfit', sans-serif;
    box-shadow: 0 2px 8px rgba(226, 55, 68, 0.05);
}
.ai-summary-title {
    font-size: 20px;
    font-weight: 700;
    color: #E23744;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.ai-summary-body {
    font-size: 15.5px;
    line-height: 1.6;
    color: #363636;
}

/* Grid Layout & Cards */
.restaurant-grid-card {
    background: #FFFFFF;
    border: 1px solid #E8E8E8;
    border-radius: 15px;
    overflow: hidden;
    margin-bottom: 25px;
    font-family: 'Outfit', sans-serif;
    transition: box-shadow 0.25s ease, transform 0.25s ease;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
}
.restaurant-grid-card:hover {
    box-shadow: 0px 8px 24px rgba(28, 28, 28, 0.1);
    transform: translateY(-4px);
}
.restaurant-img-cover {
    width: 100%;
    height: 195px;
    object-fit: cover;
}
.restaurant-card-body {
    padding: 16px;
}
.restaurant-title-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 6px;
}
.restaurant-title-name {
    font-size: 19px;
    font-weight: 600;
    color: #1C1C1C;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 75%;
}
.restaurant-badge-rating {
    background: #247F40;
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
    display: flex;
    align-items: center;
}
.restaurant-detail-row {
    display: flex;
    justify-content: space-between;
    font-size: 14.5px;
    color: #696969;
    margin-bottom: 12px;
}
.restaurant-cuisine-tag {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 60%;
}
.restaurant-cost-for-two {
    font-weight: 500;
    color: #1C1C1C;
}
.restaurant-card-locality {
    font-size: 13px;
    color: #828282;
    margin-bottom: 14px;
}
.restaurant-review-box {
    background: #FDF3F4;
    border-left: 3px solid #E23744;
    padding: 10px 12px;
    border-radius: 4px;
    font-size: 13.5px;
    line-height: 1.5;
    color: #2D2D2D;
}
.quick-cuisine-title {
    font-size: 20px;
    font-weight: 700;
    color: #1C1C1C;
    margin-bottom: 15px;
    font-family: 'Outfit', sans-serif;
}
.badge-ai-ranked {
    background: #E23744;
    color: white;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 4px;
    margin-left: 8px;
}
</style>
""", unsafe_allow_html=True)

# Navigation Bar
st.markdown("""
<div class="zomato-nav-bar">
    <div class="zomato-logo-brand">zomato</div>
    <div class="zomato-nav-links">
        <span class="zomato-nav-link">Investor Relations</span>
        <span class="zomato-nav-link">Add restaurant</span>
        <span class="zomato-nav-link">Log in</span>
        <span class="zomato-nav-link">Sign up</span>
    </div>
</div>
""", unsafe_allow_html=True)

backend_url = "http://127.0.0.1:8000"

# Fetch location choices dynamically from backend
locations_list = ["Indiranagar", "Bellandur", "Koramangala 5th Block", "Koramangala 7th Block", "BTM", "HSR", "Marathahalli", "Whitefield", "Jayanagar", "JP Nagar", "Bangalore"]
try:
    loc_resp = requests.get(f"{backend_url}/api/locations", timeout=2)
    if loc_resp.status_code == 200:
        fetched_locs = loc_resp.json().get("locations", [])
        if fetched_locs:
            locations_list = fetched_locs
except Exception:
    pass

# Helper to get local SVG vector image by cuisine (guarantees offline display)
def get_cuisine_image(cuisine_str: str) -> str:
    c = cuisine_str.lower()
    if "italian" in c or "pizza" in c or "pasta" in c:
        return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 120'><rect width='200' height='120' fill='%23FFF1F2'/><path d='M60,20 L140,20 C140,20 140,80 100,100 C60,80 60,20 60,20 Z' fill='%23FDE047' stroke='%23CA8A04' stroke-width='3'/><circle cx='85' cy='40' r='6' fill='%23EF4444'/><circle cx='115' cy='50' r='6' fill='%23EF4444'/><circle cx='100' cy='70' r='6' fill='%23EF4444'/><path d='M60,20 Q100,30 140,20' fill='none' stroke='%23CA8A04' stroke-width='4'/><text x='100' y='112' font-family='sans-serif' font-size='10' font-weight='bold' fill='%23E23744' text-anchor='middle'>Italian Cuisine</text></svg>"
    if "north indian" in c or "biryani" in c or "mughlai" in c or "kebab" in c:
        return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 120'><rect width='200' height='120' fill='%23FFF7ED'/><path d='M50,70 C50,90 150,90 150,70 L160,50 L40,50 Z' fill='%23FDBA74' stroke='%23EA580C' stroke-width='3'/><path d='M80,40 Q90,25 90,40 T100,40' fill='none' stroke='%23EA580C' stroke-width='2' stroke-linecap='round'/><path d='M110,40 Q120,25 120,40 T130,40' fill='none' stroke='%23EA580C' stroke-width='2' stroke-linecap='round'/><text x='100' y='112' font-family='sans-serif' font-size='10' font-weight='bold' fill='%23EA580C' text-anchor='middle'>North Indian Cuisine</text></svg>"
    if "south indian" in c or "dosa" in c or "idli" in c:
        return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 120'><rect width='200' height='120' fill='%23FEFCE8'/><ellipse cx='100' cy='60' rx='60' ry='25' fill='%23FEF08A' stroke='%23CA8A04' stroke-width='3'/><circle cx='80' cy='55' r='10' fill='%23F59E0B'/><circle cx='120' cy='55' r='10' fill='%23EF4444'/><text x='100' y='112' font-family='sans-serif' font-size='10' font-weight='bold' fill='%23CA8A04' text-anchor='middle'>South Indian Cuisine</text></svg>"
    if "chinese" in c or "asian" in c or "noodle" in c or "momos" in c:
        return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 120'><rect width='200' height='120' fill='%23FEF2F2'/><path d='M50,50 C50,90 150,90 150,50 Z' fill='%23FCA5A5' stroke='%23DC2626' stroke-width='3'/><path d='M35,35 L165,30 M45,30 L155,45' stroke='%23DC2626' stroke-width='3' stroke-linecap='round'/><text x='100' y='112' font-family='sans-serif' font-size='10' font-weight='bold' fill='%23DC2626' text-anchor='middle'>Chinese Cuisine</text></svg>"
    if "cafe" in c or "coffee" in c or "beverage" in c:
        return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 120'><rect width='200' height='120' fill='%23EFEBE9'/><path d='M60,40 L130,40 L120,90 L70,90 Z' fill='%23D7CCC8' stroke='%235D4037' stroke-width='3'/><path d='M125,48 C140,48 140,70 122,70' fill='none' stroke='%235D4037' stroke-width='3'/><path d='M85,25 Q90,15 90,25 T95,25' fill='none' stroke='%235D4037' stroke-width='2' stroke-linecap='round'/><path d='M100,25 Q105,15 105,25 T110,25' fill='none' stroke='%235D4037' stroke-width='2' stroke-linecap='round'/><text x='100' y='112' font-family='sans-serif' font-size='10' font-weight='bold' fill='%235D4037' text-anchor='middle'>Cafe & Beverages</text></svg>"
    if "dessert" in c or "sweet" in c or "ice cream" in c or "bakery" in c:
        return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 120'><rect width='200' height='120' fill='%23FDF2F8'/><path d='M70,70 L130,70 L120,95 L80,95 Z' fill='%23FBCFE8' stroke='%23DB2777' stroke-width='3'/><path d='M60,70 C60,50 140,50 140,70 Z' fill='%23F472B6' stroke='%23DB2777' stroke-width='3'/><circle cx='100' cy='45' r='8' fill='%23E11D48'/><text x='100' y='112' font-family='sans-serif' font-size='10' font-weight='bold' fill='%23DB2777' text-anchor='middle'>Desserts & Sweets</text></svg>"
    return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 120'><rect width='200' height='120' fill='%23FFF1F2'/><circle cx='100' cy='55' r='30' fill='none' stroke='%23E23744' stroke-width='3'/><path d='M55,35 L55,75 M145,35 L145,75' stroke='%23E23744' stroke-width='3' stroke-linecap='round'/><text x='100' y='105' font-family='sans-serif' font-size='10' font-weight='bold' fill='%23E23744' text-anchor='middle'>Delicious Dining</text></svg>"

# Initialize session states for interactive filters
if "cuisine_input" not in st.session_state:
    st.session_state.cuisine_input = "Italian"
if "location_input" not in st.session_state:
    st.session_state.location_input = "Indiranagar"

# Search panel inside the main window
st.markdown('<div class="quick-cuisine-title" style="margin-bottom:10px;">Search and filter options</div>', unsafe_allow_html=True)

# Grid layout for primary search fields
col_loc, col_cuisine, col_budget = st.columns([1, 1.5, 1])

with col_loc:
    loc_index = 0
    if st.session_state.location_input in locations_list:
        loc_index = locations_list.index(st.session_state.location_input)
    location = st.selectbox(
        "📍 Locality / Area",
        locations_list,
        index=loc_index
    )
    st.session_state.location_input = location

with col_cuisine:
    cuisine = st.text_input(
        "🍳 Search for cuisines or dishes", 
        value=st.session_state.cuisine_input
    )
    st.session_state.cuisine_input = cuisine

with col_budget:
    budget = st.selectbox(
        "💰 Budget Level", 
        ["low", "medium", "high"], 
        index=1
    )

# Advanced filters in an expander
with st.expander("⚙️ Advanced Filters (Rating & Special Requests)", expanded=True):
    col_rating, col_extra, col_status = st.columns([2, 2, 1])
    with col_rating:
        min_rating = st.slider("⭐ Minimum Restaurant Rating", 0.0, 5.0, 4.0, 0.1)
    with col_extra:
        additional_preferences = st.text_area(
            "✍️ Special Preferences", 
            placeholder="e.g. rooftop seating, craft beer, family-friendly",
            height=68
        )
    with col_status:
        st.markdown("<div style='font-size:14px; font-weight:600; margin-bottom:8px;'>System Status</div>", unsafe_allow_html=True)
        # Connect health check
        try:
            health_resp = requests.get(f"{backend_url}/health", timeout=2)
            if health_resp.status_code == 200:
                count = health_resp.json().get("restaurant_count", 0)
                st.markdown(f"<div style='color:#247F40; font-size:14px; font-weight:600;'>● Healthy<br><span style='font-size:12px; color:#696969;'>{count} spots loaded</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#E65100; font-size:14px;'>● Starting...</div>", unsafe_allow_html=True)
        except Exception:
            st.markdown("<div style='color:#D32F2F; font-size:14px;'>● Offline</div>", unsafe_allow_html=True)

# Main Page content
# 1. Quick cuisine list (like Zomato options)
st.markdown('<div class="quick-cuisine-title">Inspiration for your next meal</div>', unsafe_allow_html=True)
cols = st.columns(6)
quick_cuisines = ["Italian", "North Indian", "Chinese", "South Indian", "Desserts", "Cafe"]
for col, c_name in zip(cols, quick_cuisines):
    if col.button(f"🍜 {c_name}" if "Indian" in c_name or "Chinese" in c_name else f"🍰 {c_name}" if "Dessert" in c_name else f"☕ {c_name}" if "Cafe" in c_name else f"🍕 {c_name}", use_container_width=True, key=f"quick_{c_name}"):
        st.session_state.cuisine_input = c_name
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Automatically fetch on load or state change (fully reactive)
if True:
    with st.spinner("Finding best dining spots..."):
        payload = {
            "location": st.session_state.location_input,
            "budget": budget,
            "cuisine": st.session_state.cuisine_input,
            "min_rating": min_rating,
            "additional_preferences": additional_preferences if additional_preferences.strip() else None
        }
        
        try:
            response = requests.post(f"{backend_url}/api/recommend", json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                recommendations = result.get("recommendations", [])
                summary = result.get("summary")
                used_fallback = result.get("used_fallback", False)
                fallback_reason = result.get("fallback_reason")
                candidates_considered = result.get("candidates_considered", 0)
                
                if not recommendations:
                    st.warning(f"No restaurants found matching your criteria in **{st.session_state.location_input}**. Try resetting filters.")
                    if summary:
                        st.info(summary)
                else:
                    # 2. Render AI Summary block
                    if summary:
                        mode_badge = '<span class="badge-ai-ranked" style="background:#FFA500; color:black;">Rating Sorted</span>' if used_fallback else '<span class="badge-ai-ranked">AI Ranked</span>'
                        st.markdown(f"""
                        <div class="ai-summary-card">
                            <div class="ai-summary-title">
                                🍳 AI Critic's Overview
                                {mode_badge}
                            </div>
                            <div class="ai-summary-body">{summary}</div>
                            {f'<div style="color:#D32F2F; font-size:12px; margin-top:8px;">Fallback reason: {fallback_reason}</div>' if used_fallback else ''}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"<h3 style='font-weight:700; color:#1C1C1C; margin-bottom:20px;'>Recommended dining options in {st.session_state.location_input}</h3>", unsafe_allow_html=True)
                    
                    # 3. Render 3-column Grid Cards (matching Zomato website style)
                    # We group recommendations into chunks of 3 for the grid layout
                    grid_cols = st.columns(3)
                    
                    for idx, r in enumerate(recommendations):
                        col_idx = idx % 3
                        rest = r.get("restaurant", {})
                        rating_val = rest.get("rating")
                        rating_text = f"{rating_val:.1f} ★" if rating_val is not None else "Unrated"
                        
                        img_url = get_cuisine_image(rest.get("cuisine", ""))
                        
                        with grid_cols[col_idx]:
                            st.markdown(f"""
                            <div class="restaurant-grid-card">
                                <img src="{img_url}" class="restaurant-img-cover"/>
                                <div class="restaurant-card-body">
                                    <div class="restaurant-title-row">
                                        <div class="restaurant-title-name">#{r.get('rank')} {rest.get('name')}</div>
                                        <div class="restaurant-badge-rating">{rating_text}</div>
                                    </div>
                                    <div class="restaurant-detail-row">
                                        <div class="restaurant-cuisine-tag">{rest.get('cuisine')}</div>
                                        <div class="restaurant-cost-for-two">{rest.get('cost')}</div>
                                    </div>
                                    <div class="restaurant-card-locality">
                                        📍 {rest.get('area') or rest.get('location')}
                                    </div>
                                    <div class="restaurant-review-box">
                                        <b>AI Critic's Review:</b><br>
                                        {r.get('explanation')}
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                    st.markdown(f"<div style='color:#999; font-size:12px; margin-top:30px; text-align:center;'>Total candidate spots evaluated: {candidates_considered}</div>", unsafe_allow_html=True)
            else:
                st.error(f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
        except Exception as exc:
            st.error(f"Failed to connect to backend: {exc}")
