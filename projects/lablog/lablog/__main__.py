"""Allow ``python -m lablog`` to behave exactly like the ``lablog`` script."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
