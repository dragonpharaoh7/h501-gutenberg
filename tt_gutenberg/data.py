"""Load the TidyTuesday Project Gutenberg data sets.

Every value this module needs is produced by a function, so importing it
downloads nothing. The CSV files are read straight from their URL and are
never written to disk.
"""

from functools import lru_cache

import pandas as pd


def base_url():
    """Return the URL of the TidyTuesday 2025-06-03 data directory."""
    return (
        "https://raw.githubusercontent.com/rfordatascience/tidytuesday"
        "/main/data/2025/2025-06-03/"
    )


@lru_cache
def _read(filename):
    # Read one CSV from the data directory. Cached, so each file is
    # downloaded only once per session.
    return pd.read_csv(base_url() + filename)


def load_authors():
    """Return the authors table, one row per author."""
    return _read("gutenberg_authors.csv")


def load_metadata():
    """Return the book metadata table, one row per book."""
    return _read("gutenberg_metadata.csv")


def load_languages():
    """Return the languages table, one row per book and language."""
    return _read("gutenberg_languages.csv")


def language_counts():
    """Count the distinct languages each author's books appear in.

    Returns one row per gutenberg_author_id with a languages column.
    The language values come from the languages table rather than from
    metadata.language, because metadata stores composites such as
    "de/en" that would otherwise be counted as a single language.
    """
    books = load_metadata()[["gutenberg_id", "gutenberg_author_id"]]
    languages = load_languages()[["gutenberg_id", "language"]]
    return (
        books.merge(languages, on="gutenberg_id")
        .groupby("gutenberg_author_id")["language"]
        .nunique()
        .reset_index(name="languages")
    )
