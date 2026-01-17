# Bulk Tag Utility

**Like Bulk Rename Utility, but for music tags!**

A simple GUI tool for batch editing audio file tags with checkbox-based operations. Perfect for quickly cleaning up and organizing your music library.

## Features

✅ **6 Tag Operations:**
- **Replace Text** - Find and replace text in any tag field (case sensitive/insensitive)
- **Trim Whitespace** - Remove leading/trailing spaces from tags
- **Copy Field** - Copy or append one tag field to another
- **Change Case** - Convert to UPPERCASE, lowercase, or Title Case
- **Add Prefix/Suffix** - Add text before or after tag content
- **Remove Text** - Remove specific text from tags

✅ **User-Friendly Interface:**
- Folder browser for easy navigation
- File list with checkbox selection
- Live preview before applying changes
- Audio player controls (basic)

✅ **Supported Formats:**
- MP3, FLAC, M4A/MP4, OGG, OPUS, WAV, WMA

## Installation

### Option 1: Run from Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python bulk_tag_utility.py
```

### Option 2: Create Executable (.exe)

```bash
# Install PyInstaller
pip install pyinstaller

# Create standalone .exe
pyinstaller --onefile --windowed --name "BulkTagUtility" bulk_tag_utility.py
```

The executable will be in `dist/BulkTagUtility.exe`

## How to Use

1. **Select Folder** - Click "Select Folder" to load your music files
2. **Select Files** - Files are selected by default, click to toggle checkboxes
3. **Enable Operations** - Check the operations you want to apply
4. **Configure** - Set parameters for each operation (find text, field names, etc.)
5. **Preview** - Click "Preview Changes" to see what will happen
6. **Apply** - Click "Apply to Selected" to save changes

## Examples

### Example 1: Replace artist name across albums
- Enable **Replace Text**
- Field: `artist`
- Find: `hals`
- Replace: `oldek`
- Preview → Apply

### Example 2: Clean up messy tags
- Enable **Trim Whitespace** → Field: `ALL FIELDS`
- Enable **Change Case** → Field: `title` → Mode: `Title Case`
- Preview → Apply

### Example 3: Copy artist to comment field
- Enable **Copy Field**
- From: `artist`
- To: `comment`
- Check "Append" to add instead of replace
- Preview → Apply

### Example 4: Add prefix to all titles
- Enable **Add Prefix/Suffix**
- Field: `title`
- Prefix: `[2024] `
- Preview → Apply

## Supported Tag Fields

- Title
- Artist
- Album
- Album Artist
- Genre
- Date/Year
- Comment

## Tips

- Use **Preview** before applying to avoid mistakes
- Operations are applied in order: Replace → Trim → Copy → Case → Add → Remove
- You can enable multiple operations at once
- The preview shows changes for the first selected file

## Creating a Desktop Icon

After creating the .exe:

1. Right-click the .exe → Send to → Desktop (create shortcut)
2. Right-click shortcut → Properties → Change Icon
3. You can use any .ico file or create one online

## Requirements

- Python 3.7+
- mutagen library (for tag reading/writing)

## Future Features

- Full audio playback with seek/volume
- Regex support for advanced find/replace
- Split/combine tag fields
- Batch rename files based on tags
- Undo last operation
- Save/load operation presets
- More tag fields (BPM, Key, Mood, etc.)

## License

Free to use and modify!

## Credits

Inspired by Bulk Rename Utility - the ultimate file renaming tool.
