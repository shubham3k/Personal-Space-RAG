import pytest

from src.retrieval.query_processor import QueryProcessor


def test_query_processor_normalizes_spaces():
    assert QueryProcessor().normalize("  hello    world  ") == "hello world"


def test_query_processor_rejects_short_query():
    with pytest.raises(ValueError):
        QueryProcessor().normalize("x")
