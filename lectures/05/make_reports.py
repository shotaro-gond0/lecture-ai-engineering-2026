#!/usr/bin/env python3
"""benchmark_agent.sh が作った生ログ（q<N>_app_agent___<方式>___trace.log）から、
traces.md / hit_and_left.md / differences.md を同じディレクトリに作る（標準ライブラリのみ）。

使い方: python3 make_reports.py <ログのディレクトリ> "<プロンプト1>" "<プロンプト2>" ...
"""
import ast
import re
import sys
from pathlib import Path

METHODS = [("全文投入", "full_context"), ("ベクトル検索", "trace"), ("Tree", "tree"), ("Graph", "graph")]


def cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def log_path(d: Path, q: int, key: str) -> Path:
    return d / (f"q{q}_app_agent___trace.log" if key == "trace" else f"q{q}_app_agent___{key}___trace.log")


def answer_of(text: str) -> str:
    m = re.search(r"^\[model\][^\n]*\n(.*?)^--- trace ---", text, re.S | re.M)
    body = m.group(1) if m else ""
    body = "\n".join(l for l in body.splitlines() if not l.startswith("[full-context]"))
    return body.strip()


def label(lec: str, kind: str, n: int) -> str:
    return f"lec{lec} p.{n}" if kind == "main" else f"lec{lec}-{kind} p.{n}"


def retrieved_of(text: str, key: str):
    """検索・目次で取得したページ（(講義, 種別, ページ) の集合）と、ツール呼び出しの一覧。"""
    calls = []
    for m in re.finditer(r"^\[tool call\]\s+(\w+)\((.*)\)\s*$", text, re.M):
        try:
            a = ast.literal_eval(m[2]) if m[2] else {}
        except Exception:
            a = {}
        arg = a.get("node_id") or a.get("query") or ""
        calls.append((m[1], arg))
    pages = set()
    if key == "tree":
        for _, arg in calls:
            m = re.fullmatch(r"lec(\d+)-(\w+?)-p0*(\d+)", arg)
            if m:
                pages.add((m[1], m[2], int(m[3])))
    elif key != "full_context":
        for m in re.finditer(r'"page_id": "lec(\d+)-(\w+?)-p0*(\d+)"', text):
            pages.add((m[1], m[2], int(m[3])))
    return pages, calls


def cited_of(answer: str, default_lec: str):
    """回答文中の "p.N" 系の表記から引用ページを取り出す（講義は直前の「第N回」「lecNN-種別」から推定）。"""
    pages = set()
    seg = re.compile(r"p\.\s?\d+(?:\s*[-–]\s*\d+)?(?:\s*[,、]\s*(?:p\.\s?)?\d+(?:\s*[-–]\s*\d+)?)*")
    for m in seg.finditer(answer):
        before = answer[max(0, m.start() - 80):m.start()]
        lec, kind = default_lec, "main"
        marks = list(re.finditer(r"lec0?(\d+)-(main|exercise)|第\s?(\d+)\s?回", before))
        if marks:
            mk = marks[-1]
            lec = mk[1] or mk[3]
            kind = mk[2] or "main"
        for part in re.split(r"[,、]", m.group(0)):
            nums = [int(x) for x in re.findall(r"\d+", part)]
            if len(nums) == 2 and re.search(r"[-–]", part):
                nums = list(range(nums[0], nums[1] + 1))
            for n in nums:
                pages.add((lec.zfill(2), kind, n))
    return pages


def fmt(pages) -> str:
    return ", ".join(label(l, k, n) for l, k, n in sorted(pages)) if pages else "なし"


def main() -> None:
    d = Path(sys.argv[1])
    prompts = sys.argv[2:]
    data = {}
    for q, prompt in enumerate(prompts, 1):
        m = re.search(r"第\s?([0-9０-９])\s?回", prompt)
        default_lec = f"{int(m[1].translate(str.maketrans('０１２３４５６７８９', '0123456789'))):02d}" if m else "02"
        for name, key in METHODS:
            p = log_path(d, q, key)
            if not p.exists():
                continue
            t = p.read_text(encoding="utf-8")
            ans = answer_of(t)
            got, calls = retrieved_of(t, key)
            cited = cited_of(ans, default_lec)
            gloss = "用語集" in ans and any(c[0] == "search_glossary" for c in calls)
            usage = re.search(r"モデル応答 (\d+) 回", t)
            data[(q, key)] = dict(name=name, answer=ans, got=got, calls=calls, cited=cited,
                                  gloss=gloss, resp=usage[1] if usage else "-")
    head = [f"- 元データ: `{d.name}/` の生ログ（`--trace` 出力）。",
            "- 引用ページは回答文中の `p.N` 表記から機械的に抽出したもの（講義は直前の「第N回」「lecNN-…」から推定）。参考として挙げられたページも含む。"]

    # ---- traces.md
    out = ["# --trace のトレース整理（質問 × コマンド）", "", *head,
           "- ツール呼び出しは `[tool call]` 行を実行順に並べたもの。`browse_tree` は node_id、検索系は検索語を括弧内に示す。",
           "- 取得・開いたページ: ベクトル検索・Graph は検索結果の `page_id`、Tree は末端ページとして開いた node のみ。", "",
           "## 質問", "", *[f"- Q{i}: {p}" for i, p in enumerate(prompts, 1)], "",
           "## トレース一覧", "",
           "| 質問 | 方式 | ツール呼び出し順 | 呼び出し回数 | 取得・開いたページ | 回答で引用されたページ | モデル応答回数 |",
           "|---|---|---|---:|---|---|---:|"]
    for q in range(1, len(prompts) + 1):
        for name, key in METHODS:
            r = data.get((q, key))
            if not r:
                continue
            order = " → ".join(f"{i}. {n}({a})" for i, (n, a) in enumerate(r["calls"], 1)) or "なし"
            got = "全資料を一括投入（ツール呼び出しなし）" if key == "full_context" else (fmt(r["got"]) if r["got"] else "なし")
            cited = fmt(r["cited"]) + ("、用語集" if r["gloss"] else "")
            out.append(f"| Q{q} | {name} | {cell(order)} | {len(r['calls'])} | {cell(got)} | {cell(cited)} | {r['resp']} |")
    (d / "traces.md").write_text("\n".join(out) + "\n", encoding="utf-8")

    # ---- hit_and_left.md
    out = ["# 取得したが回答に使われなかったページ", "", *head,
           "- 全文投入は検索・取得をしないため対象外。「使われなかった」は回答文に引用されなかったという意味。", "",
           "| 質問 | 方式 | 取得・開いたページ | 回答で引用されたページ | 取得したが使われなかったページ | 件数（使われなかった／取得） |",
           "|---|---|---|---|---|---|"]
    tot = {}
    for q in range(1, len(prompts) + 1):
        for name, key in METHODS[1:]:
            r = data.get((q, key))
            if not r:
                continue
            left = r["got"] - r["cited"]
            a, b = tot.get(name, (0, 0))
            tot[name] = (a + len(left), b + len(r["got"]))
            cited = fmt(r["cited"]) + ("、用語集" if r["gloss"] else "")
            out.append(f"| Q{q} | {name} | {cell(fmt(r['got']) if r['got'] else 'なし')} | {cell(cited)} | {cell(fmt(left))} | {len(left)} / {len(r['got'])} |")
    out += ["", "## 方式ごとの合計", "", "| 方式 | 使われなかった／取得 | 割合 |", "|---|---|---|"]
    for name, (a, b) in tot.items():
        out.append(f"| {name} | {a} / {b} | {f'{a / b:.0%}' if b else '-'} |")
    (d / "hit_and_left.md").write_text("\n".join(out) + "\n", encoding="utf-8")

    # ---- differences.md
    out = ["# 方式別の比較：利用ページと回答内容", "", *head, ""]
    for q, prompt in enumerate(prompts, 1):
        rs = [data[(q, k)] for _, k in METHODS if (q, k) in data]
        if not rs:
            continue
        sets = [r["cited"] for r in rs]
        common = set.intersection(*sets)
        out += [f"## Q{q}：{prompt}", "", "### 回答で引用されたページ", "",
                "| 方式 | 引用ページ | 他方式にない（その方式だけが引用） |", "|---|---|---|"]
        for r in rs:
            others = set().union(*[o for o in sets if o is not r["cited"]]) if len(sets) > 1 else set()
            out.append(f"| {r['name']} | {cell(fmt(r['cited']))} | {cell(fmt(r['cited'] - others))} |")
        out += ["", f"- 全方式に共通: {fmt(common)}", "",
                "### 回答の冒頭（内容の共通部分・差分は下の抜粋と各ログで確認）", "",
                "| 方式 | 回答の冒頭（先頭 200 文字） |", "|---|---|"]
        for r in rs:
            s = re.sub(r"\s+", " ", r["answer"])
            out.append(f"| {r['name']} | {cell(s[:200] + ('…' if len(s) > 200 else ''))} |")
        out.append("")
    out.append("※ 回答内容の共通部分・差分の言語的な比較は自動化していない。各回答の全文は `q<N>_*.log` を参照。")
    (d / "differences.md").write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
