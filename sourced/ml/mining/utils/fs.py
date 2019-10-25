from logging import Logger
from pathlib import Path
import shutil


class IsNotAFileError(OSError):
    """Exception raised if operation only works on files."""


class IsNotADirectoryError(OSError):
    """Exception raised if operation only works on directories."""


class NonEmptyDirectoryError(OSError):
    """Exception raised if operation only works on empty directories."""


def path_with_suffix(path: Path, suffix: str):
    """Adds a suffix to a path if necessary."""
    if suffix and not path.suffix == suffix:
        path = path.with_suffix(suffix)
    return path


def check_remove_filepath(path: Path, log: Logger, force: bool):
    """Checks the path does not point to a file, if it does will raise an error or remove it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not path.is_file():
            log.error("%s exists and is not a file, aborting", path)
            raise IsNotAFileError
        if not force:
            log.error("%s already exists, aborting (use -f/--force to overwrite)", path)
            raise FileExistsError
        log.warn("%s already exists, overwritten", path)
        path.unlink()


def check_exists_filepath(path: Path, log: Logger):
    """Checks the path points to a file, if it doesn't will raise an error."""
    if not path.exists():
        log.error("%s already exists, aborting", path)
        raise FileNotFoundError


def check_empty_directory(path: Path, log: Logger, force: bool, ignore: bool):
    """Checks the path does not point to a non-empty directory, if it does will raise an error or
    empty it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not path.is_dir():
            log.error("%s exists and is not a directory, aborting", path)
            raise IsNotADirectoryError
        if not (force or ignore):
            log.error(
                "%s already exists, aborting (use -f/--force to empty or -i/--ignore to ignore)",
                path,
            )
            raise NonEmptyDirectoryError
        if ignore:
            log.warn("%s already exists and is non-empty, ignoring anyway", path)
            return
        log.warn(
            "%s already exists and is non-empty, removing all files and sub-directories",
            path,
        )
        shutil.rmtree(path.as_posix())
        path.mkdir()
