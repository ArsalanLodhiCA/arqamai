from datetime import datetime
from playwright.async_api import Page
from attachment_scraper import extract_attachments



async def wait_for_new_posts(prev_count: int, page: Page, retries: int = 3, delay: int = 1500):
    for attempt in range(retries):
        new_count = await page.locator("ul.s-edge-feed > li[id^='edge-assoc-']").count()
        print(f"🔍 Attempt {attempt+1}: Posts after click = {new_count} (before = {prev_count})")
        if new_count > prev_count:
            print("✅ New posts appeared.")
            return True
        await page.wait_for_timeout(delay)
    return False


def is_within_range(ts, start, end):
    try:
        dt = datetime.strptime(ts.strip(), "%a %b %d, %Y at %I:%M %p")
        return start <= dt <= end, dt
    except:
        return False, None

async def scrape_page_events(page: Page, seen_ids: set, msg_start: int, start_date, end_date):
    posts = await page.locator("ul.s-edge-feed > li[id^='edge-assoc-']").all()
    events = []
    msg_id = msg_start

    for post in posts:
        try:
            post_id = await post.get_attribute("id")
            # print(f"🔍 Checking post ID: {post_id}")

            if not post_id or post_id.strip() in seen_ids:
                print(f"↩️ Skipping duplicate post ID: {post_id}")
                continue
            seen_ids.add(post_id.strip())

            more_link = post.locator("a.show-more-link")
            if await more_link.is_visible():
                await more_link.click()
                await page.wait_for_timeout(500)  # let content expand

            ts_text = await post.locator("div.created span.small.gray").inner_text()
            in_range, dt = is_within_range(ts_text, start_date, end_date)
            # print(f"📅 Timestamp: {ts_text} → In range: {in_range}")

            if not in_range:
                continue

            # Scrape    
            try:
                author = await post.locator("span.long-username a").inner_text()
            except:
                author = "Unknown"

            try:
                group = await post.locator("a.sExtlink-processed").nth(1).inner_text()
            except:
                group = "Unknown"

            paragraphs = await post.locator("span.update-body.s-rte p").all_inner_texts()
            content = "\n".join(paragraphs).strip()

            if not content:
                print(f"⚠️ Post ID {post_id} has no content, skipping.")
                continue

            poll = await post.locator("div.s-poll-option-title").all_inner_texts()
            
            attachments = await extract_attachments(post)

            events.append({
                "id": f"msg{msg_id}",
                "author": author,
                "group": group,
                "timestamp": ts_text,
                "content": content,
                "poll": poll if poll else None,
                "attachments_found": attachments,
                "attachments_text": ""
            })

            msg_id += 1

        except Exception as e:
            print(f"⚠️ Post skipped due to error: {e}")

    return events

async def fetch_paginated_events(page: Page, start_date, end_date):
    all_events = []
    msg_counter = 1
    seen_ids = set()

    while True:
        prev_count = await page.locator("ul.s-edge-feed > li[id^='edge-assoc-']").count()
        print(f"📄 Found {prev_count} posts on this page.")

        new_events = await scrape_page_events(page, seen_ids, msg_counter, start_date, end_date)

        print(f"🔎 Total posts seen so far: {len(seen_ids)}")

        if not new_events:
            print("🛑 No new events on this page, stopping.")
            break

        all_events.extend(new_events)
        print(f"✅ Scraped {len(new_events)} new events, total so far: {len(all_events)}")
        msg_counter += len(new_events)

        # Locate "More" button after scraping
        more = page.locator("li.s-edge-feed-more-link a")

        # 🔐 Guard clause — does it even exist in the DOM?
        if not more or not await more.count():
            print("⚠️ 'More' link not found — exiting loop.")
            break

        try:
            if await more.is_visible():
                print("🔄 Clicking 'More' to load additional posts...")
                await more.click()

                # Wait for DOM mutation at the container level
                feed = page.locator("ul.s-edge-feed")
                await feed.wait_for(timeout=5000)

                # Try up to 3 times to detect new posts
                
                if not await wait_for_new_posts(prev_count, page):
                    print("⚠️ No new posts detected after 'More' click — exiting loop.")
                    break


                await page.wait_for_timeout(2000)  # Let DOM settle
            else:
                print("✅ No more 'More' link — finished pagination.")
                break
        except Exception as e:
            print("Error:", e)
            return []

    return all_events
