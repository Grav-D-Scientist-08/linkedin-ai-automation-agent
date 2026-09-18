from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os
import time
import requests
import re
import uuid
import random


# ============================================================
# SETTINGS
# ============================================================

PROFILE_PATH = r"D:\linkedin-ai-agent\pw_profile"

LINKEDIN_URL = "https://www.linkedin.com/feed/"


# ============================================================
# SLUGIFY
# ============================================================

def slugify(text):
    return re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()


# ============================================================
# GENERATE IMAGE
# ============================================================

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

    filename = (
        f"{slugify(topic)}_{uuid.uuid4().hex[:8]}.jpg"
    )

    path = os.path.join(folder, filename)

    prompt = (
        f"{topic}, {style}, "
        "high quality professional LinkedIn image"
    )

    url = (
        "https://image.pollinations.ai/prompt/"
        + requests.utils.quote(prompt)
    )

    try:

        print("🎨 Generating image...")

        response = requests.get(
            url,
            timeout=60
        )

        response.raise_for_status()

        with open(path, "wb") as f:
            f.write(response.content)

        print(f"🖼 Image generated: {path}")

        return path

    except Exception as e:

        print("❌ Image generation failed:", e)

        return None


# ============================================================
# FIND LINKEDIN POST EDITOR
# ============================================================

def find_post_editor(page):

    print("🔍 Looking for LinkedIn post editor...")

    # --------------------------------------------------------
    # METHOD 1:
    # Look for contenteditable elements
    # --------------------------------------------------------

    selectors = [
        "div[contenteditable='true']",
        "div[role='textbox'][contenteditable='true']",
        "[contenteditable='true'][role='textbox']",
        "div[role='textbox']"
    ]

    for attempt in range(10):

        for selector in selectors:

            try:

                elements = page.locator(selector)

                count = elements.count()

                for i in range(count):

                    element = elements.nth(i)

                    if element.is_visible():

                        print(
                            f"✅ Editor found using: {selector}"
                        )

                        return element

            except Exception:
                pass

        time.sleep(1)

    return None


# ============================================================
# OPEN CREATE POST WINDOW
# ============================================================

def open_post_composer(page):

    print("📝 Opening Create Post...")

    # --------------------------------------------------------
    # Try Start a post button
    # --------------------------------------------------------

    start_post_selectors = [

        "button:has-text('Start a post')",

        "[role='button']:has-text('Start a post')",

        "div:has-text('Start a post')"

    ]

    for selector in start_post_selectors:

        try:

            locator = page.locator(selector)

            count = locator.count()

            for i in range(count):

                element = locator.nth(i)

                if element.is_visible():

                    print(
                        f"🖱 Clicking Start a post: {selector}"
                    )

                    element.click(force=True)

                    time.sleep(3)

                    return True

        except Exception:
            pass

    # --------------------------------------------------------
    # Try accessible role
    # --------------------------------------------------------

    try:

        button = page.get_by_role(
            "button",
            name=re.compile(
                r"start a post",
                re.IGNORECASE
            )
        ).first

        if button.is_visible():

            button.click(force=True)

            time.sleep(3)

            return True

    except Exception:
        pass

    print("⚠️ Start a post button not found")

    return False


# ============================================================
# UPLOAD IMAGE
# ============================================================

def upload_image(page, image_path):

    if not image_path:
        return False

    if not os.path.exists(image_path):

        print(
            f"❌ Image file not found: {image_path}"
        )

        return False

    print("📸 Uploading image...")

    # --------------------------------------------------------
    # Possible LinkedIn media buttons
    # --------------------------------------------------------

    media_selectors = [

        "button[aria-label*='media' i]",

        "button[aria-label*='photo' i]",

        "button[aria-label*='image' i]",

        "[role='button'][aria-label*='media' i]",

        "[role='button'][aria-label*='photo' i]",

        "[role='button'][aria-label*='image' i]"

    ]

    for selector in media_selectors:

        try:

            buttons = page.locator(selector)

            count = buttons.count()

            for i in range(count):

                button = buttons.nth(i)

                if not button.is_visible():
                    continue

                print(
                    f"📎 Media button found: {selector}"
                )

                with page.expect_file_chooser(
                    timeout=10000
                ) as file_chooser_info:

                    button.click(force=True)

                file_chooser = file_chooser_info.value

                file_chooser.set_files(
                    os.path.abspath(image_path)
                )

                print("📂 Image file selected")

                time.sleep(5)

                return True

        except Exception:
            pass

    print("⚠️ Media button not found")

    return False


# ============================================================
# POST ON LINKEDIN
# ============================================================

def post_on_linkedin(post_text, image_path=None):

    # --------------------------------------------------------
    # Generate image if not provided
    # --------------------------------------------------------

    if not image_path:

        heading = post_text.split("\n")[0]

        image_path = generate_image(heading)

    # --------------------------------------------------------
    # Playwright
    # --------------------------------------------------------

    with sync_playwright() as p:

        print("🌐 Starting browser...")

        browser = p.chromium.launch_persistent_context(

            PROFILE_PATH,

            headless=False,

            args=[
                "--start-maximized"
            ],

            no_viewport=True
        )

        page = browser.new_page()

        try:

            # =================================================
            # OPEN LINKEDIN
            # =================================================

            print("🚀 Opening LinkedIn...")

            page.goto(
                LINKEDIN_URL,
                timeout=90000,
                wait_until="domcontentloaded"
            )

            time.sleep(8)

            # =================================================
            # CHECK LOGIN
            # =================================================

            if "login" in page.url.lower():

                print(
                    "👉 LinkedIn login required."
                )

                print(
                    "👉 Please login manually. "
                    "Waiting 60 seconds..."
                )

                time.sleep(60)

                page.goto(
                    LINKEDIN_URL,
                    timeout=90000,
                    wait_until="domcontentloaded"
                )

                time.sleep(8)

            # =================================================
            # VERIFY LOGIN
            # =================================================

            if "login" in page.url.lower():

                print(
                    "❌ LinkedIn login was not completed."
                )

                return

            print("✅ Logged in")

            # =================================================
            # OPEN CREATE POST
            # =================================================

            composer_opened = open_post_composer(page)

            if not composer_opened:

                print(
                    "⚠️ Could not click Start a post."
                )

                # Take screenshot for debugging

                try:

                    page.screenshot(
                        path="linkedin_debug.png",
                        full_page=True
                    )

                    print(
                        "📸 Debug screenshot saved: "
                        "linkedin_debug.png"
                    )

                except Exception:
                    pass

                return

            # =================================================
            # FIND EDITOR
            # =================================================

            editor = find_post_editor(page)

            if not editor:

                print(
                    "❌ LinkedIn post editor not found."
                )

                try:

                    page.screenshot(
                        path="linkedin_editor_debug.png",
                        full_page=True
                    )

                    print(
                        "📸 Debug screenshot saved: "
                        "linkedin_editor_debug.png"
                    )

                except Exception:
                    pass

                return

            # =================================================
            # CLICK EDITOR
            # =================================================

            editor.click(force=True)

            time.sleep(1)

            print("✅ Editor ready")

            # =================================================
            # INSERT POST TEXT
            # =================================================

            try:

                editor.fill(post_text)

            except Exception:

                # Fallback method

                page.keyboard.insert_text(
                    post_text
                )

            print("✅ Text inserted")

            time.sleep(3)

            # =================================================
            # UPLOAD IMAGE
            # =================================================

            if image_path:

                upload_success = upload_image(
                    page,
                    image_path
                )

                if upload_success:

                    print(
                        "🖼 Image uploaded successfully"
                    )

                    time.sleep(5)

                    # -----------------------------------------
                    # NEXT BUTTON
                    # -----------------------------------------

                    try:

                        next_button = page.get_by_role(
                            "button",
                            name=re.compile(
                                r"next",
                                re.IGNORECASE
                            )
                        ).first

                        if next_button.is_visible():

                            next_button.click(
                                force=True
                            )

                            print(
                                "➡️ Next clicked"
                            )

                            time.sleep(4)

                    except Exception:
                        pass

                    # -----------------------------------------
                    # DONE BUTTON
                    # -----------------------------------------

                    try:

                        done_button = page.get_by_role(
                            "button",
                            name=re.compile(
                                r"done",
                                re.IGNORECASE
                            )
                        ).first

                        if done_button.is_visible():

                            done_button.click(
                                force=True
                            )

                            print(
                                "✅ Done clicked"
                            )

                            time.sleep(4)

                    except Exception:
                        pass

                else:

                    print(
                        "⚠️ Image upload was not completed."
                    )

            # =================================================
            # FIND POST BUTTON
            # =================================================

            print("🔍 Looking for Post button...")

            post_button = None

            # Method 1
            try:

                buttons = page.get_by_role(
                    "button",
                    name=re.compile(
                        r"^post$",
                        re.IGNORECASE
                    )
                )

                count = buttons.count()

                for i in range(count):

                    btn = buttons.nth(i)

                    if btn.is_visible():

                        post_button = btn

            except Exception:
                pass

            # Method 2
            if not post_button:

                try:

                    buttons = page.locator(
                        "button:has-text('Post')"
                    )

                    count = buttons.count()

                    for i in range(count):

                        btn = buttons.nth(i)

                        if btn.is_visible():

                            post_button = btn

                except Exception:
                    pass

            # =================================================
            # CLICK POST
            # =================================================

            if not post_button:

                print(
                    "❌ Post button not found."
                )

                try:

                    page.screenshot(
                        path="linkedin_post_debug.png",
                        full_page=True
                    )

                    print(
                        "📸 Debug screenshot saved: "
                        "linkedin_post_debug.png"
                    )

                except Exception:
                    pass

                return

            print("✅ Post button found")

            # Wait until enabled

            for _ in range(30):

                try:

                    if post_button.is_enabled():

                        break

                except Exception:
                    pass

                time.sleep(1)

            # ------------------------------------------------
            # Publish
            # ------------------------------------------------

            post_button.scroll_into_view_if_needed()

            time.sleep(2)

            post_button.click(force=True)

            print("🚀 Publishing post...")

            # =================================================
            # WAIT FOR PUBLISH
            # =================================================

            time.sleep(10)

            print(
                "✅ POST PUBLISHED / SUBMITTED"
            )

        except PlaywrightTimeoutError as e:

            print(
                "❌ Playwright timeout:"
            )

            print(e)

            try:

                page.screenshot(
                    path="linkedin_timeout.png",
                    full_page=True
                )

                print(
                    "📸 Debug screenshot saved: "
                    "linkedin_timeout.png"
                )

            except Exception:
                pass

        except Exception as e:

            print(
                "❌ LinkedIn automation error:"
            )

            print(e)

            try:

                page.screenshot(
                    path="linkedin_error.png",
                    full_page=True
                )

                print(
                    "📸 Debug screenshot saved: "
                    "linkedin_error.png"
                )

            except Exception:
                pass

        finally:

            time.sleep(5)

            browser.close()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_post = """
🚀 The Future of Artificial Intelligence

AI is moving faster than ever.

Generative AI, AI agents and intelligent automation are changing how businesses work and how professionals solve problems.

The most interesting part is not just the technology itself — it's how people are using it to solve real-world problems.

What AI trend are you currently exploring?

#AI #ArtificialIntelligence #GenerativeAI #DataScience #MachineLearning
"""

    post_on_linkedin(
        test_post
    )