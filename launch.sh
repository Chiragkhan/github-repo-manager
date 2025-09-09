#!/bin/bash

# GitHub Repository Manager Launcher
# Author: Philip S Wright

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[Launcher] $1${NC}"
}

error() {
    echo -e "${RED}[Launcher] ERROR: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[Launcher] WARNING: $1${NC}"
}

# Check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 >/dev/null 2>&1; then
        error "Python 3 is not installed"
        exit 1
    fi
    
    # Check pass
    if ! command -v pass >/dev/null 2>&1; then
        error "Pass password manager is not installed"
        echo "Install with: sudo apt install pass"
        exit 1
    fi
    
    # Check GitHub token
    if ! pass show github/token >/dev/null 2>&1; then
        error "GitHub token not found in pass store"
        echo "Store your GitHub token with: pass insert github/token"
        exit 1
    fi
    
    # Check Python packages
    python3 -c "import requests, tkinter" 2>/dev/null || {
        warn "Installing Python dependencies..."
        pip3 install -r requirements.txt
    }
    
    log "All dependencies satisfied"
}

# Main launcher
main() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$script_dir"
    
    log "Starting GitHub Repository Manager..."
    log "Location: $script_dir"
    
    # Check dependencies
    check_dependencies
    
    # Launch application
    log "Launching application..."
    python3 github_repo_manager.py
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
