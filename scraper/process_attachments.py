# scraper/process_attachments.py

import aiohttp
import aiofiles
import os
import json
from pathlib import Path
from PyPDF2 import PdfReader  # or use pdfplumber
from docx import Document

DOWNLOAD_DIR = "downloads"

async def download_file(session, url, filename):
    async with session.get(url) as resp:
        if resp.status == 200:
            async with aiofiles.open(filename, "wb") as f:
                await f.write(await resp.read())
            return filename
    return None

def extract_text_from_file(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        return None

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except Exception as e:
        print(f"PDF parse error: {e}")
        return None

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print(f"DOCX parse error: {e}")
        return None

async def process_event_attachments(events):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    async with aiohttp.ClientSession() as session:
        for event in events:
            contents = []
            for attachment in event.get("attachments", []):
                filename = attachment["url"].split("/")[-1]
                local_path = os.path.join(DOWNLOAD_DIR, filename)
                downloaded = await download_file(session, attachment["url"], local_path)
                if downloaded:
                    content = extract_text_from_file(local_path)
                    if content:
                        contents.append({
                            "filename": filename,
                            "content": content
                        })
            if contents:
                event["attachment_contents"] = contents
    return events

async def main():
    # Load the event file
    with open("scraper/events_20250506_220647.json") as f:
        events = json.load(f)

    enriched = await process_event_attachments(events)

    # Save enriched data
    with open("scraper/events_enriched.json", "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
