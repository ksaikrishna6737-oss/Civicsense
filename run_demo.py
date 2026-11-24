"""Run the whole system on fake data and CHECK how well it did (not just print pretty output)."""
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from civicsense.data import generate
from civicsense.pipeline import CivicSensePipeline

train = generate(n=1500, seed=1)
test = generate(n=600, seed=2)

pipe = CivicSensePipeline().fit(train["text"], train["true_category"])
scored, ranked = pipe.run(test)
merged = test.merge(scored, on="complaint_id")

print("=== 1. CATEGORY ACCURACY (held-out synthetic data) ===")
print("accuracy:", round(accuracy_score(merged.true_category, merged.predicted_category), 3))
print(classification_report(merged.true_category, merged.predicted_category, digits=3))


def pairs(series_counts):
    return int((series_counts * (series_counts - 1) // 2).sum())


tp = pairs(merged.groupby(["true_issue_id", "issue_id"]).size())
pred_pairs = pairs(merged.groupby("issue_id").size())
true_pairs = pairs(merged.groupby("true_issue_id").size())
print("=== 2. DUPLICATE DETECTION (pairwise) ===")
print(f"real issues: {merged.true_issue_id.nunique()}  |  issues found: {merged.issue_id.nunique()}")
print(f"precision (flagged pairs that are truly the same issue): {tp / pred_pairs:.3f}")
print(f"recall    (true duplicate pairs we caught):              {tp / true_pairs:.3f}")

print("\n=== 3. TOP 5 ISSUES BY PRIORITY ===")
for r in ranked.head(5).itertuples():
    print(f"#{r.rank} [{r.category} @ {r.location}] {r.why}\n")

cols = ["complaint_id", "text", "location", "lat", "lon", "created_at",
        "predicted_category", "confidence", "needs_review", "severity", "issue_id"]
merged[cols].to_csv("complaints_scored.csv", index=False)   # ground-truth columns left out on purpose
ranked.to_csv("ranked_issues.csv", index=False)
print("Saved complaints_scored.csv and ranked_issues.csv (Power BI input).")
