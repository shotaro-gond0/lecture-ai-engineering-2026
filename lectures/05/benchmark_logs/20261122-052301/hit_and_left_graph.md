# 取得したが回答に使われなかったページ

- 元データ: `20261122-052301/` の生ログ（`--trace` 出力）。
- 引用ページは回答文中の `p.N` 表記から機械的に抽出したもの（講義は直前の「第N回」「lecNN-…」から推定）。参考として挙げられたページも含む。
- 全文投入は検索・取得をしないため対象外。「使われなかった」は回答文に引用されなかったという意味。

| 質問 | 方式 | 取得・開いたページ | 回答で引用されたページ | 取得したが使われなかったページ | 件数（使われなかった／取得） |
|---|---|---|---|---|---|
| Q1 | Graph | lec02 p.49, lec02 p.50, lec02 p.51, lec02 p.52, lec02 p.53, lec03 p.7, lec03 p.8, lec03 p.9, lec03 p.10, lec03 p.11 | lec02 p.49, lec02 p.50, lec02 p.53, lec03 p.10 | lec02 p.51, lec02 p.52, lec03 p.7, lec03 p.8, lec03 p.9, lec03 p.11 | 6 / 10 |
| Q1 | 二段Graph（用語集つき） | lec02 p.49, lec02 p.50, lec02 p.51, lec02 p.52, lec02 p.53, lec03 p.7, lec03 p.8, lec03 p.9, lec03 p.10, lec03 p.11 | lec02 p.49, lec02 p.53, lec03 p.10 | lec02 p.50, lec02 p.51, lec02 p.52, lec03 p.7, lec03 p.8, lec03 p.9, lec03 p.11 | 7 / 10 |
| Q2 | Graph | lec03 p.12, lec03 p.13, lec03 p.14, lec03 p.15, lec03 p.16, lec03 p.66, lec03 p.67, lec03 p.68, lec03 p.69, lec03 p.70 | lec03 p.12, lec03 p.14, lec03 p.68 | lec03 p.13, lec03 p.15, lec03 p.16, lec03 p.66, lec03 p.67, lec03 p.69, lec03 p.70 | 7 / 10 |
| Q2 | 二段Graph（用語集つき） | lec01 p.10, lec03 p.8, lec03 p.9, lec03 p.10, lec03 p.11, lec03 p.12, lec03 p.13, lec03 p.14, lec03 p.15, lec03 p.16, lec03 p.17 | lec03 p.9, lec03 p.10, lec03 p.11, lec03 p.12, lec03 p.13, lec03 p.14、用語集 | lec01 p.10, lec03 p.8, lec03 p.15, lec03 p.16, lec03 p.17 | 5 / 11 |

## 方式ごとの合計

| 方式 | 使われなかった／取得 | 割合 |
|---|---|---|
| Graph | 13 / 20 | 65% |
| 二段Graph（用語集つき） | 12 / 21 | 57% |
