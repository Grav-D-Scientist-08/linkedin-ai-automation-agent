from agents.content import get_trending_topic, generate_post
from linkedin import post_on_linkedin


def run_agent():
    print("🔥 Fetching trending AI topic...")

    topic = get_trending_topic()
    print(f"📌 Topic: {topic}")

    print("✍ Generating LinkedIn post...")
    post = generate_post(topic)

    print("\n📄 Final Post:\n")
    print(post)

    print("\n🚀 Posting on LinkedIn...")
    post_on_linkedin(post)


if __name__ == "__main__":
    run_agent()