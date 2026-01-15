# Tag Migration Guide

This migration converts your old personal tagging system to the new standardized system.

## Migration Mapping

### Old Tags → New Moods (TAG1)
- `mazn, stirk` → **Nasty**
- `slow, mzi, slomz` → **Dark**
- `atmosfera` → **Cosmic**
- `trippy, otnesen` → **Trippy**
- `ekek, sopa, nacepin` → **Battle**
- `utifyl, placha` → **Beautiful**
- `oldek, hals` → **Oldek**
- `extract, serioja` → **Proper**
- `laso, kopon, bomb` → **Upper**
- `schizo, electric` → **Schizo**
- `prod, treti` → **Raw**
- `podlojki` → **Filler**
- `pachanga` → **Daytime**

### Field Changes
- Situation tags (After, Morning, Intro, Peak, etc.) → Move from GENRE to LABEL
- COMMENT field preserves MixedInKey format: `9A - 5 - tags`

## Method 1: Mp3tag (Windows - Recommended)

1. **Import action group:**
   ```
   Tools → Actions → Import → Select "mp3tag-actions.mta"
   ```

2. **Load your music:**
   - File → Change Directory → Select your music folder

3. **Select all tracks:**
   - Ctrl+A

4. **Run migration:**
   - Right-click → Actions → "Migrate to New Tag System"

5. **Save:**
   - Ctrl+S

**Backup first!** Mp3tag has undo, but it's safer.

## Method 2: Python Script (Cross-platform)

### Prerequisites:
```bash
pip install mutagen
```

### Dry-run (preview changes):
```bash
python migrate_tags.py /path/to/your/music
```

### Apply changes:
```bash
python migrate_tags.py /path/to/your/music --apply
```

## Example Transformations

### Before:
```
GENRE:   Techno, After
COMMENT: 9A - 5 - mazn
```

### After:
```
GENRE:   Techno
LABEL:   After
COMMENT: 9A - 5 - Nasty
```

## Verify After Migration

In Rekordbox, check that:
- [ ] Old tag names are gone
- [ ] New mood names appear in COMMENT
- [ ] Situation tags appear in LABEL field
- [ ] MixedInKey format preserved (9A - 5)
- [ ] No data loss

## Rollback

**Mp3tag:** Ctrl+Z (undo)

**Python script:** Restore from backup

Always test on a small batch first!
