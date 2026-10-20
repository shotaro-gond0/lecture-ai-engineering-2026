#!/usr/bin/env bash
# 使い方: ./extract_flash_lite.sh [入力ファイル]
#         入力ファイルを省略した場合は標準入力から読み込みます。
#
# 各行のモデル名 (models/ プレフィックス付きでも可) から
# gemini-X.Y-flash-lite の形式のものだけを抽出し、
# X ごとに最大の Y を選んで、models/ を除いて列挙します。

set -euo pipefail

input="${1:-/dev/stdin}"

sed -E 's#^models/##' "$input" \
  | grep -E '^gemini-[0-9]+\.[0-9]+-flash-lite$' \
  | sed -E 's/^gemini-([0-9]+)\.([0-9]+)-flash-lite$/\1 \2/' \
  | awk '
      {
        if (!($1 in max) || ($2 + 0) > (max[$1] + 0)) {
          max[$1] = $2
        }
      }
      END {
        for (x in max) {
          print x, max[x]
        }
      }' \
  | sort -n -k1,1 \
  | awk '{ printf "gemini-%s.%s-flash-lite\n", $1, $2 }'