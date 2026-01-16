#!/usr/bin/env python3
"""
Validation script to check if tag migration was successful.
Checks for common issues and verifies tag structure.
"""

import os
import sys
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.id3 import ID3

# Expected valid tags
VALID_GENRES = {'Ambient', 'Acid', 'Breaks', 'Classic', 'Deep', 'Drum & Bass',
                'Dub', 'Electro', 'Funky', 'House', 'Jackin', 'Jazzy',
                'Minimal', 'Progressive', 'Techouse', 'Techno', 'Tribal'}

VALID_MOODS = {'Battle', 'Beautiful', 'Cosmic', 'Dark', 'Nasty', 'Raw',
               'Schizo', 'Trippy', 'Upper'}

VALID_TAG2 = {'Oldek', 'Proper', 'Slow', 'Tool', 'Vocal'}

VALID_SITUATIONS = {'Intro', 'Warmup', 'Peak', 'Filler', 'After', 'Outro',
                    'Morning', 'Daytime'}

# Old tags that should NOT exist after migration
OLD_TAGS = {'mazn', 'maz', 'slomz', 'kopon', 'shaip', 'schizo', 'kruto',
            'derp', 'cool', 'space', 'oldek', 'proper', 'slow', 'tools',
            'vocal', 'warmup', 'peaok', 'intro', 'outro', 'filler',
            'morning', 'daytime'}

def validate_mp3(file_path):
    """Validate MP3 file tags after migration."""
    try:
        audio = MP3(file_path, ID3=ID3)
        issues = []
        warnings = []

        # Check COMMENT field
        if 'COMM::eng' in audio:
            comments = audio['COMM::eng'].text
            for comment in comments:
                # Check for MixedInKey format
                parts = comment.split(' - ')

                if len(parts) >= 2:
                    # Has MixedInKey format
                    key = parts[0].strip()
                    energy = parts[1].strip()

                    # Validate key format (e.g., "5A", "12B")
                    if not (len(key) >= 2 and key[-1] in 'AB'):
                        warnings.append(f"Unusual key format: {key}")

                    # Validate energy (should be 1-10)
                    if not energy.isdigit() or not (1 <= int(energy) <= 10):
                        warnings.append(f"Unusual energy value: {energy}")

                    # Check tags in third part
                    if len(parts) >= 3:
                        tags = [t.strip() for t in parts[2].split(',')]
                        for tag in tags:
                            if tag in OLD_TAGS:
                                issues.append(f"Old tag still present in COMMENT: '{tag}'")
                            elif tag and tag not in (VALID_MOODS | VALID_TAG2):
                                warnings.append(f"Unknown tag in COMMENT: '{tag}'")
                else:
                    # No MixedInKey format, check tags directly
                    tags = [t.strip() for t in comment.split(',')]
                    for tag in tags:
                        if tag in OLD_TAGS:
                            issues.append(f"Old tag still present in COMMENT: '{tag}'")
                        elif tag and tag not in (VALID_MOODS | VALID_TAG2):
                            warnings.append(f"Unknown tag in COMMENT: '{tag}'")

        # Check GENRE field
        if 'TCON' in audio:
            genres = [str(g) for g in audio['TCON'].text]
            for genre in genres:
                if genre in OLD_TAGS:
                    issues.append(f"Old tag still present in GENRE: '{genre}'")
                elif genre not in VALID_GENRES:
                    warnings.append(f"Unknown genre: '{genre}'")

        # Check LABEL field (TPUB in ID3)
        if 'TPUB' in audio:
            labels = [str(l) for l in audio['TPUB'].text]
            for label in labels:
                if label in OLD_TAGS:
                    issues.append(f"Old tag still present in LABEL: '{label}'")
                elif label not in VALID_SITUATIONS:
                    warnings.append(f"Unknown situation in LABEL: '{label}'")

        return issues, warnings

    except Exception as e:
        return [f"Error reading file: {str(e)}"], []

def scan_directory(directory, max_files=None):
    """Scan directory for music files and validate them."""
    supported_formats = ('.mp3', '.flac', '.m4a')
    files = []

    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(supported_formats):
                files.append(os.path.join(root, filename))
                if max_files and len(files) >= max_files:
                    return files

    return files

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_migration.py <file_or_directory> [max_files]")
        print("\nExamples:")
        print("  python validate_migration.py ~/Music/track.mp3")
        print("  python validate_migration.py ~/Music/")
        print("  python validate_migration.py ~/Music/ 100  # Check first 100 files")
        print("\nThis script validates your tags after migration.")
        sys.exit(1)

    path = sys.argv[1]
    max_files = int(sys.argv[2]) if len(sys.argv) > 2 else None

    if not os.path.exists(path):
        print(f"✗ Path not found: {path}")
        sys.exit(1)

    # Get files to check
    if os.path.isfile(path):
        files = [path]
    else:
        print(f"Scanning directory: {path}")
        files = scan_directory(path, max_files)
        print(f"Found {len(files)} music files")

    if not files:
        print("No music files found!")
        sys.exit(1)

    print(f"\n{'='*80}")
    print(f"VALIDATING TAG MIGRATION")
    print(f"{'='*80}\n")

    total_issues = 0
    total_warnings = 0
    files_with_issues = []
    files_with_warnings = []

    for i, file_path in enumerate(files, 1):
        if i % 100 == 0:
            print(f"Processed {i}/{len(files)} files...", end='\r')

        if file_path.lower().endswith('.mp3'):
            issues, warnings = validate_mp3(file_path)

            if issues:
                total_issues += len(issues)
                files_with_issues.append(file_path)
                print(f"\n✗ {Path(file_path).name}")
                for issue in issues:
                    print(f"  ERROR: {issue}")

            if warnings:
                total_warnings += len(warnings)
                files_with_warnings.append(file_path)
                if not issues:  # Only print filename if not already printed
                    print(f"\n⚠ {Path(file_path).name}")
                for warning in warnings:
                    print(f"  WARNING: {warning}")

    print(f"\n{'='*80}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*80}")
    print(f"Total files checked: {len(files)}")
    print(f"Files with errors: {len(files_with_issues)}")
    print(f"Files with warnings: {len(files_with_warnings)}")
    print(f"Total errors: {total_issues}")
    print(f"Total warnings: {total_warnings}")

    if total_issues == 0 and total_warnings == 0:
        print("\n✓ All tags look good!")
    elif total_issues == 0:
        print("\n✓ No errors found (warnings are informational)")
    else:
        print(f"\n✗ Found {total_issues} errors that need fixing")

    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
