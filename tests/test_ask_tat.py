"""CLI tests for the ask_tat timing command."""

from app import ask_tat as ask_tat_module


def test_query_file_is_used_for_request(monkeypatch, capsys, tmp_path):
    query_file = tmp_path / "query.txt"
    query_file.write_text("ファイルからの長い質問", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        ["app.ask_tat", "--query-file", str(query_file)],
    )
    asked = []
    monkeypatch.setattr(
        ask_tat_module,
        "ask",
        lambda query: asked.append(query) or ("回答", 123, 45, 0.67),
    )

    ask_tat_module.main()

    assert asked == ["ファイルからの長い質問"]
    assert capsys.readouterr().out.splitlines() == [
        "gemini-3.5-flash-lite;123;45;0.67",
        "#" * 60,
        "回答",
    ]


def test_api_error_details_are_logged(monkeypatch, capsys, caplog):
    class TestAPIError(Exception):
        code = 429
        message = "rate limit detail"

    monkeypatch.setattr("sys.argv", ["app.ask_tat", "質問"])
    monkeypatch.setattr(ask_tat_module.errors, "APIError", TestAPIError)

    def fail_request(query):
        raise TestAPIError("rate limit detail")

    monkeypatch.setattr(ask_tat_module, "ask", fail_request)

    try:
        ask_tat_module.main()
    except SystemExit as error:
        assert error.code == 1
    else:
        raise AssertionError("API errors should exit with status 1")

    captured = capsys.readouterr()
    assert "Gemini API request failed" in caplog.text
    assert "status=429" in caplog.text
    assert "rate limit detail" in caplog.text
    assert "レート制限" in captured.out
