import os
import requests
from dotenv import load_dotenv
from groq import Groq


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set. "
        "Please check your .env file."
    )


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(api_key=GROQ_API_KEY)


# ============================================================
# GET TRENDING AI TOPIC
# ============================================================

def get_trending_topic():
    """
    Fetch a trending AI topic from Google News RSS.
    """

    try:

        url = (
            "https://news.google.com/rss/search"
            "?q=artificial+intelligence+AI"
            "&hl=en-IN"
            "&gl=IN"
            "&ceid=IN:en"
        )

        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        text = response.text

        # ----------------------------------------------------
        # Simple RSS title extraction
        # ----------------------------------------------------

        import re

        titles = re.findall(
            r"<title>(.*?)</title>",
            text,
            re.DOTALL
        )

        # Remove Google News main title
        titles = [
            title.strip()
            for title in titles
            if title.strip()
            and "Google News" not in title
        ]

        if not titles:
            raise ValueError("No AI news topics found.")

        # Take the first/latest news headline
        topic = titles[0]

        # Remove HTML if present
        topic = re.sub(
            r"<.*?>",
            "",
            topic
        )

        return topic.strip()

    except Exception as e:

        print(f"⚠️ Could not fetch trending topic: {e}")

        # Fallback topic
        return (
            "Latest developments in Artificial Intelligence "
            "and Generative AI"
        )


# ============================================================
# GENERATE LINKEDIN POST
# ============================================================

def generate_post(topic):
    """
    Generate a professional LinkedIn post using Groq.
    """

    prompt = f"""
You are an expert LinkedIn content writer specializing in:

- Artificial Intelligence
- Generative AI
- Machine Learning
- Data Science
- AI Agents
- Technology trends

Create a high-quality LinkedIn post about:

TOPIC:
{topic}

Requirements:

1. Start with a strong attention-grabbing hook.
2. Explain the topic in simple language.
3. Provide useful insights.
4. Keep the tone professional and conversational.
5. Use short paragraphs.
6. Use relevant emojis, but don't overuse them.
7. Explain why this topic matters to AI and technology professionals.
8. Avoid unsupported claims.
9. Do not mention that you are an AI.
10. End with an engaging question.
11. Add 5-8 relevant hashtags.
12. Keep the post around 250-400 words.

IMPORTANT:

Return ONLY the LinkedIn post.

Do not add:
- "LinkedIn Post"
- "Caption"
- "Generated Post"
- Explanation outside the post
"""


    # ========================================================
    # GROQ API REQUEST
    # ========================================================

    response = client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional LinkedIn content "
                    "writer specializing in AI and Data Science."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.7,

        max_completion_tokens=1200
    )


    # ========================================================
    # EXTRACT RESPONSE
    # ========================================================

    post = response.choices[0].message.content

    if not post:
        raise ValueError(
            "Groq returned an empty response."
        )

    return post.strip()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n🔥 Fetching trending AI topic...")

    topic = get_trending_topic()

    print(f"\n📌 Topic: {topic}")

    print("\n✍ Generating LinkedIn post...")

    try:

        post = generate_post(topic)

        print("\n" + "=" * 70)
        print("GENERATED LINKEDIN POST")
        print("=" * 70)

        print(post)

        print("=" * 70)

    except Exception as e:

        print("\n❌ Error generating LinkedIn post:")
        print(e)
