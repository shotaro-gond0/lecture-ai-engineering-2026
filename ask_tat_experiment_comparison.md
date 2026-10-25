# ask_tat 実験結果の比較

## 実験A: くり返し重複内容を多く含むクエリ

| モデル | クエリ | 入力トークン数 | 出力トークン数 | 合計トークン数 | 実行時間（秒） | 1分/実行時間 | (1分/実行時間)x入力トークン数 (K) |
|---|---|---:|---:|---:|---:|---:|---:|
| gemini-3.1-flash-lite | query_short.txt | 118 | 716 | 834 | 3.17 | 18.95 | 2.24 |
| gemini-3.1-flash-lite | query_medium.txt | 10023 | 797 | 10820 | 3.81 | 15.75 | 157.82 |
| gemini-3.1-flash-lite | query_long.txt | 50029 | 740 | 50769 | 4.69 | 12.80 | 640.54 |
| gemini-3.5-flash-lite | query_short.txt | 118 | 742 | 860 | 3.67 | 16.34 | 1.93 |
| gemini-3.5-flash-lite | query_medium.txt | 10023 | 1059 | 11082 | 4.68 | 12.82 | 128.49 |
| gemini-3.5-flash-lite | query_long.txt | 50029 | 1229 | 51258 | 5.32 | 11.27 | 564.05 |

| モデル | クエリ | 実行時間/入力トークン数(最小値=1で正規化) | 実行時間/出力トークン数(最小値=1で正規化) | 実行時間/合計トークン数(最小値=1で正規化) |
|---|---|---:|---:|---:|
| gemini-3.1-flash-lite | query_short.txt | 286.38 | 1.02 | 41.12 |
| gemini-3.1-flash-lite | query_medium.txt | 4.06 | 1.10 | 3.82 |
| gemini-3.1-flash-lite | query_long.txt | 1 | 1.46 | 1 |
| gemini-3.5-flash-lite | query_short.txt | 332.16 | 1.14 | 46.25 |
| gemini-3.5-flash-lite | query_medium.txt | 4.99 | 1.02 | 4.58 |
| gemini-3.5-flash-lite | query_long.txt | 1.14 | 1 | 1.12 |

<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="exp-a-title" viewBox="0 0 1000 390" style="max-width:100%;height:auto">
  <title id="exp-a-title">実験A：モデル別の合計トークン数と実行時間</title>
  <rect width="1000" height="390" fill="white"/>
  <g font-family="sans-serif" fill="#333">
    <text x="265" y="25" text-anchor="middle" font-size="16">gemini-3.1-flash-lite</text>
    <text x="755" y="25" text-anchor="middle" font-size="16">gemini-3.5-flash-lite</text>
    <g stroke="#ddd" stroke-width="1">
      <path d="M65 300H465 M65 220H465 M65 140H465 M65 60H465"/>
      <path d="M555 300H955 M555 220H955 M555 140H955 M555 60H955"/>
      <path d="M65 60V300 M165 60V300 M265 60V300 M365 60V300 M465 60V300"/>
      <path d="M555 60V300 M655 60V300 M755 60V300 M855 60V300 M955 60V300"/>
    </g>
    <g stroke="#333" stroke-width="1.5">
      <path d="M65 60V300H465 M555 60V300H955" fill="none"/>
    </g>
    <g font-size="11" text-anchor="end">
      <text x="57" y="304">0</text><text x="57" y="224">2</text><text x="57" y="144">4</text><text x="57" y="64">6</text>
      <text x="547" y="304">0</text><text x="547" y="224">2</text><text x="547" y="144">4</text><text x="547" y="64">6</text>
    </g>
    <g font-size="11" text-anchor="middle">
      <text x="65" y="318">0</text><text x="165" y="318">13.75k</text><text x="265" y="318">27.5k</text><text x="365" y="318">41.25k</text><text x="465" y="318">55k</text>
      <text x="555" y="318">0</text><text x="655" y="318">13.75k</text><text x="755" y="318">27.5k</text><text x="855" y="318">41.25k</text><text x="955" y="318">55k</text>
      <text x="265" y="344" font-size="13">合計トークン数</text><text x="755" y="344" font-size="13">合計トークン数</text>
    </g>
    <text transform="translate(18 180) rotate(-90)" text-anchor="middle" font-size="12">実行時間（秒）</text>
    <text transform="translate(508 180) rotate(-90)" text-anchor="middle" font-size="12">実行時間（秒）</text>
    <g font-size="10" fill="#555">
      <text x="73" y="168">short</text><text x="154" y="142">medium</text><text x="423" y="107">long</text>
      <text x="563" y="148">short</text><text x="644" y="108">medium</text><text x="918" y="82">long</text>
    </g>
  </g>
  <polyline points="71.1,173.4 143.7,147.6 434.2,112.6" fill="none" stroke="#2563eb" stroke-width="3"/>
  <g fill="#2563eb"><circle cx="71.1" cy="173.4" r="5"/><circle cx="143.7" cy="147.6" r="5"/><circle cx="434.2" cy="112.6" r="5"/></g>
  <polyline points="561.3,153.1 635.6,112.8 927.4,87.1" fill="none" stroke="#dc2626" stroke-width="3"/>
  <g fill="#dc2626"><circle cx="561.3" cy="153.1" r="5"/><circle cx="635.6" cy="112.8" r="5"/><circle cx="927.4" cy="87.1" r="5"/></g>
  <g font-family="sans-serif" font-size="10" fill="#555"><text x="65" y="375">点のラベルはクエリ種別を示す</text><text x="555" y="375">点のラベルはクエリ種別を示す</text></g>
</svg>

## 実験B: 青空文庫作品抜粋による自然長文のクエリ

| モデル | クエリ | 入力トークン数 | 出力トークン数 | 合計トークン数 | 実行時間（秒） | 1分/実行時間 | (1分/実行時間)x入力トークン数 (K) |
|---|---|---:|---:|---:|---:|---:|---:|
| gemini-3.1-flash-lite | query_short.txt | 183 | 582 | 765 | 61.93 | 0.97 | 0.18 |
| gemini-3.1-flash-lite | query_medium.txt | 10008 | 778 | 10786 | 44.36 | 1.35 | 13.54 |
| gemini-3.1-flash-lite | query_long.txt | 100046 | 986 | 101032 | 60.98 | 0.98 | 98.45 |
| gemini-3.5-flash-lite | query_short.txt | 183 | 401 | 584 | 2.21 | 27.17 | 4.97 |
| gemini-3.5-flash-lite | query_medium.txt | 10008 | 837 | 10845 | 4.35 | 13.79 | 138.04 |
| gemini-3.5-flash-lite | query_long.txt | 100046 | 1285 | 101331 | 7.64 | 7.86 | 785.98 |

| モデル | クエリ | 実行時間/入力トークン数(最小値=1で正規化) | 実行時間/出力トークン数(最小値=1で正規化) | 実行時間/合計トークン数(最小値=1で正規化) |
|---|---|---:|---:|---:|
| gemini-3.1-flash-lite | query_short.txt | 4433.35 | 20.48 | 1074.15 |
| gemini-3.1-flash-lite | query_medium.txt | 58.07 | 10.97 | 54.57 |
| gemini-3.1-flash-lite | query_long.txt | 7.98 | 11.90 | 8.01 |
| gemini-3.5-flash-lite | query_short.txt | 158.09 | 1.06 | 50.17 |
| gemini-3.5-flash-lite | query_medium.txt | 5.69 | 1 | 5.32 |
| gemini-3.5-flash-lite | query_long.txt | 1 | 1.14 | 1 |

<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="exp-b-title" viewBox="0 0 1000 390" style="max-width:100%;height:auto">
  <title id="exp-b-title">実験B：モデル別の合計トークン数と実行時間</title>
  <rect width="1000" height="390" fill="white"/>
  <g font-family="sans-serif" fill="#333">
    <text x="265" y="25" text-anchor="middle" font-size="16">gemini-3.1-flash-lite</text>
    <text x="755" y="25" text-anchor="middle" font-size="16">gemini-3.5-flash-lite</text>
    <g stroke="#ddd" stroke-width="1">
      <path d="M65 300H465 M65 240H465 M65 180H465 M65 120H465 M65 60H465"/>
      <path d="M555 300H955 M555 240H955 M555 180H955 M555 120H955 M555 60H955"/>
      <path d="M65 60V300 M165 60V300 M265 60V300 M365 60V300 M465 60V300"/>
      <path d="M555 60V300 M655 60V300 M755 60V300 M855 60V300 M955 60V300"/>
    </g>
    <g stroke="#333" stroke-width="1.5">
      <path d="M65 60V300H465 M555 60V300H955" fill="none"/>
    </g>
    <g font-size="11" text-anchor="end">
      <text x="57" y="304">0</text><text x="57" y="244">20</text><text x="57" y="184">40</text><text x="57" y="124">60</text><text x="57" y="64">80</text>
      <text x="547" y="304">0</text><text x="547" y="244">2</text><text x="547" y="184">4</text><text x="547" y="124">6</text><text x="547" y="64">8</text>
    </g>
    <g font-size="11" text-anchor="middle">
      <text x="65" y="318">0</text><text x="165" y="318">27.5k</text><text x="265" y="318">55k</text><text x="365" y="318">82.5k</text><text x="465" y="318">110k</text>
      <text x="555" y="318">0</text><text x="655" y="318">27.5k</text><text x="755" y="318">55k</text><text x="855" y="318">82.5k</text><text x="955" y="318">110k</text>
      <text x="265" y="344" font-size="13">合計トークン数</text><text x="755" y="344" font-size="13">合計トークン数</text>
    </g>
    <text transform="translate(18 180) rotate(-90)" text-anchor="middle" font-size="12">実行時間（秒）</text>
    <text transform="translate(508 180) rotate(-90)" text-anchor="middle" font-size="12">実行時間（秒）</text>
    <g font-size="10" fill="#555">
      <text x="68" y="105">short</text><text x="98" y="159">medium</text><text x="424" y="107">long</text>
      <text x="560" y="225">short</text><text x="590" y="165">medium</text><text x="920" y="65">long</text>
    </g>
  </g>
  <polyline points="67.8,114.2 104.2,167.0 432.4,117.1" fill="none" stroke="#2563eb" stroke-width="3"/>
  <g fill="#2563eb"><circle cx="67.8" cy="114.2" r="5"/><circle cx="104.2" cy="167.0" r="5"/><circle cx="432.4" cy="117.1" r="5"/></g>
  <polyline points="557.1,233.7 594.4,169.5 923.5,70.9" fill="none" stroke="#dc2626" stroke-width="3"/>
  <g fill="#dc2626"><circle cx="557.1" cy="233.7" r="5"/><circle cx="594.4" cy="169.5" r="5"/><circle cx="923.5" cy="70.9" r="5"/></g>
  <g font-family="sans-serif" font-size="10" fill="#555"><text x="65" y="375">点のラベルはクエリ種別を示す</text><text x="555" y="375">点のラベルはクエリ種別を示す</text></g>
</svg>
