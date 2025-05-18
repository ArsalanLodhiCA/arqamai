# from playwright.async_api import async_playwright
# from datetime import datetime
# from fetch_events import fetch_paginated_events
# from login import login
 
# from store import save_events_to_file


# START_DATE = datetime(2025, 4, 1)
# END_DATE = datetime(2025, 5, 6, 23, 59, 59)

# async def main():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         page = await browser.new_page()

#         await login(page)

#         events = await fetch_paginated_events(page, START_DATE, END_DATE)
        
#         save_events_to_file(events)

#         await browser.close()

# import asyncio
# asyncio.run(main())
