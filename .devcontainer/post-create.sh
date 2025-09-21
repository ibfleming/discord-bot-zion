#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Source logging utility
source "$(dirname "${BASH_SOURCE[0]}")/utils/log.sh"

main() {
    log_info "Starting post-create script."

    # Ensure we're running as the vscode user in a dev container
    if [[ "${USER:-}" != "vscode" ]]; then
        log_warning "Script is running as user '${USER:-unknown}' instead of 'vscode'"
    fi

    install_dependencies

    # Copy any existing Docker config from the host to the container
    cp -r /home/vscode/.docker-host/* /home/vscode/.docker/ 2>/dev/null || true

    log_success "Post-create script completed successfully."
}

#######################################
# Installs Python dependencies from requirements.txt
# Globals:
#   None
# Arguments:
#   None
# Outputs:
#   Progress messages via log_info/log_error functions
# Returns:
#   0 if successful, non-zero on error
#######################################
install_dependencies() {
    # Upgrade pip to the latest version
    log_info "Upgrading pip..."
    if ! python3 -m pip install --upgrade pip; then
        log_error "Failed to upgrade pip"
        return 1
    fi

    # Find the git repository root and locate requirements.txt
    local repo_root
    if ! repo_root="$(git rev-parse --show-toplevel)"; then
        log_error "Could not find git repository root"
        return 1
    fi

    local requirements_file="${repo_root}/requirements.txt"

    if [[ -f $requirements_file ]]; then
        log_info "Installing requirements from $requirements_file..."
        if ! python3 -m pip install -r "$requirements_file"; then
            log_error "Failed to install requirements from $requirements_file"
            return 1
        fi
    else
        log_error "Requirements file not found at $requirements_file"
        return 1
    fi

    log_info "Python dependencies installed successfully"
    return 0
}

if ! (return 0 2>/dev/null); then
    (main "$@")
fi
