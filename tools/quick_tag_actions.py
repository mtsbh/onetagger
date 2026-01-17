#!/usr/bin/env python3
"""
Quick Tag Actions - Super simple GUI for common tag operations
Just tick boxes and click Apply!
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, COMM, TCON, TPUB
import re

class QuickActions:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Tag Actions")
        self.root.geometry("600x750")

        self.files = []
        self.setup_ui()

    def setup_ui(self):
        # File selection
        file_frame = ttk.LabelFrame(self.root, text="Select Files", padding=15)
        file_frame.pack(fill=tk.X, padx=15, pady=10)

        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="📁 Add Files", command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📂 Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_files).pack(side=tk.LEFT, padx=5)

        self.file_label = ttk.Label(file_frame, text="No files selected", foreground="gray")
        self.file_label.pack(pady=10)

        # Actions frame
        action_frame = ttk.LabelFrame(self.root, text="Select Actions to Perform", padding=15)
        action_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Create scrollable frame for actions
        canvas = tk.Canvas(action_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(action_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Define all quick actions
        self.actions = []

        # Tag replacements (old → new)
        ttk.Label(scrollable_frame, text="🏷️  Replace Old Tags:", font=('', 10, 'bold')).pack(anchor=tk.W, pady=(5, 10))

        replacements = [
            ("mazn → Nasty", "mazn", "Nasty", "COMMENT"),
            ("maz → Nasty", "maz", "Nasty", "COMMENT"),
            ("slomz → Dark", "slomz", "Dark", "COMMENT"),
            ("kopon → Upper", "kopon", "Upper", "COMMENT"),
            ("hals → Oldek", "hals", "Oldek", "COMMENT"),
            ("derp → Trippy", "derp", "Trippy", "COMMENT"),
            ("cool → Beautiful", "cool", "Beautiful", "COMMENT"),
            ("space → Cosmic", "space", "Cosmic", "COMMENT"),
            ("kruto → Raw", "kruto", "Raw", "COMMENT"),
            ("shaip → Battle", "shaip", "Battle", "COMMENT"),
        ]

        for label, find, replace, field in replacements:
            var = tk.BooleanVar()
            self.actions.append(('replace', var, find, replace, field))
            ttk.Checkbutton(scrollable_frame, text=label, variable=var).pack(anchor=tk.W, pady=2, padx=20)

        # Move tags between fields
        ttk.Label(scrollable_frame, text="\n📦 Move Tags Between Fields:", font=('', 10, 'bold')).pack(anchor=tk.W, pady=(15, 10))

        moves = [
            ("After: GENRE → LABEL", "After", "GENRE", "LABEL"),
            ("Warmup: GENRE → LABEL", "Warmup", "GENRE", "LABEL"),
            ("Peak: GENRE → LABEL", "Peak", "GENRE", "LABEL"),
            ("Intro: GENRE → LABEL", "Intro", "GENRE", "LABEL"),
            ("Outro: GENRE → LABEL", "Outro", "GENRE", "LABEL"),
            ("Filler: GENRE → LABEL", "Filler", "GENRE", "LABEL"),
            ("Morning: GENRE → LABEL", "Morning", "GENRE", "LABEL"),
            ("Daytime: GENRE → LABEL", "Daytime", "GENRE", "LABEL"),
        ]

        for label, tag, from_field, to_field in moves:
            var = tk.BooleanVar()
            self.actions.append(('move', var, tag, from_field, to_field))
            ttk.Checkbutton(scrollable_frame, text=label, variable=var).pack(anchor=tk.W, pady=2, padx=20)

        # Clean operations
        ttk.Label(scrollable_frame, text="\n🧹 Clean/Fix:", font=('', 10, 'bold')).pack(anchor=tk.W, pady=(15, 10))

        self.trim_spaces_var = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="Trim extra spaces", variable=self.trim_spaces_var).pack(
            anchor=tk.W, pady=2, padx=20)

        self.remove_dupes_var = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="Remove duplicate tags", variable=self.remove_dupes_var).pack(
            anchor=tk.W, pady=2, padx=20)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bottom buttons
        button_frame = ttk.Frame(self.root, padding=15)
        button_frame.pack(fill=tk.X, padx=15, pady=10)

        ttk.Button(button_frame, text="✓ Apply Selected Actions",
                   command=self.apply_actions,
                   style="Accent.TButton").pack(fill=tk.X, pady=5)

        self.status_label = ttk.Label(button_frame, text="Ready - Select files and actions", foreground="blue")
        self.status_label.pack(pady=5)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select MP3 files",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        if files:
            self.files.extend(files)
            self.update_file_label()

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select folder with music")
        if folder:
            for root, dirs, filenames in os.walk(folder):
                for filename in filenames:
                    if filename.lower().endswith('.mp3'):
                        self.files.append(os.path.join(root, filename))
            self.update_file_label()

    def clear_files(self):
        self.files = []
        self.update_file_label()

    def update_file_label(self):
        if self.files:
            self.file_label.config(text=f"✓ {len(self.files)} files selected", foreground="green")
        else:
            self.file_label.config(text="No files selected", foreground="gray")

    def get_tag_list(self, audio, field):
        """Get list of tags from field"""
        if field == "COMMENT":
            if 'COMM::eng' in audio:
                text = audio['COMM::eng'].text[0]
                # Check for MixedInKey format
                if ' - ' in text:
                    parts = text.split(' - ')
                    if len(parts) >= 3:
                        # Format: "5A - 5 - tags"
                        return parts[0], parts[1], [t.strip() for t in parts[2].split(',')]
                    return None, None, [t.strip() for t in text.split(',')]
                return None, None, [t.strip() for t in text.split(',')]
            return None, None, []

        elif field == "GENRE":
            if 'TCON' in audio:
                genres = []
                for g in audio['TCON'].text:
                    genres.extend([t.strip() for t in str(g).split(',')])
                return None, None, genres
            return None, None, []

        elif field == "LABEL":
            if 'TPUB' in audio:
                labels = []
                for l in audio['TPUB'].text:
                    labels.extend([t.strip() for t in str(l).split(',')])
                return None, None, labels
            return None, None, []

        return None, None, []

    def set_tag_list(self, audio, field, tags, key=None, energy=None):
        """Set tags in field"""
        if field == "COMMENT":
            # Preserve MixedInKey format if present
            if key and energy:
                value = f"{key} - {energy} - {', '.join(tags)}" if tags else f"{key} - {energy}"
            else:
                value = ', '.join(tags)
            audio['COMM::eng'] = COMM(encoding=3, lang='eng', desc='', text=[value])

        elif field == "GENRE":
            audio['TCON'] = TCON(encoding=3, text=tags)

        elif field == "LABEL":
            audio['TPUB'] = TPUB(encoding=3, text=tags)

    def apply_actions(self):
        if not self.files:
            messagebox.showwarning("No files", "Please select files first!")
            return

        # Check if any action is selected
        selected_actions = [a for a in self.actions if a[1].get()]
        has_clean = self.trim_spaces_var.get() or self.remove_dupes_var.get()

        if not selected_actions and not has_clean:
            messagebox.showwarning("No actions", "Please select at least one action!")
            return

        # Confirm
        action_count = len(selected_actions) + (1 if has_clean else 0)
        confirm = messagebox.askyesno(
            "Confirm",
            f"Apply {action_count} action(s) to {len(self.files)} file(s)?\n\n"
            "This will modify your music files!"
        )

        if not confirm:
            return

        self.status_label.config(text="Processing...", foreground="orange")
        self.root.update()

        success_count = 0
        error_count = 0
        changes_made = 0

        for file_path in self.files:
            try:
                audio = MP3(file_path, ID3=ID3)
                file_changed = False

                # Apply replace actions
                for action_type, var, *params in self.actions:
                    if not var.get():
                        continue

                    if action_type == 'replace':
                        find, replace, field = params
                        key, energy, tags = self.get_tag_list(audio, field)

                        # Replace in tag list
                        new_tags = []
                        for tag in tags:
                            if tag.lower() == find.lower():
                                new_tags.append(replace)
                                file_changed = True
                            else:
                                new_tags.append(tag)

                        if file_changed:
                            self.set_tag_list(audio, field, new_tags, key, energy)

                    elif action_type == 'move':
                        tag_to_move, from_field, to_field = params
                        key_from, energy_from, from_tags = self.get_tag_list(audio, from_field)
                        key_to, energy_to, to_tags = self.get_tag_list(audio, to_field)

                        # Check if tag exists in source field
                        if tag_to_move in from_tags:
                            # Remove from source
                            from_tags.remove(tag_to_move)
                            self.set_tag_list(audio, from_field, from_tags, key_from, energy_from)

                            # Add to destination (if not already there)
                            if tag_to_move not in to_tags:
                                to_tags.append(tag_to_move)
                                self.set_tag_list(audio, to_field, to_tags, key_to, energy_to)

                            file_changed = True

                # Apply clean operations
                if self.trim_spaces_var.get() or self.remove_dupes_var.get():
                    for field in ["COMMENT", "GENRE", "LABEL"]:
                        key, energy, tags = self.get_tag_list(audio, field)

                        original_tags = tags.copy()

                        if self.trim_spaces_var.get():
                            tags = [t.strip() for t in tags if t.strip()]

                        if self.remove_dupes_var.get():
                            seen = set()
                            unique_tags = []
                            for tag in tags:
                                if tag.lower() not in seen:
                                    seen.add(tag.lower())
                                    unique_tags.append(tag)
                            tags = unique_tags

                        if tags != original_tags:
                            self.set_tag_list(audio, field, tags, key, energy)
                            file_changed = True

                if file_changed:
                    audio.save()
                    changes_made += 1

                success_count += 1

            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                error_count += 1

        messagebox.showinfo(
            "Complete!",
            f"Processed {success_count} file(s)\n"
            f"Modified {changes_made} file(s)\n"
            f"Errors: {error_count}"
        )

        self.status_label.config(
            text=f"✓ Done! Modified {changes_made} file(s)",
            foreground="green"
        )

def main():
    root = tk.Tk()
    app = QuickActions(root)
    root.mainloop()

if __name__ == '__main__':
    main()
