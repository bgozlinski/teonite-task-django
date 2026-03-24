# Netflix Tech Blog Scraper & Stats API

A Django REST API application that scrapes articles from the [Netflix Tech Blog](https://netflixtechblog.com/), processes word frequencies (with stop words removal), and exposes statistics through a REST API.

## Tech Stack

- **Python 3.13**
- **Django 6.0** + **Django REST Framework**
- **Scrapy** — web scraping
- **PostgreSQL 17** — database
- **NLTK** — stop words removal
- **Docker & Docker Compose** — containerization
- **GitHub Actions** — CI/CD with Docker Hub push

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

### Run

```bash
docker-compose up --build
```

The application will:
1. Run database migrations
2. Scrape articles from Netflix Tech Blog (via RSS feed)
3. Start the API server on **http://localhost:8080**

### Stop & Clean

```bash
# Stop containers
docker-compose down

# Stop and remove database volume (fresh start)
docker-compose down -v
```

## API Endpoints

### `GET /stats/`

Returns the top 10 most frequent words across all articles.

**Response:**
```json
{
    "aurora": 78,
    "postgresql": 76,
    "netflix": 74,
    "data": 65,
    "origin": 61,
    "live": 59,
    "streaming": 53,
    "rds": 50,
    "traffic": 50,
    "new": 45
}
```

### `GET /stats/<author_slug>/`

Returns the top 10 most frequent words for a specific author.

**Example:** `GET /stats/harshadsane/`

**Response:**
```json
{
    "cpu": 16,
    "vector": 15,
    "container": 15,
    "figure": 12,
    "api": 12,
    "cache": 12,
    "containers": 12,
    "lock": 12,
    "architecture": 11,
    "using": 10
}
```

**Error:** Returns `404 Not Found` if the author slug does not exist.

### `GET /authors/`

Returns a mapping of author slugs to full names.

**Response:**
```json
{
    "liweiguo": "Liwei Guo",
    "xiaomeiliu": "Xiaomei Liu",
    "baolinli": "Baolin Li",
    "harshadsane": "Harshad Sane",
    "valentingeffrier": "Valentin Geffrier"
}
```

## Usage Examples

### cURL

```bash
# Get global word stats
curl http://localhost:8080/stats/

# Get stats for a specific author
curl http://localhost:8080/stats/harshadsane/

# List all authors
curl http://localhost:8080/authors/
```

### Python (requests)

```python
import requests

# Global stats
response = requests.get("http://localhost:8080/stats/")
top_words = response.json()
print(top_words)

# Author stats
response = requests.get("http://localhost:8080/stats/harshadsane/")
author_words = response.json()
print(author_words)

# Authors list
response = requests.get("http://localhost:8080/authors/")
authors = response.json()
for slug, name in authors.items():
    print(f"{slug}: {name}")
```

## Running Tests

```bash
docker-compose exec app sh -c "cd src && python manage.py test stats -v 2"
```

## Project Structure

```
Teonite-task-django/
├── .env                          # Environment variables
├── .github/workflows/            # GitHub Actions CI/CD
├── docker-compose.yml            # Django (port 8080) + PostgreSQL 17
├── Dockerfile                    # Python 3.13 based
├── pyproject.toml                # Poetry dependencies
├── poetry.lock
├── README.md
└── src/
    ├── manage.py
    ├── scrapy.cfg                # Scrapy project config
    ├── core/                     # Django project settings
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── stats/                    # Django app (models, views, tests)
    │   ├── models.py             # Author, Article, WordCount
    │   ├── views.py              # API endpoints
    │   ├── urls.py               # URL routing
    │   └── tests.py              # Unit & integration tests
    └── scraper/                  # Scrapy project
        ├── settings.py
        ├── items.py              # ArticleItem
        ├── pipelines.py          # Django ORM pipeline + word counting
        └── spiders/
            └── blog_spider.py    # Netflix Tech Blog spider (RSS)
```

## Environment Variables

| Variable            | Description              | Default   |
|---------------------|--------------------------|-----------|
| `POSTGRES_DB`       | Database name            | `postgres`|
| `POSTGRES_USER`     | Database user            | `postgres`|
| `POSTGRES_PASSWORD` | Database password        | `postgres`|
| `POSTGRES_HOST`     | Database host            | `db`      |
| `POSTGRES_PORT`     | Database port            | `5432`    |
| `SECRET_KEY`        | Django secret key        | —         |
| `DEBUG`             | Django debug mode        | `True`    |

---

## Architecture Decision Records (ADR)

### ADR-001: RSS Feed Instead of HTML Scraping

**Status:** Accepted

**Context:** Netflix Tech Blog is hosted on Medium, which renders article listings via JavaScript. Traditional HTML scraping with Scrapy cannot access dynamically rendered content without a headless browser.

**Decision:** Use the RSS feed (`https://netflixtechblog.com/feed`) as the source for article URLs, then scrape individual article pages for full content.

**Consequences:**
- (+) No need for Selenium/Playwright or headless browser
- (+) Simpler, faster, and more reliable scraping
- (-) RSS feed provides only ~10 most recent articles
- (-) No access to full article archive

---

### ADR-002: Pre-computed Word Counts in Database

**Status:** Accepted

**Context:** The API must respond in < 1 second. Computing word frequencies on-the-fly for every request would be too slow for large article collections.

**Decision:** Pre-compute word counts during the scraping pipeline and store them in a dedicated `WordCount` model. API endpoints use SQL aggregation (`SUM`, `GROUP BY`) on pre-computed data.

**Consequences:**
- (+) API response time < 1s guaranteed (single SQL query with aggregation)
- (+) No runtime text processing overhead
- (-) Additional storage for WordCount table (~6000+ rows)
- (-) Word counts must be recomputed on re-scrape

---

### ADR-003: ManyToMany Author-Article Relationship

**Status:** Accepted

**Context:** Netflix Tech Blog articles frequently have multiple co-authors (e.g., "Valentin Geffrier, Tanguy Cornuau"). A ForeignKey relationship would only capture the first author.

**Decision:** Use `ManyToManyField` between `Article` and `Author` models to support multiple authors per article.

**Consequences:**
- (+) All co-authors are properly attributed
- (+) `/stats/<author>/` includes word counts from all articles the author contributed to
- (-) Slightly more complex pipeline logic (clear + add authors)
- (-) Additional join table in database

---

### ADR-004: Django Management Command for Scraping

**Status:** Accepted

**Context:** Scraping needs to run on container startup before the API server starts. Options considered: Celery task, standalone script, Django management command.

**Decision:** Implement scraping as a Django management command (`python manage.py scrape`) invoked in `docker-compose.yml` command chain: `migrate → scrape → runserver`.

**Consequences:**
- (+) No additional infrastructure (no Celery, no Redis)
- (+) Full access to Django ORM and settings
- (+) Simple sequential startup guaranteed by shell `&&` operator
- (-) Scraping blocks server startup (acceptable for ~10 articles)
- (-) No background/scheduled scraping without additional tooling

---

### ADR-005: NLTK for Stop Words Removal

**Status:** Accepted

**Context:** Word frequency statistics should exclude common English words (the, is, at, etc.) to provide meaningful results.

**Decision:** Use NLTK's English stop words corpus, downloaded at Docker build time. Additional filtering: words shorter than 3 characters and non-alphabetic tokens are excluded.

**Consequences:**
- (+) Industry-standard, comprehensive stop words list (179 words)
- (+) Downloaded once at build time, no runtime download needed
- (-) Only English stop words supported
- (-) Additional ~10MB in Docker image for NLTK data

---

### ADR-006: GitHub Actions CI/CD with Docker Hub

**Status:** Accepted

**Context:** Automated testing and image distribution needed for reliable deployments.

**Decision:** GitHub Actions workflow that builds the Docker image, runs Django tests against a PostgreSQL service, and pushes the image to Docker Hub on successful push to main/feat branches.

**Consequences:**
- (+) Automated quality gate — broken code won't be pushed to Docker Hub
- (+) Versioned images with commit SHA tags
- (+) Pull requests are tested but not pushed (safety)
- (-) Requires Docker Hub account and access token as GitHub secrets
