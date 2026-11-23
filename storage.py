import csv
import io
import json
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone

FIELDS = ["title", "description", "url", "source", "published_at", "category", "fetched_at"]

def load_news(path):
    path = Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("[]", encoding="utf-8")
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Dataset root must be a JSON list")
        return [normalize_record(row) for row in data if isinstance(row, dict) and row.get("title")]
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        backup = path.with_suffix(path.suffix + ".corrupt")
        try:
            path.replace(backup)
        except OSError:
            pass
        path.write_text("[]", encoding="utf-8")
        return []

def normalize_record(record):
    now = datetime.now(timezone.utc).isoformat()
    return {
        "title": str(record.get("title", "")).strip(),
        "description": str(record.get("description", "") or ""),
        "url": str(record.get("url", "") or ""),
        "source": str(record.get("source", "Unknown") or "Unknown"),
        "published_at": str(record.get("published_at", "") or now),
        "category": str(record.get("category", "Other") or "Other"),
        "fetched_at": str(record.get("fetched_at", "") or now)
    }

def save_news(path, items):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps([normalize_record(x) for x in items], indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)

def search_news(items, keyword="", category=""):
    q = (keyword or "").strip().lower()
    cat = (category or "").strip().lower()
    results = []
    for item in items:
        searchable = " ".join([item.get("title", ""), item.get("description", ""), item.get("source", "")]).lower()
        if q and q not in searchable:
            continue
        if cat and item.get("category", "").lower() != cat:
            continue
        results.append(item)
    return sorted(results, key=lambda x: x.get("published_at", ""), reverse=True)

def build_summary(items):
    cats = Counter(x.get("category", "Other") for x in items)
    sources = {x.get("source", "Unknown") for x in items}
    duplicate_keys = [x.get("url") or x.get("title", "").strip().lower() for x in items]
    duplicates = len(duplicate_keys) - len(set(duplicate_keys))
    return {
        "total": len(items),
        "categories": len(cats),
        "sources": len(sources),
        "duplicates": duplicates,
        "average_per_category": len(items) / len(cats) if cats else 0,
        "top_category": cats.most_common(1)[0][0] if cats else "—",
        "by_category": dict(sorted(cats.items(), key=lambda pair: pair[0].lower()))
    }

def export_csv(items, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(normalize_record(x) for x in items)
    return path

def export_json(items, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([normalize_record(x) for x in items], indent=2, ensure_ascii=False), encoding="utf-8")
    return path

def import_csv(content, existing):
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames or "title" not in [x.strip().lower() for x in reader.fieldnames]:
        raise ValueError("CSV must contain a title column")
    # Normalize header names to lowercase and trim whitespace.
    reader.fieldnames = [x.strip().lower() for x in reader.fieldnames]
    known = {x.get("url") or x.get("title", "").strip().lower() for x in existing}
    added, errors = 0, []
    for line_no, row in enumerate(reader, start=2):
        try:
            item = normalize_record(row)
            if not item["title"]:
                raise ValueError("title is blank")
            key = item["url"] or item["title"].lower()
            if key in known:
                continue
            existing.append(item)
            known.add(key)
            added += 1
        except Exception as exc:
            errors.append(f"row {line_no}: {exc}")
    return added, errors

def seed_demo_data(existing):
    samples = [
        ("India announces new digital public infrastructure initiative", "Government technology policy update.", "https://example.com/demo/1", "Demo News", "Technology"),
        ("Global markets respond to latest economic outlook", "Business and finance market coverage.", "https://example.com/demo/2", "Demo Business", "Business"),
        ("National cricket team prepares for upcoming tournament", "Sports update and match preparation.", "https://example.com/demo/3", "Demo Sports", "Sports"),
        ("Researchers report progress in clean energy study", "Science research and climate innovation.", "https://example.com/demo/4", "Demo Science", "Science"),
        ("Hospitals expand public health awareness programme", "Health services and medical awareness.", "https://example.com/demo/5", "Demo Health", "Health"),
        ("New film release attracts strong audience interest", "Entertainment industry update.", "https://example.com/demo/6", "Demo Entertainment", "Entertainment"),
        ("Leaders discuss policy priorities ahead of elections", "Politics and public policy coverage.", "https://example.com/demo/7", "Demo Politics", "Politics"),
        ("AI tools reshape software development workflows", "Technology and artificial intelligence news.", "https://example.com/demo/8", "Demo Tech", "Technology"),
    ]
    known = {x.get("url") or x.get("title", "").lower() for x in existing}
    added = 0
    now = datetime.now(timezone.utc).isoformat()
    for title, desc, url, source, category in samples:
        if url not in known:
            existing.append(normalize_record({"title": title, "description": desc, "url": url, "source": source, "category": category, "published_at": now, "fetched_at": now}))
            added += 1
    return added
