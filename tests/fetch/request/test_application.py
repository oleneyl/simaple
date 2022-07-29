import json

from simaple.fetch.application.base import KMSFetchApplication


def test_app():
    app = KMSFetchApplication()

    result = app.run("시근해스")

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)