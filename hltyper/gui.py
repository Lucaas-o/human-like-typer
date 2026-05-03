from __future__ import annotations

import logging
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import pyautogui

from hltyper import VERSION
from hltyper.config import load_config, merge_defaults, save_config
from hltyper.session import dry_run_estimate, list_windows_for_gui, run_typing_session

logger = logging.getLogger(__name__)


class TyperApp(tk.Tk):
    def __init__(self, cfg: dict):
        super().__init__()
        self.title(f"Human-like Typer v{VERSION}")
        self.geometry("720x560")
        self.cfg = merge_defaults(cfg)

        main = ttk.Frame(self, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        row = 0
        ttk.Label(main, text="Text file").grid(row=row, column=0, sticky="w")
        self.path_var = tk.StringVar()
        path_fr = ttk.Frame(main)
        path_fr.grid(row=row, column=1, sticky="ew")
        ttk.Entry(path_fr, textvariable=self.path_var, width=55).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(path_fr, text="Browse…", command=self._browse).pack(side=tk.LEFT, padx=4)
        row += 1

        ttk.Label(main, text="WPM").grid(row=row, column=0, sticky="w", pady=2)
        self.wpm_var = tk.DoubleVar(value=float(self.cfg["wpm"]))
        ttk.Spinbox(
            main,
            from_=30,
            to=220,
            textvariable=self.wpm_var,
            width=10,
        ).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(main, text="Cooldown (newline, s)").grid(row=row, column=0, sticky="w")
        self.cool_var = tk.DoubleVar(value=float(self.cfg["cooldown"]))
        ttk.Spinbox(
            main,
            from_=0,
            to=30,
            textvariable=self.cool_var,
            width=10,
        ).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(main, text="Error %").grid(row=row, column=0, sticky="w")
        self.err_var = tk.DoubleVar(value=float(self.cfg["error_prob"]))
        ttk.Spinbox(
            main,
            from_=0,
            to=20,
            textvariable=self.err_var,
            width=10,
        ).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(main, text="Language").grid(row=row, column=0, sticky="w")
        self.lang_var = tk.StringVar(value=self.cfg["language"])
        ttk.Combobox(
            main,
            textvariable=self.lang_var,
            values=("english", "spanish"),
            width=12,
            state="readonly",
        ).grid(row=row, column=1, sticky="w")
        row += 1

        self.foreground_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            main,
            text="Type into focused window only (skip window picker)",
            variable=self.foreground_var,
        ).grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1

        self.dry_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            main,
            text="Dry run (estimate timing; no keys sent)",
            variable=self.dry_var,
        ).grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1

        hot_fr = ttk.LabelFrame(main, text="Hotkeys (pynput format)", padding=6)
        hot_fr.grid(row=row, column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Label(hot_fr, text="Pause").grid(row=0, column=0, sticky="w")
        self.hp_var = tk.StringVar(value=str(self.cfg["hotkey_pause"]))
        ttk.Entry(hot_fr, textvariable=self.hp_var, width=16).grid(row=0, column=1)
        ttk.Label(hot_fr, text="Stop").grid(row=0, column=2, padx=(12, 0))
        self.hs_var = tk.StringVar(value=str(self.cfg["hotkey_stop"]))
        ttk.Entry(hot_fr, textvariable=self.hs_var, width=16).grid(row=0, column=3)
        row += 1

        win_fr = ttk.LabelFrame(main, text="Target window", padding=6)
        win_fr.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=6)
        filt_fr = ttk.Frame(win_fr)
        filt_fr.pack(fill=tk.X)
        ttk.Label(filt_fr, text="Filter").pack(side=tk.LEFT)
        self.win_filter_var = tk.StringVar()
        ttk.Entry(filt_fr, textvariable=self.win_filter_var, width=40).pack(
            side=tk.LEFT, padx=6
        )
        ttk.Button(filt_fr, text="Refresh list", command=self._refresh_windows).pack(
            side=tk.LEFT
        )
        self.win_list = tk.Listbox(win_fr, height=6, exportselection=False)
        self.win_list.pack(fill=tk.BOTH, expand=True, pady=4)
        self._window_objs = []
        row += 1

        btn_fr = ttk.Frame(main)
        btn_fr.grid(row=row, column=0, columnspan=2, pady=8)
        self.start_btn = ttk.Button(btn_fr, text="Start typing", command=self._start)
        self.start_btn.pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_fr, text="Save settings", command=self._save_settings).pack(
            side=tk.LEFT, padx=4
        )
        row += 1

        ttk.Label(main, text="Progress").grid(row=row, column=0, sticky="w")
        self.prog = ttk.Progressbar(main, mode="determinate", maximum=100)
        self.prog.grid(row=row, column=1, sticky="ew")
        row += 1

        self.stat_var = tk.StringVar(value="Ready.")
        ttk.Label(main, textvariable=self.stat_var).grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1

        log_fr = ttk.LabelFrame(main, text="Session log (recent)", padding=4)
        log_fr.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=4)
        main.rowconfigure(row, weight=1)
        self.log_box = scrolledtext.ScrolledText(log_fr, height=8, state="disabled")
        self.log_box.pack(fill=tk.BOTH, expand=True)

        main.columnconfigure(1, weight=1)

        self._log_line("Application started. Select a file and window (or focus-only mode).")
        self.after(200, self._refresh_windows)

    def _append_log(self, msg: str):
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state="disabled")

    def _log_line(self, msg: str):
        logger.info(msg)
        self.after(0, lambda: self._append_log(msg))

    def _browse(self):
        p = filedialog.askopenfilename(
            title="Text file",
            filetypes=[("Text", "*.txt"), ("All", "*.*")],
        )
        if p:
            self.path_var.set(p)

    def _gather_cfg(self) -> dict:
        c = merge_defaults(dict(self.cfg))
        c["wpm"] = float(self.wpm_var.get())
        c["cooldown"] = float(self.cool_var.get())
        c["error_prob"] = float(self.err_var.get())
        c["language"] = self.lang_var.get().strip().lower()
        c["hotkey_pause"] = self.hp_var.get().strip() or "<f8>"
        c["hotkey_stop"] = self.hs_var.get().strip() or "<esc>"
        return c

    def _save_settings(self):
        self.cfg = self._gather_cfg()
        save_config(self.cfg)
        messagebox.showinfo("Saved", "Settings written to config.json")

    def _refresh_windows(self):
        cfg = self._gather_cfg()
        filt = self.win_filter_var.get()
        wins = list_windows_for_gui(filt, cfg)
        self.win_list.delete(0, tk.END)
        self._window_objs = wins
        for w in wins:
            self.win_list.insert(tk.END, w.title[:120])

    def _progress(self, done: int, total: int):
        def upd():
            pct = (done / total) * 100 if total else 0
            self.prog["value"] = pct
            self.stat_var.set(f"{done} / {total} characters")

        self.after(0, upd)

    def _start(self):
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning("File", "Choose a text file.")
            return
        cfg = self._gather_cfg()
        fg = self.foreground_var.get()
        dry = self.dry_var.get()

        sel = self.win_list.curselection()
        pre_win = None
        if not fg:
            if not sel:
                messagebox.showwarning(
                    "Window",
                    "Select a window from the list or enable 'focused window only'.",
                )
                return
            pre_win = self._window_objs[sel[0]]

        if dry:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                est = dry_run_estimate(cfg, text)
                msg = (
                    f"~{est['approx_seconds']:.0f}s typing time at target "
                    f"{est['target_wpm']} WPM ({est['chars']} chars)."
                )
                self.stat_var.set(msg)
                self._log_line(msg)
                messagebox.showinfo("Dry run", msg)
            except Exception as e:
                messagebox.showerror("Error", str(e))
            return

        self.start_btn.configure(state="disabled")
        self.prog["value"] = 0
        self.stat_var.set("Starting…")

        def work():
            try:
                run_typing_session(
                    file_path=path,
                    cfg=cfg,
                    dry_run=False,
                    foreground_only=fg,
                    pick_window=not fg,
                    countdown=3.0,
                    progress_callback=self._progress,
                    pre_selected_window=pre_win,
                )
            except Exception as e:
                logger.exception("Typing thread")
                self.after(0, lambda: messagebox.showerror("Typing error", str(e)))
            finally:
                self.after(0, self._done_run)

        threading.Thread(target=work, daemon=True).start()

    def _done_run(self):
        self.start_btn.configure(state="normal")
        self.stat_var.set("Finished.")
        self._log_line("Session finished. See typer_session.log for details.")


def run_gui(cfg: dict | None = None):
    pyautogui.FAILSAFE = True
    cfg = merge_defaults(cfg or load_config())
    app = TyperApp(cfg)
    app.mainloop()
