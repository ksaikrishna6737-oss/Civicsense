CivicSense
An AI-driven civic complaint management and prioritization system that explains why it ranks each issue the way it does.
> College major project (B.Tech, AI & ML). Team: `<Name 1>`, `<Name 2>`, `<Name 3>` ...
---
The Problem
Civic bodies receive thousands of complaints about roads, water, garbage, streetlights and more. Today:
Complaints are sorted by hand or by arrival order, not by urgency.
The same issue gets reported many times, so authorities can't see its real scale.
Priority decisions are opaque, so citizens don't know why their complaint is waiting.
The Solution
CivicSense lets citizens submit a complaint with text, an image and a location. The system then:
Categorizes the complaint automatically (e.g. water, roads, sanitation).
Scores severity from the description and, optionally, the image.
Detects duplicates of the same issue nearby and in the same time window.
Generates a priority score for authorities.
Explains the score, showing which keywords, how many duplicate reports and how old the complaint is.
What makes it different
Explainable prioritization. Every priority score comes with its reasoning. It is not a black box.
Public duplicate counter. Each issue shows a live count of how many people reported it (e.g. "1,247 people reported this"), which makes the scale visible to citizens and authorities.
Two escalation triggers. Issues escalate automatically when they stay unresolved too long (time-based) or when reports cross a threshold (volume-based).
Analytics layer. Power BI dashboards for department-wise trends, ward-level heatmaps and recurring-issue detection.
---
How It Works
```
Citizen complaint (text + image + location)
        |
        v
  Category classification
        |
        v
  Severity scoring
        |
        v
  Duplicate detection (semantic + geo + time)
        |
        v
  Priority score + explanation
        |
        v
  Authority dashboard / Power BI analytics
```
Stage	Approach
Category classification	TF-IDF + SVM, or a zero-shot transformer
Severity scoring	Rule-based keyword lexicon, optional image hazard flag
Duplicate detection	Sentence-transformer embeddings, cosine similarity, geo and time window
Priority score	Weighted formula over severity, duplicate count and complaint age
Analytics	Power BI
---
Project Status
Update this table honestly before submitting. Reviewers and judges will read it.
Module	Status
Complaint submission (text, image, location)	`<Done / In progress / Planned>`
Category classification	`<Done / In progress / Planned>`
Severity scoring	`<Done / In progress / Planned>`
Duplicate detection (embeddings)	`<Done / In progress / Planned>`
Priority score and explanation	`<Done / In progress / Planned>`
Volume-based auto-escalation	`<Done / In progress / Planned>`
Power BI analytics	`<Done / In progress / Planned>`
---
Hack With Hyderabad 3.0
This repository existed before the event as our college major project. During the 8-hour hackathon on 3 October 2026, we will build only the following, and everything else in the repo predates the event:
`<Module or feature 1, e.g. embedding-based duplicate detection>`
`<Module or feature 2, e.g. public duplicate counter and volume-based escalation>`
New work is committed on the `hackathon` branch, so the event contribution is visible in the commit history.
---
Tech Stack
Language: Python
ML / NLP: `<scikit-learn, sentence-transformers, ...>`
Backend: `<Flask / FastAPI / ...>`
Frontend: `<React / HTML / ...>`
Database: `<SQLite / PostgreSQL / ...>`
Analytics: Power BI
---
Getting Started
```bash
# 1. Clone
git clone https://github.com/<your-username>/civicsense.git
cd civicsense

# 2. Create environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python app.py                   # replace with your actual entry point
```
---
Repository Structure
```
civicsense/
├── data/               # sample complaints and datasets
├── models/             # classification, severity, duplicate detection
├── app/                # backend and frontend
├── dashboards/         # Power BI files and screenshots
├── docs/               # abstract, diagrams, report
├── requirements.txt
└── README.md
```
Adjust this to match your real folders.
---
Screenshots
`<Add screenshots of the complaint form, priority view with explanation, and Power BI dashboard>`
---
Future Work
Multilingual complaint support
Image-based hazard classification
Integration with official municipal grievance portals
Mobile app for citizens
---
Team
Name	Role
`<Name>`	`<e.g. ML / duplicate detection>`
`<Name>`	`<e.g. backend>`
`<Name>`	`<e.g. Power BI analytics>`
License
`<MIT / Apache-2.0 / All rights reserved>`
