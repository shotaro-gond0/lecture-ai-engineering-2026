from types import SimpleNamespace

from app import model_list


def test_main_prints_only_generate_content_model_ids(monkeypatch, capsys):
    models = [
        SimpleNamespace(name="models/gemini-flash", supported_actions=["generateContent"]),
        SimpleNamespace(name="models/embedding", supported_actions=["embedContent"]),
    ]

    class FakeClient:
        def __init__(self, *, api_key):
            assert api_key == "test-key"
            self.models = SimpleNamespace(list=lambda: models)

    monkeypatch.setattr(model_list, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(model_list.genai, "Client", FakeClient)

    model_list.main()

    assert capsys.readouterr().out.splitlines() == ["gemini-flash"]
