#!/bin/bash
# =============================================================================
# Docling MCP Server Setup for Claude Code CLI
# =============================================================================
# Detects system resources (RAM, GPU) and configures the docling-mcp server
# with appropriate memory/threading constraints.
#
# Usage: bash setup-docling-mcp.sh [--force]
#   --force: Remove existing docling MCP config and reinstall
# =============================================================================

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*" >&2; }
ok()    { echo -e "${GREEN}[OK]${NC} $*" >&2; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
err()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# --- Parse Args ---
FORCE=false
for arg in "$@"; do
  [[ "$arg" == "--force" ]] && FORCE=true
done

# =============================================================================
# 1. ENVIRONMENT DETECTION
# =============================================================================

info "Detecting system resources..."

# RAM detection
TOTAL_RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
TOTAL_RAM_GB=$((TOTAL_RAM_KB / 1024 / 1024))
AVAIL_RAM_KB=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
AVAIL_RAM_GB=$((AVAIL_RAM_KB / 1024 / 1024))

info "Total RAM: ${TOTAL_RAM_GB}GB | Available: ${AVAIL_RAM_GB}GB"

# GPU detection
HAS_GPU=false
GPU_NAME="none"
GPU_VRAM_MB=0

if command -v nvidia-smi &>/dev/null; then
  if nvidia-smi &>/dev/null; then
    HAS_GPU=true
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "unknown")
    GPU_VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "0")
    info "GPU detected: ${GPU_NAME} (${GPU_VRAM_MB}MB VRAM)"
  fi
fi

if [ "$HAS_GPU" = false ]; then
  info "No NVIDIA GPU detected — CPU-only mode"
fi

# CPU detection
CPU_CORES=$(nproc)
info "CPU cores: ${CPU_CORES}"

# --- Classify environment ---
# Tiers:
#   constrained: <=8GB RAM, CPU-only  → aggressive limits, single-page only
#   moderate:    9-16GB RAM or GPU     → moderate limits, small page ranges ok
#   comfortable: 17GB+ RAM            → light limits, larger batches ok
if [ "$TOTAL_RAM_GB" -le 8 ]; then
  TIER="constrained"
elif [ "$TOTAL_RAM_GB" -le 16 ]; then
  TIER="moderate"
else
  TIER="comfortable"
fi

# GPU bumps you up one tier for Docling specifically (models offload to VRAM)
if [ "$HAS_GPU" = true ] && [ "$TIER" = "constrained" ]; then
  TIER="moderate"
  info "GPU detected — upgrading tier from constrained to moderate"
fi

ok "Environment tier: ${TIER}"

# =============================================================================
# 2. PREREQUISITE CHECKS
# =============================================================================

info "Checking prerequisites..."

# uv
if ! command -v uv &>/dev/null; then
  err "uv not found. Install it: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi
ok "uv $(uv --version 2>&1 | head -1)"

# uvx
if ! command -v uvx &>/dev/null; then
  err "uvx not found. It should come with uv. Try: uv tool install uvx"
  exit 1
fi
ok "uvx available"

# claude CLI
if ! command -v claude &>/dev/null; then
  err "claude CLI not found in PATH"
  exit 1
fi
ok "claude CLI available"

# Python version check
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
  err "Python >= 3.10 required. Found: $PYTHON_VERSION"
  exit 1
fi
ok "Python $PYTHON_VERSION"

# =============================================================================
# 3. CONFIGURE THREAD/MEMORY LIMITS BY TIER
# =============================================================================

case "$TIER" in
  constrained)
    OMP_THREADS=1
    MKL_THREADS=1
    NUMEXPR_THREADS=1
    MAX_PAGES_HINT=1
    DOCLING_NOTES="# CONSTRAINED: 8GB RAM or less, CPU-only
# - Only process single pages via Docling
# - Always extract individual pages as separate PDFs first
# - Use PNG fallback if Docling is slow or unresponsive
# - Thread counts minimized to avoid memory pressure"
    ;;
  moderate)
    OMP_THREADS=2
    MKL_THREADS=2
    NUMEXPR_THREADS=2
    MAX_PAGES_HINT=5
    DOCLING_NOTES="# MODERATE: 9-16GB RAM or GPU available
# - Can process small page ranges (up to ~5 pages)
# - Still prefer single-page extraction for complex tables
# - Thread counts balanced for performance vs memory"
    ;;
  comfortable)
    OMP_THREADS=4
    MKL_THREADS=4
    NUMEXPR_THREADS=4
    MAX_PAGES_HINT=20
    DOCLING_NOTES="# COMFORTABLE: 17GB+ RAM
# - Can process larger page ranges
# - Full document conversion may work for shorter papers (<30 pages)
# - Monitor memory on first use with: watch -n 1 free -h"
    ;;
esac

# =============================================================================
# 4. CREATE WRAPPER SCRIPT
# =============================================================================

WRAPPER_DIR="$HOME/.local/bin"
WRAPPER_PATH="$WRAPPER_DIR/docling-mcp-wrapper.sh"

mkdir -p "$WRAPPER_DIR"

info "Creating wrapper script at $WRAPPER_PATH"

cat > "$WRAPPER_PATH" << WRAPPER
#!/bin/bash
# =============================================================================
# Docling MCP Wrapper — auto-generated by setup-docling-mcp.sh
# Environment tier: ${TIER}
# System: ${TOTAL_RAM_GB}GB RAM, ${CPU_CORES} cores, GPU: ${GPU_NAME}
# Generated: $(date -Iseconds)
# =============================================================================

${DOCLING_NOTES}

# Avoid picking up project .env files (pydantic_settings reads CWD/.env)
cd /tmp

# Thread limits
export OMP_NUM_THREADS=${OMP_THREADS}
export MKL_NUM_THREADS=${MKL_THREADS}
export NUMEXPR_NUM_THREADS=${NUMEXPR_THREADS}
export TOKENIZERS_PARALLELISM=false

# Force CPU-only — prevents PyTorch GPU probe overhead
export CUDA_VISIBLE_DEVICES=""

# Reduce PyTorch memory allocation fragmentation
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"

# Limit UV's own parallelism during dependency resolution
export UV_CONCURRENT_DOWNLOADS=4

exec uvx --from=docling-mcp docling-mcp-server --transport stdio
WRAPPER

chmod +x "$WRAPPER_PATH"
ok "Wrapper script created"

# =============================================================================
# 5. TEST DOCLING MCP LAUNCH
# =============================================================================

info "Testing docling-mcp server launch (this may take a minute on first run)..."

# Run the server, wait for the startup message, then kill it
LAUNCH_OUTPUT=$(timeout 120 bash "$WRAPPER_PATH" 2>&1 &
  SERVER_PID=$!
  # Wait for either "starting up" or an error
  sleep 30
  kill $SERVER_PID 2>/dev/null
  wait $SERVER_PID 2>/dev/null
) || true

if echo "$LAUNCH_OUTPUT" | grep -q "starting up Docling MCP-server"; then
  ok "Docling MCP server starts successfully"
elif echo "$LAUNCH_OUTPUT" | grep -q "ValidationError"; then
  err "Pydantic validation error — likely a .env file conflict"
  echo "$LAUNCH_OUTPUT" | tail -5
  err "Check that no project .env files are interfering"
  exit 1
elif echo "$LAUNCH_OUTPUT" | grep -q "MemoryError\|Cannot allocate\|OOM"; then
  err "Out of memory during startup"
  err "Your system may not have enough RAM to run Docling"
  warn "Consider using only pymupdf + PNG fallback (no Docling)"
  exit 1
else
  warn "Could not confirm clean startup. Output:"
  echo "$LAUNCH_OUTPUT" | tail -10
  warn "Proceeding anyway — check /mcp status in Claude Code"
fi

# =============================================================================
# 6. REGISTER WITH CLAUDE CODE
# =============================================================================

info "Registering docling MCP with Claude Code CLI..."

# Remove existing if present
claude mcp remove docling 2>/dev/null || true

claude mcp add --scope user --transport stdio docling -- \
  bash "$WRAPPER_PATH"

ok "Docling MCP registered with Claude Code (user scope)"

# =============================================================================
# 7. GENERATE ENVIRONMENT REPORT
# =============================================================================

REPORT_PATH="$HOME/.docling-mcp-env.md"

cat > "$REPORT_PATH" << REPORT
# Docling MCP Environment Report

Generated: $(date -Iseconds)

## System
- RAM: ${TOTAL_RAM_GB}GB total, ${AVAIL_RAM_GB}GB available at setup
- CPU: ${CPU_CORES} cores
- GPU: ${GPU_NAME} (${GPU_VRAM_MB}MB VRAM)
- Python: ${PYTHON_VERSION}
- Tier: **${TIER}**

## Configuration
- Wrapper: \`${WRAPPER_PATH}\`
- OMP_NUM_THREADS: ${OMP_THREADS}
- MKL_NUM_THREADS: ${MKL_THREADS}
- Max recommended pages per Docling call: ${MAX_PAGES_HINT}

## Usage Rules for Tier: ${TIER}
$(echo "$DOCLING_NOTES" | sed 's/^# /- /' | grep -v '^#')

## Three-Tier PDF Extraction Strategy

### Tier 1: pymupdf4llm (default, fast)
\`\`\`python
import pymupdf4llm
md = pymupdf4llm.to_markdown("paper.pdf")
\`\`\`

### Tier 2: Docling MCP (targeted, for garbled tables)
Extract single page first, then send to Docling:
\`\`\`python
import pymupdf
doc = pymupdf.open("paper.pdf")
single = pymupdf.open()
single.insert_pdf(doc, from_page=N, to_page=N)
single.save("/tmp/page_N.pdf")
single.close()
doc.close()
\`\`\`
Then: "Convert the PDF at /tmp/page_N.pdf into DoclingDocument"

### Tier 3: PNG visual fallback (last resort)
\`\`\`python
import pymupdf
doc = pymupdf.open("paper.pdf")
page = doc[N]
pix = page.get_pixmap(matrix=pymupdf.Matrix(200/72, 200/72))
pix.save("/tmp/page_N.png")
doc.close()
\`\`\`
Then visually read the PNG and reconstruct the markdown.
REPORT

ok "Environment report saved to $REPORT_PATH"

# =============================================================================
# 8. SUMMARY
# =============================================================================

echo ""
echo "============================================="
echo -e "${GREEN}  Docling MCP Setup Complete${NC}"
echo "============================================="
echo ""
echo "  Tier:          $TIER"
echo "  Wrapper:       $WRAPPER_PATH"
echo "  Report:        $REPORT_PATH"
echo "  Max pages/call: $MAX_PAGES_HINT"
echo ""
echo "  Next steps:"
echo "    1. Open Claude Code: claude"
echo "    2. Verify:          /mcp  →  docling: connected"
echo "    3. Test:            'Convert /tmp/test.pdf into DoclingDocument'"
echo ""
echo "  If connection fails, debug with:"
echo "    claude --debug"
echo "    bash $WRAPPER_PATH  # run standalone"
echo ""