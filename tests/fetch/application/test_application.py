from simaple.fetch.application.base import KMSFetchApplication


def test_app():
    app = KMSFetchApplication()

    app.run("Backend")
