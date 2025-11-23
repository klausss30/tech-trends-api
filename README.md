# Tech Trends Explorer - Backend API

## 📋 Project Overview

**Tech Trends Explorer** is a full-stack web application that analyzes and visualizes trending programming languages, keywords, and popular repositories from GitHub. This repository contains the backend API that powers the data visualization dashboard.

### Business Value

- **For Developers**: Identify emerging technologies and trending tools in the developer community
- **For Companies**: Understand technology trends to make informed tech stack decisions
- **For Learners**: Discover popular projects and learning resources

**Live API**: [https://tech-trends-api-dymi.onrender.com/api](https://tech-trends-api-dymi.onrender.com/api)

---

## 🏗️ System Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   GitHub    │  ────>  │  ETL Script  │  ────>  │ PostgreSQL  │
│  Trending   │         │   (Python)   │         │  (Supabase) │
└─────────────┘         └──────────────┘         └─────────────┘
                                                        │
                                                        │
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │  <────  │  Flask API   │  <────  │             │
│  Frontend   │         │  (Render)    │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
```

### Architecture Layers

1. **Data Layer**: PostgreSQL database storing trending repository data
2. **ETL Layer**: Separate Python script that fetches and processes GitHub trending data
3. **API Layer**: Flask RESTful API serving JSON responses
4. **Client Layer**: React frontend consuming the API

---

## ⚙️ Technology Stack

### Backend Framework: Flask

**Why Flask?**

- **Lightweight**: Minimal overhead, perfect for RESTful APIs
- **Flexible**: Easy to structure with Blueprints for modular code organization
- **Python Ecosystem**: Leverages Python's data processing capabilities
- **Production Ready**: Mature framework with extensive community support

### Database: PostgreSQL

**Why PostgreSQL?**

- **Relational Data**: Repository data has clear relationships (repo → language, time spans)
- **Advanced SQL Features**: Window functions for complex queries (deduplication, ranking)
- **Performance**: Efficient for aggregation and grouping operations
- **Hosting**: Supabase provides managed PostgreSQL with connection pooling

### Deployment & Infrastructure

- **Backend**: Render (Platform-as-a-Service for easy deployment)
- **Database**: Supabase (Managed PostgreSQL with built-in connection pooling)
- **Frontend**: Vercel (Static site hosting with serverless functions)

---

## 🗄️ Database Schema

### Table: `trending_repositories`

```sql
CREATE TABLE trending_repositories (
    id SERIAL PRIMARY KEY,
    repo_name VARCHAR(255) NOT NULL,
    repo_url VARCHAR(500) NOT NULL,
    description TEXT,
    language VARCHAR(50),
    language_color VARCHAR(7),
    stars_total INTEGER,
    time_span VARCHAR(10) NOT NULL,  -- 'daily', 'weekly', 'monthly'
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Key Design Decisions:

1. **Time Span Separation**: Storing data with `time_span` allows efficient querying without date calculations
2. **Denormalized Structure**: Including `language_color` avoids joins, improving query performance
3. **Flexible Schema**: `description` as TEXT allows for varying repository description lengths

---

## 📡 API Design

### 1. Language Distribution Endpoint

**Endpoint**: `GET /api/language-distribution?since={period}`

**Purpose**: Returns the frequency distribution of programming languages in trending repositories.

**Implementation Logic**:

```python
SELECT language, language_color, COUNT(*) as count
FROM trending_repositories
WHERE time_span = %s
GROUP BY language, language_color
ORDER BY count DESC
```

**Key Features**:

- Uses SQL `GROUP BY` for efficient aggregation
- Returns language colors for frontend visualization
- Filters out NULL languages in Python layer

**Response Example**:

```json
{
  "code": 200,
  "message": "success",
  "data": [
    { "language": "Python", "count": 125, "color": "#3572A5" },
    { "language": "JavaScript", "count": 103, "color": "#f1e05a" }
  ]
}
```

### 2. Keywords Extraction Endpoint

**Endpoint**: `GET /api/keywords?since={period}`

**Purpose**: Extracts and analyzes the most common keywords from repository descriptions.

**Implementation Logic**:

1. **Text Extraction**: Concatenate all repository descriptions
2. **Tokenization**: Use regex to extract words (minimum 3 characters, alphabetic only)
3. **Stop Words Filtering**: Remove common English stop words (a, the, is, etc.)
4. **Frequency Analysis**: Use Python's `Counter` to count occurrences
5. **Ranking**: Return top 30 keywords with their weights

**Algorithm Details**:

```python
# Regex pattern for word extraction
r'\b[a-zA-Z]{3,}\b'  # Matches words with 3+ letters

# Stop words filtering
filtered_words = [w for w in words if w not in stop_words]

# Frequency counting and ranking
common = Counter(filtered_words).most_common(30)
```

**Key Features**:

- **Natural Language Processing**: Basic text analysis without heavy ML libraries
- **Custom Stop Words**: Curated list of English stop words
- **Performance**: In-memory processing for fast response times

**Response Example**:

```json
{
  "code": 200,
  "message": "success",
  "data": [
    { "keyword": "agent", "weight": 8 },
    { "keyword": "data", "weight": 6 }
  ]
}
```

### 3. Top Repositories Endpoint

**Endpoint**: `GET /api/top-repositories?since={period}`

**Purpose**: Returns the most starred repositories, deduplicated by repository name.

**Implementation Logic**:

```sql
SELECT repo_name, repo_url, description, language, stars_total
FROM (
    SELECT repo_name, repo_url, description, language, stars_total,
           ROW_NUMBER() OVER (PARTITION BY repo_name ORDER BY stars_total DESC) as rn
    FROM trending_repositories
    WHERE time_span = %s
) t
WHERE rn = 1
ORDER BY stars_total DESC
```

**Key Technical Challenge - Deduplication**:

- **Problem**: Same repository may appear multiple times with different star counts (due to multiple ETL runs or data updates)
- **Solution**: Use PostgreSQL window function `ROW_NUMBER()`
  - `PARTITION BY repo_name`: Groups records by repository
  - `ORDER BY stars_total DESC`: Ranks within each group, keeping highest stars first
  - `WHERE rn = 1`: Selects only the top-ranked record per repository

**Why This Approach?**

- **Database-Level**: More efficient than application-level deduplication
- **Accurate**: Always returns the repository with the highest star count
- **Scalable**: Window functions are optimized in PostgreSQL

**Response Example**:

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "repo_name": "mindsdb/mindsdb",
      "repo_url": "https://github.com/mindsdb/mindsdb",
      "language": "Python",
      "stars": 30776,
      "description": "AI's query engine for federated data"
    }
  ]
}
```

---

## 🎯 Key Technical Highlights

### 1. Modular Architecture with Blueprints

- **Separation of Concerns**: Each route module handles one domain (language, keywords, popular)
- **Maintainability**: Easy to add new endpoints or modify existing ones
- **Testability**: Each blueprint can be tested independently

### 2. Unified API Response Format

- **Consistency**: All endpoints return the same response structure
- **Error Handling**: Standardized error responses with appropriate HTTP codes
- **Developer Experience**: Predictable API responses simplify frontend integration

```python
def api_response(data=None, code=200, message="success"):
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    })
```

### 3. CORS Configuration

- **Cross-Origin Support**: Configured to allow requests from frontend deployed on different domain
- **Security**: Restricted to `/api/*` routes only
- **Production Ready**: Supports frontend-backend separation

### 4. Connection Management

- **Environment Variables**: Database credentials stored securely
- **Connection Pooling**: Handled by Supabase (managed service)
- **Resource Management**: Proper cursor and connection cleanup in try-except blocks

### 5. Error Handling

- **Try-Catch Blocks**: All database operations wrapped in exception handlers
- **Graceful Degradation**: Returns error responses instead of crashing
- **Logging Ready**: Exception messages can be easily logged for debugging

---

## 📂 Project Structure

```
tech-trends-api/
├── main.py                    # Application entry point
├── app/
│   ├── __init__.py           # Flask app factory, CORS configuration
│   ├── db.py                 # Database connection module
│   ├── routes/
│   │   ├── __init__.py       # Blueprint registration
│   │   ├── language.py       # Language distribution endpoint
│   │   ├── keywords.py       # Keywords extraction endpoint
│   │   └── popular.py        # Top repositories endpoint
│   └── utils/
│       ├── api_response.py   # Unified response formatter
│       └── stopwords.py      # Stop words list for NLP
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

**Design Principles**:

- **Separation of Concerns**: Database, routing, and utilities in separate modules
- **DRY (Don't Repeat Yourself)**: Shared utilities like `api_response` prevent code duplication
- **Scalability**: Easy to add new routes or utilities without refactoring

---

## 🚀 Deployment & DevOps

### Environment Configuration

- **Environment Variables**: Database URL stored in `.env` for local development
- **Production Secrets**: Render environment variables for production deployment
- **Security**: Database credentials never committed to version control

### Deployment Process

1. **Code Push**: Git push triggers Render deployment
2. **Automatic Build**: Render installs dependencies from `requirements.txt`
3. **Health Checks**: Render monitors API health automatically
4. **Zero-Downtime**: Blue-green deployment strategy

### Database Management

- **ETL Pipeline**: Separate Python script runs periodically to update data
- **Data Freshness**: Time-based queries allow filtering by time span
- **Compliance**: Fully compliant with GitHub's API usage policies

---

## 🔍 Technical Challenges & Solutions

### Challenge 1: Duplicate Repository Records

**Problem**: Same repository appeared multiple times in results with different star counts.

**Solution**: Implemented PostgreSQL window function for deduplication:

- Used `ROW_NUMBER() OVER (PARTITION BY repo_name ORDER BY stars_total DESC)`
- Ensures only one record per repository (with highest stars)
- More efficient than application-level filtering

### Challenge 2: Keyword Extraction Accuracy

**Problem**: Needed to extract meaningful keywords from repository descriptions.

**Solution**:

- Regex-based tokenization for word extraction
- Custom stop words list to filter noise
- Minimum word length (3 characters) to exclude abbreviations
- Case-insensitive processing for consistency

### Challenge 3: Performance Optimization

**Problem**: Efficient querying of large datasets.

**Solutions**:

- **Indexed Queries**: `time_span` likely indexed for fast filtering
- **Aggregation in Database**: COUNT, GROUP BY performed at database level
- **Minimal Data Transfer**: Select only necessary columns
- **Connection Pooling**: Managed by Supabase for efficient connection reuse

---

## 🎓 Learning Outcomes

This project demonstrates:

- **RESTful API Design**: Clean, predictable endpoint structure
- **Database Optimization**: Using advanced SQL features (window functions, aggregation)
- **Text Processing**: Basic NLP techniques for keyword extraction
- **System Architecture**: Separation of data, API, and client layers
- **Production Deployment**: Cloud-native deployment with managed services
- **Error Handling**: Robust exception handling and user-friendly error responses

---

## 🔮 Future Enhancements

1. **Caching**: Implement Redis caching for frequently accessed data
2. **Rate Limiting**: Add API rate limiting to prevent abuse
3. **Pagination**: Add pagination support for large result sets
4. **Real-time Updates**: WebSocket support for live data updates
5. **Advanced NLP**: Machine learning models for better keyword extraction
6. **Analytics**: Track API usage and performance metrics

---

## 🛠️ Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL database (or Supabase account)
- pip package manager

### Installation

```bash
# Clone repository
git clone https://github.com/kkklausxyz/tech-trends-api.git
cd tech-trends-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
echo "DATABASE_URL=your-postgres-connection-string" > .env

# Run application
flask run
```

### Testing Endpoints

```bash
# Language distribution
curl http://localhost:5000/api/language-distribution?since=weekly

# Keywords
curl http://localhost:5000/api/keywords?since=daily

# Top repositories
curl http://localhost:5000/api/top-repositories?since=monthly
```

---

## 📝 Notes for Interview Presentation

### Key Talking Points:

1. **Architecture Decision**: Why Flask over Django? (Lightweight, flexibility for API-only project)
2. **Database Design**: Window functions for deduplication - shows advanced SQL knowledge
3. **Text Processing**: Custom keyword extraction algorithm - demonstrates problem-solving
4. **Production Ready**: Error handling, CORS, environment configuration
5. **Scalability**: Modular design allows easy feature additions

### Questions to Be Prepared For:

- "Why did you choose PostgreSQL over NoSQL?" → Relational data, advanced SQL features
- "How would you optimize this for 1 million records?" → Indexing, caching, pagination
- "What would you do differently?" → Add caching layer, implement rate limiting
- "How do you handle data consistency?" → ETL script handles data updates, deduplication at query level

---

## 📄 License

This project is part of the Tech Trends Explorer full-stack application.

**Full Stack Components**:

- Frontend: React + Tailwind CSS (Vercel)
- Backend: Flask + PostgreSQL (Render + Supabase)
- Data: GitHub Trending (ETL via Python)

---

_Built with ❤️ using Flask and PostgreSQL_
