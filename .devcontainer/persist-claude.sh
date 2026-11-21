#!/usr/bin/env bash
# Claude Code のメモリ・スキル・設定を Rebuild をまたいで残す。
# 実体はリポジトリ外の /workspaces/.claude-persist に置き、~/.claude からリンクする。
# 認証情報 (.credentials.json, ~/.claude.json) は意図的に対象外（毎回ブラウザ認証）。
set -e

P=/workspaces/.claude-persist
mkdir -p "$P" "$HOME/.claude"

# ディレクトリ
for d in projects skills agents commands; do
  src="$HOME/.claude/$d"
  if [ -e "$src" ] && [ ! -L "$src" ]; then
    mkdir -p "$P/$d"
    cp -rn "$src/." "$P/$d/" 2>/dev/null || true
    rm -rf "$src"
  fi
  mkdir -p "$P/$d"
  ln -sfn "$P/$d" "$src"
done

# ファイル（永続側に実体がある場合のみリンク）
for f in settings.json CLAUDE.md; do
  src="$HOME/.claude/$f"
  if [ -f "$src" ] && [ ! -L "$src" ]; then
    cp -n "$src" "$P/$f" 2>/dev/null || true
    rm -f "$src"
  fi
  [ -e "$P/$f" ] && ln -sfn "$P/$f" "$src"
done

echo "Claude Code persistence ready: $P"
