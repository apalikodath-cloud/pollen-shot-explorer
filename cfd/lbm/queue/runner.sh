#!/usr/bin/env bash
# PM-012 GPU case queue runner.  usage: PM012_CFD_ROOT=<folder outside the repo> runner.sh front|back [name]
#   front pops the FIRST line of todo.txt, back pops the LAST line.
# todo.txt line: <case_id> <pm012_lbm.exe key=value args...>   (# comments and blank lines are skipped)
# Output: runs/<id>.csv (out= is added), runs/<id>.log.  done.txt / failed.txt get "<id> exit=<code> ...".
# Lock: mkdir queue/.lock (atomic). Anyone editing todo.txt must hold it: use queue/add.sh.
# GPU gate: a case starts only if nvidia-smi free memory >= need + 1024 MiB; the runner keeps the
# lock until the new process has allocated (its "PM-012 ... N=" line appears, 180 s max), so
# concurrent runners always see real free memory.
set -u
ROOT=${PM012_CFD_ROOT:?set PM012_CFD_ROOT (folder outside the repo that holds pm012_lbm/)}
Q=${PM012_QUEUE:-$ROOT/pm012_lbm/queue}
RUNS=${PM012_RUNS:-$ROOT/pm012_lbm/runs}
EXE=${PM012_EXE:-$ROOT/pm012_lbm/bin/pm012_lbm.exe}
SIDE=${1:?front|back}
NAME=${2:-$SIDE}
mkdir -p "$Q" "$RUNS"; touch "$Q/todo.txt" "$Q/running.txt" "$Q/done.txt" "$Q/failed.txt"
lock() {
  while ! mkdir "$Q/.lock" 2>/dev/null; do
    if [ -d "$Q/.lock" ] && find "$Q/.lock" -maxdepth 0 -type d -mmin +10 -print -quit | grep -q .; then
      rmdir "$Q/.lock" 2>/dev/null && log "broke stale lock"
    else
      sleep 1
    fi
  done
  trap 'rmdir "$Q/.lock" 2>/dev/null' EXIT INT TERM
}
unlock() { rmdir "$Q/.lock" 2>/dev/null; trap - EXIT INT TERM; }
need_mb() { # estimate device memory from D, box and precision (2 lattices x 19 + flags)
  local planned
  planned=$("$EXE" $1 plan=1 2>/dev/null | awk -F= '$1 == "need_mib" {v=$2} END {if (v != "") printf "%d", v}')
  if [ -n "$planned" ]; then printf '%s' "$planned"; return; fi
  awk -v a="$*" 'BEGIN{D=48;Lx=6;Ly=4;Lz=4;p="fp16";b="sphere";n=split(a,t," ");
    for(i=1;i<=n;i++){split(t[i],kv,"=");k=kv[1];v=kv[2];
      if(k=="D")D=v;if(k=="Lx")Lx=v;if(k=="Ly")Ly=v;if(k=="Lz")Lz=v;if(k=="prec")p=v;if(k=="body")b=v}
    if(b=="rotstokes"){Lx=4;Ly=4;Lz=4}
    c=int(Lx*D)*int(Ly*D)*int(Lz*D); bpc=(p=="fp32")?153:77;
    printf "%d", c*bpc/1048576+400}'
}
device_id() { printf '%s\n' "$*" | awk '{for(i=1;i<=NF;i++) if($i ~ /^device=/) {sub(/^device=/,"",$i); print $i; exit}}'; }
free_mb() { local d=${1:-0}; nvidia-smi -i "$d" --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | tr -dc 0-9; }
total_mb() { local d=${1:-0}; nvidia-smi -i "$d" --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | tr -dc 0-9; }
log() { echo "$(date '+%F %T') [$NAME] $*" >> "$Q/runner.log"; }
log "start side=$SIDE"
while true; do
  lock
  if [ "$SIDE" = back ]; then line=$(grep -v '^[[:space:]]*\(#\|$\)' "$Q/todo.txt" | tail -1)
  else line=$(grep -v '^[[:space:]]*\(#\|$\)' "$Q/todo.txt" | head -1); fi
  if [ -z "$line" ]; then unlock; sleep 20; continue; fi
  id=${line%% *}; args=${line#* }
  need=$(need_mb "$args"); dev=$(device_id "$args"); dev=${dev:-0}; free=$(free_mb "$dev"); free=${free:-0}; total=$(total_mb "$dev"); total=${total:-0}
  # the solver refuses a plan above 92 % of device memory, and the free-memory wait below needs need+1024 MiB:
  # a case that can never pass either check fails now instead of waiting forever
  if [ "$total" -gt 0 ] && { [ $((need * 100)) -gt $((total * 92)) ] || [ $((need + 1024)) -gt "$total" ]; }; then
    n=$(grep -nxF -- "$line" "$Q/todo.txt" | if [ "$SIDE" = back ]; then tail -1; else head -1; fi | cut -d: -f1)
    [ -n "$n" ] && sed -i "${n}d" "$Q/todo.txt"
    echo "$id exit=memory need=${need}MiB total=${total}MiB $(date '+%F %T')" >> "$Q/failed.txt"
    unlock; log "fail $id need=${need}MiB exceeds device=$dev total=${total}MiB"; continue
  fi
  if [ "$free" -lt $((need + 1024)) ]; then unlock; log "wait $id need=${need}MiB free=${free}MiB"; sleep 20; continue; fi
  # remove exactly that line (first or last occurrence) from todo.txt
  if [ "$SIDE" = back ]; then n=$(grep -nxF -- "$line" "$Q/todo.txt" | tail -1 | cut -d: -f1)
  else n=$(grep -nxF -- "$line" "$Q/todo.txt" | head -1 | cut -d: -f1); fi
  if [ -z "$n" ]; then unlock; log "skip $id: line left todo.txt meanwhile"; continue; fi
  sed -i "${n}d" "$Q/todo.txt"
  echo "$NAME $id need=${need}MiB $(date '+%F %T')" >> "$Q/running.txt"
  log "run $id need=${need}MiB free=${free}MiB: $args"
  t0=$(date +%s)
  "$EXE" $args out="$RUNS/$id.csv" > "$RUNS/$id.log" 2>&1 &
  pid=$!
  for i in $(seq 1 180); do grep -q '^PM-012 .* N=' "$RUNS/$id.log" 2>/dev/null && break; kill -0 $pid 2>/dev/null || break; sleep 1; done
  unlock
  wait $pid; rc=$?
  dt=$(( $(date +%s) - t0 ))
  mlups=$(grep -o 'MLUPs=[0-9.e+]*' "$RUNS/$id.csv" 2>/dev/null | tail -1)
  lock
  grep -v "^$NAME $id " "$Q/running.txt" > "$Q/running.tmp"; mv "$Q/running.tmp" "$Q/running.txt"
  if [ $rc -eq 0 ] && grep -q '^# runtime_s=' "$RUNS/$id.csv" 2>/dev/null; then
    echo "$id exit=$rc wall_s=$dt $mlups $(date '+%F %T')" >> "$Q/done.txt"
  else
    echo "$id exit=$rc wall_s=$dt $(tail -1 "$RUNS/$id.log" | tr -d '\r' | cut -c1-160) $(date '+%F %T')" >> "$Q/failed.txt"
  fi
  unlock
  log "end $id exit=$rc wall_s=$dt"
done
