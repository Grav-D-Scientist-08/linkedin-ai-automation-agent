import os
import random
import feedparser
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

LAST_TOPIC_FILE = "last_topic.txt"


def get_last_topic():
    if os.path.exists(LAST_TOPIC_FILE):
        with open(LAST_TOPIC_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def save_last_topic(topic):
    with open(LAST_TOPIC_FILE, "w", encoding="utf-8") as f:
        f.write(topic)


def get_trending_topic():
    rss_url = "https://news.google.com/rss/search?q=Artificial+Intelligence"
    feed = feedparser.parse(rss_url)

    topics = []

    for entry in feed.entries[:20]:
        title = entry.title.split(" - ")[0]
        topics.append(title)

    last_topic = get_last_topic()

    available = [t for t in topics if t != last_topic]

    if not available:
        available = topics

    topic = random.choice(available)
    save_last_topic(topic)

    return topic


def clean_generated_post(text):
    stop_words = [
        "I made the following",
        "Changes made",
        "Note:",
        "Join us",
        "Join our",
        "Register now",
        "webinar",
        "[link"
    ]

    for word in stop_words:
        if word.lower() in text.lower():
            idx = text.lower().find(word.lower())
            text = text[:idx]

    return text.strip()


def generate_post(topic):
    prompt = f"""
Write a professional LinkedIn post on: {topic}

Rules:
- Start with a catchy heading
- 3 short engaging paragraphs
- No webinar
- No links
- No note/explanation
- No spelling mistakes
- Unique content every time
- End with 3-5 hashtags
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=1.1,
        max_tokens=800
    )

    post = response.choices[0].message.content
    return clean_generated_post(post)