@echo off
echo Building Bulk Tag Utility...
echo.

REM Install requirements
pip install -r requirements.txt
pip install pyinstaller

REM Build executable
pyinstaller --onefile --windowed --name "BulkTagUtility" bulk_tag_utility.py

echo.
echo Build complete! Executable is in dist/BulkTagUtility.exe
echo.
pause
