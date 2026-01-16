#!/usr/bin/env python3
"""
Test script to preview tag migration without modifying files.
Shows what WOULD happen to your tags.
"""

import os
import sys
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, COMM, TCON, TLAB

# Tag mapping (old → new)
TAG_MAPPING = {
    # Mood mappings (old → new TAG1/Moods that will go to COMMENT)
    'mazn': 'Nasty',
    'maz': 'Nasty',
    'slomz': 'Dark',
    'kopon': 'Upper',
    'shaip': 'Battle',
    'schizo': 'Schizo',
    'kruto': 'Raw',
    'derp': 'Trippy',
    'cool': 'Beautiful',
    'space': 'Cosmic',

    # TAG2 mappings (descriptors that will go to COMMENT)
    'oldek': 'Oldek',
    'proper': 'Proper',
    'slow': 'Slow',
    'tools': 'Tool',
    'vocal': 'Vocal',

    # Situation mappings (old → new TIME that will go to LABEL)
    'After': 'After',
    'warmup': 'Warmup',
    'peaok': 'Peak',
    'intro': 'Intro',
    'outro': 'Outro',
    'filler': 'Filler',
    'morning': 'Morning',
    'daytime': 'Daytime',
}

# Which tags are moods (go to COMMENT as TAG1)
MOODS = {'Nasty', 'Dark', 'Upper', 'Battle', 'Schizo', 'Raw', 'Trippy', 'Beautiful', 'Cosmic'}

# Which tags are TAG2 (go to COMMENT)
TAG2 = {'Oldek', 'Proper', 'Slow', 'Tool', 'Vocal'}

# Which tags are situations (go to LABEL as TIME)
SITUATIONS = {'After', 'Warmup', 'Peak', 'Intro', 'Outro', 'Filler', 'Morning', 'Daytime'}

def analyze_mp3(file_path):
    """Analyze MP3 file and show what would change."""
    try:
        audio = MP3(file_path, ID3=ID3)

        print(f"\n{'='*80}")
        print(f"FILE: {Path(file_path).name}")
        print(f"{'='*80}")

        # Get current COMMENT field
        current_comments = []
        if 'COMM::eng' in audio:
            current_comments = audio['COMM::eng'].text
            print(f"\nCURRENT COMMENT: {current_comments}")

        # Parse MixedInKey format if present
        mixedinkey_data = None
        remaining_tags = []

        for comment in current_comments:
            # Check for MixedInKey format: "5A - 5 - tags"
            parts = comment.split(' - ')
            if len(parts) == 3 and parts[0] and parts[1].isdigit():
                mixedinkey_data = f"{parts[0]} - {parts[1]}"  # "5A - 5"
                if parts[2]:  # Old tags after MixedInKey
                    remaining_tags.append(parts[2])
            else:
                remaining_tags.append(comment)

        if mixedinkey_data:
            print(f"  └─ MixedInKey data: {mixedinkey_data}")

        # Get current GENRE field
        current_genres = []
        if 'TCON' in audio:
            current_genres = [str(g) for g in audio['TCON'].text]
            print(f"\nCURRENT GENRE: {current_genres}")

        # Get current LABEL field (stored as TPUB in ID3)
        current_label = []
        if 'TPUB' in audio:
            current_label = [str(l) for l in audio['TPUB'].text]
            print(f"\nCURRENT LABEL: {current_label}")

        # Process old tags from both COMMENT and GENRE
        all_old_tags = []
        for tags in remaining_tags:
            all_old_tags.extend([t.strip() for t in tags.split(',') if t.strip()])
        for genre in current_genres:
            all_old_tags.extend([t.strip() for t in genre.split(',') if t.strip()])
        for label in current_label:
            all_old_tags.extend([t.strip() for t in label.split(',') if t.strip()])

        print(f"\nOLD TAGS FOUND: {all_old_tags}")

        # Map old tags to new
        new_moods = []
        new_tag2 = []
        new_situations = []
        new_genres = []
        unmapped = []

        for old_tag in all_old_tags:
            new_tag = TAG_MAPPING.get(old_tag)
            if new_tag:
                if new_tag in MOODS:
                    new_moods.append(new_tag)
                elif new_tag in TAG2:
                    new_tag2.append(new_tag)
                elif new_tag in SITUATIONS:
                    new_situations.append(new_tag)
                print(f"  ✓ '{old_tag}' → '{new_tag}'")
            else:
                # Check if it's already a valid genre/mood/situation
                if old_tag in {'Ambient', 'Acid', 'Breaks', 'Classic', 'Deep', 'Drum & Bass',
                              'Dub', 'Electro', 'Funky', 'House', 'Jackin', 'Jazzy',
                              'Minimal', 'Progressive', 'Techouse', 'Techno', 'Tribal'}:
                    new_genres.append(old_tag)
                    print(f"  ✓ '{old_tag}' → GENRE (already valid)")
                elif old_tag in MOODS:
                    new_moods.append(old_tag)
                    print(f"  ✓ '{old_tag}' → TAG1/Mood (already valid)")
                elif old_tag in TAG2:
                    new_tag2.append(old_tag)
                    print(f"  ✓ '{old_tag}' → TAG2 (already valid)")
                elif old_tag in SITUATIONS:
                    new_situations.append(old_tag)
                    print(f"  ✓ '{old_tag}' → TIME/Situation (already valid)")
                else:
                    unmapped.append(old_tag)
                    print(f"  ⚠ '{old_tag}' → NO MAPPING (will be kept as-is)")

        # Show what the NEW tags would be
        print(f"\n{'─'*80}")
        print("AFTER MIGRATION:")
        print(f"{'─'*80}")

        # New COMMENT field
        new_comment_parts = []
        if mixedinkey_data:
            new_comment_parts.append(mixedinkey_data)

        # Add moods and TAG2
        mood_tag2_combined = new_moods + new_tag2
        if mood_tag2_combined:
            if mixedinkey_data:
                new_comment_parts.append(', '.join(mood_tag2_combined))
            else:
                new_comment_parts.append(', '.join(mood_tag2_combined))

        new_comment = ' - '.join(new_comment_parts) if new_comment_parts else ''
        print(f"NEW COMMENT: {new_comment}")

        # New GENRE field
        if new_genres:
            print(f"NEW GENRE: {new_genres}")
        else:
            print(f"NEW GENRE: (unchanged or empty)")

        # New LABEL field (first situation only)
        if new_situations:
            print(f"NEW LABEL: {new_situations[0]}")  # Only first situation
            if len(new_situations) > 1:
                print(f"  ⚠ Multiple situations found, only using first: {new_situations}")
        else:
            print(f"NEW LABEL: (unchanged or empty)")

        if unmapped:
            print(f"\n⚠ UNMAPPED TAGS (need manual review): {unmapped}")

        return True

    except Exception as e:
        print(f"✗ ERROR: {file_path}: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_migration.py <file1> [file2] [file3] ...")
        print("\nExample:")
        print("  python test_migration.py ~/Music/test1.mp3 ~/Music/test2.mp3")
        print("\nThis script shows what WOULD happen without modifying files.")
        sys.exit(1)

    files = sys.argv[1:]

    print(f"\n{'='*80}")
    print(f"TAG MIGRATION TEST - DRY RUN")
    print(f"{'='*80}")
    print(f"Testing {len(files)} file(s)...")

    success_count = 0
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"\n✗ File not found: {file_path}")
            continue

        if file_path.lower().endswith('.mp3'):
            if analyze_mp3(file_path):
                success_count += 1
        else:
            print(f"\n✗ Unsupported format: {file_path}")

    print(f"\n{'='*80}")
    print(f"SUMMARY: Analyzed {success_count}/{len(files)} files successfully")
    print(f"{'='*80}")
    print("\nNOTE: This was a DRY RUN - no files were modified!")
    print("Review the output above to verify the migration looks correct.")

if __name__ == '__main__':
    main()
