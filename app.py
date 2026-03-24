import os
import threading
import customtkinter as ctk
from tkinter import filedialog

from detector import detect_provider, PROVIDERS
from cleaners import NOVCleaner, RigcloudCleaner, PasonCleaner
from cleaners.base import BaseCleaner


CLEANER_MAP: dict[str, type[BaseCleaner]] = {
    "NOV": NOVCleaner,
    "Rigcloud": RigcloudCleaner,
    "Pason": PasonCleaner,
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CSV Cleaner for Corva")
        self.geometry("640x480")
        self.minsize(560, 420)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self._filepath: str = ""
        self._detected_provider: str = ""

        self.grid_columnconfigure(0, weight=1)

        # --- File selection row ---
        file_frame = ctk.CTkFrame(self, fg_color="transparent")
        file_frame.grid(row=0, column=0, padx=20, pady=(20, 8), sticky="ew")
        file_frame.grid_columnconfigure(1, weight=1)

        self.browse_btn = ctk.CTkButton(
            file_frame, text="Browse File...", width=130, height=36,
            command=self._browse_file,
        )
        self.browse_btn.grid(row=0, column=0, padx=(0, 10))

        self.file_label = ctk.CTkLabel(
            file_frame, text="No file selected",
            font=ctk.CTkFont(size=13), text_color=("gray50", "gray55"),
            anchor="w",
        )
        self.file_label.grid(row=0, column=1, sticky="ew")

        # --- Provider selector row ---
        provider_frame = ctk.CTkFrame(self, fg_color="transparent")
        provider_frame.grid(row=1, column=0, padx=20, pady=8, sticky="ew")
        provider_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            provider_frame, text="Provider:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=(0, 10))

        self.provider_var = ctk.StringVar(value="Auto-detect")
        self.provider_menu = ctk.CTkOptionMenu(
            provider_frame,
            values=["Auto-detect"] + list(PROVIDERS),
            variable=self.provider_var,
            width=180, height=36,
            state="disabled",
        )
        self.provider_menu.grid(row=0, column=1, sticky="w")

        self.provider_info = ctk.CTkLabel(
            provider_frame, text="",
            font=ctk.CTkFont(size=12), text_color=("gray50", "gray55"),
        )
        self.provider_info.grid(row=0, column=2, padx=(12, 0))

        # --- File info ---
        self.info_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13),
            anchor="w",
        )
        self.info_label.grid(row=2, column=0, padx=20, pady=8, sticky="ew")

        # --- Progress bar ---
        self.progress = ctk.CTkProgressBar(self, width=400, height=16)
        self.progress.grid(row=3, column=0, padx=20, pady=8, sticky="ew")
        self.progress.set(0)

        # --- Clean button ---
        self.clean_btn = ctk.CTkButton(
            self, text="Clean & Export", height=44, state="disabled",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._start_clean,
        )
        self.clean_btn.grid(row=4, column=0, padx=20, pady=(12, 8), sticky="ew")

        # --- Status output ---
        self.status_text = ctk.CTkTextbox(self, height=140, state="disabled")
        self.status_text.grid(row=5, column=0, padx=20, pady=(8, 12), sticky="nsew")
        self.grid_rowconfigure(5, weight=1)

        # --- Theme toggle at bottom ---
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=6, column=0, padx=20, pady=(0, 12), sticky="ew")

        self.theme_btn = ctk.CTkButton(
            bottom_frame, text="Toggle Theme", width=120, height=30,
            fg_color="transparent", hover_color=("gray85", "gray30"),
            text_color=("gray40", "gray60"), font=ctk.CTkFont(size=12),
            command=self._toggle_theme,
        )
        self.theme_btn.pack(side="right")

    # ------ File browsing ------

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Select raw CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return

        self._filepath = path
        display = path if len(path) < 60 else "..." + path[-57:]
        self.file_label.configure(text=display, text_color=("gray10", "gray90"))

        self._detect_and_preview()

    def _detect_and_preview(self):
        detected = detect_provider(self._filepath)
        self._detected_provider = detected or ""

        if detected:
            self.provider_var.set(detected)
            self.provider_info.configure(text=f"(auto-detected: {detected})")
        else:
            self.provider_var.set("Auto-detect")
            self.provider_info.configure(text="(could not auto-detect)")

        self.provider_menu.configure(state="normal")

        try:
            with open(self._filepath, "r", encoding="utf-8-sig") as f:
                line_count = sum(1 for _ in f) - 1
            import csv
            with open(self._filepath, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                header = next(reader, [])
                col_count = len(header)
            self.info_label.configure(
                text=f"Rows: {line_count:,}  |  Columns: {col_count}"
            )
        except Exception as e:
            self.info_label.configure(text=f"Error reading file: {e}")

        self.clean_btn.configure(state="normal")
        self.progress.set(0)
        self._log_status(f"Loaded: {os.path.basename(self._filepath)}")

    # ------ Cleaning ------

    def _start_clean(self):
        provider = self.provider_var.get()
        if provider == "Auto-detect":
            provider = self._detected_provider
        if provider not in CLEANER_MAP:
            self._log_status("ERROR: Could not determine provider. Please select one manually.")
            return

        self.clean_btn.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self.provider_menu.configure(state="disabled")
        self.progress.set(0)

        self._log_status(f"Cleaning with {provider} rules...")

        thread = threading.Thread(target=self._run_clean, args=(provider,), daemon=True)
        thread.start()

    def _run_clean(self, provider: str):
        cleaner_cls = CLEANER_MAP[provider]
        cleaner = cleaner_cls(self._filepath, progress_cb=self._update_progress)

        try:
            result = cleaner.clean()
            self.after(0, self._on_clean_done, result, None)
        except Exception as e:
            self.after(0, self._on_clean_done, None, e)

    def _update_progress(self, fraction: float):
        self.after(0, lambda: self.progress.set(fraction))

    def _on_clean_done(self, result, error):
        self.clean_btn.configure(state="normal")
        self.browse_btn.configure(state="normal")
        self.provider_menu.configure(state="normal")

        if error:
            self._log_status(f"ERROR: {error}")
            return

        self.progress.set(1.0)
        self._log_status(
            f"Done! Cleaned {result.kept_rows:,} rows "
            f"({result.removed_rows:,} removed from {result.total_rows:,} total)."
        )
        self._log_status(f"Saved to: {result.output_path}")

    # ------ Helpers ------

    def _log_status(self, msg: str):
        self.status_text.configure(state="normal")
        self.status_text.insert("end", msg + "\n")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current == "Dark" else "Dark")
