# --trace のトレース整理（質問 × コマンド）

- 元データ: `20261122-051250/` の生ログ（`--trace` 出力）。
- 引用ページは回答文中の `p.N` 表記から機械的に抽出したもの（講義は直前の「第N回」「lecNN-…」から推定）。参考として挙げられたページも含む。
- ツール呼び出しは `[tool call]` 行を実行順に並べたもの。`browse_tree` は node_id、検索系は検索語を括弧内に示す。
- 取得・開いたページ: ベクトル検索・Graph は検索結果の `page_id`、Tree は末端ページとして開いた node のみ。

## 質問

- Q1: 第２回の説明では、LoRAは何を固定し何を学ぶか？QLoRA は何を加えるか。
- Q2: 第３回の説明では、コンパクションとセッションをまたぐメモリの違いは？日々のメモは全部長期メモリになる？
- Q3: 今回作ったRAGの実測平均応答時間と正答率は？

## トレース一覧

| 質問 | 方式 | ツール呼び出し順 | 呼び出し回数 | 取得・開いたページ | 回答で引用されたページ | モデル応答回数 |
|---|---|---|---:|---|---|---:|
| Q1 | Graph | 1. search_graph(LoRA 固定 QLoRA 加える) | 1 | lec02 p.47, lec02 p.49, lec02 p.50, lec02 p.51, lec02 p.52, lec02 p.53, lec02 p.59, lec02 p.60, lec02 p.61, lec02 p.62 | lec02 p.51, lec02 p.52 | 2 |
| Q1 | 二段Graph（用語集つき） | 1. search_graph_with_glossary(第2回 LoRA QLoRA 固定 学ぶ 加える) | 1 | lec02 p.47, lec02 p.49, lec02 p.50, lec02 p.51, lec02 p.52, lec02 p.53, lec02 p.59, lec02 p.60, lec02 p.61, lec02 p.62 | lec02 p.51, lec02 p.52、用語集 | 2 |
| Q2 | Graph | 1. search_graph(コンパクション セッション 長期メモリ 第3回) | 1 | lec03 p.37, lec03 p.38, lec03 p.39, lec03 p.40, lec03 p.41, lec03 p.63, lec03 p.64, lec03 p.65, lec03 p.66, lec03 p.67 | lec03 p.38, lec03 p.39, lec03 p.40, lec03 p.65 | 2 |
| Q2 | 二段Graph（用語集つき） | 1. search_graph_with_glossary(コンパクション セッション メモリ 日々のメモ 長期メモリ 第3回) | 1 | lec03 p.37, lec03 p.38, lec03 p.39, lec03 p.40, lec03 p.41, lec03 p.63, lec03 p.64, lec03 p.65, lec03 p.66, lec03 p.67 | lec03 p.39, lec03 p.40, lec03 p.65 | 2 |
| Q3 | Graph | 1. search_graph(RAG 実測平均応答時間 正答率) | 1 | lec02 p.11, lec02 p.12, lec02 p.13, lec02 p.14, lec03 p.18, lec03 p.19, lec03 p.20, lec03 p.63, lec03 p.64, lec03 p.65 | lec02 p.13, lec02 p.14 | 2 |
| Q3 | 二段Graph（用語集つき） | 1. search_graph_with_glossary(RAG 実測 平均応答時間 正答率) → 2. search_graph_with_glossary(RAG 構築 実装 評価 平均応答時間 正答率) | 2 | lec01 p.48, lec01 p.49, lec01 p.50, lec02 p.11, lec02 p.12, lec02 p.13, lec02 p.14, lec02 p.23, lec02 p.24, lec02 p.25, lec03 p.18, lec03 p.19, lec03 p.20, lec03 p.63, lec03 p.64, lec03 p.65 | lec02 p.13、用語集 | 3 |
