import requests
from bs4 import BeautifulSoup
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def search_reddit_trustpilot(developer):
    reddit_query = f"{developer} reviews site:reddit.com"
    trustpilot_query = f"{developer} reviews site:trustpilot.com"

    results = []

    for query in [reddit_query, trustpilot_query]:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for result in soup.select("div.tF2Cxc"):
            snippet = result.select_one("div.VwiC3b").text if result.select_one("div.VwiC3b") else ""
            if developer.lower() in snippet.lower():
                results.append(snippet)
    return results

def get_developer_summary(developer_name):
    snippets = search_reddit_trustpilot(developer_name)
    if not snippets:
        return "No major developer reviews found on Reddit or Trustpilot."

    combined_text = "\n".join(snippets[:10])
    prompt = f"""
Based on the following text snippets from Reddit and Trustpilot about {developer_name}, summarize the general reputation of the developer. Mention positive and negative aspects and keep it brief and clear.

{combined_text}

Summary:
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return "Could not analyze developer reputation due to an error."
