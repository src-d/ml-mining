from logging import Logger
from pathlib import Path


def path_with_suffix(path: Path, suffix: str):
    """Adds a suffix to a path if necessary."""
    if suffix and not path.suffix == suffix:
        path = path.with_suffix(suffix)
    return path


def check_remove_filepath(path: Path, log: Logger, force: bool):
    """Checks the path does not point to a file, if it does will raise an error or remove it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not force:
            log.error("%s already exists, aborting (use -f/--force to overwrite)", path)
            raise FileExistsError
        log.warn("%s already exists, overwritten", path)
        path.unlink()
