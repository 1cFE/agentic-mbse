#!/bin/bash
# Get metadata for project documents
echo "Date: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "Branch: $(git branch --show-current 2>/dev/null || echo 'N/A')"
echo "User: $(git config --get user.name 2>/dev/null || echo 'N/A')"
echo "Commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')"
