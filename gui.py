import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Optional drag-and-drop support via tkinterdnd2 (if installed)
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore

    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False


class App:
    def __init__(self):
        # Create root window (with optional DnD-aware Tk)
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        self.root.title("Huffman Compressor")
        self.root.geometry("520x240")
        self.root.resizable(False, False)

        # State
        self.input_var = tk.StringVar()
        self.mode_running = None  # "compress" or "decompress" or None

        # UI
        self._build_ui()

    def _build_ui(self):
        pad_x = 10
        pad_y = 8

        title = tk.Label(
            self.root, text="Huffman Coding Tool", font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=(14, 4))

        sub = tk.Label(
            self.root,
            text="Lossless data compression using Huffman algorithm",
            font=("Segoe UI", 9),
        )
        sub.pack(pady=(0, 8))

        # Input row
        row = tk.Frame(self.root)
        row.pack(fill="x", padx=pad_x, pady=pad_y)

        tk.Label(row, text="Input:", width=8, anchor="w").pack(side="left")
        self.input_entry = tk.Entry(row, textvariable=self.input_var)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Button(row, text="Browse...", command=self._browse_input).pack(side="left")

        # Enable drag-and-drop onto the entry if available
        if DND_AVAILABLE:
            try:
                self.input_entry.drop_target_register(DND_FILES)
                self.input_entry.dnd_bind("<<Drop>>", self._on_drop_files)
                hint = tk.Label(
                    self.root,
                    text="Tip: Drag & drop a file into the input box",
                    fg="#666",
                    font=("Segoe UI", 8),
                )
                hint.pack(padx=pad_x, anchor="w")
            except Exception:
                pass

        # Action buttons
        btns = tk.Frame(self.root)
        btns.pack(pady=(10, 6))
        self.compress_btn = tk.Button(
            btns,
            text="Compress",
            width=16,
            bg="#4CAF50",
            fg="white",
            command=lambda: self.start("compress"),
        )
        self.compress_btn.pack(side="left", padx=6)

        self.decompress_btn = tk.Button(
            btns,
            text="Decompress",
            width=16,
            bg="#2196F3",
            fg="white",
            command=lambda: self.start("decompress"),
        )
        self.decompress_btn.pack(side="left", padx=6)

        # Minimal progress bar (indeterminate) - Hidden by default
        self.progress = ttk.Progressbar(self.root, mode="indeterminate", length=360)

        # Status bar
        self.status = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Segoe UI", 9),
        )
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def _browse_input(self):
        path = filedialog.askopenfilename(title="Select input file")
        if path:
            self.input_var.set(path)

    def _on_drop_files(self, event):
        # event.data can be a list of files. We'll take the first one.
        data = event.data.strip()
        if not data:
            return
        # Handle paths with spaces that come wrapped in braces {C:\path with spaces}
        if data.startswith("{") and data.endswith("}"):
            data = data[1:-1]
        # If multiple, split on } { pattern or just space. Keep it minimal: take up to first space if many.
        if "}" in data and " {" in data:
            # In case of multiple brace-wrapped files, split and take first
            data = data.split("} {")[0].strip("{}")
        elif " " in data and not os.path.exists(data):
            # Fallback split by space if unwrapped and multiple
            data = data.split(" ")[0]
        self.input_var.set(data)

    def start(self, mode: str):
        # Check executable relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(script_dir, "huffman.exe")

        if not os.path.exists(exe_path):
            messagebox.showerror(
                "Error",
                "huffman.exe not found!\n\nPlease compile the project first using 'mingw32-make' or gcc.",
            )
            return

        # Get input
        input_path = self.input_var.get().strip()
        if not input_path:
            input_path = filedialog.askopenfilename(title=f"Select file to {mode}")
            if not input_path:
                return
            self.input_var.set(input_path)

        if not os.path.exists(input_path):
            messagebox.showerror("Error", f"Input file not found:\n{input_path}")
            return

        # Ask for output
        def_ext = ".bin" if mode == "compress" else ".txt"
        output_path = filedialog.asksaveasfilename(
            title="Save result as", defaultextension=def_ext
        )
        if not output_path:
            return

        # Disable UI and start progress
        self._set_running_state(True, mode)

        # Show progress bar
        self.progress.pack(pady=(6, 0))
        self.progress.start(10)

        self._set_status(f"{mode.capitalize()} in progress...")

        # Run in background
        t = threading.Thread(
            target=self._run_huffman_worker,
            args=(exe_path, mode, input_path, output_path),
            daemon=True,
        )
        t.start()

    def _run_huffman_worker(self, exe_path, mode, input_path, output_path):
        # Capture sizes for post-run stats
        in_size = os.path.getsize(input_path) if os.path.exists(input_path) else 0

        try:
            # Use startupinfo to hide console window on Windows
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            result = subprocess.run(
                [exe_path, mode, input_path, output_path],
                capture_output=True,
                text=True,
                startupinfo=startupinfo,
            )
        except Exception as e:
            self.root.after(
                0,
                lambda: self._finish_with_error(
                    f"Failed to execute huffman.exe:\n{str(e)}"
                ),
            )
            return

        if result.returncode != 0:
            err = result.stderr.strip() or "Unknown error in C program."
            self.root.after(
                0, lambda: self._finish_with_error(f"C Program Error:\n{err}")
            )
            return

        # Success path: compute compression ratio or sizes
        out_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

        if mode == "compress":
            ratio_msg = self._compute_compression_ratio_message(in_size, out_size)
            msg_title = "Compression Complete"
            success_msg = f"{msg_title}\n\n{ratio_msg}\n\nOutput:\n{output_path}"
        else:
            # Decompress: show size transition (compressed -> decompressed)
            success_msg = (
                "Decompression Complete\n\n"
                f"Sizes: {in_size} bytes -> {out_size} bytes\n\n"
                f"Output:\n{output_path}"
            )

        self.root.after(0, lambda: self._finish_success(success_msg))

    def _compute_compression_ratio_message(self, in_size, out_size):
        if in_size <= 0:
            return f"Sizes: {in_size} bytes -> {out_size} bytes"
        saved = in_size - out_size
        ratio = (1.0 - (out_size / in_size)) * 100.0
        return f"Sizes: {in_size} bytes -> {out_size} bytes\nSaved: {saved} bytes ({ratio:.2f}%)"

    def _finish_with_error(self, message):
        self.progress.stop()
        self.progress.pack_forget()
        self._set_running_state(False)
        self._set_status("Error")
        messagebox.showerror("Error", message)

    def _finish_success(self, message):
        self.progress.stop()
        self.progress.pack_forget()
        self._set_running_state(False)
        self._set_status("Done")
        messagebox.showinfo("Success", message)

    def _set_running_state(self, running: bool, mode: str | None = None):
        self.mode_running = mode if running else None
        state = tk.DISABLED if running else tk.NORMAL
        self.compress_btn.config(state=state)
        self.decompress_btn.config(state=state)
        self.input_entry.config(state=tk.DISABLED if running else tk.NORMAL)

    def _set_status(self, text: str):
        self.status.config(text=text)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
