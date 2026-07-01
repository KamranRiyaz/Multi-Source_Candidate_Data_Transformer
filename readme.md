# Multi-Source Candidate Data Transformer

This project satisfies the Eightfold AI Engineering Intern (Jul-Dec 2026) Assignment requirements. It processes candidate profiles from multiple disparate sources, normalizes them, resolves conflicts, and projects them into a dynamic runtime configuration.

## Features Built

- **Backend**: Python + FastAPI (Strict validation, high performance, clean architecture)
- **Frontend**: React + Tailwind CSS (Minimal, fast UI for testing the pipeline)
- **CLI**: Included Python script for headless execution
- **Pipeline Stages**: Extract &rarr; Normalize &rarr; Merge &rarr; Project
- **Sources Handled**:
  - **Structured**: Recruiter CSV Export, ATS JSON
  - **Unstructured**: GitHub Profile JSON, Recruiter Notes (.txt)

---

## 🚀 How to Run

### Prerequisites

- Node.js (v18+)
- Python (3.10+)

### 1. Clone the Repository

```bash
git init
git clone https://github.com/KamranRiyaz/Multi-Source_Candidate_Data_Transformer.git
cd Multi-Source_Candidate_Data_Transformer
```

### 2. Run the FastAPI Backend

The backend does the heavy lifting. It must be running for the UI to work.
After cloning the repo go to the project folder in the terminal and run the following

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

_The backend API will be available at `http://localhost:8000`. You can view the auto-generated API docs at `http://localhost:8000/docs`._

### 3. Run the React Frontend (Optional UI)

In a new terminal window, go to the project folder again and run the following to start the react app:

```bash
cd frontend
npm install
npm run dev
```

_The UI will be available at `http://localhost:3000`._

Troubleshooting Note for Reviewers: > The npm run dev script uses npx to ensure the local Vite binary resolves correctly regardless of environment caching. If you happen to encounter any missing dependency errors on a fresh machine, a clean install (rm -rf node_modules package-lock.json && npm install) will resolve them

### 4. Run the CLI

You can run the pipeline purely from the command line without the web server. I have included sample files in the `/sample_data` directory. The CLI groups candidates automatically across multiple files based on email/name matching.

**Process individual files:**
```bash
cd backend
python cli.py --csv ./sample_data/recruiter.csv --ats ./sample_data/ats.json --notes ./sample_data/notes.txt --config ./config.json --out result.json
```

**Process an entire directory of mixed files:**
```bash
cd backend
python cli.py --dir ./sample_data --config ./config.json --out batch_results.json
```

### 5. Run the Tests

```bash
cd backend
pytest tests/
```

---

## 🏗️ Architecture & Decisions

- **Why Python + FastAPI?** Python is the industry standard for data transformation and data engineering tasks. FastAPI brings Pydantic, which provides strict type-checking and schema validation out of the box, ensuring the "trustworthy profile" requirement is met.
- **Why a Pipeline Pattern?** Keeping Extraction, Normalization, Merging, and Projection strictly separated allows us to add new source types without touching the core canonical merging logic.
- **Why Confidence-Based Merging?** Instead of blindly concatenating strings (which creates "Frankenstein" records), the system assigns a confidence weight to each source (ATS > CSV > GitHub > Notes). Single-value fields take the highest confidence value, while arrays (skills, emails) are unioned and deduplicated.

## 📝 Assumptions & Descoped Items

- **Descoped**: Advanced NLP / LLM integration for unstructured text. Given time constraints and the need for determinism, the recruiter notes are extracted using robust RegEx heuristics instead of an LLM call.
- **Descoped**: Advanced fuzzy matching for company names (e.g. treating "Google" and "Google LLC" as the exact same entity).
- **Assumed**: The React frontend runs locally alongside the FastAPI backend on port 8000.
