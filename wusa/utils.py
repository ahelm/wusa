from functools import wraps
import sys

from click import secho
from click import style

from wusa import WUSA_CONFIG_FILE


def requires_config_file(f):
    """Decorator to annotate a function which requires a wusa config file."""

    @wraps(f)
    def inner(*args, **kwargs):
        if not WUSA_CONFIG_FILE.exists():
            secho(
                "Could not find valid configuration! Please run: "
                + style("wusa init", bold=True),
                fg="yellow",
                err=True,
            )
            sys.exit(2)
        return f(*args, **kwargs)

    return inner