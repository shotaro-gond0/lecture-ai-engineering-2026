#!/usr/bin/env bash
# Claude Code のスキルとメモリを、専用 private リポジトリと同期する。
#
#   claude-data.sh setup  : clone/pull して ~/.claude/skills と memory をリンクする（Codespace 起動時）
#   claude-data.sh push   : 変更を commit & push する（Claude Code の SessionEnd フックから）
#
# 必要な Codespaces シークレット（値はこのリポジトリに書かない）:
#   CLAUDE_DATA_REPO  : "owner/repo" 形式の private リポジトリ名
#   CLAUDE_DATA_TOKEN : そのリポジトリだけに Contents: Read and write を付けた fine-grained PAT
# どちらかが無い場合（他の人の Codespace など）は何もせず正常終了する。
set -u

MODE="${1:-}"
D="${CLAUDE_DATA_DIR:-/workspaces/claude-data}"

if [ -z "${CLAUDE_DATA_REPO:-}" ] || [ -z "${CLAUDE_DATA_TOKEN:-}" ]; then
  echo "claude-data: CLAUDE_DATA_REPO / CLAUDE_DATA_TOKEN が未設定のためスキップします"
  exit 0
fi

# トークンは URL にも .git/config にも書かず、実行時のヘッダーでだけ渡す
AUTH="$(printf 'x-access-token:%s' "$CLAUDE_DATA_TOKEN" | base64 -w0)"
g() {
  git -c credential.helper= \
      -c "http.https://github.com/.extraheader=AUTHORIZATION: basic $AUTH" "$@"
}

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJ="$(printf '%s' "$REPO_ROOT" | sed 's/[^A-Za-z0-9]/-/g')"
SKILLS="$HOME/.claude/skills"
MEMORY="$HOME/.claude/projects/$PROJ/memory"

# $1 のリンク先を $2 (永続側) に統一する。既存の実体があれば中身を退避してからリンクに置き換える
link_dir() {
  local src="$1" dst="$2"
  mkdir -p "$dst" "$(dirname "$src")"
  if [ -L "$src" ] && [ "$(readlink -f "$src")" = "$(readlink -f "$dst")" ]; then return 0; fi
  if [ -e "$src" ]; then
    cp -rn "$src/." "$dst/" 2>/dev/null || true
    rm -rf "$src"
  fi
  ln -sfn "$dst" "$src"
}

case "$MODE" in
  setup)
    if [ -d "$D/.git" ]; then
      g -C "$D" pull --rebase --autostash --quiet 2>/dev/null \
        || echo "claude-data: pull に失敗しました（オフライン等）。手元の内容を使います"
    else
      g clone --quiet "https://github.com/${CLAUDE_DATA_REPO}.git" "$D" \
        || { echo "claude-data: clone に失敗しました。トークンとリポジトリ名を確認してください"; exit 0; }
    fi
    mkdir -p "$D/skills" "$D/memory"
    link_dir "$SKILLS" "$D/skills"
    link_dir "$MEMORY" "$D/memory"
    echo "claude-data: ready ($D)"
    ;;

  push)
    [ -d "$D/.git" ] || exit 0
    cd "$D" || exit 0
    # スキルとメモリだけを対象にする
    git add -A skills memory
    if git diff --cached --quiet; then exit 0; fi
    # git の user 未設定の環境用（設定済みならそれを使う）
    git config user.name  >/dev/null || git config user.name  "claude-data-sync"
    git config user.email >/dev/null || git config user.email "claude-data-sync@users.noreply.github.com"
    git commit --quiet -m "Update Claude Code skills/memory ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
    g pull --rebase --autostash --quiet 2>/dev/null || true
    g push --quiet 2>/dev/null \
      && echo "claude-data: pushed" \
      || echo "claude-data: push に失敗しました（次回の push で再試行されます）"
    ;;

  *)
    echo "usage: $0 {setup|push}" >&2
    exit 2
    ;;
esac
exit 0
