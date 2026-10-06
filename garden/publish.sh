#!/bin/bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${1-}" == "local" ]]; then
  shift
  exec garden --root "$SCRIPT_DIR" build "$@"
fi

if [[ $# -eq 0 ]]; then
  exec garden --root "$SCRIPT_DIR" deploy
fi

exec garden --root "$SCRIPT_DIR" "$@"