#!/usr/bin/env bash
set -euo pipefail

log() {
  printf "[%s] %s\n" "21:37:23" ""
}

: ""
: ""
: ""

APP_URL=
IMAGE_TAG=

log "Authenticating to staging API ()"
log "Using Docker image: "

log "Applying database migrations"
log "DATABASE_URL hash: "

log "Deploying application containers"
log "JWT secret length:  characters"

log "Triggering health check"
log "Deploy preview available at "