# ask_tat 実行結果（合計トークン数・グラフ付き）

| モデル | クエリ | 入力トークン数 | 出力トークン数 | 合計トークン数 | 実行時間（秒） |
|---|---|---:|---:|---:|---:|
| gemini-3.1-flash-lite | query_short.txt | 103 | 818 | 921 | 3.70 |
| gemini-3.1-flash-lite | query_medium.txt | 10008 | 734 | 10742 | 7.48 |
| gemini-3.1-flash-lite | query_long.txt | 50014 | 880 | 50894 | 8.37 |
| gemini-3.5-flash-lite | query_short.txt | 103 | 1073 | 1176 | 4.79 |
| gemini-3.5-flash-lite | query_medium.txt | 10008 | 979 | 10987 | 22.04 |
| gemini-3.5-flash-lite | query_long.txt | 50014 | 828 | 50842 | 222.94 |

## 合計トークン数と実行時間

<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="chart-title chart-desc" viewBox="0 0 760 420" style="max-width: 100%; height: auto;">
  <title id="chart-title">合計トークン数と実行時間</title>
  <desc id="chart-desc">横軸は入力と出力の合計トークン数、縦軸は実行時間（秒）。gemini-3.1-flash-liteを青、gemini-3.5-flash-liteを赤で示す。</desc>
  <rect width="760" height="420" fill="white"/>
  <g font-family="sans-serif" font-size="12" fill="#333">
    <g stroke="#ddd" stroke-width="1">
      <line x1="85" y1="315" x2="685" y2="315"/>
      <line x1="85" y1="261" x2="685" y2="261"/>
      <line x1="85" y1="207" x2="685" y2="207"/>
      <line x1="85" y1="153" x2="685" y2="153"/>
      <line x1="85" y1="99" x2="685" y2="99"/>
      <line x1="85" y1="45" x2="685" y2="45"/>
      <line x1="194.09" y1="45" x2="194.09" y2="315"/>
      <line x1="303.18" y1="45" x2="303.18" y2="315"/>
      <line x1="412.27" y1="45" x2="412.27" y2="315"/>
      <line x1="521.36" y1="45" x2="521.36" y2="315"/>
      <line x1="630.45" y1="45" x2="630.45" y2="315"/>
    </g>
    <g stroke="#333" stroke-width="1.5">
      <line x1="85" y1="45" x2="85" y2="315"/>
      <line x1="85" y1="315" x2="685" y2="315"/>
    </g>
    <g text-anchor="end">
      <text x="76" y="319">0</text>
      <text x="76" y="265">50</text>
      <text x="76" y="211">100</text>
      <text x="76" y="157">150</text>
      <text x="76" y="103">200</text>
      <text x="76" y="49">250</text>
    </g>
    <g text-anchor="middle">
      <text x="85" y="334">0</text>
      <text x="194.09" y="334">10,000</text>
      <text x="303.18" y="334">20,000</text>
      <text x="412.27" y="334">30,000</text>
      <text x="521.36" y="334">40,000</text>
      <text x="630.45" y="334">50,000</text>
      <text x="385" y="366" font-size="14">合計トークン数（入力＋出力）</text>
    </g>
    <text transform="translate(24 180) rotate(-90)" text-anchor="middle" font-size="14">実行時間（秒）</text>
  </g>
  <polyline points="95.06,311.00 202.19,306.92 640.21,305.95" fill="none" stroke="#2563eb" stroke-width="3"/>
  <g fill="#2563eb">
    <circle cx="95.06" cy="311.00" r="5"/>
    <circle cx="202.19" cy="306.92" r="5"/>
    <circle cx="640.21" cy="305.95" r="5"/>
  </g>
  <polyline points="97.83,309.83 204.85,291.20 639.64,74.23" fill="none" stroke="#dc2626" stroke-width="3"/>
  <g fill="#dc2626">
    <circle cx="97.83" cy="309.83" r="5"/>
    <circle cx="204.85" cy="291.20" r="5"/>
    <circle cx="639.64" cy="74.23" r="5"/>
  </g>
  <g font-family="sans-serif" font-size="12">
    <line x1="190" y1="395" x2="218" y2="395" stroke="#2563eb" stroke-width="3"/>
    <circle cx="204" cy="395" r="4" fill="#2563eb"/>
    <text x="224" y="399" fill="#333">gemini-3.1-flash-lite</text>
    <line x1="420" y1="395" x2="448" y2="395" stroke="#dc2626" stroke-width="3"/>
    <circle cx="434" cy="395" r="4" fill="#dc2626"/>
    <text x="454" y="399" fill="#333">gemini-3.5-flash-lite</text>
  </g>
</svg>
