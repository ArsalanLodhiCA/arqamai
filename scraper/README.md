

# 🧭 Pipeline Overview


```scraper/__init__.py  ←  🧠 Orchestration script (driver)
   └── login.py        ←  🔑 Login to Schoology
   └── fetch_events.py ←  📥 Fetch & parse all posts (calls scrape_page_events)
        └── attachment_scraper.py ←  📎 Called inside scrape_page_events to extract attachment links
   └── store.py        ←  💾 Save scraped events to a timestamped JSON
   ↓
process_attachments.py ←  📄 Load that JSON, download files, extract text, enrich data
```

# 🔁 Execution Flow
```
Step 1: Run `__init__.py`
├── Login using login.py
├── Call `fetch_paginated_events()` from fetch_events.py
│   └── Repeatedly call `scrape_page_events()`
│       ├── Parse each post
│       ├── Extract metadata
│       ├── Extract attachments using extract_attachments(post) in attachment_scraper.py
│       └── Return list of event dicts
├── Save result JSON using store.py
└── Done ✅

Step 2: Run `process_attachments.py`
├── Load JSON saved by Step 1
├── For each event:
│   └── Download each attachment
│   └── Extract text from `.pdf` or `.docx`
│   └── Add `attachment_contents` field to the event
├── Save enriched output to a new JSON
└── Done ✅
```