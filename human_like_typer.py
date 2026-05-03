"""
Human-like Typer — entry point.
Default: graphical UI. Use --cli for the console menu.
"""

from __future__ import annotations

import argparse
import sys

import pyautogui

from hltyper.config import load_config, save_config
from hltyper.logutil import setup_logging
from hltyper.session import dry_run_estimate, run_typing_session


def _parse_args(argv):
    p = argparse.ArgumentParser(
        description="Simulate human-like typing from a text file into the focused or selected window.",
    )
    p.add_argument(
        "--cli",
        action="store_true",
        help="Console menu instead of the graphical UI.",
    )
    p.add_argument(
        "--file",
        "-f",
        metavar="PATH",
        help="Run one typing session from this file and exit (no GUI).",
    )
    p.add_argument(
        "--wpm",
        type=float,
        metavar="N",
        help="Override target WPM for this run (also saved if combined with --save).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Estimate timing only; do not send keystrokes.",
    )
    p.add_argument(
        "--foreground-only",
        action="store_true",
        help="Do not show window picker; type into whichever window is already focused.",
    )
    p.add_argument(
        "--countdown",
        type=float,
        default=3.0,
        metavar="SEC",
        help="Seconds before typing starts (default: 3). Use 0 to skip.",
    )
    p.add_argument(
        "--save",
        action="store_true",
        help="Persist --wpm into config.json when used with one-shot mode.",
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose log output.",
    )
    return p.parse_args(argv)


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    args = _parse_args(argv)
    setup_logging()
    import logging

    logging.getLogger().setLevel(logging.DEBUG if args.verbose else logging.INFO)

    print(
        "Note: This program simulates keyboard input. Use responsibly and only where permitted."
    )
    pyautogui.FAILSAFE = True

    cfg = load_config()
    if args.wpm is not None:
        cfg["wpm"] = float(args.wpm)
        if args.save:
            save_config(cfg)

    if args.file:
        if args.dry_run:
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    text = f.read()
                est = dry_run_estimate(cfg, text)
                print(
                    f"Chars: {est['chars']}\n"
                    f"Target WPM: {est['target_wpm']}\n"
                    f"Avg delay/char: {est['avg_delay_per_char']:.4f}s\n"
                    f"Approx. duration: {est['approx_seconds']:.1f}s"
                )
            except OSError as e:
                print(f"Error: {e}")
                return 1
            return 0
        run_typing_session(
            file_path=args.file,
            cfg=cfg,
            dry_run=False,
            foreground_only=args.foreground_only,
            pick_window=not args.foreground_only,
            countdown=max(0.0, float(args.countdown)),
        )
        return 0

    if args.cli:
        from hltyper.cli import run_cli_main

        run_cli_main(cfg)
        return 0

    from hltyper.gui import run_gui

    run_gui(cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
