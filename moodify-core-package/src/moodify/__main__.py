"""Allow ``python -m moodify`` to invoke the command-line interface."""

from moodify.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
