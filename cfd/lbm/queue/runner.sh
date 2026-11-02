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
lock()   { until mkdir "$Q/.lock" 2>/dev/null; do sleep 1; done; }
unlock() { rmdir "$Q/.lock" 2>/dev/null; }
need_mb() { # estimate device memory from D, box and precision (2 lattices x 19 + flags)
  awk -v a="$*" 'BEGIN{D=48;Lx=6;Ly=4;Lz=4;p="fp16";b="sphere";n=split(a,t," ");
    for(i=1;i<=n;i++){split(t[i],kv,"=");k=kv[1];v=kv[2];
      if(k=="D")D=v;if(k=="Lx")Lx=v;if(k=="Ly")Ly=v;if(k=="Lz")Lz=v;if(k=="prec")p=v;if(k=="body")b=v}
    if(b=="rotstokes"){Lx=4;Ly=4;Lz=4}
    c=int(Lx*D)*int(Ly*D)*int(Lz*D); bpc=(p=="fp32")?153:77;
    printf "%d", c*bpc/1048576+400}'
}
free_mb() { nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -dc 0-9; }
log() { echo "$(date '+%F %T') [$NAME] $*" >> "$Q/runner.log"; }
log "start side=$SIDE"
while true; do
  lock
  if [ "$SIDE" = back ]; then line=$(grep -v '^[[:space:]]*\(#\|$\)' "$Q/todo.txt" | tail -1)
  else line=$(grep -v '^[[:space:]]*\(#\|$\)' "$Q/todo.txt" | head -1); fi
  if [ -z "$line" ]; then unlock; sleep 20; continue; fi
  id=${line%% *}; args=${line#* }
  need=$(need_mb "$args"); free=$(free_mb); free=${free:-0}
  if [ "$free" -lt $((need + 1024)) ]; then unlock; log "wait $id need=${need}MiB free=${free}MiB"; sleep 20; continue; fi
  # remove exactly that line (first or last occurrence) from todo.txt
  if [ "$SIDE" = back ]; then n=$(grep -nxF -- "$line" "$Q/todo.txt" | tail -1 | cut -d: -f1)
  else n=$(grep -nxF -- "$line" "$Q/todo.txt" | head -1 | cut -d: -f1); fi
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
