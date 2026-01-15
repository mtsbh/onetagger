#!/usr/bin/env python3
"""
OneTagger Tag Migration Script
Migrates old personal tags to new standardized system
"""

import os
import sys
from pathlib import Path
from mutagen.id3 import ID3, COMM, TPUB, TCON
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
import re

# Tag mapping: old tags → new tags
TAG_MAPPING = {
    # TAG1 (Moods)
    r'\bmazn\b': 'Nasty',
    r'\bstirk\b': 'Nasty',
    r'\bslow\b': 'Dark',
    r'\bmzi\b': 'Dark',
    r'\bslomz\b': 'Dark',
    r'\batmosfera\b': 'Cosmic',
    r'\btrippy\b': 'Trippy',
    r'\botnesen\b': 'Trippy',
    r'\bekek\b': 'Battle',
    r'\bsopa\b': 'Battle',
    r'\bnacepin\b': 'Battle',
    r'\butifyl\b': 'Beautiful',
    r'\bplacha\b': 'Beautiful',
    r'\boldek\b': 'Oldek',
    r'\bhals\b': 'Oldek',
    r'\bextract\b': 'Proper',
    r'\bserioja\b': 'Proper',
    r'\blaso\b': 'Upper',
    r'\bkopon\b': 'Upper',
    r'\bbomb\b': 'Upper',
    r'\bschizo\b': 'Schizo',
    r'\belectric\b': 'Schizo',
    r'\bprod\b': 'Raw',
    r'\btreti\b': 'Raw',
    r'\bpodlojki\b': 'Filler',
    r'\bpachanga\b': 'Daytime',
}

# Situation tags to move from GENRE to LABEL
SITUATION_TAGS = [
    'After', 'Morning', 'Sustain', 'Intro', 'Warmup',
    'Peak', 'Filler', 'Outro', 'Daytime', 'Tool'
]


def migrate_mp3(file_path, dry_run=True):
    """Migrate tags in MP3 file"""
    try:
        audio = ID3(file_path)
        changed = False

        # Get COMMENT field (COMM frame)
        comment_frames = audio.getall('COMM')
        if comment_frames:
            for frame in comment_frames:
                old_comment = frame.text[0]
                new_comment = old_comment

                # Apply tag mapping
                for old_pattern, new_tag in TAG_MAPPING.items():
                    new_comment = re.sub(old_pattern, new_tag, new_comment, flags=re.IGNORECASE)

                if new_comment != old_comment:
                    print(f"  COMMENT: '{old_comment}' → '{new_comment}'")
                    if not dry_run:
                        frame.text[0] = new_comment
                    changed = True

        # Move situation tags from GENRE (TCON) to LABEL (TPUB)
        if 'TCON' in audio:
            genre = str(audio['TCON'])
            if genre in SITUATION_TAGS:
                print(f"  Moving '{genre}' from GENRE → LABEL")
                if not dry_run:
                    audio['TPUB'] = TPUB(encoding=3, text=genre)
                    del audio['TCON']
                changed = True

        if changed and not dry_run:
            audio.save()

        return changed

    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def migrate_flac(file_path, dry_run=True):
    """Migrate tags in FLAC file"""
    try:
        audio = FLAC(file_path)
        changed = False

        # COMMENT field
        if 'COMMENT' in audio:
            old_comment = audio['COMMENT'][0]
            new_comment = old_comment

            for old_pattern, new_tag in TAG_MAPPING.items():
                new_comment = re.sub(old_pattern, new_tag, new_comment, flags=re.IGNORECASE)

            if new_comment != old_comment:
                print(f"  COMMENT: '{old_comment}' → '{new_comment}'")
                if not dry_run:
                    audio['COMMENT'] = new_comment
                changed = True

        # Move situation tags from GENRE to PUBLISHER (LABEL)
        if 'GENRE' in audio:
            genre = audio['GENRE'][0]
            if genre in SITUATION_TAGS:
                print(f"  Moving '{genre}' from GENRE → PUBLISHER")
                if not dry_run:
                    audio['PUBLISHER'] = genre
                    del audio['GENRE']
                changed = True

        if changed and not dry_run:
            audio.save()

        return changed

    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def migrate_m4a(file_path, dry_run=True):
    """Migrate tags in M4A file"""
    try:
        audio = MP4(file_path)
        changed = False

        # COMMENT field (©cmt)
        if '©cmt' in audio:
            old_comment = audio['©cmt'][0]
            new_comment = old_comment

            for old_pattern, new_tag in TAG_MAPPING.items():
                new_comment = re.sub(old_pattern, new_tag, new_comment, flags=re.IGNORECASE)

            if new_comment != old_comment:
                print(f"  COMMENT: '{old_comment}' → '{new_comment}'")
                if not dry_run:
                    audio['©cmt'] = [new_comment]
                changed = True

        # Move situation tags from GENRE to com.apple.iTunes:LABEL
        if '©gen' in audio:
            genre = audio['©gen'][0]
            if genre in SITUATION_TAGS:
                print(f"  Moving '{genre}' from GENRE → LABEL")
                if not dry_run:
                    audio['com.apple.iTunes:LABEL'] = [genre]
                    del audio['©gen']
                changed = True

        if changed and not dry_run:
            audio.save()

        return changed

    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def migrate_file(file_path, dry_run=True):
    """Migrate tags based on file type"""
    ext = file_path.suffix.lower()

    if ext == '.mp3':
        return migrate_mp3(file_path, dry_run)
    elif ext == '.flac':
        return migrate_flac(file_path, dry_run)
    elif ext in ['.m4a', '.mp4']:
        return migrate_m4a(file_path, dry_run)
    else:
        return False


def scan_directory(directory, dry_run=True):
    """Scan directory and migrate all audio files"""
    directory = Path(directory)

    if not directory.exists():
        print(f"ERROR: Directory not found: {directory}")
        return

    print(f"{'DRY RUN - ' if dry_run else ''}Scanning: {directory}\n")

    total_files = 0
    changed_files = 0

    for ext in ['.mp3', '.flac', '.m4a', '.mp4']:
        for file_path in directory.rglob(f'*{ext}'):
            total_files += 1
            print(f"[{total_files}] {file_path.name}")

            if migrate_file(file_path, dry_run):
                changed_files += 1

    print(f"\n{'DRY RUN - ' if dry_run else ''}Summary:")
    print(f"  Total files scanned: {total_files}")
    print(f"  Files that need changes: {changed_files}")

    if dry_run:
        print("\nTo apply changes, run with --apply flag")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Migrate OneTagger tags')
    parser.add_argument('directory', help='Music directory to scan')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')

    args = parser.parse_args()

    scan_directory(args.directory, dry_run=not args.apply)
