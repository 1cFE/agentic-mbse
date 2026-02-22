#!/usr/bin/env bash
# Pandoc HTML→Markdown experiment runner
# Each iteration saves output to pandoc-experiments/iter-NN/

HTML="tests/corpus/html/paischer_2025.html"
BASE="tests/corpus/pandoc-experiments"

run_iter() {
    local num="$1"
    shift
    local dir="$BASE/iter-$(printf '%02d' $num)"
    mkdir -p "$dir"
    echo "=== Iteration $num: $* ==="
    echo "Command: pandoc $*" > "$dir/command.txt"
    pandoc "$@" > "$dir/paischer_2025.md" 2>"$dir/stderr.txt"
    echo "Exit code: $?" >> "$dir/command.txt"
    python tests/corpus/metrics.py "$dir/paischer_2025.md" > "$dir/metrics.json"
    echo "  -> $(wc -c < "$dir/paischer_2025.md") bytes, $(wc -l < "$dir/paischer_2025.md") lines"
}

# Iter 1: Baseline — default flags
run_iter 1 "$HTML" -f html -t markdown

# Iter 2: --wrap=none
run_iter 2 "$HTML" -f html -t markdown --wrap=none

# Iter 3: --wrap=preserve
run_iter 3 "$HTML" -f html -t markdown --wrap=preserve

# Iter 4: ATX headings
run_iter 4 "$HTML" -f html -t markdown --markdown-headings=atx

# Iter 5: Math — tex_math_dollars extension
run_iter 5 "$HTML" -f html -t markdown+tex_math_dollars

# Iter 6: Math — tex_math_single_backslash
run_iter 6 "$HTML" -f html -t markdown+tex_math_single_backslash

# Iter 7: --mathml output flag
run_iter 7 "$HTML" -f html -t markdown --mathml

# Iter 8: --katex output flag
run_iter 8 "$HTML" -f html -t markdown --katex

# Iter 9: Grid tables instead of pipe tables
run_iter 9 "$HTML" -f html -t markdown+grid_tables-pipe_tables

# Iter 10: Wide columns
run_iter 10 "$HTML" -f html -t markdown --columns=120

# Iter 11: --wrap=none + ATX headings (combining two known-good settings)
run_iter 11 "$HTML" -f html -t markdown --wrap=none --markdown-headings=atx

# Iter 12: Combined best candidate (wrap=none, atx, tex_math_dollars, columns=120)
run_iter 12 "$HTML" -f html -t markdown+tex_math_dollars --wrap=none --markdown-headings=atx --columns=120

echo ""
echo "=== All iterations complete ==="
echo "Metrics summary:"
for d in "$BASE"/iter-*/; do
    iter=$(basename "$d")
    if [ -f "$d/metrics.json" ]; then
        cmd=$(head -1 "$d/command.txt" | sed 's/Command: pandoc //')
        chars=$(python -c "import json; d=json.load(open('${d}metrics.json')); print(d['char_count'])")
        headings=$(python -c "import json; d=json.load(open('${d}metrics.json')); print(d['heading_count'])")
        tables=$(python -c "import json; d=json.load(open('${d}metrics.json')); print(d['table_row_count'])")
        math=$(python -c "import json; d=json.load(open('${d}metrics.json')); print(d['math_symbol_count'])")
        figrefs=$(python -c "import json; d=json.load(open('${d}metrics.json')); print(d['figure_ref_count'])")
        printf "  %-8s chars=%-7s hdg=%-3s tbl=%-4s math=%-3s fig=%-3s %s\n" "$iter" "$chars" "$headings" "$tables" "$math" "$figrefs" "$cmd"
    fi
done
