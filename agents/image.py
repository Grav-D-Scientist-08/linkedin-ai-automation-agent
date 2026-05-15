import requests
import os

def generate_image(topic):
    # Folder ensure karo
    os.makedirs("images", exist_ok=True)

    # Image API (free)
    url = f"https://image.pollinations.ai/prompt/{topic}"

    response = requests.get(url)

    filename = topic.replace(" ", "_") + ".jpg"
    path = os.path.join("images", filename)

    with open(path, "wb") as f:
        f.write(response.content)

    return path