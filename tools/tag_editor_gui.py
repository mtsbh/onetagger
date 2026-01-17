#!/usr/bin/env python3
"""
Quick Tag Editor - GUI tool for batch music tag operations
Similar to Bulk Rename Utility but for music tags
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, COMM, TCON, TPUB, TPE1

class QuickTagEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Tag Editor")
        self.root.geometry("900x700")

        self.files = []
        self.preview_data = []

        self.setup_ui()

    def setup_ui(self):
        # Top frame - File selection
        file_frame = ttk.LabelFrame(self.root, text="Files", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(file_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Clear", command=self.clear_files).pack(side=tk.LEFT, padx=5)

        self.file_count_label = ttk.Label(file_frame, text="0 files selected")
        self.file_count_label.pack(side=tk.LEFT, padx=20)

        # Operations frame
        ops_frame = ttk.LabelFrame(self.root, text="Operations", padding=10)
        ops_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create notebook for different operation types
        notebook = ttk.Notebook(ops_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Find & Replace
        replace_tab = ttk.Frame(notebook, padding=10)
        notebook.add(replace_tab, text="Find & Replace")
        self.setup_replace_tab(replace_tab)

        # Tab 2: Move Between Fields
        move_tab = ttk.Frame(notebook, padding=10)
        notebook.add(move_tab, text="Move Tags")
        self.setup_move_tab(move_tab)

        # Tab 3: Quick Presets
        preset_tab = ttk.Frame(notebook, padding=10)
        notebook.add(preset_tab, text="Presets")
        self.setup_preset_tab(preset_tab)

        # Tab 4: Clean/Trim
        clean_tab = ttk.Frame(notebook, padding=10)
        notebook.add(clean_tab, text="Clean/Trim")
        self.setup_clean_tab(clean_tab)

        # Preview frame
        preview_frame = ttk.LabelFrame(self.root, text="Preview", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Preview table
        columns = ("File", "Field", "Before", "After")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="tree headings", height=8)

        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=200)

        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)

        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bottom buttons
        button_frame = ttk.Frame(self.root, padding=10)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(button_frame, text="Preview Changes", command=self.preview_changes,
                   style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Apply Changes", command=self.apply_changes,
                   style="Accent.TButton").pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(button_frame, text="Ready")
        self.status_label.pack(side=tk.RIGHT, padx=20)

    def setup_replace_tab(self, parent):
        """Tab for find & replace operations"""

        ttk.Label(parent, text="Field:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.replace_field = ttk.Combobox(parent, values=["COMMENT", "GENRE", "LABEL"], width=20)
        self.replace_field.set("COMMENT")
        self.replace_field.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        ttk.Label(parent, text="Find:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.find_text = ttk.Entry(parent, width=30)
        self.find_text.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        ttk.Label(parent, text="Replace with:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.replace_text = ttk.Entry(parent, width=30)
        self.replace_text.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)

        self.case_sensitive = tk.BooleanVar()
        ttk.Checkbutton(parent, text="Case sensitive", variable=self.case_sensitive).grid(
            row=3, column=1, sticky=tk.W, pady=5, padx=5)

        self.whole_word = tk.BooleanVar()
        ttk.Checkbutton(parent, text="Whole word only", variable=self.whole_word).grid(
            row=4, column=1, sticky=tk.W, pady=5, padx=5)

        ttk.Label(parent, text="\nExamples:", font=('', 9, 'bold')).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=10)
        examples = [
            "Find: 'hals'  Replace: 'oldek'",
            "Find: 'mazn'  Replace: 'Nasty'",
            "Find: 'slomz'  Replace: 'Dark'"
        ]
        for i, ex in enumerate(examples):
            ttk.Label(parent, text=f"• {ex}", foreground="gray").grid(
                row=6+i, column=0, columnspan=2, sticky=tk.W, padx=20)

    def setup_move_tab(self, parent):
        """Tab for moving tags between fields"""

        ttk.Label(parent, text="Find tag:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.move_tag = ttk.Entry(parent, width=30)
        self.move_tag.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        ttk.Label(parent, text="In field:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.move_from_field = ttk.Combobox(parent, values=["COMMENT", "GENRE", "LABEL"], width=20)
        self.move_from_field.set("GENRE")
        self.move_from_field.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        ttk.Label(parent, text="Move to field:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.move_to_field = ttk.Combobox(parent, values=["COMMENT", "GENRE", "LABEL"], width=20)
        self.move_to_field.set("LABEL")
        self.move_to_field.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)

        self.remove_from_source = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Remove from source field", variable=self.remove_from_source).grid(
            row=3, column=1, sticky=tk.W, pady=5, padx=5)

        ttk.Label(parent, text="\nExamples:", font=('', 9, 'bold')).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)
        examples = [
            "Move 'After' from GENRE to LABEL",
            "Move 'Warmup' from GENRE to LABEL",
            "Copy 'Dark' from COMMENT to GENRE"
        ]
        for i, ex in enumerate(examples):
            ttk.Label(parent, text=f"• {ex}", foreground="gray").grid(
                row=5+i, column=0, columnspan=2, sticky=tk.W, padx=20)

    def setup_preset_tab(self, parent):
        """Tab for common preset operations"""

        ttk.Label(parent, text="Common tag migrations:", font=('', 10, 'bold')).pack(anchor=tk.W, pady=10)

        # Old tag → New tag presets
        presets = [
            ("mazn → Nasty (in COMMENT)", "mazn", "Nasty", "COMMENT"),
            ("slomz → Dark (in COMMENT)", "slomz", "Dark", "COMMENT"),
            ("kopon → Upper (in COMMENT)", "kopon", "Upper", "COMMENT"),
            ("hals → Oldek (in COMMENT)", "hals", "Oldek", "COMMENT"),
            ("After: GENRE → LABEL", "After", "After", "GENRE→LABEL"),
            ("Warmup: GENRE → LABEL", "Warmup", "Warmup", "GENRE→LABEL"),
        ]

        self.preset_vars = []
        for i, (label, old, new, field) in enumerate(presets):
            var = tk.BooleanVar()
            self.preset_vars.append((var, old, new, field))
            ttk.Checkbutton(parent, text=label, variable=var).pack(anchor=tk.W, pady=3, padx=20)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)

        ttk.Button(parent, text="Apply Selected Presets",
                   command=self.apply_presets).pack(pady=10)

    def setup_clean_tab(self, parent):
        """Tab for cleaning/trimming operations"""

        ttk.Label(parent, text="Clean operations:", font=('', 10, 'bold')).pack(anchor=tk.W, pady=10)

        self.trim_spaces = tk.BooleanVar()
        ttk.Checkbutton(parent, text="Trim extra spaces", variable=self.trim_spaces).pack(
            anchor=tk.W, pady=3, padx=20)

        self.remove_duplicates = tk.BooleanVar()
        ttk.Checkbutton(parent, text="Remove duplicate tags in same field",
                       variable=self.remove_duplicates).pack(anchor=tk.W, pady=3, padx=20)

        self.fix_case = tk.BooleanVar()
        ttk.Checkbutton(parent, text="Fix capitalization (Title Case)",
                       variable=self.fix_case).pack(anchor=tk.W, pady=3, padx=20)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)

        ttk.Label(parent, text="Remove specific tag:").pack(anchor=tk.W, pady=5, padx=20)
        self.remove_tag = ttk.Entry(parent, width=30)
        self.remove_tag.pack(anchor=tk.W, pady=5, padx=40)

        ttk.Label(parent, text="From field:").pack(anchor=tk.W, pady=5, padx=20)
        self.remove_from_field = ttk.Combobox(parent, values=["COMMENT", "GENRE", "LABEL"], width=20)
        self.remove_from_field.set("COMMENT")
        self.remove_from_field.pack(anchor=tk.W, pady=5, padx=40)

    def add_files(self):
        """Add individual files"""
        files = filedialog.askopenfilenames(
            title="Select music files",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        if files:
            self.files.extend(files)
            self.update_file_count()

    def add_folder(self):
        """Add all music files from folder"""
        folder = filedialog.askdirectory(title="Select folder")
        if folder:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith('.mp3'):
                        self.files.append(os.path.join(root, file))
            self.update_file_count()

    def clear_files(self):
        """Clear file list"""
        self.files = []
        self.update_file_count()
        self.preview_tree.delete(*self.preview_tree.get_children())

    def update_file_count(self):
        """Update file count label"""
        self.file_count_label.config(text=f"{len(self.files)} files selected")

    def get_field_value(self, audio, field):
        """Get value from ID3 field"""
        if field == "COMMENT":
            return audio.get('COMM::eng', [])
        elif field == "GENRE":
            return audio.get('TCON', [])
        elif field == "LABEL":
            return audio.get('TPUB', [])
        return []

    def preview_changes(self):
        """Preview what will change"""
        if not self.files:
            messagebox.showwarning("No files", "Please add files first")
            return

        self.preview_tree.delete(*self.preview_tree.get_children())
        self.preview_data = []

        changes_count = 0

        for file_path in self.files:
            try:
                audio = MP3(file_path, ID3=ID3)
                file_name = Path(file_path).name

                # Check find & replace
                field = self.replace_field.get()
                find = self.find_text.get()
                replace = self.replace_text.get()

                if find:
                    tag_obj = self.get_field_value(audio, field)
                    if tag_obj:
                        current = ', '.join([str(t) for t in tag_obj.text]) if hasattr(tag_obj, 'text') else str(tag_obj)

                        if self.case_sensitive.get():
                            new_value = current.replace(find, replace)
                        else:
                            # Case insensitive replace
                            import re
                            pattern = re.compile(re.escape(find), re.IGNORECASE)
                            new_value = pattern.sub(replace, current)

                        if current != new_value:
                            self.preview_tree.insert("", tk.END, values=(
                                file_name, field, current, new_value
                            ))
                            self.preview_data.append({
                                'file': file_path,
                                'operation': 'replace',
                                'field': field,
                                'old': current,
                                'new': new_value
                            })
                            changes_count += 1

            except Exception as e:
                print(f"Error previewing {file_path}: {e}")

        self.status_label.config(text=f"Preview: {changes_count} changes")

    def apply_changes(self):
        """Apply the changes to files"""
        if not self.preview_data:
            messagebox.showwarning("No changes", "Preview changes first")
            return

        confirm = messagebox.askyesno(
            "Apply changes",
            f"Apply {len(self.preview_data)} changes to {len(self.files)} files?\n\n"
            "This will modify your music files!"
        )

        if not confirm:
            return

        success_count = 0
        error_count = 0

        for change in self.preview_data:
            try:
                audio = MP3(change['file'], ID3=ID3)

                if change['operation'] == 'replace':
                    field = change['field']

                    if field == "COMMENT":
                        from mutagen.id3 import COMM
                        audio['COMM::eng'] = COMM(encoding=3, lang='eng', desc='', text=[change['new']])
                    elif field == "GENRE":
                        from mutagen.id3 import TCON
                        audio['TCON'] = TCON(encoding=3, text=[change['new']])
                    elif field == "LABEL":
                        from mutagen.id3 import TPUB
                        audio['TPUB'] = TPUB(encoding=3, text=[change['new']])

                    audio.save()
                    success_count += 1

            except Exception as e:
                print(f"Error applying change to {change['file']}: {e}")
                error_count += 1

        messagebox.showinfo(
            "Complete",
            f"Applied {success_count} changes\n"
            f"Errors: {error_count}"
        )

        self.status_label.config(text=f"Applied {success_count} changes")
        self.preview_data = []

    def apply_presets(self):
        """Apply selected preset operations"""
        if not self.files:
            messagebox.showwarning("No files", "Please add files first")
            return

        # Get selected presets
        selected = [(old, new, field) for var, old, new, field in self.preset_vars if var.get()]

        if not selected:
            messagebox.showwarning("No presets", "Please select at least one preset")
            return

        # Apply each preset
        for old, new, field in selected:
            if '→' in field:  # Move operation
                from_field, to_field = field.split('→')
                # TODO: Implement move operation
                print(f"Move {old} from {from_field} to {to_field}")
            else:  # Replace operation
                self.replace_field.set(field)
                self.find_text.delete(0, tk.END)
                self.find_text.insert(0, old)
                self.replace_text.delete(0, tk.END)
                self.replace_text.insert(0, new)

        # Preview the changes
        self.preview_changes()

def main():
    root = tk.Tk()
    app = QuickTagEditor(root)
    root.mainloop()

if __name__ == '__main__':
    main()
