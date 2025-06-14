def suggest_negotiation(subject: dict, comps: list) -> str:
    if not comps:
        return "No market data available to suggest a negotiation strategy."

    subject_pps = subject['price'] / subject['size'] if subject['size'] else 0
    comp_pps = [c['price'] / c['size'] for c in comps if c.get('size') and c['size'] > 0]
    avg_pps = sum(comp_pps) / len(comp_pps) if comp_pps else 0

    if subject_pps > avg_pps:
        margin = 0.05
        suggested_price = int(subject['price'] * (1 - margin))
        return f"You could try negotiating to around AED {suggested_price}. Starting with a 5–8% lower offer is reasonable."
    else:
        return "The price is already competitive. A small discount may be possible if you offer fewer cheques or pay upfront."
