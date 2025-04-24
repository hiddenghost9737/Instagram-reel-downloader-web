from flask import Flask, render_template, request
import random
import re

app = Flask(__name__)

EMOTIONAL_TRIGGERS = [
    "Amazing", "Incredible", "Unbelievable", "Mind-blowing", "Secrets", "Revealed",
    "Untold", "Discover", "Now", "Instant", "Hurry", "Quick", "Insider", "Exclusive",
    "Limited", "VIP", "Proven", "Guaranteed", "Reliable", "Authentic"
]

def generate_title(keyword):
    return ' '.join([
        random.choice(EMOTIONAL_TRIGGERS),
        keyword.title(),
        random.choice(["Secrets", "Adventures", "Discoveries", "Explorations"]),
        f"({random.choice(EMOTIONAL_TRIGGERS)} Tips)"
    ])[:70]

def generate_description(keyword):
    return f"""
{random.choice(EMOTIONAL_TRIGGERS)}! {random.choice(EMOTIONAL_TRIGGERS)} guide to {keyword}! 

Embark on an extraordinary journey into the world of {keyword}. Discover hidden gems, expert insights, and breathtaking experiences.

🔔 {random.choice(EMOTIONAL_TRIGGERS)}! SUBSCRIBE now for {random.choice(EMOTIONAL_TRIGGERS)} {keyword} content!

👇 Share your {random.choice(EMOTIONAL_TRIGGERS)} thoughts! What's your experience with {keyword}?

Don't miss out on more {random.choice(EMOTIONAL_TRIGGERS)} content!
""".strip()

def generate_tags(keyword):
    base_tags = keyword.split()
    related_terms = [
        "adventure", "exploration", "discovery", "travel", "experience",
        "guide", "tips", "secrets", "hidden", "amazing", "breathtaking",
        "unforgettable", "journey", "expedition", "ultimate"
    ]
    tags = [keyword] + base_tags + related_terms
    tags += [f"{keyword} {term}" for term in related_terms]
    tags += [f"{term} {keyword}" for term in related_terms]
    return list(dict.fromkeys(tags))[:30]

def generate_hashtags(tags, keyword):
    hashtags = [f"#{tag.replace(' ', '')}" for tag in tags[:14] if len(tag) > 2]
    keyword_hashtag = f"#{keyword.replace(' ', '')}"
    if keyword_hashtag not in hashtags:
        hashtags.insert(0, keyword_hashtag)
    return list(dict.fromkeys(hashtags))[:15]

def calculate_seo_score(title, description, tags, hashtags):
    score = 0
    if len(title) <= 70: score += 20
    if 500 <= len(description) <= 2000: score += 30
    score += min(len(tags), 30)
    score += min(len(hashtags) * 2, 20)
    return min(score, 100)

def get_mock_analytics():
    return {
        "views": random.randint(10000, 1000000),
        "likes": random.randint(1000, 100000),
        "comments": random.randint(100, 10000),
        "shares": random.randint(50, 5000)
    }

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        title = generate_title(keyword)
        description = generate_description(keyword)
        tags = generate_tags(keyword)
        hashtags = generate_hashtags(tags, keyword)
        seo_score = calculate_seo_score(title, description, tags, hashtags)
        analytics = get_mock_analytics()
        return render_template("index.html", title=title, description=description,
                               tags=tags, hashtags=hashtags, seo_score=seo_score,
                               analytics=analytics, keyword=keyword)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
