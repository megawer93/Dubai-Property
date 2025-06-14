from agents.neighborhood_matcher import match_neighborhood
from agents.property_fetcher import analyze_property_url, get_comparables
from agents.developer_reputation import get_developer_summary
from agents.price_evaluator import evaluate_price
from agents.negotiation_advisor import suggest_negotiation
import re

def handle_query(query: str) -> str:
    url_match = re.search(r"https?://\S+", query)
    if url_match:
        url = url_match.group()
        listing = analyze_property_url(url)
        if not listing:
            return "❌ Unable to fetch listing details. Please try another link."
        comps = get_comparables(listing)
        price_eval = evaluate_price(listing, comps)
        developer_info = get_developer_summary(listing.get("developer", ""))
        negotiation = suggest_negotiation(listing, comps)
        return f"""### 🏘️ Property Overview
**Title:** {listing['title']}  
**Location:** {listing['area']}  
**Price:** AED {listing['price']}  
**Size:** {listing['size']} sqft  
**Bedrooms:** {listing['bedrooms']}  
**Developer:** {listing.get('developer', 'N/A')}

### 📊 Price Evaluation
{price_eval}

### 🧱 Developer Insight
{developer_info}

### 🤝 Negotiation Advice
{negotiation}
"""
    else:
        return match_neighborhood(query)
