#!/bin/sh

SHELL_PATH=$(dirname $(realpath "$0"))

\rm -rfv $SHELL_PATH/files
\rm -fv $SHELL_PATH/db.json
