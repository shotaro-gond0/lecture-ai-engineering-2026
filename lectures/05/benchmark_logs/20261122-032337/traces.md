# --trace のトレース整理（質問 × コマンド）

- 元データ: `20261122-032337/` の生ログ（`--trace` 出力）。
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
| Q1 | 全文投入 | なし | 0 | 全資料を一括投入（ツール呼び出しなし） | lec02 p.51, lec02 p.52 | 1 |
| Q1 | ベクトル検索 | 1. search_glossary(LoRA) → 2. search_materials_with_context(LoRA QLoRA 固定) | 2 | lec02 p.46, lec02 p.47, lec02 p.48, lec02 p.50, lec02 p.51, lec02 p.52, lec02 p.53, lec02 p.54, lec02 p.55, lec02 p.59, lec02 p.60, lec02 p.61 | lec02 p.51, lec02 p.52、用語集 | 2 |
| Q1 | Tree | 1. browse_tree() → 2. browse_tree(lec02-main) → 3. browse_tree(lec02-main-s045) → 4. browse_tree(lec02-main-p052) | 4 | lec02 p.52 | lec02 p.52 | 5 |
| Q1 | Graph | 1. search_graph(LoRA 固定 QLoRA) | 1 | lec02 p.47, lec02 p.49, lec02 p.50, lec02 p.51, lec02 p.52, lec02 p.53, lec02 p.59, lec02 p.60, lec02 p.61, lec02 p.62 | lec02 p.51, lec02 p.52 | 2 |
| Q2 | 全文投入 | なし | 0 | 全資料を一括投入（ツール呼び出しなし） | lec03 p.39, lec03 p.40, lec03 p.65 | 1 |
| Q2 | ベクトル検索 | 1. search_materials_with_context(コンパクション セッションをまたぐメモリ 日々のメモ 長期メモリ) | 1 | lec03 p.12, lec03 p.13, lec03 p.14, lec03 p.37, lec03 p.38, lec03 p.39, lec03 p.40, lec03 p.41, lec03 p.64, lec03 p.65, lec03 p.66 | lec03 p.13, lec03 p.39, lec03 p.40 | 2 |
| Q2 | Tree | 1. browse_tree() → 2. browse_tree(lec03-main) → 3. browse_tree(lec03-main-s037) → 4. browse_tree(lec03-main-p037) → 5. browse_tree(lec03-main-p038) → 6. browse_tree(lec03-main-p039) → 7. browse_tree(lec03-main-p040) | 7 | lec03 p.37, lec03 p.38, lec03 p.39, lec03 p.40 | lec03 p.38, lec03 p.39, lec03 p.40 | 8 |
| Q2 | Graph | 1. search_graph(コンパクション セッション 長期メモリ) | 1 | lec03 p.37, lec03 p.38, lec03 p.39, lec03 p.40, lec03 p.41, lec03 p.63, lec03 p.64, lec03 p.65, lec03 p.66, lec03 p.67 | lec03 p.39, lec03 p.40 | 2 |
| Q3 | 全文投入 | なし | 0 | 全資料を一括投入（ツール呼び出しなし） | lec01 p.35, lec02 p.13 | 1 |
| Q3 | ベクトル検索 | 1. search_materials_with_context(RAG 実測 平均応答時間 正答率) | 1 | lec01 p.18, lec01 p.19, lec01 p.20, lec02 p.12, lec02 p.13, lec02 p.14, lec02 p.23, lec02 p.24, lec02 p.25, lec03 p.18, lec03 p.19, lec03 p.20, lec03 p.63, lec03 p.64, lec03 p.65 | lec01 p.19, lec02 p.13 | 2 |
| Q3 | Tree | 1. browse_tree() → 2. browse_tree(lec01-main) → 3. browse_tree(lec02-main) → 4. browse_tree(lec03-main) | 4 | なし | なし | 5 |
| Q3 | Graph | 1. search_graph(RAG 実測平均応答時間 正答率) | 1 | lec02 p.11, lec02 p.12, lec02 p.13, lec02 p.14, lec03 p.18, lec03 p.19, lec03 p.20, lec03 p.63, lec03 p.64, lec03 p.65 | lec02 p.13 | 2 |
