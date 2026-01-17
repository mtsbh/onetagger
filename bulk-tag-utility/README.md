# Bulk Tag Utility - Enhanced Edition

**Like Bulk Rename Utility, but for music tags!**

A professional GUI tool for batch editing audio file tags with checkbox-based operations. Perfect for quickly cleaning up and organizing your music library.

## Features

### ⚡ 7 Powerful Tag Operations

1. **Replace Text** - Find and replace with regex support
   - Simple text find/replace
   - Regex pattern matching
   - Case sensitive/insensitive

2. **Trim Whitespace** - Clean up messy tags
   - Remove leading/trailing spaces
   - Apply to single field or all fields

3. **Copy Field** - Duplicate or append tags
   - Copy one tag to another
   - Append mode to combine fields

4. **Change Case** - Standardize text formatting
   - Title Case, UPPERCASE, lowercase, Sentence case

5. **Add Prefix/Suffix** - Add text around existing content
   - Add text before, after, or both

6. **Remove Text** - Delete specific words/patterns

7. **Split Field** - Separate combined fields (NEW!)
   - Split "Artist - Title" into separate tags
   - Custom separators (" - ", "/", etc.)

### 🎵 Full Audio Playback

- Built-in audio player with volume control
- Play/pause/stop controls
- Next/previous track navigation
- Double-click to play files
- Shows track duration

### 💾 Preset System

- Save your operation configurations
- Load presets instantly
- Perfect for recurring tasks
- Stored in `~/.bulktagutility/presets.json`

### ↶ Undo/Redo Support

- Undo up to 50 recent actions
- Full history tracking
- Restores original tags
- Keyboard shortcuts (Ctrl+Z / Ctrl+Y)

### 🏷️ Extended Tag Fields

Supports all common tag fields:
- Title, Artist, Album, Album Artist
- Composer, Conductor, Lyricist, Remixer
- Genre, Date/Year
- BPM, Key, Mood
- Label, ISRC, Copyright
- Comment

### 🎨 Enhanced Interface

- Clean 3-panel layout
- Menu bar with keyboard shortcuts
- Folder browser
- Checkbox file selection
- Live preview before applying
- Scrollable operations panel

## Supported Formats

MP3, FLAC, M4A/MP4, OGG, OPUS, WAV, WMA, AAC

## Installation

### Quick Start

```bash
# Clone or download the files
cd bulk-tag-utility

# Install dependencies
pip install -r requirements.txt

# Run the application
python bulk_tag_utility.py
```

### Dependencies

- **mutagen** - Audio tag library (required)
- **pygame** - Audio playback (optional but recommended)

If pygame is not installed, the app will still work but audio playback will be disabled.

### Create Standalone Executable

#### Windows:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "BulkTagUtility" bulk_tag_utility.py
```

#### Linux/Mac:
```bash
./build_exe.sh
```

The executable will be in `dist/`

## How to Use

### Basic Workflow

1. **File → Open Folder** (or Ctrl+O) - Load your music files
2. **Select Files** - Click to toggle checkboxes (all selected by default)
3. **Enable Operations** - Check the operations you want to apply
4. **Configure** - Set parameters for each operation
5. **Preview Changes** - See what will happen before applying
6. **Apply to Selected** - Save changes to files

### Keyboard Shortcuts

- `Ctrl+O` - Open folder
- `Ctrl+A` - Select all files
- `Ctrl+Z` - Undo last action
- `Ctrl+Y` - Redo last action
- `Double-click` - Play audio file

## Usage Examples

### Example 1: Replace artist name globally

```
☑ Replace Text
   Field: artist
   Find: hals
   Replace: oldek
   ☐ Case sensitive
   ☐ Use Regex

Preview → Apply
```

### Example 2: Clean up all tags

```
☑ Trim Whitespace
   Field: ALL FIELDS
   ☑ Leading spaces
   ☑ Trailing spaces

☑ Change Case
   Field: title
   ⦿ Title Case

Preview → Apply
```

### Example 3: Split combined title

For files with titles like "Artist Name - Song Title":

```
☑ Split Field
   Source: title
   Separator:  -
   Left → Field: artist
   Right → Field: title

Preview → Apply
```

### Example 4: Use regex to remove text

```
☑ Replace Text
   Field: comment
   Find: \[.*?\]
   Replace:
   ☑ Use Regex

This removes text in brackets like [ID: 12345]

Preview → Apply
```

### Example 5: Copy and format tags

```
☑ Copy Field
   From: artist
   To: albumartist
   ☐ Append

☑ Add Prefix/Suffix
   Field: title
   Prefix:
   Suffix:  (Extended Mix)

Preview → Apply
```

## Preset Workflows

Save common operations as presets:

1. Configure your operations
2. **File → Save Preset**
3. Enter a name (e.g., "Clean Up Tags")
4. Later: **File → Load Preset** to instantly restore

**Suggested Presets:**

- **Clean & Title Case** - Trim + Title case for artist/title
- **Remove Brackets** - Regex to remove [text] and (text)
- **Format Classical** - Composer → artist, conductor → albumartist
- **DJ Tags** - Add BPM prefix, copy key to comment

## Operation Order

When multiple operations are enabled, they execute in this order:

1. Replace
2. Trim
3. Copy
4. Change Case
5. Add Prefix/Suffix
6. Remove
7. Split Field

This order is optimized for most common workflows.

## Advanced Tips

### Regex Patterns

Enable "Use Regex" in Replace operation for advanced patterns:

- `\d+` - Match numbers
- `\[.*?\]` - Match text in brackets
- `^\s+|\s+$` - Match whitespace
- `feat\..*$` - Match "feat. Artist" at end

### Safety Features

- Always preview before applying
- Undo available for last 50 actions
- Original tags preserved in memory
- Confirmation dialog before applying

### Performance

- Handles large folders efficiently
- Loads tags on demand
- Background file processing
- Minimal memory footprint

## Troubleshooting

### Audio playback not working?

```bash
pip install pygame
```

Then restart the application.

### Tags not saving?

- Check file permissions
- Ensure files aren't read-only
- Some formats have limited tag support

### Undo not available?

Undo only works for operations applied in the current session. Closing the app clears history.

## Configuration

Settings stored in:
- **Presets**: `~/.bulktagutility/presets.json`
- **History**: In-memory only (not persistent)

## Building from Source

```bash
git clone <repository>
cd bulk-tag-utility
pip install -r requirements.txt
python bulk_tag_utility.py
```

## Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)
- mutagen >= 1.47.0
- pygame >= 2.5.0 (optional)

## Roadmap

Completed features:
- ✅ Extended tag fields (BPM, Key, Mood, etc.)
- ✅ Regex support
- ✅ Split field operation
- ✅ Save/load presets
- ✅ Undo/redo functionality
- ✅ Full audio playback with volume control

Potential future additions:
- Batch file renaming based on tags
- Tag from filename
- Online metadata lookup
- Duplicate finder
- Tag statistics/analysis
- Plugin system

## License

Free and open source. Use and modify as you wish!

## Credits

- Inspired by **Bulk Rename Utility** - the ultimate file renaming tool
- Built with **Python** + **tkinter** + **mutagen** + **pygame**
- Tag management powered by **Mutagen library**

## Contributing

Suggestions and improvements welcome!

## Support

For issues or questions, please open an issue on the repository.

---

**Made for music lovers who appreciate clean, organized metadata!** 🎵
