#!/usr/bin/env python3
"""
Bulk Tag Utility - Enhanced Version
Like Bulk Rename Utility but for music tags
A professional GUI tool for batch editing audio file tags

Features:
- Extended tag support (BPM, Key, Mood, Energy, etc.)
- Regex support for advanced pattern matching
- Split/combine field operations
- Save/load operation presets
- Undo functionality with history
- Full audio playback with seek/volume controls
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from typing import List, Dict, Optional, Callable, Any
import os
import json
import re
import copy
from datetime import datetime

# Import tag library
try:
    import mutagen
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, COMM, TDRC, TCON, TPE2, TBPM, TKEY, TMOO
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
except ImportError:
    print("Installing mutagen...")
    import subprocess
    subprocess.check_call(["pip", "install", "mutagen"])
    import mutagen
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, COMM, TDRC, TCON, TPE2, TBPM, TKEY, TMOO
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4

# Try to import pygame for audio playback
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("pygame not available - audio playback disabled")
    print("Install with: pip install pygame")


# Extended tag field list
TAG_FIELDS = [
    'title', 'artist', 'album', 'albumartist', 'composer', 'conductor',
    'genre', 'date', 'comment', 'bpm', 'key', 'mood',
    'lyricist', 'remixer', 'label', 'isrc', 'copyright'
]


class AudioFile:
    """Represents an audio file with extended tag information"""

    def __init__(self, path: Path):
        self.path = path
        self.filename = path.name
        self.selected = True
        self.tags = {}
        self.original_tags = {}
        self.modified = False
        self.duration = 0
        self.load_tags()

    def load_tags(self):
        """Load extended tags from the audio file"""
        try:
            audio = mutagen.File(self.path, easy=True)
            if audio is None:
                return

            # Get duration
            if hasattr(audio.info, 'length'):
                self.duration = audio.info.length

            # Load all supported tags
            self.tags = {}
            for field in TAG_FIELDS:
                self.tags[field] = self._get_tag(audio, field)

            # Store original for comparison and undo
            self.original_tags = self.tags.copy()

        except Exception as e:
            print(f"Error loading {self.path}: {e}")

    def _get_tag(self, audio, key: str) -> str:
        """Get tag value safely with extended field support"""
        val = audio.get(key, [''])
        if isinstance(val, list) and len(val) > 0:
            return str(val[0])
        return str(val) if val else ''

    def save_tags(self) -> bool:
        """Save modified tags back to file"""
        try:
            audio = mutagen.File(self.path, easy=True)
            if audio is None:
                return False

            for key, value in self.tags.items():
                if value:
                    audio[key] = value
                elif key in audio:
                    del audio[key]

            audio.save()
            self.original_tags = self.tags.copy()
            self.modified = False
            return True
        except Exception as e:
            print(f"Error saving {self.path}: {e}")
            return False

    def create_snapshot(self) -> Dict[str, str]:
        """Create a snapshot of current tags for undo"""
        return self.tags.copy()

    def restore_snapshot(self, snapshot: Dict[str, str]):
        """Restore tags from snapshot"""
        self.tags = snapshot.copy()

    def format_duration(self) -> str:
        """Format duration as MM:SS"""
        if self.duration:
            mins = int(self.duration // 60)
            secs = int(self.duration % 60)
            return f"{mins}:{secs:02d}"
        return "0:00"


class UndoManager:
    """Manages undo history for tag operations"""

    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.history: List[Dict[str, Any]] = []
        self.current_index = -1

    def record_action(self, action_name: str, files_snapshot: List[tuple]):
        """Record an action with snapshots of affected files

        Args:
            action_name: Description of the action
            files_snapshot: List of (AudioFile, tags_snapshot) tuples
        """
        # Remove any redo history
        self.history = self.history[:self.current_index + 1]

        # Add new action
        self.history.append({
            'name': action_name,
            'timestamp': datetime.now(),
            'snapshots': files_snapshot
        })

        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.current_index += 1

    def can_undo(self) -> bool:
        """Check if undo is available"""
        return self.current_index >= 0

    def can_redo(self) -> bool:
        """Check if redo is available"""
        return self.current_index < len(self.history) - 1

    def undo(self) -> Optional[Dict[str, Any]]:
        """Undo last action"""
        if not self.can_undo():
            return None

        action = self.history[self.current_index]
        self.current_index -= 1
        return action

    def redo(self) -> Optional[Dict[str, Any]]:
        """Redo previously undone action"""
        if not self.can_redo():
            return None

        self.current_index += 1
        action = self.history[self.current_index]
        return action

    def get_undo_description(self) -> str:
        """Get description of action that would be undone"""
        if self.can_undo():
            return self.history[self.current_index]['name']
        return ""

    def get_redo_description(self) -> str:
        """Get description of action that would be redone"""
        if self.can_redo():
            return self.history[self.current_index + 1]['name']
        return ""


class AudioPlayer:
    """Audio player with full playback controls"""

    def __init__(self):
        self.initialized = False
        self.playing = False
        self.current_file = None
        self.volume = 0.7
        self.position = 0

        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.initialized = True
            except Exception as e:
                print(f"Failed to initialize audio: {e}")

    def load(self, file_path: Path):
        """Load an audio file"""
        if not self.initialized:
            return False

        try:
            pygame.mixer.music.load(str(file_path))
            self.current_file = file_path
            pygame.mixer.music.set_volume(self.volume)
            return True
        except Exception as e:
            print(f"Error loading audio: {e}")
            return False

    def play(self):
        """Start playback"""
        if not self.initialized:
            return

        try:
            pygame.mixer.music.play()
            self.playing = True
        except Exception as e:
            print(f"Error playing: {e}")

    def pause(self):
        """Pause playback"""
        if not self.initialized:
            return

        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False
        else:
            pygame.mixer.music.unpause()
            self.playing = True

    def stop(self):
        """Stop playback"""
        if not self.initialized:
            return

        pygame.mixer.music.stop()
        self.playing = False

    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        if not self.initialized:
            return

        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)

    def is_playing(self) -> bool:
        """Check if currently playing"""
        if not self.initialized:
            return False

        return pygame.mixer.music.get_busy() and self.playing

    def seek(self, position: float):
        """Seek to position in seconds"""
        if not self.initialized:
            return

        try:
            pygame.mixer.music.set_pos(position)
        except Exception as e:
            # Not all formats support seeking
            print(f"Seek not supported: {e}")


class BulkTagUtility:
    """Enhanced main application window"""

    def __init__(self, root):
        self.root = root
        self.root.title("Bulk Tag Utility - Enhanced")
        self.root.geometry("1400x800")

        self.current_folder = None
        self.audio_files: List[AudioFile] = []
        self.undo_manager = UndoManager()
        self.player = AudioPlayer()
        self.current_playing_index = -1

        # Config directory for presets
        self.config_dir = Path.home() / '.bulktagutility'
        self.config_dir.mkdir(exist_ok=True)
        self.presets_file = self.config_dir / 'presets.json'

        self.setup_ui()
        self.setup_menu()
        self.update_undo_buttons()

    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Folder...", command=self.select_folder, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save Preset...", command=self.save_preset)
        file_menu.add_command(label="Load Preset...", command=self.load_preset)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        self.undo_menu_item = edit_menu.add_command(label="Undo", command=self.undo_last_action, accelerator="Ctrl+Z", state=tk.DISABLED)
        self.redo_menu_item = edit_menu.add_command(label="Redo", command=self.redo_last_action, accelerator="Ctrl+Y", state=tk.DISABLED)
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All Files", command=self.select_all_files, accelerator="Ctrl+A")
        edit_menu.add_command(label="Deselect All Files", command=self.deselect_all_files)

        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.select_folder())
        self.root.bind('<Control-z>', lambda e: self.undo_last_action())
        self.root.bind('<Control-y>', lambda e: self.redo_last_action())
        self.root.bind('<Control-a>', lambda e: self.select_all_files())

    def setup_ui(self):
        """Setup the enhanced UI layout"""

        # Main container with 3 columns
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: Folder Browser (20%)
        folder_frame = ttk.LabelFrame(main_frame, text="📁 Folder Browser", padding=5)
        folder_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 2))

        ttk.Button(folder_frame, text="Select Folder", command=self.select_folder).pack(fill=tk.X, pady=(0, 5))

        self.folder_label = ttk.Label(folder_frame, text="No folder selected", wraplength=180)
        self.folder_label.pack(fill=tk.X, pady=5)

        self.file_count_label = ttk.Label(folder_frame, text="Files: 0", font=("Arial", 9))
        self.file_count_label.pack(fill=tk.X, pady=5)

        # Preset management
        ttk.Separator(folder_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(folder_frame, text="Presets", font=("Arial", 9, "bold")).pack()
        ttk.Button(folder_frame, text="Save Preset", command=self.save_preset).pack(fill=tk.X, pady=2)
        ttk.Button(folder_frame, text="Load Preset", command=self.load_preset).pack(fill=tk.X, pady=2)

        # Undo/Redo buttons
        ttk.Separator(folder_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(folder_frame, text="History", font=("Arial", 9, "bold")).pack()
        self.undo_button = ttk.Button(folder_frame, text="↶ Undo", command=self.undo_last_action, state=tk.DISABLED)
        self.undo_button.pack(fill=tk.X, pady=2)
        self.redo_button = ttk.Button(folder_frame, text="↷ Redo", command=self.redo_last_action, state=tk.DISABLED)
        self.redo_button.pack(fill=tk.X, pady=2)

        # Middle: File List (45%)
        file_frame = ttk.LabelFrame(main_frame, text="📋 Files", padding=5)
        file_frame.grid(row=0, column=1, sticky="nsew", padx=2)

        file_controls = ttk.Frame(file_frame)
        file_controls.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(file_controls, text="Select All", command=self.select_all_files, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_controls, text="Deselect All", command=self.deselect_all_files, width=12).pack(side=tk.LEFT, padx=2)

        file_list_frame = ttk.Frame(file_frame)
        file_list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(file_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            file_list_frame,
            selectmode=tk.EXTENDED,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9)
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        self.file_listbox.bind('<Double-Button-1>', self.on_file_double_click)
        scrollbar.config(command=self.file_listbox.yview)

        # Right: Operations Panel (35%)
        ops_frame = ttk.LabelFrame(main_frame, text="⚙️ Tag Operations", padding=5)
        ops_frame.grid(row=0, column=2, sticky="nsew", padx=(2, 0))

        ops_canvas = tk.Canvas(ops_frame, highlightthickness=0)
        ops_scrollbar = ttk.Scrollbar(ops_frame, orient=tk.VERTICAL, command=ops_canvas.yview)
        self.ops_container = ttk.Frame(ops_canvas)

        self.ops_container.bind(
            "<Configure>",
            lambda e: ops_canvas.configure(scrollregion=ops_canvas.bbox("all"))
        )

        ops_canvas.create_window((0, 0), window=self.ops_container, anchor="nw")
        ops_canvas.configure(yscrollcommand=ops_scrollbar.set)

        ops_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ops_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.setup_operations()

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.columnconfigure(2, weight=2)
        main_frame.rowconfigure(0, weight=1)

        # Bottom: Player + Actions
        self.setup_bottom_panel()

    def setup_bottom_panel(self):
        """Setup bottom panel with player and actions"""
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        # Player section
        if PYGAME_AVAILABLE and self.player.initialized:
            player_frame = ttk.LabelFrame(bottom_frame, text="▶ Audio Player", padding=5)
            player_frame.pack(fill=tk.X, pady=(0, 5))

            self.player_label = ttk.Label(player_frame, text="No file loaded", font=("Arial", 9))
            self.player_label.pack()

            # Playback controls
            player_controls = ttk.Frame(player_frame)
            player_controls.pack(pady=5)

            ttk.Button(player_controls, text="◀◀", width=5, command=self.play_previous).pack(side=tk.LEFT, padx=2)
            self.play_button = ttk.Button(player_controls, text="▶", width=8, command=self.toggle_play)
            self.play_button.pack(side=tk.LEFT, padx=2)
            ttk.Button(player_controls, text="⏹", width=5, command=self.stop_playback).pack(side=tk.LEFT, padx=2)
            ttk.Button(player_controls, text="▶▶", width=5, command=self.play_next).pack(side=tk.LEFT, padx=2)

            # Volume control
            volume_frame = ttk.Frame(player_frame)
            volume_frame.pack(pady=2)

            ttk.Label(volume_frame, text="🔊").pack(side=tk.LEFT)
            self.volume_scale = ttk.Scale(
                volume_frame,
                from_=0,
                to=100,
                orient=tk.HORIZONTAL,
                command=self.on_volume_change,
                length=200
            )
            self.volume_scale.set(70)
            self.volume_scale.pack(side=tk.LEFT, padx=5)
            self.volume_label = ttk.Label(volume_frame, text="70%", width=4)
            self.volume_label.pack(side=tk.LEFT)

        # Preview section
        preview_frame = ttk.LabelFrame(bottom_frame, text="Preview Changes", padding=5)
        preview_frame.pack(fill=tk.X, pady=(0, 5))

        preview_scroll = ttk.Scrollbar(preview_frame)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.preview_text = tk.Text(
            preview_frame,
            height=4,
            font=("Consolas", 8),
            wrap=tk.WORD,
            yscrollcommand=preview_scroll.set
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        preview_scroll.config(command=self.preview_text.yview)

        # Action buttons
        action_frame = ttk.Frame(bottom_frame)
        action_frame.pack(fill=tk.X)

        ttk.Button(
            action_frame,
            text="Preview Changes",
            command=self.preview_changes
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Button(
            action_frame,
            text="Apply to Selected",
            command=self.apply_changes
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    def setup_operations(self):
        """Setup all operation panels with enhanced features"""

        # Operation 1: Replace Text (with Regex support)
        self.op_replace_var = tk.BooleanVar(value=False)
        replace_frame = self.create_operation_frame("Replace Text", self.op_replace_var)

        ttk.Label(replace_frame, text="Field:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.replace_field = ttk.Combobox(replace_frame, values=TAG_FIELDS, width=15, state='readonly')
        self.replace_field.set('title')
        self.replace_field.grid(row=0, column=1, sticky=tk.EW, pady=2)

        ttk.Label(replace_frame, text="Find:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.replace_find = ttk.Entry(replace_frame, width=18)
        self.replace_find.grid(row=1, column=1, sticky=tk.EW, pady=2)

        ttk.Label(replace_frame, text="Replace:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.replace_with = ttk.Entry(replace_frame, width=18)
        self.replace_with.grid(row=2, column=1, sticky=tk.EW, pady=2)

        self.replace_case_sensitive = tk.BooleanVar(value=False)
        self.replace_use_regex = tk.BooleanVar(value=False)

        ttk.Checkbutton(replace_frame, text="Case sensitive", variable=self.replace_case_sensitive).grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Checkbutton(replace_frame, text="Use Regex", variable=self.replace_use_regex).grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=2)

        replace_frame.columnconfigure(1, weight=1)

        # Operation 2: Trim
        self.op_trim_var = tk.BooleanVar(value=False)
        trim_frame = self.create_operation_frame("Trim Whitespace", self.op_trim_var)

        ttk.Label(trim_frame, text="Field:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.trim_field = ttk.Combobox(trim_frame, values=TAG_FIELDS + ['ALL FIELDS'], width=15, state='readonly')
        self.trim_field.set('ALL FIELDS')
        self.trim_field.grid(row=0, column=1, sticky=tk.EW, pady=2)

        self.trim_leading = tk.BooleanVar(value=True)
        self.trim_trailing = tk.BooleanVar(value=True)

        ttk.Checkbutton(trim_frame, text="Leading spaces", variable=self.trim_leading).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Checkbutton(trim_frame, text="Trailing spaces", variable=self.trim_trailing).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=2)

        trim_frame.columnconfigure(1, weight=1)

        # Operation 3: Copy Field
        self.op_copy_var = tk.BooleanVar(value=False)
        copy_frame = self.create_operation_frame("Copy Field", self.op_copy_var)

        ttk.Label(copy_frame, text="From:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.copy_from = ttk.Combobox(copy_frame, values=TAG_FIELDS, width=15, state='readonly')
        self.copy_from.set('artist')
        self.copy_from.grid(row=0, column=1, sticky=tk.EW, pady=2)

        ttk.Label(copy_frame, text="To:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.copy_to = ttk.Combobox(copy_frame, values=TAG_FIELDS, width=15, state='readonly')
        self.copy_to.set('comment')
        self.copy_to.grid(row=1, column=1, sticky=tk.EW, pady=2)

        self.copy_append = tk.BooleanVar(value=False)
        ttk.Checkbutton(copy_frame, text="Append (not replace)", variable=self.copy_append).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=2)

        copy_frame.columnconfigure(1, weight=1)

        # Operation 4: Change Case
        self.op_case_var = tk.BooleanVar(value=False)
        case_frame = self.create_operation_frame("Change Case", self.op_case_var)

        ttk.Label(case_frame, text="Field:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.case_field = ttk.Combobox(case_frame, values=TAG_FIELDS, width=15, state='readonly')
        self.case_field.set('title')
        self.case_field.grid(row=0, column=1, sticky=tk.EW, pady=2)

        self.case_mode = tk.StringVar(value='title')
        ttk.Radiobutton(case_frame, text="Title Case", variable=self.case_mode, value='title').grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Radiobutton(case_frame, text="UPPERCASE", variable=self.case_mode, value='upper').grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Radiobutton(case_frame, text="lowercase", variable=self.case_mode, value='lower').grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Radiobutton(case_frame, text="Sentence case", variable=self.case_mode, value='sentence').grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=2)

        case_frame.columnconfigure(1, weight=1)

        # Operation 5: Add Prefix/Suffix
        self.op_add_var = tk.BooleanVar(value=False)
        add_frame = self.create_operation_frame("Add Prefix/Suffix", self.op_add_var)

        ttk.Label(add_frame, text="Field:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.add_field = ttk.Combobox(add_frame, values=TAG_FIELDS, width=15, state='readonly')
        self.add_field.set('title')
        self.add_field.grid(row=0, column=1, sticky=tk.EW, pady=2)

        ttk.Label(add_frame, text="Prefix:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.add_prefix = ttk.Entry(add_frame, width=18)
        self.add_prefix.grid(row=1, column=1, sticky=tk.EW, pady=2)

        ttk.Label(add_frame, text="Suffix:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.add_suffix = ttk.Entry(add_frame, width=18)
        self.add_suffix.grid(row=2, column=1, sticky=tk.EW, pady=2)

        add_frame.columnconfigure(1, weight=1)

        # Operation 6: Remove Text
        self.op_remove_var = tk.BooleanVar(value=False)
        remove_frame = self.create_operation_frame("Remove Text", self.op_remove_var)

        ttk.Label(remove_frame, text="Field:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.remove_field = ttk.Combobox(remove_frame, values=TAG_FIELDS, width=15, state='readonly')
        self.remove_field.set('title')
        self.remove_field.grid(row=0, column=1, sticky=tk.EW, pady=2)

        ttk.Label(remove_frame, text="Remove:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.remove_text = ttk.Entry(remove_frame, width=18)
        self.remove_text.grid(row=1, column=1, sticky=tk.EW, pady=2)

        remove_frame.columnconfigure(1, weight=1)

        # Operation 7: Split Field (NEW)
        self.op_split_var = tk.BooleanVar(value=False)
        split_frame = self.create_operation_frame("Split Field", self.op_split_var)

        ttk.Label(split_frame, text="Source:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.split_source = ttk.Combobox(split_frame, values=TAG_FIELDS, width=15, state='readonly')
        self.split_source.set('title')
        self.split_source.grid(row=0, column=1, sticky=tk.EW, pady=2)

        ttk.Label(split_frame, text="Separator:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.split_separator = ttk.Entry(split_frame, width=18)
        self.split_separator.insert(0, ' - ')
        self.split_separator.grid(row=1, column=1, sticky=tk.EW, pady=2)

        ttk.Label(split_frame, text="Left → Field:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.split_left_field = ttk.Combobox(split_frame, values=TAG_FIELDS, width=15, state='readonly')
        self.split_left_field.set('artist')
        self.split_left_field.grid(row=2, column=1, sticky=tk.EW, pady=2)

        ttk.Label(split_frame, text="Right → Field:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.split_right_field = ttk.Combobox(split_frame, values=TAG_FIELDS, width=15, state='readonly')
        self.split_right_field.set('title')
        self.split_right_field.grid(row=3, column=1, sticky=tk.EW, pady=2)

        split_frame.columnconfigure(1, weight=1)

    def create_operation_frame(self, title: str, var: tk.BooleanVar) -> ttk.Frame:
        """Create a collapsible operation frame"""
        container = ttk.Frame(self.ops_container)
        container.pack(fill=tk.X, pady=5)

        header = ttk.Frame(container)
        header.pack(fill=tk.X)

        check = ttk.Checkbutton(header, text=title, variable=var)
        check.pack(side=tk.LEFT)

        content = ttk.Frame(container, padding=(20, 5, 5, 5))
        content.pack(fill=tk.X)

        return content

    def select_folder(self):
        """Open folder selection dialog"""
        folder = filedialog.askdirectory(title="Select Music Folder")
        if folder:
            self.current_folder = Path(folder)
            self.load_audio_files()

    def load_audio_files(self):
        """Load audio files from selected folder"""
        if not self.current_folder:
            return

        self.audio_files.clear()
        self.file_listbox.delete(0, tk.END)

        self.folder_label.config(text=str(self.current_folder))

        extensions = ['.mp3', '.flac', '.m4a', '.ogg', '.opus', '.wav', '.wma', '.aac']

        files_found = 0
        for ext in extensions:
            for file_path in self.current_folder.rglob(f'*{ext}'):
                try:
                    audio_file = AudioFile(file_path)
                    self.audio_files.append(audio_file)
                    files_found += 1
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")

        self.update_file_list()
        self.file_count_label.config(text=f"Files: {files_found}")

    def update_file_list(self):
        """Update the file listbox"""
        self.file_listbox.delete(0, tk.END)

        for audio_file in self.audio_files:
            check = "☑" if audio_file.selected else "☐"
            title = audio_file.tags.get('title', '')
            artist = audio_file.tags.get('artist', '')

            display = f"{check} {audio_file.filename}"
            if title or artist:
                display += f" - {artist} - {title}"

            self.file_listbox.insert(tk.END, display)

    def on_file_select(self, event):
        """Handle file selection in listbox"""
        selection = self.file_listbox.curselection()
        if selection:
            idx = selection[0]
            if idx < len(self.audio_files):
                self.audio_files[idx].selected = not self.audio_files[idx].selected
                self.update_file_list()
                self.file_listbox.selection_clear(0, tk.END)

    def on_file_double_click(self, event):
        """Handle double-click to play file"""
        selection = self.file_listbox.curselection()
        if selection and PYGAME_AVAILABLE:
            idx = selection[0]
            if idx < len(self.audio_files):
                self.play_file(idx)

    def select_all_files(self):
        """Select all files"""
        for audio_file in self.audio_files:
            audio_file.selected = True
        self.update_file_list()

    def deselect_all_files(self):
        """Deselect all files"""
        for audio_file in self.audio_files:
            audio_file.selected = False
        self.update_file_list()

    def get_selected_files(self) -> List[AudioFile]:
        """Get list of selected audio files"""
        return [f for f in self.audio_files if f.selected]

    def preview_changes(self):
        """Preview what changes will be made"""
        self.preview_text.delete(1.0, tk.END)

        selected = self.get_selected_files()
        if not selected:
            self.preview_text.insert(1.0, "No files selected!")
            return

        test_file = selected[0]
        original_tags = test_file.tags.copy()

        self.apply_operations_to_file(test_file, preview=True)

        preview_lines = [f"Preview for: {test_file.filename}\n"]
        preview_lines.append(f"Selected files: {len(selected)}\n\n")

        for field, new_value in test_file.tags.items():
            old_value = original_tags.get(field, '')
            if old_value != new_value:
                preview_lines.append(f"{field.upper()}:\n")
                preview_lines.append(f"  Before: '{old_value}'\n")
                preview_lines.append(f"  After:  '{new_value}'\n\n")

        test_file.tags = original_tags

        if len(preview_lines) == 3:
            preview_lines.append("No changes detected!")

        self.preview_text.insert(1.0, ''.join(preview_lines))

    def apply_changes(self):
        """Apply operations to selected files with undo support"""
        selected = self.get_selected_files()
        if not selected:
            messagebox.showwarning("No Selection", "Please select files to modify!")
            return

        count = len(selected)
        if not messagebox.askyesno("Confirm", f"Apply changes to {count} file(s)?"):
            return

        # Create snapshots for undo
        snapshots = [(f, f.create_snapshot()) for f in selected]

        # Apply and save
        success_count = 0
        for audio_file in selected:
            self.apply_operations_to_file(audio_file, preview=False)
            if audio_file.save_tags():
                success_count += 1

        # Record for undo
        self.undo_manager.record_action(
            f"Applied operations to {success_count} file(s)",
            snapshots
        )
        self.update_undo_buttons()

        messagebox.showinfo("Complete", f"Successfully updated {success_count}/{count} files!")
        self.update_file_list()

    def apply_operations_to_file(self, audio_file: AudioFile, preview: bool = False):
        """Apply enabled operations to a file with enhanced features"""

        # Operation 1: Replace (with Regex support)
        if self.op_replace_var.get():
            field = self.replace_field.get()
            find = self.replace_find.get()
            replace = self.replace_with.get()
            case_sensitive = self.replace_case_sensitive.get()
            use_regex = self.replace_use_regex.get()

            if field in audio_file.tags and find:
                original = audio_file.tags[field]

                if use_regex:
                    # Regex mode
                    try:
                        flags = 0 if case_sensitive else re.IGNORECASE
                        audio_file.tags[field] = re.sub(find, replace, original, flags=flags)
                    except re.error as e:
                        print(f"Regex error: {e}")
                else:
                    # Normal replace
                    if case_sensitive:
                        audio_file.tags[field] = original.replace(find, replace)
                    else:
                        audio_file.tags[field] = re.sub(
                            re.escape(find), replace, original, flags=re.IGNORECASE
                        )

        # Operation 2: Trim
        if self.op_trim_var.get():
            field = self.trim_field.get()
            fields_to_trim = [field] if field != 'ALL FIELDS' else list(audio_file.tags.keys())

            for f in fields_to_trim:
                if f in audio_file.tags:
                    value = audio_file.tags[f]
                    if self.trim_leading.get():
                        value = value.lstrip()
                    if self.trim_trailing.get():
                        value = value.rstrip()
                    audio_file.tags[f] = value

        # Operation 3: Copy Field
        if self.op_copy_var.get():
            from_field = self.copy_from.get()
            to_field = self.copy_to.get()

            if from_field in audio_file.tags:
                source_value = audio_file.tags[from_field]
                if self.copy_append.get() and to_field in audio_file.tags:
                    audio_file.tags[to_field] += f" {source_value}"
                else:
                    audio_file.tags[to_field] = source_value

        # Operation 4: Change Case
        if self.op_case_var.get():
            field = self.case_field.get()
            mode = self.case_mode.get()

            if field in audio_file.tags:
                value = audio_file.tags[field]
                if mode == 'upper':
                    audio_file.tags[field] = value.upper()
                elif mode == 'lower':
                    audio_file.tags[field] = value.lower()
                elif mode == 'title':
                    audio_file.tags[field] = value.title()
                elif mode == 'sentence':
                    audio_file.tags[field] = value.capitalize()

        # Operation 5: Add Prefix/Suffix
        if self.op_add_var.get():
            field = self.add_field.get()
            prefix = self.add_prefix.get()
            suffix = self.add_suffix.get()

            if field in audio_file.tags:
                value = audio_file.tags[field]
                audio_file.tags[field] = f"{prefix}{value}{suffix}"

        # Operation 6: Remove Text
        if self.op_remove_var.get():
            field = self.remove_field.get()
            remove = self.remove_text.get()

            if field in audio_file.tags and remove:
                audio_file.tags[field] = audio_file.tags[field].replace(remove, '')

        # Operation 7: Split Field
        if self.op_split_var.get():
            source = self.split_source.get()
            separator = self.split_separator.get()
            left_field = self.split_left_field.get()
            right_field = self.split_right_field.get()

            if source in audio_file.tags and separator:
                value = audio_file.tags[source]
                parts = value.split(separator, 1)

                if len(parts) == 2:
                    audio_file.tags[left_field] = parts[0].strip()
                    audio_file.tags[right_field] = parts[1].strip()
                elif len(parts) == 1:
                    audio_file.tags[left_field] = parts[0].strip()

    # Undo/Redo functionality
    def undo_last_action(self):
        """Undo the last action"""
        action = self.undo_manager.undo()
        if not action:
            return

        # Restore snapshots
        for audio_file, snapshot in action['snapshots']:
            audio_file.restore_snapshot(snapshot)
            audio_file.save_tags()

        self.update_file_list()
        self.update_undo_buttons()
        messagebox.showinfo("Undo", f"Undone: {action['name']}")

    def redo_last_action(self):
        """Redo the last undone action"""
        action = self.undo_manager.redo()
        if not action:
            return

        # Re-apply the changes by undoing the undo
        # (snapshots contain the "before" state, so we need to re-run operations)
        messagebox.showinfo("Redo", "Redo functionality requires re-applying operations.\nUse Undo to go back.")
        self.update_undo_buttons()

    def update_undo_buttons(self):
        """Update undo/redo button states"""
        if self.undo_manager.can_undo():
            self.undo_button.config(state=tk.NORMAL)
            desc = self.undo_manager.get_undo_description()
            self.undo_button.config(text=f"↶ Undo: {desc[:20]}...")
        else:
            self.undo_button.config(state=tk.DISABLED, text="↶ Undo")

        if self.undo_manager.can_redo():
            self.redo_button.config(state=tk.NORMAL)
        else:
            self.redo_button.config(state=tk.DISABLED)

    # Preset management
    def save_preset(self):
        """Save current operation settings as a preset"""
        preset_name = tk.simpledialog.askstring("Save Preset", "Enter preset name:")
        if not preset_name:
            return

        preset = {
            'name': preset_name,
            'operations': {}
        }

        # Save all operation states
        if self.op_replace_var.get():
            preset['operations']['replace'] = {
                'field': self.replace_field.get(),
                'find': self.replace_find.get(),
                'with': self.replace_with.get(),
                'case_sensitive': self.replace_case_sensitive.get(),
                'use_regex': self.replace_use_regex.get()
            }

        if self.op_trim_var.get():
            preset['operations']['trim'] = {
                'field': self.trim_field.get(),
                'leading': self.trim_leading.get(),
                'trailing': self.trim_trailing.get()
            }

        if self.op_copy_var.get():
            preset['operations']['copy'] = {
                'from': self.copy_from.get(),
                'to': self.copy_to.get(),
                'append': self.copy_append.get()
            }

        if self.op_case_var.get():
            preset['operations']['case'] = {
                'field': self.case_field.get(),
                'mode': self.case_mode.get()
            }

        if self.op_add_var.get():
            preset['operations']['add'] = {
                'field': self.add_field.get(),
                'prefix': self.add_prefix.get(),
                'suffix': self.add_suffix.get()
            }

        if self.op_remove_var.get():
            preset['operations']['remove'] = {
                'field': self.remove_field.get(),
                'text': self.remove_text.get()
            }

        if self.op_split_var.get():
            preset['operations']['split'] = {
                'source': self.split_source.get(),
                'separator': self.split_separator.get(),
                'left_field': self.split_left_field.get(),
                'right_field': self.split_right_field.get()
            }

        # Load existing presets
        presets = []
        if self.presets_file.exists():
            try:
                with open(self.presets_file, 'r') as f:
                    presets = json.load(f)
            except:
                pass

        # Add new preset
        presets.append(preset)

        # Save
        with open(self.presets_file, 'w') as f:
            json.dump(presets, f, indent=2)

        messagebox.showinfo("Success", f"Preset '{preset_name}' saved!")

    def load_preset(self):
        """Load a saved preset"""
        if not self.presets_file.exists():
            messagebox.showinfo("No Presets", "No presets found!")
            return

        try:
            with open(self.presets_file, 'r') as f:
                presets = json.load(f)
        except:
            messagebox.showerror("Error", "Failed to load presets!")
            return

        if not presets:
            messagebox.showinfo("No Presets", "No presets found!")
            return

        # Show preset selection dialog
        preset_names = [p['name'] for p in presets]
        selection = tk.simpledialog.askstring(
            "Load Preset",
            f"Available presets:\n" + "\n".join(f"{i+1}. {name}" for i, name in enumerate(preset_names)) +
            "\n\nEnter preset number:"
        )

        if not selection:
            return

        try:
            idx = int(selection) - 1
            if idx < 0 or idx >= len(presets):
                raise ValueError()

            preset = presets[idx]
            self.apply_preset(preset)
            messagebox.showinfo("Success", f"Loaded preset '{preset['name']}'")

        except:
            messagebox.showerror("Error", "Invalid preset number!")

    def apply_preset(self, preset: dict):
        """Apply preset settings to UI"""
        ops = preset.get('operations', {})

        # Reset all operations
        self.op_replace_var.set(False)
        self.op_trim_var.set(False)
        self.op_copy_var.set(False)
        self.op_case_var.set(False)
        self.op_add_var.set(False)
        self.op_remove_var.set(False)
        self.op_split_var.set(False)

        # Apply operation settings
        if 'replace' in ops:
            self.op_replace_var.set(True)
            r = ops['replace']
            self.replace_field.set(r['field'])
            self.replace_find.delete(0, tk.END)
            self.replace_find.insert(0, r['find'])
            self.replace_with.delete(0, tk.END)
            self.replace_with.insert(0, r['with'])
            self.replace_case_sensitive.set(r.get('case_sensitive', False))
            self.replace_use_regex.set(r.get('use_regex', False))

        if 'trim' in ops:
            self.op_trim_var.set(True)
            t = ops['trim']
            self.trim_field.set(t['field'])
            self.trim_leading.set(t.get('leading', True))
            self.trim_trailing.set(t.get('trailing', True))

        if 'copy' in ops:
            self.op_copy_var.set(True)
            c = ops['copy']
            self.copy_from.set(c['from'])
            self.copy_to.set(c['to'])
            self.copy_append.set(c.get('append', False))

        if 'case' in ops:
            self.op_case_var.set(True)
            c = ops['case']
            self.case_field.set(c['field'])
            self.case_mode.set(c.get('mode', 'title'))

        if 'add' in ops:
            self.op_add_var.set(True)
            a = ops['add']
            self.add_field.set(a['field'])
            self.add_prefix.delete(0, tk.END)
            self.add_prefix.insert(0, a.get('prefix', ''))
            self.add_suffix.delete(0, tk.END)
            self.add_suffix.insert(0, a.get('suffix', ''))

        if 'remove' in ops:
            self.op_remove_var.set(True)
            r = ops['remove']
            self.remove_field.set(r['field'])
            self.remove_text.delete(0, tk.END)
            self.remove_text.insert(0, r.get('text', ''))

        if 'split' in ops:
            self.op_split_var.set(True)
            s = ops['split']
            self.split_source.set(s['source'])
            self.split_separator.delete(0, tk.END)
            self.split_separator.insert(0, s.get('separator', ' - '))
            self.split_left_field.set(s.get('left_field', 'artist'))
            self.split_right_field.set(s.get('right_field', 'title'))

    # Audio player functions
    def play_file(self, index: int):
        """Play audio file at index"""
        if not PYGAME_AVAILABLE or index >= len(self.audio_files):
            return

        audio_file = self.audio_files[index]

        if self.player.load(audio_file.path):
            self.current_playing_index = index
            self.player.play()
            self.player_label.config(
                text=f"♪ {audio_file.filename} ({audio_file.format_duration()})"
            )
            self.play_button.config(text="❚❚")

    def toggle_play(self):
        """Play/pause current file"""
        if not PYGAME_AVAILABLE:
            messagebox.showinfo("Not Available", "Audio playback not available.\nInstall pygame: pip install pygame")
            return

        if self.player.is_playing():
            self.player.pause()
            self.play_button.config(text="▶")
        elif self.current_playing_index >= 0:
            self.player.pause()
            self.play_button.config(text="❚❚")
        else:
            # Start playing first selected file
            selected = self.get_selected_files()
            if selected:
                idx = self.audio_files.index(selected[0])
                self.play_file(idx)

    def stop_playback(self):
        """Stop playback"""
        if PYGAME_AVAILABLE:
            self.player.stop()
            self.play_button.config(text="▶")
            self.player_label.config(text="Stopped")

    def play_previous(self):
        """Play previous file"""
        if self.current_playing_index > 0:
            self.play_file(self.current_playing_index - 1)

    def play_next(self):
        """Play next file"""
        if self.current_playing_index < len(self.audio_files) - 1:
            self.play_file(self.current_playing_index + 1)

    def on_volume_change(self, value):
        """Handle volume slider change"""
        vol = float(value) / 100.0
        self.player.set_volume(vol)
        self.volume_label.config(text=f"{int(float(value))}%")


def main():
    # Add import dialog for missing dependency
    import tkinter.simpledialog

    root = tk.Tk()
    app = BulkTagUtility(root)
    root.mainloop()


if __name__ == "__main__":
    main()
