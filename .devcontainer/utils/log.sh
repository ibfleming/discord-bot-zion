#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

log() {
    local type="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %I:%M:%S %p')

    case "$type" in
    success)
        echo -e "\033[90m[$timestamp]\033[0m \033[32m[SUCCESS] $message\033[0m"
        ;;
    warning)
        echo -e "\033[90m[$timestamp]\033[0m \033[33m[WARNING] $message\033[0m"
        ;;
    error)
        echo -e "\033[90m[$timestamp]\033[0m \033[31m[ERROR] $message\033[0m"
        ;;
    info)
        echo -e "\033[90m[$timestamp]\033[0m \033[34m[INFO] $message\033[0m"
        ;;
    *)
        echo -e "\033[90m[$timestamp]\033[0m [UNKNOWN] $message"
        ;;
    esac
}

log_success() {
    log success "$1"
}

log_warning() {
    log warning "$1"
}

log_error() {
    log error "$1"
}

log_info() {
    log info "$1"
}
