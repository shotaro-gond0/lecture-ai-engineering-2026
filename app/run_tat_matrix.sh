#!/usr/bin/env bash
# Run ask_tat for both models and all three query sizes, then write a Markdown table.
# Usage: ./app/run_tat_matrix.sh

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
output_file="$repo_root/ask_tat_matrix.md"
temp_output="$(mktemp "$repo_root/.ask_tat_matrix.XXXXXX")"
run_output="$(mktemp)"
response_output="$(mktemp)"
query_input="$(mktemp)"
trap 'rm -f -- "$temp_output" "$run_output" "$response_output" "$query_input"' EXIT

models=("gemini-3.1-flash-lite" "gemini-3.5-flash-lite")
queries=("query_short.txt" "query_medium.txt" "query_long.txt")

{
  printf '# ask_tat 実行結果\n\n'
  printf '| モデル | クエリ | 入力トークン数 | 出力トークン数 | 合計トークン数 | 実行時間（秒） |\n'
  printf '|---|---|---:|---:|---:|---:|\n'
} >"$temp_output"

for model in "${models[@]}"; do
  for query in "${queries[@]}"; do
    query_file="$repo_root/$query"
    if [[ ! -f "$query_file" ]]; then
      echo "クエリファイルが見つかりません: $query_file" >&2
      exit 1
    fi

    {
      printf '以下の文章を要約し、あなたの考えを述べてください。\n\n'
      cat -- "$query_file"
    } >"$query_input"

    echo "実行中: AIE_MODEL=$model, query=$query" >&2
    if ! AIE_MODEL="$model" uv run --project "$repo_root" \
      python -m app.ask_tat --query-file "$query_input" >"$run_output"; then
      echo "ask_tat の実行に失敗しました: AIE_MODEL=$model, query=$query" >&2
      exit 1
    fi

    IFS=';' read -r result_model input_tokens output_tokens elapsed_time <"$run_output"
    if [[ -z "${result_model:-}" || -z "${input_tokens:-}" || -z "${output_tokens:-}" || -z "${elapsed_time:-}" ]]; then
      echo "ask_tat の計測行を解析できませんでした: AIE_MODEL=$model, query=$query" >&2
      exit 1
    fi
    if [[ ! "$input_tokens" =~ ^[0-9]+$ || ! "$output_tokens" =~ ^[0-9]+$ ]]; then
      echo "トークン数が整数ではありません: AIE_MODEL=$model, query=$query" >&2
      exit 1
    fi
    total_tokens=$((input_tokens + output_tokens))

    response_file="$repo_root/${model}_${query%.txt}.txt"
    separator="$(printf '%060d' 0 | tr '0' '#')"
    if ! awk -v separator="$separator" '
      $0 == separator {
        found = 1
        next
      }
      found {
        print
      }
      END {
        if (!found) {
          exit 1
        }
      }
    ' "$run_output" >"$response_output"; then
      echo "LLM応答を抽出できませんでした: AIE_MODEL=$model, query=$query" >&2
      exit 1
    fi
    mv -- "$response_output" "$response_file"

    printf '| %s | %s | %s | %s | %s | %s |\n' \
      "$result_model" "$query" "$input_tokens" "$output_tokens" "$total_tokens" "$elapsed_time" \
      >>"$temp_output"
  done
done

mv -- "$temp_output" "$output_file"
echo "結果を出力しました: $output_file"
