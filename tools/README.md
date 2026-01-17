# Quick Tag Editor Tools

GUI tools for batch editing music tags - like **Bulk Rename Utility** but for music tags!

## 🎯 Quick Tag Actions (Recommended - Super Easy!)

The simplest tool - just tick boxes and click Apply!

### Features:
- ✅ Pre-configured actions for your tag migrations
- ✅ Replace old tags with new ones (mazn → Nasty, etc.)
- ✅ Move tags between fields (After from GENRE → LABEL)
- ✅ Clean/trim spaces and duplicates
- ✅ Preserves MixedInKey format ("5A - 5 - tags")
- ✅ No regex needed!

### Usage:

```bash
python quick_tag_actions.py
```

**Steps:**
1. Click "Add Files" or "Add Folder" to select music
2. Tick the checkboxes for actions you want:
   - Tag replacements (mazn → Nasty)
   - Move tags (After: GENRE → LABEL)
   - Clean operations (trim spaces, remove duplicates)
3. Click "Apply Selected Actions"
4. Done!

### Example Use Cases:

**Quick migration of old tags:**
1. Add your music folder
2. Tick all the tag replacements (mazn → Nasty, slomz → Dark, etc.)
3. Tick all the move operations (After, Warmup, Peak to LABEL)
4. Click Apply
5. All done in one click!

**Clean up messy tags:**
1. Add files
2. Tick "Trim extra spaces"
3. Tick "Remove duplicate tags"
4. Apply

---

## 🛠️ Tag Editor GUI (Advanced)

More flexible tool for custom operations.

### Features:
- 🔍 Find & Replace (with case sensitivity options)
- 📦 Move tags between fields
- 🧹 Clean/trim operations
- 👁️ Preview changes before applying
- 📋 Custom operations

### Usage:

```bash
python tag_editor_gui.py
```

**Steps:**
1. Add files/folder
2. Choose operation type (tabs at top):
   - **Find & Replace**: Replace text in tags
   - **Move Tags**: Move specific tags between fields
   - **Presets**: Quick common operations
   - **Clean/Trim**: Clean up tags
3. Configure the operation
4. Click "Preview Changes" to see what will happen
5. Review the preview table
6. Click "Apply Changes" to save

### Example Operations:

**Find & Replace:**
- Field: COMMENT
- Find: `hals`
- Replace with: `oldek`
- ✓ Case sensitive
- Result: All occurrences of "hals" → "oldek"

**Move Tags:**
- Find tag: `After`
- In field: GENRE
- Move to field: LABEL
- ✓ Remove from source
- Result: "After" moves from GENRE to LABEL

---

## 📋 Requirements

```bash
pip install mutagen
```

That's it! Tkinter comes with Python.

---

## 🎨 How It Works

Both tools:
- Read MP3 ID3 tags using mutagen
- Support fields: COMMENT, GENRE, LABEL
- Preserve MixedInKey format in COMMENT ("5A - 5 - tags")
- Work with comma-separated tags
- Modify files in-place (make backups!)

### Field Mapping:
- **COMMENT** = ID3 COMM::eng (stores moods + TAG2)
- **GENRE** = ID3 TCON (stores genres)
- **LABEL** = ID3 TPUB (stores situations/time)

---

## ⚠️ Safety Tips

1. **Always backup first!** These tools modify your music files.
2. **Test on a few files** before batch processing thousands
3. Use the preview feature in Tag Editor GUI
4. Keep the migration validation scripts handy

---

## 🆚 Which Tool Should I Use?

**Use Quick Tag Actions if:**
- You want the easiest experience
- You're migrating your old tag system
- You want preset operations
- You don't need custom find/replace

**Use Tag Editor GUI if:**
- You need custom find/replace operations
- You want to preview before applying
- You need more control
- You want to do one-off operations

---

## 💡 Tips

**Batch Processing:**
1. Add entire music library
2. Select all relevant operations
3. Apply once - done!

**Iterative Approach:**
1. Process 10-20 files first
2. Check results in OneTagger/Rekordbox
3. If good, process the rest

**Undo:**
- These tools don't have undo
- Use version control or backups
- Or use Mp3tag which has undo (Ctrl+Z)

---

## 🔄 Workflow Comparison

### Traditional way (Mp3tag):
1. Open Mp3tag
2. Import action file
3. Select files
4. Run action
5. Repeat for each operation

### Quick Tag Actions:
1. Open tool
2. Add files
3. Tick all operations
4. Click Apply
5. Done!

Much faster for multiple operations!

---

## 🚀 Future Ideas

Want to add:
- Support for FLAC/M4A
- Regex patterns (advanced users)
- Batch rename files based on tags
- Export/import custom presets
- History/undo
- Tag templates

Let me know if you want any of these!
