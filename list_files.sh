#!/bin/bash

# Directory to scan
FRONTEND_DIR="./frontend"

# Check if directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
  echo "Error: $FRONTEND_DIR does not exist."
  exit 1
fi

echo "Listing contents of files in $FRONTEND_DIR and $FRONTEND_DIR/src:"

# Loop through all files in frontend and src
for file in "$FRONTEND_DIR"/* "$FRONTEND_DIR"/src/*; do
  if [ -f "$file" ]; then
    echo "=== File: $(basename "$file") ==="
    cat "$file"
    echo "=================="
  fi
done