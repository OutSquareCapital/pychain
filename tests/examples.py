import re
from collections import defaultdict
from datetime import datetime
from typing import TypedDict

import polars as pl

import pychain as pc

# --- Example 1: Word Frequency Analysis ---

TEXT_DATA = """
Pychain is a Python library that provides functional-style chaining operations.
This library helps in writing clean, readable, and declarative code.
Functional programming is a paradigm that pychain embraces.
"""
STOP_WORDS = {"a", "is", "in", "that", "the", "and"}


def dataframe_example():
    """
    Example of creating a Polars DataFrame using pychain's Dict wrapper.
    When passing list of different lengths, polars will throw an error.
    """
    data = {
        "name": ["Alice", "Bob", "Charlie", "David", "Eva"],
        "age": [25, 30, 35, 40],
        "city": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
    }
    try:
        pl.DataFrame(data)
    except Exception:
        pass  # Will raise an error due to different lengths
    return pc.Dict(data).implode().into(pl.LazyFrame).explode("name").collect()


def word_frequency_python() -> list[tuple[str, int]]:
    """
    Cleans text, counts word frequencies, and returns the 3 most common words.
    """
    from collections import Counter

    return Counter(
        [
            word
            for word in re.findall(r"\w+", TEXT_DATA.lower())
            if word not in STOP_WORDS
        ]
    ).most_common(3)


def word_frequency_pychain():
    """
    Pychain version of the word frequency analysis pipeline.
    """
    return (
        pc.Iter(re.findall(r"\w+", TEXT_DATA.lower()))
        .filter_notin(STOP_WORDS)
        .most_common(3)
        .into(list)
    )


# --- Example 2: Sales Data Aggregation ---


class Sale(TypedDict):
    date: str
    category: str
    amount: float


SALES_DATA: list[Sale] = [
    {"date": "2023-10-01", "category": "electronics", "amount": 250.0},
    {"date": "2023-10-15", "category": "books", "amount": 45.5},
    {"date": "2023-11-05", "category": "electronics", "amount": 220.0},
    {"date": "2023-11-20", "category": "clothing", "amount": 120.0},
    {"date": "2023-10-25", "category": "books", "amount": 30.0},
]
START_DATE = datetime.strptime("2023-10-01", "%Y-%m-%d").date()
END_DATE = datetime.strptime("2023-10-31", "%Y-%m-%d").date()


def aggregate_sales_python() -> dict[str, float]:
    """
    Filters sales by date and aggregates total amount by category.
    """
    filtered_sales: list[Sale] = []
    for sale in SALES_DATA:
        sale_date = datetime.strptime(sale["date"], "%Y-%m-%d").date()
        if START_DATE <= sale_date <= END_DATE:
            filtered_sales.append(sale)

    category_totals: dict[str, float] = defaultdict(float)
    for sale in filtered_sales:
        category_totals[sale["category"]] += sale["amount"]

    return dict(category_totals)


def aggregate_sales_pychain() -> pc.Dict[str, float]:
    """
    Pychain version of the sales aggregation pipeline.
    """

    def _sales_filter(sale: Sale) -> bool:
        sale_date = datetime.strptime(sale["date"], "%Y-%m-%d").date()
        return START_DATE <= sale_date <= END_DATE

    def _sales_aggregate(sales: list[Sale]) -> float:
        return pc.Iter(sales).map(lambda s: s["amount"]).sum()

    return (
        pc.Iter(SALES_DATA)
        .filter(_sales_filter)
        .group_by(lambda sale: sale["category"])
        .map_values(_sales_aggregate)
    )


# --- Example 3: Nested Data Processing ---


class Book(TypedDict):
    title: str
    rating: float


class AuthorData(TypedDict):
    author: str
    books: list[Book]


AUTHORS_DATA: list[AuthorData] = [
    {
        "author": "Author A",
        "books": [
            {"title": "Book 1", "rating": 4.5},
            {"title": "Book 2", "rating": 4.8},
        ],
    },
    {
        "author": "Author B",
        "books": [
            {"title": "Book 3", "rating": 4.2},
            {"title": "Book 4", "rating": 4.3},
        ],
    },
]


def best_author_python() -> tuple[str, float] | None:
    """
    Calculates the average rating for each author and finds the one with the highest average.
    """
    author_avg_ratings: dict[str, float] = {}
    for author_data in AUTHORS_DATA:
        author_name = author_data["author"]
        ratings = [book["rating"] for book in author_data["books"]]
        if ratings:
            author_avg_ratings[author_name] = sum(ratings) / len(ratings)

    if not author_avg_ratings:
        return None

    return max(author_avg_ratings.items(), key=lambda item: item[1])


def best_author_pychain() -> tuple[str, float] | None:
    """
    Pychain version to find the author with the highest average book rating.
    """

    def _map_author(data: AuthorData) -> tuple[str, float]:
        return (
            data["author"],
            pc.Iter(data["books"]).map(lambda book: book["rating"]).mean(),
        )

    return pc.Iter(AUTHORS_DATA).map(_map_author).max(key=lambda item: item[1])  # type: ignore


if __name__ == "__main__":
    # --- Assertions for Cookbook Examples ---
    assert word_frequency_python() == [
        ("pychain", 2),
        ("library", 2),
        ("functional", 2),
    ]
    assert word_frequency_pychain() == [
        ("pychain", 2),
        ("library", 2),
        ("functional", 2),
    ]

    assert aggregate_sales_python() == {"electronics": 250.0, "books": 75.5}
    assert aggregate_sales_pychain().unwrap() == {"electronics": 250.0, "books": 75.5}

    assert best_author_python() == ("Author A", 4.65)
    assert best_author_pychain() == ("Author A", 4.65)
    assert dataframe_example().shape == (5, 3)

    print("All checks passed! ✅")
