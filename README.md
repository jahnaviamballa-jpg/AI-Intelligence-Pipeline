# AI Intelligence Pipeline

An end-to-end AI-powered research intelligence pipeline for collecting, enriching, analyzing, searching, and recommending research papers.

## Overview

The **AI Intelligence Pipeline** transforms raw research-paper data into structured and enriched research intelligence.

The system combines:

* Research paper collection
* Keyword extraction
* Topic classification
* GitHub repository enrichment
* Research intelligence generation
* Paper scoring
* Trend analysis
* Research recommendations
* Search indexing
* Similarity-based search
* REST API access
* Automated testing

## Architecture

```text
Research Sources
       |
       v
+-------------------+
|     Crawlers      |
|      arXiv        |
+---------+---------+
          |
          v
+-------------------+
|    Enrichment     |
|-------------------|
| Keywords          |
| Topics            |
| GitHub            |
| Intelligence      |
+---------+---------+
          |
          v
+-------------------+
|     Analysis      |
|-------------------|
| Scoring           |
| Trends            |
| Recommendations   |
+---------+---------+
          |
          v
+-------------------+
| Search & Indexing |
|-------------------|
| Text Search       |
| Similarity Search |
+---------+---------+
          |
          v
+-------------------+
|     FastAPI       |
|     REST API      |
+-------------------+
```

## Features

### Research Paper Collection

Collects research papers from arXiv and processes the retrieved metadata into structured research-paper objects.

### Keyword Extraction

Extracts important keywords from research-paper titles and abstracts.

### Topic Classification

Classifies research papers into research areas and topics.

### GitHub Enrichment

Enriches research papers with related GitHub repository information when available.

A GitHub Personal Access Token can be configured for GitHub API access.

### Research Intelligence

Combines multiple enrichment signals to generate structured research intelligence for each paper.

### Research Scoring

Calculates research relevance and scoring signals for processed papers.

### Trend Analysis

Analyzes research topics and identifies emerging research trends.

### Research Recommendations

Generates research-paper recommendations based on the processed research intelligence.

### Search

Provides indexed search functionality for finding relevant research papers.

### Similarity Search

Supports similarity-based research-paper discovery using machine-learning techniques.

### REST API

Provides access to the research intelligence pipeline through a FastAPI-based REST API.

## Technology Stack

| Technology     | Purpose                      |
| -------------- | ---------------------------- |
| Python         | Core development             |
| FastAPI        | REST API                     |
| Pydantic       | Data models and validation   |
| aiohttp        | Asynchronous HTTP requests   |
| feedparser     | arXiv feed processing        |
| NumPy          | Numerical processing         |
| scikit-learn   | Similarity and ML processing |
| pytest         | Automated testing            |
| Uvicorn        | API server                   |
| python-dotenv  | Environment configuration    |
| Git and GitHub | Version control              |

## Project Structure

```text
AI-Intelligence-Pipeline/
|
+-- src/
|   +-- api/
|   +-- crawlers/
|   +-- enrichers/
|   +-- indexers/
|   +-- models/
|   +-- search/
|   +-- storage/
|   +-- validators/
|
+-- tests/
|   +-- test_api_server.py
|   +-- test_arxiv_crawler.py
|   +-- test_github_api.py
|   +-- test_github_enricher.py
|   +-- test_research_paper.py
|
+-- data/
|   +-- processed/
|
+-- .env.example
+-- .gitignore
+-- pytest.ini
+-- requirements.txt
+-- README.md
```

## Requirements

* Python 3.10 or newer
* Git
* Internet connection for external API/data sources

## Installation

Clone the repository:

```bash
git clone https://github.com/jahnaviamballa-jpg/AI-Intelligence-Pipeline.git
cd AI-Intelligence-Pipeline
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Environment Configuration

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

The project currently supports the following environment variable:

```text
GITHUB_TOKEN=
```

A GitHub Personal Access Token can be added when GitHub enrichment is required.

Never commit the `.env` file to Git.

The repository already ignores `.env` through `.gitignore`.

## Running the Tests

Run the complete test suite:

```powershell
pytest
```

The project includes tests covering:

* API server
* arXiv crawler
* GitHub API functionality
* GitHub enrichment
* Research paper models

## Running the API

Start the FastAPI server with:

```powershell
uvicorn src.api.api_server:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
```

## Main API Endpoints

| Endpoint               | Purpose                             |
| ---------------------- | ----------------------------------- |
| `GET /health`          | Check API health                    |
| `GET /papers`          | Retrieve research papers            |
| `GET /search`          | Search research papers              |
| `GET /areas`           | List research areas                 |
| `GET /area/{area}`     | Retrieve papers for a research area |
| `GET /emerging`        | Retrieve emerging research trends   |
| `GET /recommendations` | Retrieve research recommendations   |

Example:

```text
GET /health
```

Example search:

```text
GET /search?q=LLM%20reasoning&limit=5
```

## Data Pipeline

The project processes research papers through multiple stages:

```text
arXiv Collection
       |
       v
Paper Storage
       |
       v
Keyword Extraction
       |
       v
Topic Classification
       |
       v
GitHub Enrichment
       |
       v
Research Intelligence
       |
       v
Research Scoring
       |
       v
Trend Analysis
       |
       v
Recommendations
       |
       v
Search Index
       |
       v
REST API
```

Generated and processed datasets are intentionally excluded from Git tracking through `.gitignore`.

## Security

Sensitive configuration is stored locally in `.env`.

The repository does not track:

* `.env`
* Virtual environments
* Python cache files
* Generated processed datasets
* Log files

Only `.env.example` is included in the repository as a configuration template.

## Current Status

The project currently includes:

* Modular research intelligence pipeline
* arXiv data collection
* Multiple enrichment stages
* Research scoring
* Trend analysis
* Recommendation engine
* Search and similarity functionality
* FastAPI REST API
* Automated test suite
* Environment configuration
* GitHub-ready project structure

## Future Improvements

Potential future improvements include:

* Web-based research intelligence dashboard
* Scheduled pipeline execution
* Additional research-paper sources
* More advanced semantic search
* Vector database integration
* Improved recommendation models
* Research trend visualization
* Authentication and API authorization
* Containerized deployment
* Cloud deployment
* CI/CD automation

## License

This project is currently provided for educational and research purposes.
