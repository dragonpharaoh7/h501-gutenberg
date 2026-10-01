"""List Project Gutenberg authors, optionally ranked by translations."""

from tt_gutenberg.data import language_counts, load_authors

# Zero-width and bidirectional marks. Twenty-six aliases carry one of
# these, which makes two otherwise identical names look different.
INVISIBLE = "[​-‏‪-‮﻿]"


def list_authors(by_languages=True, alias=True):
    """Return author names as a list, cleaned and deduplicated.

    Names come from the alias column, or from author when alias is
    False. With by_languages the list runs from the most translated
    author to the least, ties broken alphabetically so that the order
    is the same on every run; otherwise it is alphabetical.
    """
    column = "alias" if alias else "author"
    authors = load_authors()[["gutenberg_author_id", column]]
    authors = authors.dropna(subset=[column])
    authors = authors.merge(
        language_counts(), on="gutenberg_author_id", how="left"
    )

    # Strip the invisible marks and surrounding spaces, and give authors
    # with no translated book a count of zero rather than a missing one.
    names = authors[column].str.replace(INVISIBLE, "", regex=True)
    authors = authors.assign(**{
        column: names.str.strip(),
        "languages": authors["languages"].fillna(0).astype(int),
    })
    authors = authors[authors[column] != ""]

    # One row per name, keeping its highest count, so that authors
    # sharing an alias are listed once.
    authors = authors.groupby(column, as_index=False)["languages"].max()

    keys = ["languages", column] if by_languages else [column]
    ascending = [False, True] if by_languages else [True]
    return authors.sort_values(keys, ascending=ascending)[column].tolist()
