#!/usr/bin/env bash
# app.agent を「コマンド × プロンプト」の条件マトリクスで実行し、
# --trace の [time] / [usage] / [cost] 行を抜き出して Markdown の表にまとめる。
#
# 使い方（リポジトリ内のどこからでも可）:
#   bash lectures/05/benchmark_agent.sh                 # カレントディレクトリに出力
#   bash lectures/05/benchmark_agent.sh -d out/         # out/ に出力（なければ作成）
#
# 出力（-d で指定したディレクトリ。未指定ならカレントディレクトリ）:
#   benchmark_agent.md : 全コマンド × 全プロンプトの結果表（標準出力にも表示）
#   q1.md              : 1 つめの質問の方式別比較表（方式／回答の要点／引用ページ／時間／トークン／応答回数／費用）
#
# 実行するコマンドは COMMAND_LIST（uv run python -m の後ろ）、プロンプトは PROMPTS で編集する。
#
# 各実行の生ログは LOG_DIR（既定: lectures/05/benchmark_logs/<日時>/）に保存する。

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

OUT_DIR="."
while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--dir) OUT_DIR="$2"; shift 2 ;;
    -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$OUT_DIR" || exit 1
OUT_DIR="$(cd "$OUT_DIR" && pwd)"   # cd "$REPO_ROOT" の前に絶対パス化しておく

# ---- 条件マトリクス ---------------------------------------------------------
# コマンド（uv run python -m の後ろ、プロンプトの前の部分）
COMMAND_LIST=(
  "app.agent --full-context --trace"
  "app.agent --trace"
  "app.agent --tree --trace"
  "app.agent --graph --trace"
)

# q1.md の「方式」列の名前（COMMAND_LIST と同じ順）
METHOD_NAMES=("全文投入" "ベクトル検索" "Tree" "Graph")

# プロンプト（一行一件）
PROMPTS=(
  "第２回の説明では、LoRAは何を固定し何を学ぶか？QLoRA は何を加えるか。"
  "第３回の説明では、コンパクションとセッションをまたぐメモリの違いは？日々のメモは全部長期メモリになる？"
  "今回作ったRAGの実測平均応答時間と正答率は？"
)
# -----------------------------------------------------------------------------

LOG_DIR="${LOG_DIR:-$SCRIPT_DIR/benchmark_logs/$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$LOG_DIR"

# [tool return] の表示を何文字まで残すか（app/agent.py の既定は 120）。ログでツール結果全体を確認できるようにする。
export AIE_TRACE_LIMIT="${AIE_TRACE_LIMIT:-100000}"

# Markdown の表セル用にエスケープ（| と改行）
md_cell() { printf '%s' "$1" | tr '\n' ' ' | sed 's/|/\\|/g'; }

# ログから回答本文（[model] 行〜"--- trace ---" の間）を 1 行にして取り出す
answer_of() {
  sed -n '/^\[model\]/,/^--- trace ---/p' "$1" | grep -v '^\[model\]\|^\[full-context\]\|^--- trace ---' \
    | tr '\n' ' ' | sed 's/  */ /g; s/^ //; s/ $//'
}
# 引用ページ: 回答中の "PDF p.N" と、検索ツールが返した page_id（重複除去）
citations_of() {
  local log="$1" in_answer from_tools
  in_answer=$(answer_of "$log" | grep -oE 'PDF p\.[0-9]+([,、] ?(p\.)?[0-9]+)*' | sort -u | paste -sd ';' - | sed 's/;/; /g')
  from_tools=$(grep -oP '"page_id": "\K[^"]+' "$log" | sort -u | paste -sd ',' - | sed 's/,/, /g')
  printf '%s' "回答中の引用: ${in_answer:--}<br>検索で取得: ${from_tools:--}"
}

Q1_TABLE="| 方式 | 回答の要点・正しさ | 引用ページと根拠 | 時間（秒） | 入力／出力トークン数 | モデル応答回数 | 生成API推定費用（USD） |
|---|---|---|---|---|---|---|"

TABLE="| # | コマンド | プロンプト | time (秒) | 入力tokens | 出力tokens | モデル応答回数 | 推定コスト (USD) | 状態 |
|---|---|---|---:|---:|---:|---:|---:|---|"

cd "$REPO_ROOT" || exit 1
n=0
for p_idx in "${!PROMPTS[@]}"; do
  prompt="${PROMPTS[$p_idx]}"
  for c_idx in "${!COMMAND_LIST[@]}"; do
    cmd="${COMMAND_LIST[$c_idx]}"
    n=$((n + 1))
    read -r -a cmd_args <<< "$cmd"
    log="$LOG_DIR/q$((p_idx + 1))_$(tr -c 'a-zA-Z0-9\n' '_' <<< "$cmd").log"

    echo ">> [$n] uv run python -m $cmd \"$prompt\"" >&2
    uv run python -m "${cmd_args[@]}" "$prompt" > "$log" 2>&1 < /dev/null
    status=$?

    time_s=$(grep -oP '\[time\] 回答完了まで \K[0-9.]+' "$log" | tail -1)
    usage_line=$(grep '\[usage\]' "$log" | tail -1)
    in_tok=$(grep -oP '入力 \K[0-9,]+(?= tokens)' <<< "$usage_line")
    out_tok=$(grep -oP '出力 \K[0-9,]+(?= tokens)' <<< "$usage_line")
    reqs=$(grep -oP 'モデル応答 \K[0-9]+(?= 回)' <<< "$usage_line")
    cost=$(grep -oP '\[cost\] 生成APIの推定コスト: \$?\K[0-9.]+|算定不可' "$log" | tail -1)

    if [[ $status -ne 0 ]]; then
      state="エラー(exit $status): $(grep -E 'Error|Exception' "$log" | tail -1 | cut -c1-80)"
    elif [[ -z "$usage_line" ]]; then
      state="usage 行なし"
    else
      state="OK"
    fi

    TABLE+="
| $n | \`$(md_cell "$cmd")\` | $(md_cell "$prompt") | ${time_s:--} | ${in_tok:--} | ${out_tok:--} | ${reqs:--} | ${cost:--} | $(md_cell "$state") |"

    # 1 つめの質問だけ、方式別の比較表（q1.md）用の行を作る
    if [[ $p_idx -eq 0 ]]; then
      ans=$(answer_of "$log"); ans="${ans:0:300}"; [[ ${#ans} -ge 300 ]] && ans+="…"
      Q1_TABLE+="
| ${METHOD_NAMES[$c_idx]:-$(md_cell "$cmd")} | (正誤は要確認) $(md_cell "$ans") | $(md_cell "$(citations_of "$log")") | ${time_s:--} | ${in_tok:--} / ${out_tok:--} | ${reqs:--} | ${cost:--} |"
    fi
  done
done

OUTPUT="## app.agent 条件マトリクス実行結果（$(date '+%Y-%m-%d %H:%M:%S')）

$TABLE

生ログ: \`${LOG_DIR#$REPO_ROOT/}\`
"

echo "$OUTPUT"
printf '%s' "$OUTPUT" > "$OUT_DIR/benchmark_agent.md"
printf '## Q1: %s\n\n%s\n' "${PROMPTS[0]}" "$Q1_TABLE" > "$OUT_DIR/q1.md"
echo "saved: $OUT_DIR/benchmark_agent.md, $OUT_DIR/q1.md" >&2
