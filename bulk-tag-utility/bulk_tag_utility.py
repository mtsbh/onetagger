#!/usr/bin/env python3
"""
Bulk Tag Utility - Like Bulk Rename Utility but for music tags
A GUI tool for batch editing audio file tags with simple checkbox operations
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from typing import List, Dict, Optional, Callable
import os

try:
    import mutagen
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, COMM, TDRC, TCON, TPE2
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
except ImportError:
    print("Installing mutagen...")
    import subprocess
    subprocess.check_call(["pip", "install", "mutagen"])
    import mutagen
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, COMM, TDRC, TCON, TPE2
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4


class AudioFile:
    """Represents an audio file with tag information"""

    def __init__(self, path: Path):
        self.path = path
        self.filename = path.name
        self.selected = True
        self.tags = {}
        self.original_tags = {}
        self.modified = False
        self.load_tags()

    def load_tags(self):
        """Load tags from the audio file"""
        try:
            audio = mutagen.File(self.path, easy=True)
            if audio is None:
                return

            # Common tags
            self.tags = {
                'title': self._get_tag(audio, 'title'),
                'artist': self._get_tag(audio, 'artist'),
                'album': self._get_tag(audio, 'album'),
                'albumartist': self._get_tag(audio, 'albumartist'),
                'genre': self._get_tag(audio, 'genre'),
                'date': self._get_tag(audio, 'date'),
                'comment': self._get_tag(audio, 'comment'),
            }

            # Store original for comparison
            self.original_tags = self.tags.copy()

        except Exception as e:
            print(f"Error loading {self.path}: {e}")

    def _get_tag(self, audio, key: str) -> str:
        """Get tag value safely"""
        val = audio.get(key, [''])
        if isinstance(val, list) and len(val) > 0:
            return str(val[0])
        return str(val) if val else ''

    def save_tags(self):
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

    def apply_operation(self, operation: Callable[[str], str], field: str):
        """Apply an operation to a specific field"""
        if field in self.tags:
            original = self.tags[field]
            self.tags[field] = operation(original)
            self.modified = self.tags != self.original_tags


class BulkTagUtility:
    """Main application window"""

    def __init__(self, root):
        self.root = root
        self.root.title("Bulk Tag Utility")
        self.root.geometry("1200x700")

        self.current_folder = None
        self.audio_files: List[AudioFile] = []
        self.selected_files: List[AudioFile] = []

        # Audio player state
        self.current_playing = None
        self.player_thread = None

        self.setup_ui()

    def setup_ui(self):
        """Setup the main UI layout"""

        # Main container with 3 columns
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: Folder Browser (25%)
        folder_frame = ttk.LabelFrame(main_frame, text="📁 Folder Browser", padding=5)
        folder_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 2))

        # Folder selection button
        ttk.Button(folder_frame, text="Select Folder", command=self.select_folder).pack(fill=tk.X, pady=(0, 5))

        # Folder tree
        self.folder_label = ttk.Label(folder_frame, text="No folder selected", wraplength=200)
        self.folder_label.pack(fill=tk.X, pady=5)

        # File count
        self.file_count_label = ttk.Label(folder_frame, text="Files: 0", font=("Arial", 9))
        self.file_count_label.pack(fill=tk.X, pady=5)

        # Middle: File List (45%)
        file_frame = ttk.LabelFrame(main_frame, text="📋 Files", padding=5)
        file_frame.grid(row=0, column=1, sticky="nsew", padx=2)

        # File list controls
        file_controls = ttk.Frame(file_frame)
        file_controls.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(file_controls, text="Select All", command=self.select_all_files, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_controls, text="Deselect All", command=self.deselect_all_files, width=12).pack(side=tk.LEFT, padx=2)

        # File list with scrollbar
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
        scrollbar.config(command=self.file_listbox.yview)

        # Right: Operations Panel (30%)
        ops_frame = ttk.LabelFrame(main_frame, text="⚙️ Tag Operations", padding=5)
        ops_frame.grid(row=0, column=2, sticky="nsew", padx=(2, 0))

        # Operations canvas with scrollbar
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
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Bottom: Player + Actions
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        # Player section
        player_frame = ttk.LabelFrame(bottom_frame, text="▶ Audio Player", padding=5)
        player_frame.pack(fill=tk.X, pady=(0, 5))

        self.player_label = ttk.Label(player_frame, text="No file selected", font=("Arial", 9))
        self.player_label.pack()

        player_controls = ttk.Frame(player_frame)
        player_controls.pack(pady=5)

        ttk.Button(player_controls, text="◀◀", width=5, command=self.play_previous).pack(side=tk.LEFT, padx=2)
        ttk.Button(player_controls, text="▶/❚❚", width=8, command=self.toggle_play).pack(side=tk.LEFT, padx=2)
        ttk.Button(player_controls, text="▶▶", width=5, command=self.play_next).pack(side=tk.LEFT, padx=2)

        # Preview section
        preview_frame = ttk.LabelFrame(bottom_frame, text="Preview Changes", padding=5)
        preview_frame.pack(fill=tk.X, pady=(0, 5))

        self.preview_text = tk.Text(preview_frame, height=4, font=("Consolas", 8), wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        # Action buttons
        action_frame = ttk.Frame(bottom_frame)
        action_frame.pack(fill=tk.X)

        ttk.Button(action_frame, text="Preview Changes", command=self.preview_changes, style="Accent.TButton").pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(action_frame, text="Apply to Selected", command=self.apply_changes, style="Accent.TButton").pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    def setup_operations(self):
        """Setup operation panels"""

        # Operation 1: Replace Text
        self.op_replace_var = tk.BooleanVar(value=False)
        replace_frame = self.create_operation_frame("Replace Text", self.op_replace_var)

        ttk.Label(replace_frame, text="Field:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.replace_field = ttk.Combobox(replace_frame, values=['title', 'artist', 'album', 'albumartist', 'genre', 'comment'], width=15, state='readonly')
        self.replace_field.set('title')
        self.replace_field.grid(row=0, column=1, sticky=tk.EW, pady=2)

        ttk.Label(replace_frame, text="Find:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.replace_find = ttk.Entry(replace_frame, width=18)
        self.replace_find.grid(row=1, column=1, sticky=tk.EW, pady=2)

        ttk.Label(replace_frame, text="Replace:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.replace_with = ttk.Entry(replace_frame, width=18)
        self.replace_with.grid(row=2, column=1, sticky=tk.EW, pady=2)

        self.replace_case_sensitive = tk.BooleanVar(value=False)
        ttk.Checkbutton(replace_frame, text="Case sensitive", variable=self.replace_case_sensitive).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)

        replace_frame.columnconfigure(1, weight=1)

        # Operation 2: Trim
        self.op_trim_var = tk.BooleanVar(value=False)
        trim_frame = self.create_operation_frame("Trim Whitespace", self.op_trim_var)

        ttk.Label(trim_frame, text="Field:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.trim_field = ttk.Combobox(trim_frame, values=['title', 'artist', 'album', 'albumartist', 'genre', 'comment', 'ALL FIELDS'], width=15, state='readonly')
        self.trim_field.set('ALL FIELDS')
        self.trim_field.grid(row=0, column=1, sticky=tk.EW, pady=2)

        self.trim_leading = tk.BooleanVar(value=True)
        self.trim_trailing = tk.BooleanVar(value=True)

        ttk.Checkbutton(trim_frame, text="Leading spaces", variable=self.trim_leading).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Checkbutton(trim_frame, text="Trailing spaces", variable=self.trim_trailing).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)

        trim_frame.columnconfigure(1, weight=1)

        # Operation 3: Copy Field
        self.op_copy_var = tk.BooleanVar(value=False)
        copy_frame = self.create_operation_frame("Copy Field", self.op_copy_var)

        ttk.Label(copy_frame, text="From:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.copy_from = ttk.Combobox(copy_frame, values=['title', 'artist', 'album', 'albumartist', 'genre', 'date', 'comment'], width=15, state='readonly')
        self.copy_from.set('artist')
        self.copy_from.grid(row=0, column=1, sticky=tk.EW, pady=2)

        ttk.Label(copy_frame, text="To:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.copy_to = ttk.Combobox(copy_frame, values=['title', 'artist', 'album', 'albumartist', 'genre', 'date', 'comment'], width=15, state='readonly')
        self.copy_to.set('comment')
        self.copy_to.grid(row=1, column=1, sticky=tk.EW, pady=2)

        self.copy_append = tk.BooleanVar(value=False)
        ttk.Checkbutton(copy_frame, text="Append (not replace)", variable=self.copy_append).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)

        copy_frame.columnconfigure(1, weight=1)

        # Operation 4: Change Case
        self.op_case_var = tk.BooleanVar(value=False)
        case_frame = self.create_operation_frame("Change Case", self.op_case_var)

        ttk.Label(case_frame, text="Field:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.case_field = ttk.Combobox(case_frame, values=['title', 'artist', 'album', 'albumartist', 'genre', 'comment'], width=15, state='readonly')
        self.case_field.set('title')
        self.case_field.grid(row=0, column=1, sticky=tk.EW, pady=2)

        self.case_mode = tk.StringVar(value='title')
        ttk.Radiobutton(case_frame, text="Title Case", variable=self.case_mode, value='title').grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Radiobutton(case_frame, text="UPPERCASE", variable=self.case_mode, value='upper').grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Radiobutton(case_frame, text="lowercase", variable=self.case_mode, value='lower').grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)

        case_frame.columnconfigure(1, weight=1)

        # Operation 5: Add Prefix/Suffix
        self.op_add_var = tk.BooleanVar(value=False)
        add_frame = self.create_operation_frame("Add Prefix/Suffix", self.op_add_var)

        ttk.Label(add_frame, text="Field:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.add_field = ttk.Combobox(add_frame, values=['title', 'artist', 'album', 'albumartist', 'genre', 'comment'], width=15, state='readonly')
        self.add_field.set('title')
        self.add_field.grid(row=0, column=1, sticky=tk.EW, pady=2)

        ttk.Label(add_frame, text="Prefix:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.add_prefix = ttk.Entry(add_frame, width=18)
        self.add_prefix.grid(row=1, column=1, sticky=tk.EW, pady=2)

        ttk.Label(add_frame, text="Suffix:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.add_suffix = ttk.Entry(add_frame, width=18)
        self.add_suffix.grid(row=2, column=1, sticky=tk.EW, pady=2)

        add_frame.columnconfigure(1, weight=1)

        # Operation 6: Remove Pattern
        self.op_remove_var = tk.BooleanVar(value=False)
        remove_frame = self.create_operation_frame("Remove Text", self.op_remove_var)

        ttk.Label(remove_frame, text="Field:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.remove_field = ttk.Combobox(remove_frame, values=['title', 'artist', 'album', 'albumartist', 'genre', 'comment'], width=15, state='readonly')
        self.remove_field.set('title')
        self.remove_field.grid(row=0, column=1, sticky=tk.EW, pady=2)

        ttk.Label(remove_frame, text="Remove:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.remove_text = ttk.Entry(remove_frame, width=18)
        self.remove_text.grid(row=1, column=1, sticky=tk.EW, pady=2)

        remove_frame.columnconfigure(1, weight=1)

    def create_operation_frame(self, title: str, var: tk.BooleanVar) -> ttk.Frame:
        """Create a collapsible operation frame"""
        container = ttk.Frame(self.ops_container)
        container.pack(fill=tk.X, pady=5)

        # Header with checkbox
        header = ttk.Frame(container)
        header.pack(fill=tk.X)

        check = ttk.Checkbutton(header, text=title, variable=var)
        check.pack(side=tk.LEFT)

        # Content frame
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

        # Update folder label
        self.folder_label.config(text=str(self.current_folder))

        # Supported formats
        extensions = ['.mp3', '.flac', '.m4a', '.ogg', '.opus', '.wav', '.wma']

        # Load files
        files_found = 0
        for ext in extensions:
            for file_path in self.current_folder.rglob(f'*{ext}'):
                try:
                    audio_file = AudioFile(file_path)
                    self.audio_files.append(audio_file)
                    files_found += 1
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")

        # Update file list
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
                # Toggle selection
                self.audio_files[idx].selected = not self.audio_files[idx].selected
                self.update_file_list()
                self.file_listbox.selection_clear(0, tk.END)

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

        # Create test copy
        test_file = selected[0]
        original_tags = test_file.tags.copy()

        # Apply operations (without saving)
        self.apply_operations_to_file(test_file, preview=True)

        # Show changes
        preview_lines = [f"Preview for: {test_file.filename}\n"]
        preview_lines.append(f"Selected files: {len(selected)}\n\n")

        for field, new_value in test_file.tags.items():
            old_value = original_tags.get(field, '')
            if old_value != new_value:
                preview_lines.append(f"{field.upper()}:\n")
                preview_lines.append(f"  Before: '{old_value}'\n")
                preview_lines.append(f"  After:  '{new_value}'\n\n")

        # Restore original
        test_file.tags = original_tags

        if len(preview_lines) == 3:
            preview_lines.append("No changes detected!")

        self.preview_text.insert(1.0, ''.join(preview_lines))

    def apply_changes(self):
        """Apply operations to selected files"""
        selected = self.get_selected_files()
        if not selected:
            messagebox.showwarning("No Selection", "Please select files to modify!")
            return

        # Confirm
        count = len(selected)
        if not messagebox.askyesno("Confirm", f"Apply changes to {count} file(s)?"):
            return

        # Apply and save
        success_count = 0
        for audio_file in selected:
            self.apply_operations_to_file(audio_file, preview=False)
            if audio_file.save_tags():
                success_count += 1

        messagebox.showinfo("Complete", f"Successfully updated {success_count}/{count} files!")
        self.update_file_list()

    def apply_operations_to_file(self, audio_file: AudioFile, preview: bool = False):
        """Apply enabled operations to a file"""

        # Operation 1: Replace
        if self.op_replace_var.get():
            field = self.replace_field.get()
            find = self.replace_find.get()
            replace = self.replace_with.get()
            case_sensitive = self.replace_case_sensitive.get()

            if field in audio_file.tags and find:
                original = audio_file.tags[field]
                if case_sensitive:
                    audio_file.tags[field] = original.replace(find, replace)
                else:
                    # Case insensitive replace
                    import re
                    audio_file.tags[field] = re.sub(re.escape(find), replace, original, flags=re.IGNORECASE)

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

    def toggle_play(self):
        """Play/pause current file"""
        selected = self.get_selected_files()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a file to play!")
            return

        # Simple implementation - just show which file would play
        self.current_playing = selected[0]
        self.player_label.config(text=f"Playing: {self.current_playing.filename}")

        # Note: Full audio playback would require pygame.mixer or similar
        # For now this is a placeholder

    def play_previous(self):
        """Play previous file in list"""
        selected = self.get_selected_files()
        if not selected or not self.current_playing:
            return

        current_idx = selected.index(self.current_playing)
        if current_idx > 0:
            self.current_playing = selected[current_idx - 1]
            self.player_label.config(text=f"Playing: {self.current_playing.filename}")

    def play_next(self):
        """Play next file in list"""
        selected = self.get_selected_files()
        if not selected or not self.current_playing:
            return

        current_idx = selected.index(self.current_playing)
        if current_idx < len(selected) - 1:
            self.current_playing = selected[current_idx + 1]
            self.player_label.config(text=f"Playing: {self.current_playing.filename}")


def main():
    root = tk.Tk()
    app = BulkTagUtility(root)
    root.mainloop()


if __name__ == "__main__":
    main()
