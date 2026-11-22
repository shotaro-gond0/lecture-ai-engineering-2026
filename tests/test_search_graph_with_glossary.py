"""tools.search_graph_with_glossary（2段階のグラフ検索）のテスト。

埋め込みAPI・検索DB・用語集ファイルには依存せず、retrieval.search_graph と用語集を差し替えて検証する。
"""

import json

import pytest
from google.genai.errors import APIError
from pydantic_ai.models.test import TestModel

from app import retrieval, tools
from app.config import api_error_message

GLOSSARY = [
    {"id": "lora", "term": "LoRA", "aliases": ["Low-Rank Adaptation"], "lecture": 2,
     "definition": "重みの更新分を小さな行列の積で表すPEFT手法。"},
    {"id": "rag", "term": "RAG", "aliases": ["検索拡張生成"], "lecture": 3,
     "definition": "外部資料を検索して回答に使う方式。"},
    {"id": "r", "term": "R", "aliases": [], "lecture": 1, "definition": "1文字の用語（除外される）。"},
]


def _result(content, **extra):
    page = {"page_id": "p1", "title": "タイトル", "content": content}
    return {"seeds": [page], "expanded": [], "max_hops": 2, **extra}


@pytest.fixture(autouse=True)
def fake_glossary(monkeypatch):
    monkeypatch.setattr(tools, "load_glossary", lambda: GLOSSARY)


def _patch_search(monkeypatch, results):
    """search_graph を、呼ばれた順に results を返す偽物に差し替え、受け取った query を記録して返す。"""
    queries = []

    def fake(query):
        queries.append(query)
        return dict(results[min(len(queries), len(results)) - 1])

    monkeypatch.setattr(retrieval, "search_graph", fake)
    return queries


def test_searches_twice_when_term_is_in_query_and_pages(monkeypatch):
    queries = _patch_search(monkeypatch, [_result("LoRA は低ランク適応です"),
                                          _result("2回目の本文")])
    data = json.loads(tools.search_graph_with_glossary("LoRAとは何ですか"))

    assert len(queries) == 2
    assert queries[0] == "LoRAとは何ですか"
    assert queries[1].startswith("LoRAとは何ですか\n")
    assert "LoRA: 重みの更新分を小さな行列の積で表すPEFT手法。" in queries[1]
    assert data["search_query"] == queries[1]
    assert data["seeds"][0]["content"] == "2回目の本文"  # 回答には2段目の結果を使う
    assert [g["term"] for g in data["glossary"]] == ["LoRA"]
    assert data["glossary"][0]["lecture"] == 2


def test_term_only_in_query_is_not_searched_again(monkeypatch):
    queries = _patch_search(monkeypatch, [_result("関係のない本文")])
    data = json.loads(tools.search_graph_with_glossary("LoRAとは何ですか"))

    assert len(queries) == 1
    assert data["glossary"] == []
    assert "search_query" not in data


def test_term_only_in_pages_is_not_searched_again(monkeypatch):
    queries = _patch_search(monkeypatch, [_result("LoRA は低ランク適応です")])
    data = json.loads(tools.search_graph_with_glossary("微調整の方法を教えて"))

    assert len(queries) == 1
    assert data["glossary"] == []


def test_matches_alias_and_expanded_pages(monkeypatch):
    first = {"seeds": [], "max_hops": 2,
             "expanded": [{"page_id": "p2", "title": "t", "content": "検索拡張生成の説明"}]}
    queries = _patch_search(monkeypatch, [first, _result("x")])
    data = json.loads(tools.search_graph_with_glossary("検索拡張生成とは"))

    assert len(queries) == 2
    assert [g["term"] for g in data["glossary"]] == ["RAG"]


def test_single_character_terms_are_ignored(monkeypatch):
    queries = _patch_search(monkeypatch, [_result("R の話")])
    data = json.loads(tools.search_graph_with_glossary("R について"))

    assert len(queries) == 1
    assert data["glossary"] == []


def test_definition_in_search_query_is_truncated(monkeypatch):
    long_glossary = [{**GLOSSARY[0], "definition": "あ" * 300}]
    monkeypatch.setattr(tools, "load_glossary", lambda: long_glossary)
    queries = _patch_search(monkeypatch, [_result("LoRA の本文"), _result("x")])
    tools.search_graph_with_glossary("LoRA?")

    assert queries[1].endswith("LoRA: " + "あ" * 100)


def test_glossary_is_limited_to_five(monkeypatch):
    many = [{"id": f"t{i}", "term": f"用語{i}", "aliases": [], "lecture": 1, "definition": "d"}
            for i in range(8)]
    monkeypatch.setattr(tools, "load_glossary", lambda: many)
    text = " ".join(f"用語{i}" for i in range(8))
    _patch_search(monkeypatch, [_result(text), _result("x")])
    data = json.loads(tools.search_graph_with_glossary(text))

    assert len(data["glossary"]) == 5


def test_keeps_japanese_unescaped(monkeypatch):
    _patch_search(monkeypatch, [_result("LoRA の本文"), _result("日本語の本文")])
    raw = tools.search_graph_with_glossary("LoRA?")

    assert "日本語の本文" in raw
    assert "\\u" not in raw


@pytest.mark.parametrize("exc", [ValueError("検索語が空です。"), FileNotFoundError("検索DBがありません。")])
def test_reports_expected_errors(monkeypatch, exc):
    def boom(query):
        raise exc

    monkeypatch.setattr(retrieval, "search_graph", boom)
    assert json.loads(tools.search_graph_with_glossary("Q")) == {"error": str(exc)}


def test_reports_error_from_second_search(monkeypatch):
    calls = []

    def fake(query):
        calls.append(query)
        if len(calls) == 2:
            raise ValueError("2回目で失敗")
        return _result("LoRA の本文")

    monkeypatch.setattr(retrieval, "search_graph", fake)
    assert json.loads(tools.search_graph_with_glossary("LoRA?")) == {"error": "2回目で失敗"}


def test_reports_api_error_in_japanese(monkeypatch):
    def boom(query):
        raise APIError(429, {"error": {"message": "quota"}})

    monkeypatch.setattr(retrieval, "search_graph", boom)
    assert json.loads(tools.search_graph_with_glossary("Q")) == {"error": api_error_message(429)}


def test_search_graph_mode_exposes_only_this_tool(monkeypatch):
    from app import agent as agent_module

    model = TestModel(call_tools=[])
    monkeypatch.setattr("sys.argv", ["app.agent", "--search-graph", "質問"])
    monkeypatch.setattr(agent_module, "build_model", lambda: model)

    agent_module.main()
    params = model.last_model_request_parameters
    assert [t.name for t in params.function_tools] == ["search_graph_with_glossary"]


def test_vector_mode_exposes_only_search_materials(monkeypatch):
    from app import agent as agent_module

    model = TestModel(call_tools=[])
    monkeypatch.setattr("sys.argv", ["app.agent", "--vector", "質問"])
    monkeypatch.setattr(agent_module, "build_model", lambda: model)

    agent_module.main()
    params = model.last_model_request_parameters
    assert [t.name for t in params.function_tools] == ["search_materials"]


def test_vector_mode_uses_vector_instructions(monkeypatch):
    from pydantic_ai.messages import ModelResponse, TextPart
    from pydantic_ai.models.function import FunctionModel
    from app import agent as agent_module

    seen = []

    def fake_model(messages, info):
        seen.append(messages[-1].instructions)
        return ModelResponse(parts=[TextPart("ok")])

    monkeypatch.setattr("sys.argv", ["app.agent", "--vector", "質問"])
    monkeypatch.setattr(agent_module, "build_model", lambda: FunctionModel(fake_model))

    agent_module.main()
    assert [s.strip() for s in seen] == [agent_module.INSTRUCTIONS_VECTOR.strip()]


def test_vector_is_exclusive_with_search_graph(monkeypatch):
    from app import agent as agent_module

    monkeypatch.setattr("sys.argv", ["app.agent", "--vector", "--search-graph", "質問"])
    with pytest.raises(SystemExit):
        agent_module.main()
