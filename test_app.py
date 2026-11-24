"""Headless tests for the app. Run:  python test_app.py"""
import os, tempfile
os.environ["CIVICSENSE_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
os.environ["CIVICSENSE_ADMIN"] = "pw"
from streamlit.testing.v1 import AppTest


def go(at, page):
    at.radio[0].set_value(page).run(timeout=120)
    assert not at.exception, [e.value for e in at.exception]


def submit(at, text):
    go(at, "Report a problem")
    at.text_area[0].input(text)
    [b for b in at.button if b.label == "Submit report"][0].click().run(timeout=120)
    assert not at.exception, [e.value for e in at.exception]


at = AppTest.from_file("app.py", default_timeout=120).run()
assert not at.exception, [e.value for e in at.exception]
print("1 app starts: OK")

submit(at, "Big pothole near the school, bikes are skidding")
assert any("CS-000001" in m.value for m in at.markdown)
print("2 first report gets a ticket card: CS-000001")
import re
def info(label):
    html = [m.value for m in at.markdown if 'class="cs-info"' in m.value and label in m.value][0]
    return re.search(r'class="v">(.*?)</div>', html).group(1)
print("   category shown:", info("Category"))

submit(at, "Deep pothole on the road, very dangerous")
people = info("People who reported this")
assert people == "2", people
print("3 second nearby report is merged: people who reported =", people)

submit(at, "hi")
assert at.error, "short text should be rejected"
print("4 too-short text rejected: OK")

go(at, "Track my report")
at.text_input[0].input("CS-000001")
[b for b in at.button if b.label == "Check status"][0].click().run(timeout=120)
assert not at.exception
print("5 tracking works, progress text:", at.progress[0].text if at.progress else "n/a")

go(at, "Officer dashboard")
at.text_input[0].input("wrong")
[b for b in at.button if b.label == "Log in"][0].click().run(timeout=120)
assert at.error
at.text_input[0].input("pw")
[b for b in at.button if b.label == "Log in"][0].click().run(timeout=120)
assert not at.exception, [e.value for e in at.exception]
print("6 wrong password rejected, right password accepted; open issues =", [m for m in at.metric if m.label == "Open issues"][0].value)

[b for b in at.button if b.label == "Load 150 demo complaints"][0].click().run(timeout=180)
assert not at.exception, [e.value for e in at.exception]
n1 = int([m for m in at.metric if m.label == "Open issues"][0].value)
print("7 demo data loaded; open issues =", n1)

[b for b in at.button if b.label == "Mark as resolved"][0].click().run(timeout=180)
assert not at.exception, [e.value for e in at.exception]
n2 = int([m for m in at.metric if m.label == "Open issues"][0].value)
assert n2 == n1 - 1, (n1, n2)
print("8 resolving an issue removes it from the open list:", n1, "->", n2)

go(at, "Most-reported issues")
print("9 public board renders: OK")
print("ALL TESTS PASSED")
