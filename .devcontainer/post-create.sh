#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Source logging utility
source "$(dirname "${BASH_SOURCE[0]}")/utils/log.sh"

main() {
    log_info "Starting post-create script."

    # Upgrade pip to the latest version
    log_info "Upgrading pip..."
    python3 -m pip install --upgrade pip

    # Find the git repository root and locate requirements.txt
    local repo_root
    if ! repo_root="$(git rev-parse --show-toplevel)"; then
        log_error "Could not find git repository root"
        exit 1
    fi

    local requirements_file="${repo_root}/requirements.txt"

    if [[ -f "$requirements_file" ]]; then
        log_info "Installing requirements from $requirements_file..."
        python3 -m pip install -r "$requirements_file"
    else
        log_error "Requirements file not found at $requirements_file"
        exit 1
    fi

    # Copy any existing Docker config from the host to the container
    cp -r /home/vscode/.docker-host/* /home/vscode/.docker/ 2>/dev/null || true

    log_success "Post-create script completed successfully."
}

if ! (return 0 2>/dev/null); then
    (main "$@")
fi
