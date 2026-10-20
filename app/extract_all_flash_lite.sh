#!/usr/bin/env bash
# 使い方: ./extract_all_flash_lite.sh [入力ファイル]
#         入力ファイルを省略した場合は標準入力から読み込みます。
#
# 各行のモデル名 (models/ プレフィックス付きでも可) から
# gemini-X.Y-flash-lite の形式のものをすべて抽出し、
# models/ を除いて重複なしで、バージョン順に列挙します。

set -euo pipefail

input="${1:-/dev/stdin}"

sed -E 's#^models/##' "$input" \
  | grep -E '^gemini-[0-9]+\.[0-9]+-flash-lite$' \
  | sed -E 's/^gemini-([0-9]+)\.([0-9]+)-flash-lite$/\1 \2/' \
  | sort -u -n -k1,1 -k2,2 \
  | awk '{ printf "gemini-%s.%s-flash-lite\n", $1, $2 }'