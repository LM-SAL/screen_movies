"""
Very simple/rudimentary script to play movies in random order.
"""

import logging
import os
import shutil
import time
from pathlib import Path

from config import FILENAMES, PATHS, REQUIRED_PROGRAMS, SAMPLE_FREQUENCY

logging.basicConfig(level=logging.INFO)


def timeit(func):
    """
    Decorator to measure the time taken to execute a function.
    """

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        logging.info(f"Time taken to execute {func.__name__}: {time.time() - start} seconds.")  # NOQA: G004
        return result

    return wrapper


@timeit
def check_everything_is_installed() -> None:
    """
    Check if all required programs are installed.

    Raises
    ------
    ModuleNotFoundError
        If any of the required programs are not installed.
    """
    for program in REQUIRED_PROGRAMS:
        if shutil.which(program) is None:
            msg = f"Error: {program} is not installed."
            raise ModuleNotFoundError(msg)


@timeit
def check_directories_mounted() -> None:
    """
    Check if the net directory are mounted.

    Raises
    ------
    IOError
        If the directory does not exist.
    """
    for directory in PATHS:
        if directory is not None and not directory.expanduser().resolve().exists():
            msg = f"Error: Directory '{directory}' not found."
            raise OSError(msg)


@timeit
def get_paths_for_movies(base_path: Path, filename: str) -> list:
    """
    Get all the paths for the movies in the given directory.

    Parameters
    ----------
    base_path : Path
        The base path to search for movies.
    filename : str
        The filename pattern to search for.

    Returns
    -------
    list
        A list of paths to the movies.
    """
    return list(map(str, base_path.rglob(filename)))


@timeit
def create_playlist(movies: list) -> None:
    """
    Create a playlist m3u file.

    Parameters
    ----------
    movies : list
        A list of paths to the movies.
    """
    logging.info("Removing existing(?) playlist.m3u")
    Path("playlist.m3u").unlink(missing_ok=True)
    logging.info("Creating playlist.m3u")
    Path("playlist.m3u").write_text("\n".join(movies))


@timeit
def play_movies_in_random_order() -> None:
    """
    Play the movies in random order using a playlist.

    Parameters
    ----------
    movies : list
        A list of paths to the movies.
    """
    if not Path("playlist.m3u").exists():
        msg = "playlist.m3u not found"
        raise FileNotFoundError(msg)
    # Assuming the first program in the list is the default program to play the movies.
    os.system(f"{REQUIRED_PROGRAMS[0]} --fullscreen --random --loop playlist.m3u")  # NOQA: S605


if __name__ == "__main__":
    check_everything_is_installed()
    check_directories_mounted()
    movies = []
    for base_path, sample_frequency, filename_pattern in zip(PATHS, SAMPLE_FREQUENCY, FILENAMES, strict=True):
        if base_path is None:
            continue
        logging.info(f"Searching for movies in {base_path}")  # NOQA: G004
        movies.extend(get_paths_for_movies(base_path, filename_pattern)[::sample_frequency])
    create_playlist(movies)
    play_movies_in_random_order()
