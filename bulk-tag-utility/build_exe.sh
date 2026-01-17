#!/bin/bash
echo "Building Bulk Tag Utility..."
echo

# Install requirements
pip install -r requirements.txt
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name "BulkTagUtility" bulk_tag_utility.py

echo
echo "Build complete! Executable is in dist/BulkTagUtility"
echo
