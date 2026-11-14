from app.config import api_error_message


def test_503_error_includes_provider_detail():
    message = api_error_message(503, "backend is unavailable")

    assert "503" in message
    assert "backend is unavailable" in message


def test_503_error_without_detail_remains_actionable():
    message = api_error_message(503)

    assert "503" in message
    assert "再実行" in message
