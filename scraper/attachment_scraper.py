# scraper/attachment_scraper.py

from playwright.async_api import Locator

BASE_URL = "https://app.schoology.com"

async def extract_attachments(post: Locator):
    attachments = []

    try:
        # Select only true downloadable file links from attachment blocks
        links = await post.locator("span.attachments-file-name a.sExtlink-processed").all()
        for link in links:
            href = await link.get_attribute("href")
            text = await link.inner_text()

            if href:
                attachments.append({
                    "text": text.strip() if text else "Unnamed",
                    "url": BASE_URL + href.strip()
                })

    except Exception as e:
        print(f"⚠️ Error extracting attachments: {e}")

    return attachments if attachments else None
