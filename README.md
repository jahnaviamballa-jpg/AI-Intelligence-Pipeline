# AI Intelligence Pipeline

An end-to-end AI-powered research intelligence pipeline for collecting, enriching, analyzing, searching, and recommending research papers.

## 🚀 Overview

The **AI Intelligence Pipeline** transforms raw research-paper data into structured and enriched research intelligence.

The system combines data collection, enrichment, scoring, trend analysis, recommendation, search, similarity analysis, and REST API capabilities into a modular pipeline.

## ✨ Features

* 📚 **arXiv Research Paper Collection**
* 🔍 **Keyword Extraction**
* 🏷️ **Research Topic Classification**
* 🐙 **GitHub Repository Enrichment**
* 📊 **Research Paper Scoring**
* 📈 **Research Trend Analysis**
* 🤖 **Research Recommendations**
* 🔎 **Full-text/Search Indexing**
* 🧠 **Similarity-based Research Search**
* 🌐 **FastAPI REST API**
* ✅ **Dataset and API Validation**
* 🧪 **Automated Pytest Test Suite**

## 🏗️ Pipeline Architecture

```text
Research Sources
      │
      ▼
┌─────────────────┐
│    Crawlers     │
│     arXiv       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Enrichment    │
│ Keywords        │
│ Topics          │
│ GitHub          │
│ Intelligence    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Analysis        │
│ Scoring         │
│ Trends          │
│ Recommendations │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Search &        │
│ Similarity      │
│ Indexing        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    FastAPI      │
│   REST API      │
└─────────────────┘
```

## 🛠️ Technology Stack

| Technology    | Purpose                      |
| ------------- | ---------------------------- |
| Python        | Core development             |
| FastAPI       | REST API                     |
| Pydantic      | Data models and validation   |
| aiohttp       | Asynchronous HTTP requests   |
| feedparser    | arXiv feed processing        |
| NumPy         | Numerical processing         |
| scikit-learn  | Similarity and ML processing |
| pytest        | Automated testing            |
| Uvicorn       | API server                   |
| python-dotenv | Environment configuration    |
| Git & GitHub  | Version control              |

## 📁 Project Structure

```text
AI-Intelligence-Pipeline/
│
├── src/
│   ├── api/
│   ├── crawlers/
│   ├── enrichers/
│   ├── indexers/
│   ├── models/
│   ├── search/
│   ├── storage/
│   └── validators/
│
├── tests/
│   ├── test_api_server.py
│   ├── test_arxiv_crawler.py
│   ├── test_github_api.py
│   ├── test_github_enricher.py
│   └── test_research_paper.py
│
├── data/
│   └── processed/
│
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```
