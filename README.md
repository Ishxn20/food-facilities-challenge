# SF Mobile Food Facilities API

## Problem & Solution

The City of San Francisco maintains data on permitted mobile food vendors (like food trucks). This project creates a simple web-based API and UI to search through this data in three ways:

1. **By applicant name** – users can type the full or partial name of a food truck and optionally filter by permit status.
2. **By address substring** – users can enter a partial street name and see food trucks operating there.
3. **By geographic proximity** – users can input a latitude and longitude and get back the 5 closest food trucks (optionally filtering only for active/approved ones).

The application is built with **FastAPI**, uses **pandas** to load and filter data from the CSV file, and calculates distances using the **haversine** package. A **Bootstrap-based UI** is also provided for ease of use.

---

## Technical & Architectural Decisions

- **FastAPI** was chosen for its speed, clean async support, built-in validation, and automatic documentation generation.
- **pandas** is used because the data comes as a CSV, and pandas is the most convenient way to filter and manipulate tabular data in-memory.
- **haversine** is used to compute accurate great-circle distances between two latitude/longitude points for the "nearby" endpoint.
- **Docker** was added to ensure portability and ease of testing without dependency conflicts.
- **Bootstrap** was used for a quick and responsive frontend layout.
- **pytest** is used for testing all three endpoint behaviors including edge cases and parameter validation.

---

## Critique

### 1. What would I have done differently with more time?

- Replaced the CSV-based backend with a real database (e.g. PostgreSQL + PostGIS).
- Implemented more sophisticated search features like fuzzy name matching or typo-tolerance.
- Added pagination to return longer result lists without overloading the UI or API.
- Polished the UI further (add loading indicators, error messages, mobile responsiveness).

---

### 2. What trade-offs did I make?

- **CSV in-memory** approach: Faster to build and sufficient for a prototype, but doesn't scale well.
- **Frontend is static + minimal**: Focused effort on backend logic and correctness, rather than on advanced UI features.
- Used **synchronous pandas operations**: Easier to reason about, but not optimized for concurrency or performance under heavy load.

---

### 3. What was left out?

- Authentication and rate limiting.
- Full RESTful filtering options (e.g., exact vs partial match toggles).
- Geo search optimizations like spatial indexing.
- UI enhancements like map visualizations or advanced styling.
- Tests for frontend behavior (e.g., integration or E2E tests with tools like Playwright or Selenium).

---

### 4. How would I scale this to many users?

- Replace CSV with a database (e.g. PostgreSQL + PostGIS).
- Index geolocation columns for fast spatial queries.
- Cache repeated or expensive queries (e.g. nearest truck lookups) using Redis or similar.
- Add a CDN and deploy behind a load balancer (e.g., with AWS ECS or GKE).
- Add structured monitoring, logging, and error reporting.
- Move from synchronous pandas to async-compatible tools or background workers.

---

### 5. How to run this project and its tests

#### 🐳 Run the app using Docker:

```bash
docker build -t sf-food-backend .
docker run --rm -p 8000:8000 sf-food-backend
```

Then visit: [http://localhost:8000/ui](http://localhost:8000/ui)

Or view the API documentation at: [http://localhost:8000/docs](http://localhost:8000/docs)

#### 🧪 Run tests:

```bash
export PYTHONPATH=$PWD
pytest

docker run --rm sf-food-backend pytest
```

---

## Final Thoughts

This project was designed to be clean, correct, and robust under basic use cases. While some features were left out intentionally due to time constraints, the core functionality is complete and well-tested.
