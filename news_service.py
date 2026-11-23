
import re
import requests
import xml.etree.ElementTree as ET

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.parse import quote_plus


# --------------------------------------------------
# GOOGLE NEWS RSS CONFIGURATION
# --------------------------------------------------

COUNTRIES = {
    "in": {
        "hl": "en-IN",
        "gl": "IN",
        "ceid": "IN:en",
    },
    "us": {
        "hl": "en-US",
        "gl": "US",
        "ceid": "US:en",
    },
    "gb": {
        "hl": "en-GB",
        "gl": "GB",
        "ceid": "GB:en",
    },
}

CATEGORY_QUERIES = {
    "business": "business economy markets",
    "entertainment": "entertainment movies music",
    "general": "latest news",
    "health": "health medical science",
    "science": "science research",
    "sports": "sports",
    "technology": "technology artificial intelligence",
}


# --------------------------------------------------
# HEADLINE CLASSIFICATION
# --------------------------------------------------

KEYWORDS = {
    "Technology": [
        "technology", "software", "artificial intelligence",
        "ai", "computer", "robot", "cyber", "internet",
        "smartphone", "app", "digital", "startup",
        "chip", "semiconductor", "google", "microsoft"
    ],

    "Business": [
        "business", "market", "economy", "stock",
        "finance", "company", "trade", "bank",
        "investment", "profit", "revenue", "inflation",
        "economic", "rupee", "dollar"
    ],

    "Sports": [
        "sport", "cricket", "football", "soccer",
        "tennis", "match", "tournament", "player",
        "team", "olympic", "ipl", "wicket",
        "goal", "championship"
    ],

    "Entertainment": [
        "movie", "film", "actor", "actress",
        "music", "celebrity", "hollywood",
        "bollywood", "concert", "series",
        "singer", "television"
    ],

    "Health": [
        "health", "hospital", "doctor", "medical",
        "disease", "medicine", "patient",
        "treatment", "virus", "vaccine",
        "healthcare", "nutrition"
    ],

    "Science": [
        "science", "research", "space",
        "nasa", "climate", "discovery",
        "scientist", "environment", "physics",
        "biology", "astronomy"
    ],
}


def categorize_headline(text):
    """Classify a headline using keyword matching."""

    text = (text or "").lower()

    scores = {}

    for category, keywords in KEYWORDS.items():

        scores[category] = sum(
            1 for keyword in keywords
            if keyword in text
        )

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "General"

    return best_category


# --------------------------------------------------
# CLEAN RSS TEXT
# --------------------------------------------------

def clean_text(value):
    """Remove HTML and clean RSS text."""

    if not value:
        return ""

    value = unescape(value)

    value = re.sub(
        r"<[^>]+>",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# --------------------------------------------------
# DATE CONVERSION
# --------------------------------------------------

def format_date(value):
    """Convert RSS publication dates into ISO format."""

    if not value:
        return datetime.now(timezone.utc).isoformat()

    try:

        parsed = parsedate_to_datetime(value)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.isoformat()

    except (TypeError, ValueError, OverflowError):

        return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------
# FETCH HEADLINES WITHOUT API KEY
# --------------------------------------------------

def fetch_headlines(country="in", category=None):
    """
    Fetch current headlines using public Google News RSS.

    No NewsAPI key or registration is required.
    An internet connection is required.
    """

    country = (country or "in").lower().strip()

    if country not in COUNTRIES:
        country = "in"

    country_settings = COUNTRIES[country]

    category = (category or "").lower().strip()

    if category not in CATEGORY_QUERIES:
        category = ""

    if category:

        query = CATEGORY_QUERIES[category]

        rss_url = (
            "https://news.google.com/rss/search?q="
            + quote_plus(query)
        )

    else:

        rss_url = "https://news.google.com/rss"

    params = {
        **country_settings,
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    response = requests.get(
        rss_url,
        params=params,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    root = ET.fromstring(response.content)

    articles = []

    for item in root.findall(".//item"):

        title = clean_text(
            item.findtext("title", default="")
        )

        link = item.findtext(
            "link",
            default=""
        ).strip()

        description = clean_text(
            item.findtext("description", default="")
        )

        published = format_date(
            item.findtext("pubDate", default="")
        )

        source_element = item.find("source")

        if source_element is not None:
            source = clean_text(source_element.text or "")
        else:
            source = "Google News"

        if not title or not link:
            continue

        if category:
            classified_category = (
                category.capitalize()
            )
        else:
            classified_category = categorize_headline(
                title + " " + description
            )

        articles.append({
            "title": title,
            "description": description,
            "url": link,
            "source": source or "Google News",
            "published_at": published,
            "category": classified_category,
        })

    return articles[:50]
