# 取得したが回答に使われなかったページ

- 元データ: `20261122-051250/` の生ログ（`--trace` 出力）。
- 引用ページは回答文中の `p.N` 表記から機械的に抽出したもの（講義は直前の「第N回」「lecNN-…」から推定）。参考として挙げられたページも含む。
- 全文投入は検索・取得をしないため対象外。「使われなかった」は回答文に引用されなかったという意味。

| 質問 | 方式 | 取得・開いたページ | 回答で引用されたページ | 取得したが使われなかったページ | 件数（使われなかった／取得） |
|---|---|---|---|---|---|
| Q1 | Graph | lec02 p.47, lec02 p.49, lec02 p.50, lec02 p.51, lec02 p.52, lec02 p.53, lec02 p.59, lec02 p.60, lec02 p.61, lec02 p.62 | lec02 p.51, lec02 p.52 | lec02 p.47, lec02 p.49, lec02 p.50, lec02 p.53, lec02 p.59, lec02 p.60, lec02 p.61, lec02 p.62 | 8 / 10 |
| Q1 | 二段Graph（用語集つき） | lec02 p.47, lec02 p.49, lec02 p.50, lec02 p.51, lec02 p.52, lec02 p.53, lec02 p.59, lec02 p.60, lec02 p.61, lec02 p.62 | lec02 p.51, lec02 p.52、用語集 | lec02 p.47, lec02 p.49, lec02 p.50, lec02 p.53, lec02 p.59, lec02 p.60, lec02 p.61, lec02 p.62 | 8 / 10 |
| Q2 | Graph | lec03 p.37, lec03 p.38, lec03 p.39, lec03 p.40, lec03 p.41, lec03 p.63, lec03 p.64, lec03 p.65, lec03 p.66, lec03 p.67 | lec03 p.38, lec03 p.39, lec03 p.40, lec03 p.65 | lec03 p.37, lec03 p.41, lec03 p.63, lec03 p.64, lec03 p.66, lec03 p.67 | 6 / 10 |
| Q2 | 二段Graph（用語集つき） | lec03 p.37, lec03 p.38, lec03 p.39, lec03 p.40, lec03 p.41, lec03 p.63, lec03 p.64, lec03 p.65, lec03 p.66, lec03 p.67 | lec03 p.39, lec03 p.40, lec03 p.65 | lec03 p.37, lec03 p.38, lec03 p.41, lec03 p.63, lec03 p.64, lec03 p.66, lec03 p.67 | 7 / 10 |
| Q3 | Graph | lec02 p.11, lec02 p.12, lec02 p.13, lec02 p.14, lec03 p.18, lec03 p.19, lec03 p.20, lec03 p.63, lec03 p.64, lec03 p.65 | lec02 p.13, lec02 p.14 | lec02 p.11, lec02 p.12, lec03 p.18, lec03 p.19, lec03 p.20, lec03 p.63, lec03 p.64, lec03 p.65 | 8 / 10 |
| Q3 | 二段Graph（用語集つき） | lec01 p.48, lec01 p.49, lec01 p.50, lec02 p.11, lec02 p.12, lec02 p.13, lec02 p.14, lec02 p.23, lec02 p.24, lec02 p.25, lec03 p.18, lec03 p.19, lec03 p.20, lec03 p.63, lec03 p.64, lec03 p.65 | lec02 p.13、用語集 | lec01 p.48, lec01 p.49, lec01 p.50, lec02 p.11, lec02 p.12, lec02 p.14, lec02 p.23, lec02 p.24, lec02 p.25, lec03 p.18, lec03 p.19, lec03 p.20, lec03 p.63, lec03 p.64, lec03 p.65 | 15 / 16 |

## 方式ごとの合計

| 方式 | 使われなかった／取得 | 割合 |
|---|---|---|
| Graph | 22 / 30 | 73% |
| 二段Graph（用語集つき） | 30 / 36 | 83% |
