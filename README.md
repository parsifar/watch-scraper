# Watch Price Scraper

A FastAPI application that lets users search for watches and scrapes multiple retailer sites for pricing information. The frontend is served from the backend’s static folder, so no separate frontend server is required.

---

## Table of Contents

-   [Features](#features)
-   [Project Structure](#project-structure)
-   [Requirements](#requirements)
-   [Environment Variables](#environment-variables)
-   [Running Locally](#running-locally)
-   [Running on Server / Production](#running-on-server--production)
-   [Adding New Scrapers or Apps](#adding-new-scrapers-or-apps)
-   [License](#license)

---

## Features

-   FastAPI backend
-   Scraping multiple retailer sites
-   Filtering and returning the lowest price
-   Rate limiting with `slowapi`
-   Static frontend served directly from FastAPI
-   Environment variables support via `.env`
-   Dockerized for easy deployment

---

## Project Structure

watch-scraper/
├── backend/
│ ├── app.py # Main FastAPI app
│ ├── scrapers/ # Scraper modules
│ │ ├── init.py
│ │ └── site_scrapers.py
│ ├── relevance.py # Filtering logic
│ └── static/ # Frontend HTML/CSS/JS
├── .env # Environment variables
├── Dockerfile # Docker build instructions
├── deploy-watch-scraper.sh # Optional deploy script
└── README.md

---

## Requirements

-   Docker >= 24
-   Python 3.12 (for local development)
-   `.env` file with required environment variables

---

## Environment Variables

Create a `.env` file in the project root with:

ENV=development
RATE_LIMIT_PER_MINUTE=11

## Running Locally

1- Build Docker image

```bash
docker build -t watch-scraper .
```

2- Run Docker container in development mode

```bash
docker run --name watch-scraper \
 -p 8000:8000 \
 --env-file .env \
 -v "$(pwd):/app" \
 watch-scraper \
 uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

The --reload flag ensures changes in backend/ are automatically applied.

3- Access the app
http://localhost:8000

## Running on Server / Production

1- Build Docker image on the server

```bash
docker build -t watch-scraper .
```

2- Run container in detached mode

```bash
docker run -d --name watch-scraper \
  -p 8000:8000 \
  --env-file /home/ubuntu/apps/watch-scraper/.env \
  watch-scraper
```
