#!/bin/bash
# PostToolUse hook for ruff formatting
# Reads tool input from stdin and runs ruff on Python files

# Read JSON from stdin
input=$(cat)

# Extract file_path from tool_input using jq
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# Exit if no file path or not a Python file
if [ -z "$file_path" ] || [[ ! "$file_path" == *.py ]]; then
    exit 0
fi

# Check if file exists
if [ ! -f "$file_path" ]; then
    exit 0
fi

# Run ruff check and format
ruff check --fix "$file_path" 2>/dev/null
ruff format "$file_path" 2>/dev/null

exit 0
