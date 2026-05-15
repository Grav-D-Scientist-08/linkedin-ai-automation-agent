from playwright.sync_api import sync_playwright
import os
import time
import requests
import re
import uuid
import random

PROFILE_PATH = r"D:\linkedin-ai-agent\pw_profile"


def slugify(text):
    return re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()


def generate_image(topic):
    folder = "images/generated"
    os.makedirs(folder, exist_ok=True)

    styles = [
        "futuristic digital art",
        "professional business illustration",
        "modern AI technology poster",
        "clean minimal tech artwork",
        "cyber futuristic concept art",
        "high-tech office environment",
        "AI robotics concept"
    ]

    style = random.choice(styles)

    filename = f"{slugify(topic)}_{uuid.uuid4().hex[:8]}.jpg"
    path = os.path.join(folder, filename)

    prompt = f"{topic}, {style}, high quality professional LinkedIn image"

    url = "https://image.pollinations.ai/prompt/" + requests.utils.quote(prompt)

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        with open(path, "wb") as f:
            f.write(response.content)

        print(f"🖼 Image generated: {path}")
        return path

    except Exception as e:
        print("❌ Image generation failed:", e)
        return None


def post_on_linkedin(post_text, image_path=None):

    if not image_path:
        heading = post_text.split("\n")[0]
        image_path = generate_image(heading)

    with sync_playwright() as p:

        browser = p.chromium.launch_persistent_context(
            PROFILE_PATH,
            headless=False,
            args=["--start-maximized"],
            no_viewport=True
        )

        page = browser.new_page()

        print("🚀 Opening LinkedIn...")
        page.goto("https://www.linkedin.com/feed/?shareActive=true", timeout=90000)
        time.sleep(8)

        if "login" in page.url:
            print("👉 Login manually (40 sec)...")
            time.sleep(40)
            page.goto("https://www.linkedin.com/feed/?shareActive=true")
            time.sleep(8)

        print("✅ Logged in")

        # FIND EDITOR
        editor = None

        for _ in range(12):
            boxes = page.locator("div[role='textbox']")

            for i in range(boxes.count()):
                el = boxes.nth(i)

                aria = el.get_attribute("aria-label") or ""
                cls = el.get_attribute("class") or ""

                if "msg-form" in cls:
                    continue

                if (
                    "What do you want to talk about" in aria
                    or "Text editor" in aria
                    or "Start a post" in aria
                ):
                    editor = el
                    break

            if editor:
                break

            time.sleep(2)

        if not editor:
            print("❌ Editor not found")
            browser.close()
            return

        editor.click(force=True)
        time.sleep(2)

        print("✅ Editor ready")

        # INSERT TEXT
        element = editor.element_handle()

        page.evaluate("""
        (data) => {
            const el = data.el;
            const text = data.text;

            el.innerHTML = "";
            el.focus();

            const lines = text.split("\\n");

            lines.forEach((line, i) => {
                document.execCommand("insertText", false, line);
                if (i !== lines.length - 1) {
                    document.execCommand("insertHTML", false, "<br>");
                }
            });

            el.dispatchEvent(new Event('input', { bubbles: true }));
        }
        """, {
            "el": element,
            "text": post_text
        })

        print("✅ Text inserted")
        time.sleep(3)

        # IMAGE UPLOAD
        try:
            if image_path and os.path.exists(image_path):

                print("📸 Uploading image...")

                with page.expect_file_chooser() as fc:
                    page.locator("button[aria-label*='media']").first.click()

                fc.value.set_files(os.path.abspath(image_path))
                print("📂 File selected")

                time.sleep(6)

                # NEXT
                try:
                    next_btn = page.locator("button:has-text('Next')").first
                    if next_btn.is_visible():
                        next_btn.click()
                        print("➡️ Next clicked")
                        time.sleep(4)
                except:
                    pass

                # DONE
                try:
                    done_btn = page.locator("button:has-text('Done')").first
                    if done_btn.is_visible():
                        done_btn.click()
                        print("✅ Done clicked")
                        time.sleep(4)
                except:
                    pass

                print("🖼 Image uploaded")

        except Exception as e:
            print("❌ Image upload error:", e)

        # POST
        try:
            post_btn = page.locator("button:has-text('Post')").last
            post_btn.wait_for(timeout=30000)

            while not post_btn.is_enabled():
                time.sleep(1)

            post_btn.scroll_into_view_if_needed()
            time.sleep(2)

            post_btn.click(force=True)

            print("🚀 Publishing post...")

            time.sleep(10)

            if page.locator("div[role='dialog']").count() == 0:
                print("✅ POST PUBLISHED SUCCESSFULLY")
            else:
                print("⚠️ Post status uncertain. Check manually.")

        except Exception as e:
            print("❌ Post error:", e)

        time.sleep(5)
        browser.close()