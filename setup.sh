#!/bin/bash
# MyGPU - Lightweight GPU Management Utility - Setup Script (Bash)
# Supports Linux and macOS.

set -e

# Colors for output
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

write_info() { echo -e "${CYAN}$1${NC}"; }
write_ok() { echo -e "${GREEN}$1${NC}"; }
write_warn() { echo -e "${YELLOW}$1${NC}"; }
write_err() { echo -e "${RED}$1${NC}"; }

# Detect script directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

get_project_version() {
    local ver_file="monitor/__version__.py"
    if [[ -f "$ver_file" ]]; then
        # Matches both single and double quotes
        local version=$(grep "__version__" "$ver_file" | sed -E "s/__version__[[:space:]]*=[[:space:]]*['\"]([^'\"]+)['\"].*/\1/")
        echo "$version"
    else
        echo "(unknown)"
    fi
}

ensure_uv() {
    if command -v uv &> /dev/null; then
        write_ok "[OK] uv detected: $(uv --version)"
        return
    fi

    write_info "[INFO] uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to path for this session
    export PATH="$HOME/.local/bin:$PATH"

    if ! command -v uv &> /dev/null; then
        write_err "[ERROR] uv still not found after install attempt."
        write_warn "Try adding $HOME/.local/bin to your PATH manually."
        exit 1
    fi

    write_ok "[OK] uv installed: $(uv --version)"
}

test_cuda() {
    if command -v nvidia-smi &> /dev/null; then
        if nvidia-smi -L &> /dev/null; then
            return 0
        fi
    fi
    return 1
}

ensure_venv() {
    local venv_dir="$PROJECT_DIR/.venv"
    local venv_python="$venv_dir/bin/python"

    if [[ -f "$venv_python" ]]; then
        write_ok "[OK] Found existing venv: $venv_dir"
        echo "$venv_python"
        return
    fi

    write_info "Creating virtual environment with uv..."
    uv venv "$venv_dir" &> /dev/null
    
    if [[ ! -f "$venv_python" ]]; then
        write_err "[ERROR] uv venv created, but python not found in $venv_dir"
        exit 1
    fi

    write_ok "[OK] Created venv: $venv_dir"
    echo "$venv_python"
}

version=$(get_project_version)
write_info "\n=== MyGPU — Lightweight GPU Management Utility Setup ($version) ===\n"

ensure_uv

cuda_available=false
if test_cuda; then
    write_ok "[OK] CUDA/NVIDIA driver detected."
    cuda_available=true
else
    write_warn "[INFO] CUDA not detected (nvidia-smi check failed)."
    write_warn "Full (GPU) mode may fail or run CPU-only depending on platform."
fi

VENV_PYTHON=$(ensure_venv)
write_ok "[OK] Using venv python: $VENV_PYTHON"

req_path="requirements.txt"
if [[ ! -f "$req_path" ]]; then
    write_err "[ERROR] requirements.txt not found!"
    exit 1
fi

write_info "\n=== Install Options ==="
echo "1) minimal  - CLI monitoring only"
echo "2) normal   - CLI + Web UI"
echo "3) full     - normal + GPU benchmarking"

default_choice="2"
[[ "$cuda_available" == true ]] && default_choice="3"

read -p "Select [1-3] (default $default_choice): " choice
choice=${choice:-$default_choice}

case $choice in
    1) mode="minimal" ;;
    2) mode="normal" ;;
    3) mode="full" ;;
    *) 
        write_warn "Invalid choice '$choice'; using default $default_choice"
        [[ "$default_choice" == "3" ]] && mode="full" || mode="normal"
        ;;
esac

write_info "\nSelected mode: $mode\n"

# Simple parser for requirements.txt sections
get_requirements() {
    local section=$1
    local in_section=false
    while IFS= read -r line; do
        if [[ "$line" =~ ^[[:space:]]*#[[:space:]]*\[$section\] ]]; then
            in_section=true
            continue
        fi
        if [[ "$line" =~ ^[[:space:]]*#[[:space:]]*\[ ]]; then
            in_section=false
            continue
        fi
        if [[ "$in_section" == true ]] && [[ -n "$line" ]] && [[ ! "$line" =~ ^[[:space:]]*# ]]; then
            echo "$line"
        fi
    done < "$req_path"
}

pkgs=""
if [[ "$mode" == "minimal" ]]; then
    pkgs=$(get_requirements "minimal")
elif [[ "$mode" == "normal" ]]; then
    pkgs=$(echo -e "$(get_requirements "minimal")\n$(get_requirements "normal")")
else
    pkgs=$(echo -e "$(get_requirements "minimal")\n$(get_requirements "normal")\n$(get_requirements "full")")
fi

if [[ -z "$pkgs" ]]; then
    write_err "[ERROR] No packages resolved for mode '$mode'."
    exit 1
fi

# Install packages
write_info "Installing dependencies..."
if [[ "$mode" != "full" ]]; then
    uv pip install --python "$VENV_PYTHON" $pkgs
else
    # Full mode: handle torch specially if needed
    torch_pkgs=""
    other_pkgs=""
    while read -r p; do
        if [[ "$p" =~ ^(torch|torchvision|torchaudio) ]]; then
            torch_pkgs="$torch_pkgs $p"
        else
            other_pkgs="$other_pkgs $p"
        fi
    done <<< "$pkgs"

    if [[ -n "$other_pkgs" ]]; then
        uv pip install --python "$VENV_PYTHON" $other_pkgs
    fi

    if [[ -n "$torch_pkgs" ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS: install standard torch (MPS support included)
            uv pip install --python "$VENV_PYTHON" $torch_pkgs
        else
            # Linux: use CUDA index
            uv pip install --python "$VENV_PYTHON" --extra-index-url https://download.pytorch.org/whl/cu128 $torch_pkgs
        fi
    fi
fi

write_info "\n=== Done ==="
write_ok "To run (no activation needed):"
echo "  CLI:  $VENV_PYTHON health_monitor.py cli"
echo "  Web:  $VENV_PYTHON health_monitor.py web"
echo "  Help: $VENV_PYTHON health_monitor.py --help"
if [[ "$mode" == "full" ]]; then
    echo "  Benchmark: $VENV_PYTHON health_monitor.py benchmark --mode quick"
fi
echo ""
write_warn "Tip: If you want an activated shell, run: source .venv/bin/activate"
