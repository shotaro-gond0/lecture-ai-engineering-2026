"""講座全体で共通の設定。

APIキーやモデル名はコードに書かず、環境変数から読み込む。
"""

import os
import math
from pathlib import Path

# 既定モデル。環境変数 AIE_MODEL を設定すると切り替えられる。
#   例: export AIE_MODEL=gemini-3.5-flash
DEFAULT_MODEL = "gemini-3.5-flash-lite"
MODEL = os.getenv("AIE_MODEL", DEFAULT_MODEL)
LEARNING_LOG_FOLDER = os.getenv("LEARNING_LOG_FOLDER", "/workspaces/lecture-ai-engineering-2026/learning_log/")

def parse_temperature(name: str) -> float | None:
    """環境変数に有効なtemperature値がセットされていればfloatに変換"""
    raw = os.getenv(name)
    if raw is None:
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    # "nan" や "inf" も float() は受け付けるため、有限数かを確認する
    if not math.isfinite(value):
        return None
    if 0.0 <= value <= 2.0:
        return value
    else:
        return None
MODEL_TEMPERATURE = parse_temperature("AIE_TEMPERATURE")
# 第5回: 1ページを1チャンクとして検索する。索引はscripts/build_rag_index.pyで作成する。
ROOT = Path(__file__).resolve().parent.parent
RAG_SOURCE = ROOT / "data/rag_data/lectures.json"
RAG_TREE = ROOT / "data/rag_data/tree.json"
RAG_GRAPH = ROOT / "data/rag_data/graph.json"
RAG_DB = Path(os.getenv("AIE_RAG_DB", str(ROOT / "data/rag_data/index.sqlite3")))
RAG_DOCUMENT_IDS = ("lec01-main", "lec02-main", "lec03-main")
RAG_TOP_K = 5
GRAPH_START_K = 3
GRAPH_HOPS = 2
GRAPH_MAX_RESULTS = 10
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
# 2,048トークンの上限に対し、タスク指定等の分を残す。超過時は切り捨てず停止する。
EMBEDDING_MAX_TOKENS = 2000


def api_error_message(status: int, detail: str = "") -> str:
    """HTTPステータスコードを、受講生向けの日本語の説明にする（ask.py と agent.py で共用）。"""
    if status == 429:
        return "レート制限に達しました。1分ほど待ってから再実行してください。"
    if status == 503:
        message = "モデル API が一時エラー（503）を返しました。少し待ってから再実行してください。"
        return f"{message} 詳細: {detail}" if detail else message
    if status in (400, 401, 403, 404):
        return f"APIキーかモデル名に問題があります（{status}）: {detail}"
    return f"APIエラー（{status}）: {detail}"


def get_api_key() -> str:
    """環境変数 GEMINI_API_KEY を返す。未設定なら手順を表示して終了する。"""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise SystemExit(
            "環境変数 GEMINI_API_KEY が見つかりません。\n"
            "1. GitHub の Settings → Codespaces → Secrets に GEMINI_API_KEY を登録し、\n"
            "   使う repository に自分の fork を選んでください。\n"
            "2. Codespaces を起動したあとに登録した場合は、Codespaces を再起動してください。\n"
            "   （左下の「Codespaces」→「Stop Current Codespace」→ 再度開く）"
        )
    return key
