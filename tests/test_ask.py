"""CLI tests for the one-shot ask command."""

from app import ask as ask_module


def test_non_interactive_exits_after_answer(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["app.ask", "--non-interactive", "質問"])
    monkeypatch.setattr(ask_module, "compaction", lambda context: context)
    asked = []
    monkeypatch.setattr(ask_module, "ask", lambda context: asked.append(context) or "回答")

    def unexpected_input(prompt):
        raise AssertionError("input should not be called")

    monkeypatch.setattr("builtins.input", unexpected_input)

    ask_module.main()

    assert len(asked) == 1
    assert "質問" in asked[0]
    assert "回答" in capsys.readouterr().out


def test_interactive_mode_continues_until_exit(monkeypatch):
    monkeypatch.setattr("sys.argv", ["app.ask", "最初の質問"])
    monkeypatch.setattr(ask_module, "compaction", lambda context: context)
    asked = []
    monkeypatch.setattr(ask_module, "ask", lambda context: asked.append(context) or "回答")
    inputs = iter(["続ける質問", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

    ask_module.main()

    assert len(asked) == 2


def test_list_models_takes_precedence_over_non_interactive(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["app.ask", "--list-models", "--non-interactive", "質問"],
    )
    listed = []
    monkeypatch.setattr(ask_module, "list_models", lambda: listed.append(True))

    def unexpected_ask(context):
        raise AssertionError("ask should not be called")

    monkeypatch.setattr(ask_module, "ask", unexpected_ask)

    ask_module.main()

    assert listed == [True]
