"""v2 benchmark on HARD synthetic data: paraphrased wording, 35% typos, noisy GPS, and different
problems only 40-120 m apart. Run in Colab to include the embedding backend:  !pip install sentence-transformers
"""
import warnings; warnings.filterwarnings("ignore")
from sklearn.metrics import accuracy_score, f1_score
from civicsense.data import generate
from civicsense.pipeline import CivicSensePipeline

train = generate(1500, seed=1)                  # normal templated training data
test = generate(600, seed=3, hard=True)         # hard test data the model has not seen


def pairs(c):
    return int((c * (c - 1) // 2).sum())


def dup_scores(pipe):
    sc, _ = pipe.run(test)
    m = test.merge(sc, on="complaint_id")
    tp = pairs(m.groupby(["true_issue_id", "issue_id"]).size())
    pp, tt = pairs(m.groupby("issue_id").size()), pairs(m.groupby("true_issue_id").size())
    p, r = tp / pp, tp / tt
    return p, r, 2 * p * r / (p + r), m.issue_id.nunique(), m.true_issue_id.nunique()


print("=== A. CATEGORY on hard data (paraphrases + 35% typos); trained on templated data ===")
for name, ch in [("word TF-IDF", False), ("word + character n-grams", True)]:
    pipe = CivicSensePipeline(char_ngrams=ch).fit(train.text, train.true_category)
    sc, _ = pipe.run(test)
    m = test.merge(sc, on="complaint_id")
    ok = m[~m.needs_review]
    print(f"{name:26s} accuracy {accuracy_score(m.true_category, m.predicted_category):.3f} | macro-F1 {f1_score(m.true_category, m.predicted_category, average='macro'):.3f}"
          f" | flagged for review {m.needs_review.mean():.1%} | accuracy on unflagged {accuracy_score(ok.true_category, ok.predicted_category):.3f}")
    for t in ["pothhole on road", "A tree has fallen on the road"]:
        c, conf, _w = pipe.cat.predict(t); print(f"    {t!r} -> {c} ({conf:.2f}) {'REVIEW' if conf < pipe.review_below else ''}")

print("\n=== B. DUPLICATES on hard data (pairwise precision / recall / F1) ===")
backends = ["tfidf_word", "tfidf_char"]
try:
    import sentence_transformers  # noqa
    backends.append("embedding")
except ImportError:
    print("(embedding backend skipped: sentence-transformers not installed here)")
print(f"{'backend':12s} {'thr':>5s} {'prec':>6s} {'recall':>7s} {'F1':>6s} {'issues':>7s}")
for b in backends:
    for thr in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
        pipe = CivicSensePipeline(dup_threshold=thr, backend=b).fit(train.text, train.true_category)
        p, r, f, n, true_n = dup_scores(pipe)
        print(f"{b:12s} {thr:5.2f} {p:6.3f} {r:7.3f} {f:6.3f} {n:7d}")
print(f"(true issues: {true_n}; thr 0.00 = GPS + time + category only)")

print("\n=== C. GPS radius only (no text check), hard data ===")
for rad in [50, 100, 150, 200]:
    pipe = CivicSensePipeline(radius_m=rad).fit(train.text, train.true_category)
    p, r, f, n, _ = dup_scores(pipe)
    print(f"radius {rad:3d} m  prec {p:.3f}  recall {r:.3f}  F1 {f:.3f}  issues {n}")
