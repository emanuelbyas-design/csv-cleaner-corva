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
    BG_PRIMARY = "#0d1117"
    BG_SECONDARY = "#161b22"
    BG_TERTIARY = "#21262d"
    ACCENT_CYAN = "#00bcd4"
    ACCENT_CYAN_HOVER = "#00acc1"
    ACCENT_GREEN = "#4caf50"
    TEXT_PRIMARY = "#e0e0e0"
    TEXT_SECONDARY = "#999999"
    TEXT_MUTED = "#666666"
    BORDER_ACCENT = "#1a3a40"

    def __init__(self):
        super().__init__()

        self.title("Corva Automatic CSV Formatter")
        self.geometry("660x520")
        self.minsize(580, 460)

        ctk.set_appearance_mode("Dark")

        self.configure(fg_color=self.BG_PRIMARY)

        self._filepath: str = ""
        self._detected_provider: str = ""

        self.grid_columnconfigure(0, weight=1)

        # --- Header with app name ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=24, pady=(20, 4), sticky="ew")

        logo_label = ctk.CTkLabel(
            header_frame, text="Corva",
            font=ctk.CTkFont(family="Roboto", size=22, weight="bold"),
            text_color=self.TEXT_PRIMARY,
        )
        logo_label.pack(side="left")

        accent_label = ctk.CTkLabel(
            header_frame, text="  Automatic CSV Formatter",
            font=ctk.CTkFont(family="Roboto", size=22, weight="bold"),
            text_color=self.ACCENT_CYAN,
        )
        accent_label.pack(side="left")

        subtitle = ctk.CTkLabel(
            self, text="Clean and format EDR CSV files for Corva stream ingestion.",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=self.TEXT_SECONDARY, anchor="w",
        )
        subtitle.grid(row=1, column=0, padx=24, pady=(0, 12), sticky="ew")

        # --- Card panel ---
        card = ctk.CTkFrame(
            self, fg_color=self.BG_SECONDARY,
            border_color=self.BORDER_ACCENT, border_width=1,
            corner_radius=8,
        )
        card.grid(row=2, column=0, padx=24, pady=(0, 12), sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # --- File selection row (inside card) ---
        file_frame = ctk.CTkFrame(card, fg_color="transparent")
        file_frame.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        file_frame.grid_columnconfigure(1, weight=1)

        self.browse_btn = ctk.CTkButton(
            file_frame, text="Browse File...", width=130, height=36,
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            fg_color=self.BG_TERTIARY, hover_color="#2d333b",
            text_color=self.TEXT_PRIMARY, border_color=self.BORDER_ACCENT,
            border_width=1, corner_radius=6,
            command=self._browse_file,
        )
        self.browse_btn.grid(row=0, column=0, padx=(0, 10))

        self.file_label = ctk.CTkLabel(
            file_frame, text="No file selected",
            font=ctk.CTkFont(family="Roboto", size=13),
            text_color=self.TEXT_MUTED, anchor="w",
        )
        self.file_label.grid(row=0, column=1, sticky="ew")

        # --- Provider selector row (inside card) ---
        provider_frame = ctk.CTkFrame(card, fg_color="transparent")
        provider_frame.grid(row=1, column=0, padx=16, pady=(4, 16), sticky="ew")
        provider_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            provider_frame, text="Provider:",
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            text_color=self.TEXT_SECONDARY,
        ).grid(row=0, column=0, padx=(0, 10))

        self.provider_var = ctk.StringVar(value="Auto-detect")
        self.provider_menu = ctk.CTkOptionMenu(
            provider_frame,
            values=["Auto-detect"] + list(PROVIDERS),
            variable=self.provider_var,
            width=180, height=36,
            font=ctk.CTkFont(family="Roboto", size=13),
            fg_color=self.BG_TERTIARY, button_color=self.BG_TERTIARY,
            button_hover_color="#2d333b",
            dropdown_fg_color=self.BG_SECONDARY,
            dropdown_hover_color=self.BG_TERTIARY,
            text_color=self.TEXT_PRIMARY,
            state="disabled",
        )
        self.provider_menu.grid(row=0, column=1, sticky="w")

        self.provider_info = ctk.CTkLabel(
            provider_frame, text="",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=self.TEXT_MUTED,
        )
        self.provider_info.grid(row=0, column=2, padx=(12, 0))

        # --- File info ---
        self.info_label = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(family="Roboto", size=13),
            text_color=self.TEXT_SECONDARY, anchor="w",
        )
        self.info_label.grid(row=3, column=0, padx=24, pady=(0, 4), sticky="ew")

        # --- Progress bar ---
        self.progress = ctk.CTkProgressBar(
            self, width=400, height=14,
            fg_color=self.BG_TERTIARY,
            progress_color=self.ACCENT_CYAN,
            corner_radius=4,
        )
        self.progress.grid(row=4, column=0, padx=24, pady=6, sticky="ew")
        self.progress.set(0)

        # --- Clean button ---
        self.clean_btn = ctk.CTkButton(
            self, text="Clean & Export", height=46, state="disabled",
            font=ctk.CTkFont(family="Roboto", size=16, weight="bold"),
            fg_color=self.ACCENT_CYAN, hover_color=self.ACCENT_CYAN_HOVER,
            text_color=self.BG_PRIMARY, corner_radius=8,
            command=self._start_clean,
        )
        self.clean_btn.grid(row=5, column=0, padx=24, pady=(8, 8), sticky="ew")

        # --- Status output ---
        self.status_text = ctk.CTkTextbox(
            self, height=140, state="disabled",
            font=ctk.CTkFont(family="Roboto", size=12),
            fg_color=self.BG_SECONDARY, text_color=self.TEXT_PRIMARY,
            border_color=self.BORDER_ACCENT, border_width=1,
            corner_radius=8,
        )
        self.status_text.grid(row=6, column=0, padx=24, pady=(4, 16), sticky="nsew")
        self.grid_rowconfigure(6, weight=1)

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
        self.file_label.configure(text=display, text_color=self.ACCENT_GREEN)

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
        if len(result.output_paths) > 1:
            self._log_status(
                f"Output split into {len(result.output_paths)} files "
                f"(>{1_048_000:,} rows):"
            )
        for path in result.output_paths:
            self._log_status(f"Saved to: {path}")

    # ------ Helpers ------

    def _log_status(self, msg: str):
        self.status_text.configure(state="normal")
        self.status_text.insert("end", msg + "\n")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")
