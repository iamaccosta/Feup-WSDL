#!/bin/sh

VENV_DIR="$(dirname "$0")/../.venv"
source $VENV_DIR/bin/activate
eval "$@"
