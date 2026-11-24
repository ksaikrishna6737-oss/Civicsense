"""Glue between the app and the CivicSense engine."""
import pandas as pd
from civicsense.data import generate
from civicsense.pipeline import CivicSensePipeline

PRETTY = {"pothole": "Pothole / road damage", "garbage": "Garbage", "streetlight": "Streetlight",
          "water_leak": "Water leak", "sewage": "Sewage / drainage"}
DEPARTMENT = {"pothole": "Roads", "streetlight": "Electrical", "garbage": "Sanitation",
              "sewage": "Sanitation", "water_leak": "Water Board"}   # our own assumption, change as needed


def build_pipeline():
    train = generate(1500, seed=1)     # synthetic training data until real labelled complaints exist
    return CivicSensePipeline().fit(train.text, train.true_category)


def analyse(pipe, df, now):
    """df = open complaints from the database. Returns (per-complaint table, ranked issues table)."""
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    d = df.rename(columns={"id": "complaint_id"})[["complaint_id", "text", "location", "lat", "lon", "created_at"]]
    scored, ranked = pipe.run(d, now=now)
    scored["status"] = scored.complaint_id.map(df.set_index("id")["status"])
    issue_status = scored.groupby("issue_id").status.apply(lambda s: "Assigned" if (s == "Assigned").any() else "Received")
    ranked["status"] = ranked.issue_id.map(issue_status)
    ranked["department"] = ranked.category.map(DEPARTMENT)
    ranked["category_name"] = ranked.category.map(PRETTY)
    return scored, ranked
