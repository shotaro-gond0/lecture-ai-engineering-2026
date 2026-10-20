#!/usr/bin/env bash
# 使い方: ./run_matrix.sh
#
# uv run python -m app.ask --list-models の出力から、
# gemini-X.Y-flash-lite 形式のモデル名を抽出し、
# モデル (AIE_MODEL) × temperature (AIE_TEMPERATURE) の全組み合わせで
# uv run python -m app.ask を実行します。

set -uo pipefail

temperatures=("0.0" "1.0" "2.0")

# モデル一覧を配列に読み込む (ループ内の uv run が標準入力を消費しないようにするため)
mapfile -t models < <(uv run python -m app.ask --list-models | ./app/extract_all_flash_lite.sh)

if [ "${#models[@]}" -eq 0 ]; then
  echo "対象のモデルが見つかりませんでした。" >&2
  exit 1
fi

total=$(( ${#models[@]} * ${#temperatures[@]} ))
count=0
failed=0

for model in "${models[@]}"; do
  for temp in "${temperatures[@]}"; do
    count=$(( count + 1 ))
    echo "[${count}/${total}] AIE_MODEL=${model} AIE_TEMPERATURE=${temp}"

    if ! AIE_MODEL="$model" AIE_TEMPERATURE="$temp" \
         uv run python -m app.ask </dev/null; then
      echo "  -> 失敗: AIE_MODEL=${model} AIE_TEMPERATURE=${temp}" >&2
      failed=$(( failed + 1 ))
    fi
    echo
  done
done

echo "完了: 実行 ${total} 回, 失敗 ${failed} 回"