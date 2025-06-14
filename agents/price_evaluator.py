def evaluate_price(subject: dict, comps: list) -> str:
    if not comps:
        return "No comparable listings found to evaluate the price."

    subject_pps = subject['price'] / subject['size'] if subject['size'] else 0
    comp_pps = [c['price'] / c['size'] for c in comps if c.get('size') and c['size'] > 0]

    avg_pps = sum(comp_pps) / len(comp_pps) if comp_pps else 0
    diff_pct = ((subject_pps - avg_pps) / avg_pps) * 100 if avg_pps else 0

    if diff_pct > 10:
        return f"The property appears overpriced by about {diff_pct:.1f}% compared to similar listings."
    elif diff_pct < -10:
        return f"The property seems underpriced by about {abs(diff_pct):.1f}% – possibly a good deal."
    else:
        return "The property's price is within the typical range for similar listings."
