"""前後ページ付き検索（retrieval.expand_with_neighbors / search_with_context と
tools.search_materials_with_context）のテスト。

資料JSONや埋め込みAPIには依存せず、小さな偽の文書構造とモンキーパッチで検証する。
文書構成: lec01(sec A: p1,p2,p3 / sec B: p4,p5) → lec02(sec C: p6,p7)
"""

import json
import sqlite3

import pytest
from google.genai.errors import APIError
from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel

from app import retrieval, tools
from app.agent import agent
from app.config import api_error_message


def _page(n, document_id, section):
    return {"page_id": f"p{n}", "document_id": document_id, "lecture": int(document_id[3:5]),
            "document_title": document_id, "section": section,
            "title": f"t{n}", "page": n, "content": f"body{n}"}


PAGES = [
    _page(1, "lec01", "A"), _page(2, "lec01", "A"), _page(3, "lec01", "A"),
    _page(4, "lec01", "B"), _page(5, "lec01", "B"),
    _page(6, "lec02", "C"), _page(7, "lec02", "C"),
]


def _hit(n, distance=0.1):
    return {**PAGES[n - 1], "distance": distance}


def _ids(results):
    return [r["page_id"] for r in results]


@pytest.fixture(autouse=True)
def fake_pages(monkeypatch):
    """_page_order は @cache されているので、差し替え前後で必ずキャッシュを捨てる。"""
    retrieval._page_order.cache_clear()
    monkeypatch.setattr(retrieval, "load_pages", lambda *args, **kwargs: PAGES)
    yield
    retrieval._page_order.cache_clear()


# --- _page_order ---

def test_page_order_maps_page_id_to_position():
    pages, position = retrieval._page_order()
    assert pages == PAGES
    assert position == {f"p{n}": n - 1 for n in range(1, 8)}


def test_page_order_is_cached():
    assert retrieval._page_order() is retrieval._page_order()


# --- expand_with_neighbors ---

def test_adds_previous_and_next_page_in_document_order():
    results = retrieval.expand_with_neighbors([_hit(2)])
    assert _ids(results) == ["p1", "p2", "p3"]
    roles = {r["page_id"]: r["role"] for r in results}
    assert roles == {"p1": "neighbor", "p2": "hit", "p3": "neighbor"}


def test_neighbor_has_reference_to_hit_and_no_distance():
    results = {r["page_id"]: r for r in retrieval.expand_with_neighbors([_hit(2, 0.3)])}
    assert results["p2"]["distance"] == 0.3
    assert "neighbor_of" not in results["p2"]
    assert results["p1"]["distance"] is None
    assert results["p1"]["neighbor_of"] == "p2"
    assert results["p3"]["neighbor_of"] == "p2"
    assert results["p1"]["content"] == "body1"  # 隣接ページも本文付き


def test_window_zero_returns_only_hits():
    results = retrieval.expand_with_neighbors([_hit(2)], window=0)
    assert _ids(results) == ["p2"]


def test_larger_window():
    results = retrieval.expand_with_neighbors([_hit(3)], window=2)
    assert _ids(results) == ["p1", "p2", "p3", "p4", "p5"]


def test_does_not_go_past_document_start_or_end():
    assert _ids(retrieval.expand_with_neighbors([_hit(1)])) == ["p1", "p2"]
    assert _ids(retrieval.expand_with_neighbors([_hit(7)])) == ["p6", "p7"]


def test_does_not_cross_document_boundary():
    # p5(lec01末尾)の次は p6(lec02先頭)だが、別講義なので含めない
    assert _ids(retrieval.expand_with_neighbors([_hit(5)])) == ["p4", "p5"]
    assert _ids(retrieval.expand_with_neighbors([_hit(6)])) == ["p6", "p7"]


def test_crosses_section_boundary_by_default():
    assert _ids(retrieval.expand_with_neighbors([_hit(3)])) == ["p2", "p3", "p4"]


def test_same_section_stops_at_section_boundary():
    results = retrieval.expand_with_neighbors([_hit(3)], same_section=True)
    assert _ids(results) == ["p2", "p3"]


def test_adjacent_hits_are_not_duplicated_or_demoted():
    results = retrieval.expand_with_neighbors([_hit(2), _hit(3)])
    assert _ids(results) == ["p1", "p2", "p3", "p4"]
    roles = {r["page_id"]: r["role"] for r in results}
    assert roles["p2"] == "hit" and roles["p3"] == "hit"
    assert "neighbor_of" not in next(r for r in results if r["page_id"] == "p2")


def test_overlapping_neighbors_appear_once():
    results = retrieval.expand_with_neighbors([_hit(1), _hit(3)])
    assert _ids(results) == ["p1", "p2", "p3", "p4"]
    assert [r["role"] for r in results if r["page_id"] == "p2"] == ["neighbor"]


def test_result_order_is_document_order_not_hit_rank():
    results = retrieval.expand_with_neighbors([_hit(6, 0.1), _hit(1, 0.2)])
    assert _ids(results) == ["p1", "p2", "p6", "p7"]


def test_empty_hits():
    assert retrieval.expand_with_neighbors([]) == []


def test_unknown_page_id_is_ignored():
    unknown = {"page_id": "zzz", "content": "x", "distance": 0.1}
    assert retrieval.expand_with_neighbors([unknown]) == []
    assert _ids(retrieval.expand_with_neighbors([unknown, _hit(2)])) == ["p1", "p2", "p3"]


def test_does_not_mutate_input_hits():
    hit = _hit(2)
    before = dict(hit)
    retrieval.expand_with_neighbors([hit])
    assert hit == before


def test_max_results_keeps_hits_first():
    results = retrieval.expand_with_neighbors([_hit(2), _hit(6)], max_results=2)
    assert _ids(results) == ["p2", "p6"]
    assert all(r["role"] == "hit" for r in results)


def test_max_results_fills_remaining_with_neighbors_in_document_order():
    results = retrieval.expand_with_neighbors([_hit(2)], max_results=2)
    assert len(results) == 2
    assert "p2" in _ids(results)
    assert _ids(results) == sorted(_ids(results))


def test_max_results_larger_than_results_is_noop():
    assert _ids(retrieval.expand_with_neighbors([_hit(2)], max_results=10)) == ["p1", "p2", "p3"]


# --- search_with_context ---

def test_search_with_context_expands_search_results(monkeypatch):
    monkeypatch.setattr(retrieval, "search", lambda query: [_hit(2)] if query == "Q" else [])
    assert _ids(retrieval.search_with_context("Q")) == ["p1", "p2", "p3"]
    assert retrieval.search_with_context("other") == []


def test_search_with_context_passes_window(monkeypatch):
    monkeypatch.setattr(retrieval, "search", lambda query: [_hit(3)])
    assert _ids(retrieval.search_with_context("Q", window=0)) == ["p3"]
    assert len(retrieval.search_with_context("Q", window=2)) == 5


# --- tools.search_materials_with_context ---

def test_tool_returns_json_with_roles(monkeypatch):
    monkeypatch.setattr(retrieval, "search", lambda query: [_hit(2)])
    data = json.loads(tools.search_materials_with_context("Q"))
    assert [r["page_id"] for r in data["results"]] == ["p1", "p2", "p3"]
    assert [r["role"] for r in data["results"]] == ["neighbor", "hit", "neighbor"]
    assert data["results"][0]["distance"] is None


def test_tool_keeps_japanese_unescaped(monkeypatch):
    hit = {**_hit(2), "content": "日本語の本文"}
    monkeypatch.setattr(retrieval, "search", lambda query: [hit])
    assert "日本語の本文" in tools.search_materials_with_context("Q")


def test_tool_with_no_hits(monkeypatch):
    monkeypatch.setattr(retrieval, "search", lambda query: [])
    assert json.loads(tools.search_materials_with_context("Q")) == {"results": []}


@pytest.mark.parametrize("exc", [ValueError("bad"), FileNotFoundError("no index"), sqlite3.Error("db")])
def test_tool_reports_expected_errors(monkeypatch, exc):
    def boom(query):
        raise exc
    monkeypatch.setattr(retrieval, "search", boom)
    data = json.loads(tools.search_materials_with_context("Q"))
    assert data["results"] == []
    assert data["error"] == str(exc)


def test_tool_reports_api_error_in_japanese(monkeypatch):
    def boom(query):
        raise APIError(429, {"error": {"message": "quota"}})
    monkeypatch.setattr(retrieval, "search", boom)
    data = json.loads(tools.search_materials_with_context("Q"))
    assert data == {"error": api_error_message(429), "results": []}


def test_tool_does_not_swallow_unexpected_errors(monkeypatch):
    def boom(query):
        raise RuntimeError("bug")
    monkeypatch.setattr(retrieval, "search", boom)
    with pytest.raises(RuntimeError):
        tools.search_materials_with_context("Q")


# --- agent wiring ---

def test_agent_registers_context_tool_and_result_reaches_model(monkeypatch):
    monkeypatch.setattr("app.retrieval.search", lambda *a, **k: [_hit(2)])
    model = TestModel(call_tools=["search_materials_with_context"])
    with agent.override(model=model):
        result = agent.run_sync("RAGとは？")

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert {"search_materials", "search_materials_with_context"} <= offered

    calls = [p for m in result.all_messages() for p in m.parts if isinstance(p, ToolCallPart)]
    returns = [p for m in result.all_messages() for p in m.parts if isinstance(p, ToolReturnPart)]
    assert [c.tool_name for c in calls] == ["search_materials_with_context"]
    results = json.loads(returns[0].content)["results"]
    assert [r["page_id"] for r in results] == ["p1", "p2", "p3"]
