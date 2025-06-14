import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

def analyze_property_url(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code >= 400:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        domain = urlparse(url).netloc

        if "propertyfinder.ae" in domain:
            script = soup.find("script", id="__NEXT_DATA__", type="application/json")
            if script and script.string:
                try:
                    data = json.loads(script.string)
                    page = data.get("props", {}).get("pageProps", {})
                    listing = (
                        page.get("listing")
                        or page.get("initialListing")
                        or page.get("propertyResult", {}).get("property")
                    )
                    if listing:
                        price = listing.get("price")
                        if isinstance(price, dict):
                            price = int(re.sub(r"[^\d]", "", str(price.get("value", 0))))
                        else:
                            price = int(price or 0)

                        size = listing.get("size")
                        if isinstance(size, dict):
                            size = int(size.get("value", 0))

                        developer = (
                            listing.get("developerName")
                            or listing.get("project", {}).get("developer", {}).get("name")
                        )

                        area_name = None
                        location = listing.get("location")
                        if isinstance(location, dict):
                            area_name = location.get("full_name")

                        return {
                            "url": url,
                            "title": listing.get("title", "N/A"),
                            "price": price,
                            "area": area_name or listing.get("communityName", "Unknown"),
                            "size": size or 0,
                            "bedrooms": listing.get("bedrooms") or 0,
                            "developer": developer or "Unknown",
                        }
                except Exception:
                    pass

        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "N/A"
        price_tag = soup.select_one('[aria-label*="AED"]')
        price_text = price_tag.get_text(strip=True) if price_tag else ""
        price = int(re.sub(r"[^\d]", "", price_text)) if price_text else 0

        area = soup.find(text=re.compile("Location|Community", re.I))
        if area:
            area = area.find_next().get_text(strip=True)

        size_text = soup.find(text=re.compile("Size", re.I))
        size = int(re.sub(r"[^\d]", "", size_text.find_next().get_text())) if size_text else 0

        beds_text = soup.find(text=re.compile("Bedroom", re.I))
        bedrooms = int(re.sub(r"[^\d]", "", beds_text.find_next().get_text())) if beds_text else 0

        developer = None
        dev_tag = soup.find(text=re.compile("Developer", re.I))
        if dev_tag:
            developer = dev_tag.find_next().get_text(strip=True)

        return {
            "url": url,
            "title": title,
            "price": price,
            "area": area or "Unknown",
            "size": size,
            "bedrooms": bedrooms,
            "developer": developer or "Unknown",
        }

    except Exception:
        return None

def get_comparables(subject):
    url = subject.get("url", "")
    listings = []

    if "propertyfinder.ae" in urlparse(url).netloc:
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code < 400:
                soup = BeautifulSoup(response.text, "html.parser")
                script = soup.find("script", id="__NEXT_DATA__", type="application/json")
                if script and script.string:
                    data = json.loads(script.string)
                    prop = data.get("props", {}).get("pageProps", {}).get("propertyResult", {}).get("property")
                    comparables = prop.get("similar_price_transactions", {}).get("rent", [])
                    for comp in comparables[:5]:
                        price = int(re.sub(r"[^\d]", "", str(comp.get("amount", "0"))))
                        size = int(comp.get("size") or 0)
                        if price and size:
                            listings.append({"price": price, "size": size})
            if listings:
                return listings
        except Exception:
            pass

    area = subject.get("area", "Dubai Marina").replace(" ", "-").lower()
    bedrooms = subject.get("bedrooms", 2)
    search_url = (
        f"https://www.propertyfinder.ae/en/search?c=2&l=0&ob=mr&rp=y&fu=0&pt=101&bedrooms={bedrooms}&t=rent&kw={area}"
    )
    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        if response.status_code >= 400:
            return []
        soup = BeautifulSoup(response.text, "html.parser")

        script = soup.find("script", id="__NEXT_DATA__", type="application/json")
        if script and script.string:
            try:
                data = json.loads(script.string)
                cards = data.get("props", {}).get("pageProps", {}).get("hits", [])
                for card in cards[:5]:
                    price = int(card.get("price", 0))
                    size = int(card.get("size", 0))
                    if price and size:
                        listings.append({"price": price, "size": size})
            except Exception:
                pass

        if not listings:
            cards = soup.select("li._93444fe79c--card")
            for card in cards[:5]:
                price_tag = card.select_one("span[data-testid='price']")
                size_tag = card.select_one("span[data-testid='property-area']")
                if price_tag and size_tag:
                    price = int(re.sub(r"[^\d]", "", price_tag.text))
                    size = int(re.sub(r"[^\d]", "", size_tag.text))
                    listings.append({"price": price, "size": size})

        return listings
    except Exception:
        return []
