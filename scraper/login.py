from playwright.async_api import Page

async def login(page: Page):
    await page.goto("https://app.schoology.com/login")

    await page.fill('input#edit-mail', "amimalodhi@arqamschool.org")
    await page.fill('input#edit-pass', "Engin2day!")
    await page.click('input#edit-submit')  # Login button

    await page.wait_for_load_state('networkidle')
    print("✅ Logged in.")
