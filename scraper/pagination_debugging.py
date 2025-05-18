from playwright.async_api import async_playwright, Page
import asyncio

USERNAME = "amimalodhi@arqamschool.org"
PASSWORD = "Engin2day!"


# 🔁 Reusable helper to test "More" pagination
async def test_more_clicks(page: Page, max_clicks: int = 5):
    for i in range(max_clicks):
        more = page.locator('li.s-edge-feed-more-link a')

        try:
            await more.wait_for(state="visible", timeout=5000)
        except:
            print("✅ No more 'More' link found — exiting loop.")
            break

        print(f"🔁 Clicking More (page {i + 1})...")
        await more.click()
        await page.wait_for_timeout(4000)  # wait for new posts to render

        # Print partial DOM content
        html = await page.content()
        print(f"\n🌐 DOM Snapshot after page {i + 1}:\n{'-' * 50}\n{html[:2000]}\n{'-' * 50}\n")

        count = await page.locator("ul.s-edge-feed > li[id^='edge-assoc-']").count()
        print(f"📄 Posts now visible: {count}")


# 🚀 Main function to login and trigger test
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 🔐 Login
        await page.goto("https://app.schoology.com/login")
        await page.fill("input#edit-mail", USERNAME)
        await page.fill("input#edit-pass", PASSWORD)
        await page.click("input#edit-submit")
        await page.wait_for_load_state("networkidle")
        print("✅ Logged in — waiting 5 seconds before clicking 'More'...")
        await page.wait_for_timeout(5000)

        print("✅ Logged in — pausing for DevTools inspection...")

        await page.pause()  # ← INSERT HERE

        # ▶️ Initial Click "More"
        more_link = page.locator("li.s-edge-feed-more-link a")
        if await more_link.is_visible():
            print("🔄 Clicking initial 'More' link...")
            await more_link.click()
        else:
            print("❌ Initial 'More' link not found.")

        # 🔁 Run extended pagination test
        await test_more_clicks(page, max_clicks=4)

        # ⏳ Manual inspection pause
        print("⏸️  Pausing 60 seconds — inspect the browser manually.")
        await page.wait_for_timeout(60000)

        await browser.close()

# 🧠 Kick off
asyncio.run(main())
