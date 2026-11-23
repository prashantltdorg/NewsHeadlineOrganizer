
import requests

from pathlib import Path

from fasthtml.common import *
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse

from news_service import fetch_headlines, categorize_headline

from storage import (
    load_news,
    save_news,
    search_news,
    import_csv,
    export_csv,
    export_json,
    build_summary,
    seed_demo_data,
)

from charts import (
    create_category_chart,
    create_timeline_chart,
)


# ==================================================
# PROJECT CONFIGURATION
# ==================================================

ROOT = Path(__file__).resolve().parent

DATA_DIR = ROOT / "data"
STATIC_DIR = ROOT / "static"
REPORTS_DIR = ROOT / "reports"

DATA_FILE = DATA_DIR / "news_data.json"

DATA_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


# ==================================================
# CREATE FASTHTML APPLICATION
# ==================================================

app, rt = fast_app()

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)


# ==================================================
# COMMON PAGE LAYOUT
# ==================================================

def page(content, active="Dashboard"):

    nav_items = [
        ("Dashboard", "/"),
        ("Headlines", "/headlines"),
        ("Analytics", "/analytics"),
        ("Import / Export", "/data-tools"),
    ]

    return Html(
        Head(
            Title("News Headline Organizer"),

            Meta(
                name="viewport",
                content="width=device-width, initial-scale=1"
            ),

            Link(
                rel="preconnect",
                href="https://fonts.googleapis.com"
            ),

            Link(
                rel="preconnect",
                href="https://fonts.gstatic.com",
                crossorigin="anonymous"
            ),

            Link(
                rel="stylesheet",
                href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap"
            ),

            Link(
                rel="stylesheet",
                href="/static/style.css"
            ),
        ),

        Body(
            Div(

                Header(

                    Div(
                        Div(
                            "NEWS",
                            Span(" / "),
                            "ORGANIZER",
                            cls="brand"
                        ),

                        Div(
                            "PYTHON • FASTHTML • LOCAL DATA",
                            cls="pill"
                        ),

                        cls="top"
                    ),

                    Div(
                        Div(
                            "NEWS INTELLIGENCE WORKSPACE",
                            cls="eyebrow"
                        ),

                        H1("Stay informed. Stay organized."),

                        P(
                            "Fetch, classify, search and analyze headlines in one focused workspace.",
                            cls="sub"
                        ),

                        Div(
                            *[
                                A(
                                    name,
                                    href=href,
                                    cls=(
                                        "active"
                                        if name == active
                                        else ""
                                    )
                                )
                                for name, href in nav_items
                            ],

                            cls="nav"
                        ),

                        cls="hero"
                    ),
                ),

                content,

                Footer(
                    "News Headline Organizer • Local-first Python application • Built with FastHTML",
                    cls="footer"
                ),

                cls="shell"
            )
        )
    )


# ==================================================
# NOTIFICATION MESSAGE
# ==================================================

def flash(message, error=False):

    return Div(
        message,
        cls="notice error" if error else "notice"
    )


# ==================================================
# HEADLINE TABLE
# ==================================================

def headline_rows(items):

    if not items:

        return Tbody(
            Tr(
                Td(
                    "No headlines found. Fetch news or adjust your search.",
                    colspan="4",
                    cls="empty"
                )
            )
        )

    rows = []

    for item in items[:100]:

        rows.append(
            Tr(

                Td(
                    Div(
                        item.get("title", "Untitled"),
                        cls="headline"
                    ),

                    P(
                        item.get("description", "")[:145],
                        cls="small"
                    ) if item.get("description") else ""
                ),

                Td(
                    Span(
                        item.get("category", "Other"),
                        cls="tag"
                    )
                ),

                Td(
                    A(
                        item.get("source", "Source"),
                        href=item.get("url") or "#",
                        target="_blank"
                    )
                ),

                Td(
                    item.get("published_at", "")[:16].replace("T", " ")
                )

            )
        )

    return Tbody(*rows)


# ==================================================
# DASHBOARD
# ==================================================

@rt("/")
def get():

    items = load_news(DATA_FILE)

    summary = build_summary(items)

    recent = sorted(
        items,
        key=lambda x: x.get("published_at", ""),
        reverse=True
    )[:6]

    return page(

        Div(

            # STATISTICS

            Div(

                Div(
                    Div("TOTAL HEADLINES", cls="metric-label"),
                    Div(str(summary["total"]), cls="metric"),
                    Div("Stored locally", cls="metric-note"),
                    cls="card"
                ),

                Div(
                    Div("CATEGORIES", cls="metric-label"),
                    Div(str(summary["categories"]), cls="metric"),
                    Div("Distinct classifications", cls="metric-note"),
                    cls="card"
                ),

                Div(
                    Div("SOURCES", cls="metric-label"),
                    Div(str(summary["sources"]), cls="metric"),
                    Div("Unique publishers", cls="metric-note"),
                    cls="card"
                ),

                Div(
                    Div("DUPLICATES", cls="metric-label"),
                    Div(str(summary["duplicates"]), cls="metric"),
                    Div("Detected during ingestion", cls="metric-note"),
                    cls="card"
                ),

                cls="grid"
            ),

            # FETCH LATEST NEWS

            Div(

                Div(

                    H2("Fetch latest headlines"),

                    P(
                        "Fetch the latest headlines from Google News RSS. No API key or registration required.",
                        cls="small"
                    ),

                    Form(

                        Label("Country", fr="country"),

                        Select(
                            Option("India", value="in"),
                            Option("United States", value="us"),
                            Option("United Kingdom", value="gb"),
                            name="country",
                            id="country"
                        ),

                        Label("Category", fr="category"),

                        Select(
                            Option("All categories", value=""),

                            *[
                                Option(c, value=c.lower())
                                for c in [
                                    "Business",
                                    "Entertainment",
                                    "General",
                                    "Health",
                                    "Science",
                                    "Sports",
                                    "Technology"
                                ]
                            ],

                            name="category",
                            id="category"
                        ),

                        Button("Fetch headlines"),

                        action="/fetch",
                        method="post"
                    ),

                    Div(
                        "FREE NEWS FETCHING • NO API KEY REQUIRED",
                        cls="small"
                    ),

                    cls="card stack"
                ),

                # RECENT HEADLINES

                Div(

                    Div(
                        H2("Recent headlines"),

                        A(
                            "View all →",
                            href="/headlines"
                        ),

                        cls="section-head"
                    ),

                    Table(

                        Thead(
                            Tr(
                                Th("Headline"),
                                Th("Category"),
                                Th("Source"),
                                Th("Published")
                            )
                        ),

                        headline_rows(recent)

                    ),

                    cls="card"
                ),

                cls="layout"
            ),

            # QUICK ACTIONS

            Div(

                H2("Quick actions"),

                Div(

                    A(
                        "Browse headlines",
                        href="/headlines",
                        cls="btn secondary"
                    ),

                    A(
                        "Open analytics",
                        href="/analytics",
                        cls="btn secondary"
                    ),

                    A(
                        "Import / export data",
                        href="/data-tools",
                        cls="btn secondary"
                    ),

                    cls="row"
                ),

                cls="card"
            )

        ),

        "Dashboard"
    )


# ==================================================
# FETCH NEWS - NO API KEY REQUIRED
# ==================================================

@rt("/fetch", methods=["POST"])
def post(country: str = "in", category: str = ""):

    try:

        # Fetch headlines from Google News RSS

        fetched = fetch_headlines(
            country=country,
            category=category or None
        )

        existing = load_news(DATA_FILE)

        # Identify existing headlines

        known = {
            x.get("url") or x.get("title", "").strip().lower()
            for x in existing
        }

        added = 0

        # Add only new headlines

        for article in fetched:

            key = (
                article.get("url")
                or article.get("title", "").strip().lower()
            )

            if key and key not in known:

                article["category"] = (
                    article.get("category")
                    or categorize_headline(
                        article.get("title", "")
                        + " "
                        + article.get("description", "")
                    )
                )

                existing.append(article)

                known.add(key)

                added += 1

        # Save locally

        save_news(DATA_FILE, existing)

        return page(

            Div(

                flash(
                    f"News fetched successfully! "
                    f"Received {len(fetched)} headlines "
                    f"and added {added} new headlines."
                ),

                A(
                    "View headlines",
                    href="/headlines",
                    cls="btn"
                ),

                A(
                    "Back to dashboard",
                    href="/",
                    cls="btn secondary"
                ),

                cls="card"
            )

        )

    except requests.RequestException as exc:

        return page(

            Div(

                flash(
                    f"Could not connect to Google News RSS. "
                    f"Check your internet connection. Details: {exc}",
                    True
                ),

                A(
                    "Back to dashboard",
                    href="/",
                    cls="btn secondary"
                ),

                cls="card"
            )

        )

    except Exception as exc:

        return page(

            Div(

                flash(
                    f"Something went wrong while fetching news: {exc}",
                    True
                ),

                A(
                    "Back to dashboard",
                    href="/",
                    cls="btn secondary"
                ),

                cls="card"
            )

        )


# ==================================================
# HEADLINES AND SEARCH
# ==================================================

@rt("/headlines")
def get(q: str = "", category: str = ""):

    items = search_news(
        load_news(DATA_FILE),
        keyword=q,
        category=category
    )

    return page(

        Div(

            Div(

                H2("Headline library"),

                P(
                    f"{len(items)} matching records • showing up to 100",
                    cls="small"
                ),

                cls="section-head"
            ),

            Div(

                Form(

                    Div(

                        Input(
                            name="q",
                            value=q,
                            placeholder="Search headline, description or source..."
                        ),

                        Select(

                            Option(
                                "All categories",
                                value=""
                            ),

                            *[
                                Option(
                                    c,
                                    value=c,
                                    selected=(
                                        category.lower() == c.lower()
                                    )
                                )

                                for c in [
                                    "Business",
                                    "Entertainment",
                                    "General",
                                    "Health",
                                    "Science",
                                    "Sports",
                                    "Technology",
                                    "Other"
                                ]
                            ],

                            name="category"
                        ),

                        Button("Search"),

                        cls="row"
                    ),

                    action="/headlines",
                    method="get"
                ),

                cls="card"
            ),

            Div(

                Table(

                    Thead(
                        Tr(
                            Th("Headline"),
                            Th("Category"),
                            Th("Source"),
                            Th("Published")
                        )
                    ),

                    headline_rows(items)

                ),

                cls="card"
            )

        ),

        "Headlines"
    )


# ==================================================
# ANALYTICS
# ==================================================

@rt("/analytics")
def get():

    items = load_news(DATA_FILE)

    summary = build_summary(items)

    create_category_chart(
        items,
        STATIC_DIR / "category_chart.png"
    )

    create_timeline_chart(
        items,
        STATIC_DIR / "timeline_chart.png"
    )

    category_rows = [

        Tr(
            Td(k),
            Td(str(v))
        )

        for k, v in summary["by_category"].items()

    ]

    return page(

        Div(

            H2("Analytics overview"),

            # ANALYTICS STATISTICS

            Div(

                Div(
                    Div("TOTAL RECORDS", cls="metric-label"),
                    Div(str(summary["total"]), cls="metric"),
                    cls="card"
                ),

                Div(
                    Div("AVERAGE PER CATEGORY", cls="metric-label"),
                    Div(
                        f'{summary["average_per_category"]:.1f}',
                        cls="metric"
                    ),
                    cls="card"
                ),

                Div(
                    Div("MOST ACTIVE CATEGORY", cls="metric-label"),
                    Div(summary["top_category"], cls="metric"),
                    cls="card"
                ),

                Div(
                    Div("UNIQUE SOURCES", cls="metric-label"),
                    Div(str(summary["sources"]), cls="metric"),
                    cls="card"
                ),

                cls="grid"
            ),

            # CHARTS

            Div(

                Div(

                    H2("Headlines by category"),

                    Img(
                        src="/static/category_chart.png",
                        cls="chart",
                        alt="Headlines by category chart"
                    ),

                    cls="card"
                ),

                Div(

                    H2("Collection timeline"),

                    Img(
                        src="/static/timeline_chart.png",
                        cls="chart",
                        alt="Headline collection timeline chart"
                    ),

                    cls="card"
                ),

                cls="layout"
            ),

            # CATEGORY BREAKDOWN

            Div(

                H2("Category breakdown"),

                Table(

                    Thead(
                        Tr(
                            Th("Category"),
                            Th("Headlines")
                        )
                    ),

                    Tbody(*category_rows)
                    if category_rows
                    else Tbody(
                        Tr(
                            Td("No data yet.", colspan="2")
                        )
                    )

                ),

                cls="card"
            )

        ),

        "Analytics"
    )


# ==================================================
# IMPORT / EXPORT PAGE
# ==================================================

@rt("/data-tools")
def get():

    return page(

        Div(

            H2("Data management"),

            Div(

                # CSV AND JSON EXPORT

                Div(

                    H2("Export records"),

                    P(
                        "Download your stored dataset for backup, analysis or sharing.",
                        cls="small"
                    ),

                    A(
                        "Download CSV",
                        href="/export/csv",
                        cls="btn"
                    ),

                    A(
                        "Download JSON",
                        href="/export/json",
                        cls="btn secondary"
                    ),

                    cls="card"
                ),

                # CSV IMPORT

                Div(

                    H2("Import CSV"),

                    P(
                        "Expected columns: title, description, url, source, published_at, category.",
                        cls="small"
                    ),

                    Form(

                        Label("CSV file", fr="file"),

                        Input(
                            type="file",
                            name="file",
                            accept=".csv",
                            required=True
                        ),

                        Button("Import CSV"),

                        action="/import",
                        method="post",
                        enctype="multipart/form-data"
                    ),

                    cls="card"
                ),

                # DEMO DATA

                Div(

                    H2("Demo data"),

                    P(
                        "Load sample headlines to explore the application.",
                        cls="small"
                    ),

                    Form(

                        Button(
                            "Load demo headlines",
                            cls="secondary"
                        ),

                        action="/demo",
                        method="post"
                    ),

                    cls="card"
                ),

                cls="layout"
            ),

            Div(

                flash(
                    "Your primary local dataset is stored in data/news_data.json. CSV export is generated on demand."
                ),

                cls="card"
            )

        ),

        "Import / Export"
    )


# ==================================================
# LOAD DEMO DATA
# ==================================================

@rt("/demo", methods=["POST"])
def post():

    items = load_news(DATA_FILE)

    added = seed_demo_data(items)

    save_news(DATA_FILE, items)

    return page(

        Div(

            flash(
                f"Demo dataset ready. Added {added} sample headlines."
            ),

            A(
                "View headlines",
                href="/headlines",
                cls="btn"
            ),

            cls="card"
        )

    )


# ==================================================
# CSV IMPORT
# ==================================================

@rt("/import", methods=["POST"])
async def post(request):

    form = await request.form()

    upload = form.get("file")

    if not upload or not getattr(upload, "filename", ""):

        return page(

            Div(

                flash(
                    "Please choose a CSV file.",
                    True
                ),

                A(
                    "Back",
                    href="/data-tools",
                    cls="btn secondary"
                ),

                cls="card"
            )

        )

    try:

        content = (
            await upload.read()
        ).decode("utf-8-sig")

        current = load_news(DATA_FILE)

        added, errors = import_csv(
            content,
            current
        )

        save_news(
            DATA_FILE,
            current
        )

        message = (
            f"Import complete: {added} rows added, "
            f"{len(errors)} rejected."
        )

        if errors:

            message += (
                " First issues: "
                + "; ".join(errors[:3])
            )

        return page(

            Div(

                flash(
                    message,
                    bool(errors)
                ),

                A(
                    "View headlines",
                    href="/headlines",
                    cls="btn"
                ),

                cls="card"
            )

        )

    except Exception as exc:

        return page(

            Div(

                flash(
                    f"Import failed: {exc}",
                    True
                ),

                A(
                    "Back",
                    href="/data-tools",
                    cls="btn secondary"
                ),

                cls="card"
            )

        )


# ==================================================
# CSV EXPORT
# ==================================================

@rt("/export/csv")
def get():

    items = load_news(DATA_FILE)

    path = export_csv(
        items,
        REPORTS_DIR / "news_export.csv"
    )

    return FileResponse(
        path,
        filename="news_export.csv",
        media_type="text/csv"
    )


# ==================================================
# JSON EXPORT
# ==================================================

@rt("/export/json")
def get():

    items = load_news(DATA_FILE)

    path = export_json(
        items,
        REPORTS_DIR / "news_export.json"
    )

    return FileResponse(
        path,
        filename="news_export.json",
        media_type="application/json"
    )


# ==================================================
# START SERVER
# ==================================================

if __name__ == "__main__":
    serve()
