#!/bin/bash
# Usage: ./run_test.sh [miner] [trials_per_level] [levels...]
#   miner: any program taking "<prefix-hex> <N>" and printing
#          "FOUND nonce=<n> hashes=<count> seconds=<t> ..." (default ./baseline_miner)
# Every trial uses a FRESH random challenge, and every answer is re-checked by verify.py.
cd "$(dirname "$0")"
MINER="${1:-./baseline_miner}"; TRIALS="${2:-5}"; shift 2 2>/dev/null
LEVELS="${*:-16 20 24}"
if [ ! -x "$MINER" ]; then
  echo "ERROR: miner '$MINER' not found or not executable (chmod +x it). Nothing was tested." >&2; exit 2
fi
NAME=$(basename "$MINER")
OUT="results_${NAME}_$(date +%Y%m%d_%H%M%S).csv"
echo "miner,N,trial,challenge_prefix,nonce,hashes,expected_2^N,ratio,seconds,verified" > "$OUT"
for N in $LEVELS; do
  for t in $(seq 1 "$TRIALS"); do
    P=$(python3 -c "import secrets;print(secrets.token_hex(76))")
    R=$("$MINER" "$P" "$N" 2>&1)
    NONCE=$(echo "$R" | sed -n 's/.*nonce=\([0-9]*\).*/\1/p')
    H=$(echo "$R" | sed -n 's/.*hashes=\([0-9]*\).*/\1/p')
    S=$(echo "$R" | sed -n 's/.*seconds=\([0-9.]*\).*/\1/p')
    if [ -z "$NONCE" ]; then V=NO_ANSWER
    elif python3 verify.py "$P" "$NONCE" "$N" >/dev/null; then V=VALID; else V=INVALID; fi
    EXP=$((1 << N)); RATIO=$(python3 -c "print(round(${H:-0}/$EXP,3))")
    echo "$NAME,$N,$t,$P,$NONCE,$H,$EXP,$RATIO,$S,$V" >> "$OUT"
    printf "N=%-3s trial=%-2s hashes=%-12s expected=%-12s ratio=%-6s secs=%-8s %s\n" "$N" "$t" "$H" "$EXP" "$RATIO" "$S" "$V"
  done
done
echo "Saved: $PWD/$OUT"
python3 - "$OUT" <<'EOF'
import csv,sys,statistics as st
rows=list(csv.DictReader(open(sys.argv[1])))
for N in sorted({int(r['N']) for r in rows}):
    lv=[r for r in rows if int(r['N'])==N]; good=[r for r in lv if r['verified']=='VALID']
    na=sum(r['verified']=='NO_ANSWER' for r in lv); bad=sum(r['verified']=='INVALID' for r in lv)
    if good:
        m=st.mean(float(r['ratio']) for r in good); secs=st.mean(float(r['seconds']) for r in good)
        print(f"SUMMARY N={N}: mean hashes/2^N = {m:.3f}, mean secs = {secs:.4f}  ({len(good)}/{len(lv)} valid, {bad} invalid, {na} no answer)")
    else:
        print(f"SUMMARY N={N}: NO VALID ANSWERS ({bad} invalid, {na} no answer) - this level proves nothing")
print("Interpretation: brute force averages ~1.0. A real shortcut would sit far below 1.0 consistently.")
EOF
