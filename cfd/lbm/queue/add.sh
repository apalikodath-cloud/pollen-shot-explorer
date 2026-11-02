#!/usr/bin/env bash
# Append case lines to todo.txt under the queue lock.  usage: add.sh "<id> <args>" ... | add.sh --front "<id> <args>"
Q=${PM012_QUEUE:-${PM012_CFD_ROOT:?set PM012_CFD_ROOT}/pm012_lbm/queue}
front=0; [ "${1:-}" = --front ] && { front=1; shift; }
log() { echo "$(date '+%F %T') [add] $*" >> "$Q/runner.log"; }
while ! mkdir "$Q/.lock" 2>/dev/null; do
  if [ -d "$Q/.lock" ] && find "$Q/.lock" -maxdepth 0 -type d -mmin +10 -print -quit | grep -q .; then
    rmdir "$Q/.lock" 2>/dev/null && log "broke stale lock"
  else
    sleep 1
  fi
done
trap 'rmdir "$Q/.lock" 2>/dev/null' EXIT INT TERM
if [ $front = 1 ]; then { printf '%s\n' "$@"; cat "$Q/todo.txt"; } > "$Q/todo.tmp" && mv "$Q/todo.tmp" "$Q/todo.txt"
else printf '%s\n' "$@" >> "$Q/todo.txt"; fi
rmdir "$Q/.lock"
trap - EXIT INT TERM
