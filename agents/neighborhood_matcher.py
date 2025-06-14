import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def match_neighborhood(query: str) -> str:
    prompt = f"""
You are a Dubai real estate expert.

A user described their lifestyle and preferences: "{query}"

Based on that, recommend 3 Dubai neighborhoods that match them. For each, give a short reason.
Only suggest areas that exist in Dubai. Focus on local knowledge like traffic, vibe, prices, and amenities.

Output format:
1. Neighborhood - Reason
2. Neighborhood - Reason
3. Neighborhood - Reason
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return "Sorry, I couldn't generate neighborhood recommendations at the moment."
