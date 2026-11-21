#!/usr/bin/env bash
# Claude Code のスキルとメモリを、専用 private リポジトリ (claude-data) と同期する。
# 複数のリポジトリで同じスクリプトを使える（どのリポジトリに置いても、dotfiles から使っても同一）。
#
#   claude-data.sh setup [プロジェクトのパス] : clone/pull して ~/.claude の skills と memory をリンクする
#   claude-data.sh push                       : 変更を commit & push する（SessionEnd フックから）
#
# 保存先のレイアウト（claude-data リポジトリ）:
#   skills/              ユーザースキル（全プロジェクト共通）
#   memory/<リポジトリ名>/ メモリ（プロジェクトごと）
#
# 必要な Codespaces シークレット（値はリポジトリに書かない）:
#   CLAUDE_DATA_REPO  : "owner/repo" 形式の private リポジトリ名
#   CLAUDE_DATA_TOKEN : そのリポジトリだけに Contents: Read and write を付けた fine-grained PAT
# どちらかが無い場合（他の人の Codespace など）は何もせず正常終了する。
set -u

MODE="${1:-}"
PROJECT_ARG="${2:-}"
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

# 対象プロジェクトのディレクトリを決める（引数 > フックの環境変数 > Codespaces > git のルート）
resolve_project_dir() {
  local c
  for c in "$PROJECT_ARG" "${CLAUDE_PROJECT_DIR:-}" "${CODESPACE_VSCODE_FOLDER:-}" \
           "$(git rev-parse --show-toplevel 2>/dev/null || true)"; do
    if [ -n "$c" ] && [ -d "$c" ]; then
      (cd "$c" && pwd)
      return 0
    fi
  done
  return 1
}

# $1 を $2 (永続側) へのリンクにする。既存の実体があれば、中身を $2 に退避してから置き換える
link_dir() {
  local src="$1" dst="$2"
  mkdir -p "$dst" "$(dirname "$src")"
  if [ -L "$src" ] && [ "$(readlink -f "$src")" = "$(readlink -f "$dst")" ]; then return 0; fi
  if [ -L "$src" ]; then
    rm -f "$src"                       # 別の場所へのリンク（旧レイアウトなど）は張り替えるだけ
  elif [ -e "$src" ]; then
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

    mkdir -p "$D/skills"
    link_dir "$HOME/.claude/skills" "$D/skills"

    if PROJECT_DIR="$(resolve_project_dir)"; then
      NAME="$(basename "$PROJECT_DIR")"
      PROJ="$(printf '%s' "$PROJECT_DIR" | sed 's/[^A-Za-z0-9]/-/g')"
      link_dir "$HOME/.claude/projects/$PROJ/memory" "$D/memory/$NAME"
      echo "claude-data: ready (skills + memory/$NAME → $D)"
    else
      echo "claude-data: プロジェクトを特定できないため、スキルのみリンクしました"
    fi
    ;;

  push)
    [ -d "$D/.git" ] || exit 0
    cd "$D" || exit 0
    # スキルとメモリだけを対象にする
    git add -A skills memory 2>/dev/null
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
    echo "usage: $0 {setup [project-dir]|push}" >&2
    exit 2
    ;;
esac
exit 0
