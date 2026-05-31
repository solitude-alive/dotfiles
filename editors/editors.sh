#!/bin/bash
# Wrapper around editors.py: snapshot | check | apply. See README.md.
exec python3 "$(dirname "$0")/editors.py" "$@"
