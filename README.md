# Tech Trends Explorer API

Backend API for a tech-trend dashboard that analyzes GitHub trending repository data by programming language, repository popularity, and keywords extracted from project descriptions.

## Highlights

- Flask REST API with modular blueprints
- PostgreSQL queries for aggregation, ranking, and repository deduplication
- Keyword extraction from repository descriptions using regex tokenization and stop-word filtering
- Unified JSON response format across endpoints
- Environment-based database configuration for local and production deployments
- Basic validation and safe error responses for public API usage

## Tech Stack

- Python
- Flask
- PostgreSQL
- psycopg2
- Supabase PostgreSQL
- Docker
- Cloudflare Tunnel

## API Endpoints

All data endpoints accept `since=daily`, `since=weekly`, or `since=monthly`.

| Method | Endpoint                                  | Description                                                |
| ------ | ----------------------------------------- | ---------------------------------------------------------- |
| `GET`  | `/api`                                    | Service metadata and available routes                      |
| `GET`  | `/api/health`                             | Health check                                               |
| `GET`  | `/api/language-distribution?since=weekly` | Programming language frequency distribution                |
| `GET`  | `/api/keywords?since=daily`               | Top keywords from repository descriptions                  |
| `GET`  | `/api/top-repositories?since=monthly`     | Most-starred repositories, deduplicated by repository name |

Example response:

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "language": "Python",
      "color": "#3572A5",
      "count": 125
    }
  ]
}
```

## Architecture

```text
GitHub trending data
        |
        v
Python ETL pipeline
        |
        v
PostgreSQL / Supabase
        |
        v
Dockerized Flask API
        |
        v
Cloudflare Tunnel
        |
        v
React dashboard
```

The API reads preprocessed trending repository records from PostgreSQL. Each route focuses on one analysis surface:

- `language.py`: groups repositories by programming language
- `keywords.py`: extracts common keywords from repository descriptions
- `popular.py`: ranks repositories by stars and removes duplicate repository records

## Database Schema

```sql
CREATE TABLE trending_repositories (
    id SERIAL PRIMARY KEY,
    repo_name VARCHAR(255) NOT NULL,
    repo_url VARCHAR(500) NOT NULL,
    description TEXT,
    language VARCHAR(50),
    language_color VARCHAR(7),
    stars_total INTEGER,
    time_span VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Technical Notes

Repository deduplication is handled in PostgreSQL with a window function:

```sql
ROW_NUMBER() OVER (
    PARTITION BY repo_name
    ORDER BY stars_total DESC
)
```

This keeps the highest-starred record for each repository and avoids doing duplicate removal in application code.

Keyword extraction is intentionally lightweight:

- Merge repository descriptions for the requested time span
- Extract alphabetic words with at least three characters
- Remove common English stop words
- Return the top 30 words by frequency

## Local Development

Prerequisites:

- Python 3.8+
- PostgreSQL database or Supabase project

Setup:

```bash
git clone https://github.com/klausss30/tech-trends-api.git
cd tech-trends-api

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Update `.env` with your own database connection string:

```env
DATABASE_URL=postgresql://username:password@host:5432/database
```

Run the API:

```bash
flask --app main run --debug
```

Test the API:

```bash
curl "http://localhost:5000/api/health"
curl "http://localhost:5000/api/language-distribution?since=weekly"
curl "http://localhost:5000/api/keywords?since=daily"
curl "http://localhost:5000/api/top-repositories?since=monthly"
```

## Docker

Create your local environment file:

```bash
cp .env.example .env
```

Set `DATABASE_URL` in `.env`, then build and run the API:

```bash
docker compose up --build api
```

The API will be available at:

```text
http://localhost:5000/api/health
```

You can also build and run without Docker Compose:

```bash
docker build -t tech-trends-api .
docker run --rm -p 5000:5000 --env-file .env tech-trends-api
```

## Cloudflare Tunnel

For a stable public URL, create a Cloudflare Tunnel in the Cloudflare Zero Trust dashboard, route it to this internal service:

```text
http://api:5000
```

Then copy the tunnel token into `.env`:

```env
CLOUDFLARE_TUNNEL_TOKEN=your-cloudflare-tunnel-token
```

Run the API and tunnel together:

```bash
docker compose --profile tunnel up --build
```

For local-only development, keep using:

```bash
docker compose up --build api
```

## Tests

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest
```

## Security Notes

- Real database credentials should be stored in `.env` locally and in secure deployment environment variables.
- `.env` files are ignored by Git; `.env.example` is committed as a safe template.
- API errors return a generic message to clients while server-side details are logged.
- Before making the repository public, scan the git history for secrets if real credentials were ever committed.

## Future Improvements

- Add caching for frequently requested trend data
- Add pagination for repository lists
- Add API rate limiting
- Add OpenAPI documentation
- Add CI for automated tests

## License

MIT
