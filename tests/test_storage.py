import json
from storage import load_news, save_news, search_news, build_summary, import_csv

def test_missing_file_creates_empty_dataset(tmp_path):
    path = tmp_path / "news.json"
    assert load_news(path) == []
    assert json.loads(path.read_text()) == []

def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "news.json"
    records = [{"title": "Test headline", "category": "Technology", "source": "Unit Test"}]
    save_news(path, records)
    assert load_news(path)[0]["title"] == "Test headline"

def test_search_and_summary():
    records = [
        {"title": "AI changes software", "category": "Technology", "source": "A"},
        {"title": "Markets move", "category": "Business", "source": "B"},
    ]
    assert len(search_news(records, keyword="software")) == 1
    summary = build_summary(records)
    assert summary["total"] == 2
    assert summary["categories"] == 2

def test_csv_import_rejects_duplicate():
    existing = [{"title": "One", "url": "https://example.com/1"}]
    csv_text = "title,url,category\nOne,https://example.com/1,General\nTwo,https://example.com/2,Science\n"
    added, errors = import_csv(csv_text, existing)
    assert added == 1
    assert len(existing) == 2
    assert errors == []
