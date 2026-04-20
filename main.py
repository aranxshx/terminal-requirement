from __future__ import annotations

import argparse

from lib.app import create_default_application_service
from lib.cli_app import WattzUpCLI


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WattzUp Electricity Consumption Monitoring System")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run the terminal interface instead of the default GUI.",
    )
    return parser


def run_cli() -> None:
    app_service = create_default_application_service()
    WattzUpCLI(app_service).run()


def run_gui() -> None:
    try:
        from lib.ui import WattzUpVisual
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "GUI dependencies are not installed. Install customtkinter and Pillow, or run with --cli."
        ) from exc

    app_service = create_default_application_service()
    window = WattzUpVisual(app_service)
    window.mainloop()


def main() -> None:
    args = _build_parser().parse_args()

    if args.cli:
        run_cli()
        return

    try:
        run_gui()
    except RuntimeError as exc:
        print(f"{exc}\nFalling back to CLI mode.")
        run_cli()


if __name__ == "__main__":
    main()
