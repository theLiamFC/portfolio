#!/bin/bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -ge 2 && "$2" != -* ]]; then
	page_name="$1"
	page_type="$2"
	shift 2
	exec garden --root "$SCRIPT_DIR" plant "$page_name" --type "$page_type" "$@"
fi

exec garden --root "$SCRIPT_DIR" plant "$@"