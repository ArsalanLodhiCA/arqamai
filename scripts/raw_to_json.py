import re
from datetime import datetime
import pytz
import json
import os
import requests
import fitz  # PyMuPDF for PDFs
from docx import Document

def parse_schoology_messages(raw_text, timezone="America/Los_Angeles", download_dir="downloads"):
    messages = raw_text.strip().split('--@@--')
    results = []

    for idx, msg in enumerate(messages):
        if not msg.strip():
            continue

        # --- Header Parsing ---
        header_match = re.match(r'^(.*?) posted to (.*?)(?:\n|$)', msg.strip())
        sender = header_match.group(1).strip() if header_match else "Unknown"
        subject = header_match.group(2).strip() if header_match else "General"

        # --- Date Parsing ---
        date_match = re.search(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s\w+\s\d{1,2},\s\d{4}\sat\s\d{1,2}:\d{2}\s\w{2}', msg)
        today_match = re.search(r'Today at (\d{1,2}):(\d{2})\s(\w{2})', msg)

        if today_match:
            hour = int(today_match.group(1))
            minute = int(today_match.group(2))
            ampm = today_match.group(3).lower()
            if ampm == 'pm' and hour < 12:
                hour += 12
            now = datetime.now(pytz.timezone(timezone))
            sent_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0).isoformat()
        elif date_match:
            dt = datetime.strptime(date_match.group(0), "%a %b %d, %Y at %I:%M %p")
            dt = pytz.timezone(timezone).localize(dt)
            sent_at = dt.isoformat()
        else:
            sent_at = "Unknown"

        # --- Body Text Extraction ---
        body_parts = msg.strip().split('\n', maxsplit=2)
        body = body_parts[-1].strip() if len(body_parts) >= 3 else msg.strip()

        # --- Table Detection ---
        table_data = extract_table_from_body(body)

        # --- Attachment URL Detection ---
        attachment_urls = extract_attachment_urls(body)

        # --- Download + Extract Attachment Text ---
        attachments_text = ""
        for url in attachment_urls:
            downloaded_file = download_file(url, download_dir)
            if downloaded_file:
                attachments_text += extract_text_from_file(downloaded_file) + "\n"

        results.append({
            "id": f"msg{idx+1}",
            "source": "Schoology",
            "from": sender,
            "subject": subject,
            "sent_at": sent_at,
            "body": body,
            "table_block": table_data,
            "attachments_found": attachment_urls,
            "attachments_text": attachments_text.strip()
        })

    return results

# Helper: Detect tables/bulleted structures
def extract_table_from_body(text):
    if "|" in text and "---" in text:
        return "Possible table block detected"
    elif re.search(r'^\s*\d+\.\s+.+$', text, re.MULTILINE):
        return "Numbered list structure found"
    elif re.search(r'^\s*[-*+]\s+.+$', text, re.MULTILINE):
        return "Bulleted list structure found"
    return None

# Helper: Extract attachment links
def extract_attachment_urls(text):
    return re.findall(r'https?:\/\/[^\s]+?\.(?:pdf|docx|doc)', text)

# Helper: Download attachment
def download_file(url, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)
    filename = url.split("/")[-1]
    filepath = os.path.join(output_dir, filename)

    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"✅ Downloaded: {filename}")
            return filepath
        else:
            print(f"❌ Failed to download {url} (status {response.status_code})")
            return None
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return None

# Helper: Extract text from PDF/DOCX
def extract_text_from_file(filepath):
    if filepath.lower().endswith(".pdf"):
        try:
            doc = fitz.open(filepath)
            return "\n".join(page.get_text() for page in doc)
        except Exception as e:
            print(f"❌ Error reading PDF {filepath}: {e}")
            return ""
    elif filepath.lower().endswith(".docx"):
        try:
            doc = Document(filepath)
            return "\n".join(para.text for para in doc.paragraphs)
        except Exception as e:
            print(f"❌ Error reading DOCX {filepath}: {e}")
            return ""
    else:
        return ""

# 🚀 Usage Example
if __name__ == "__main__":
    with open("../data/schoology_raw.txt", "r") as f:
        raw_input = f.read()

    messages = parse_schoology_messages(raw_input)
    with open("../app/data/schoology_messages.json", "w") as f:
        json.dump(messages, f, indent=2)

    print("✅ All messages parsed and saved!")
