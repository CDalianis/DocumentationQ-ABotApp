from app.config import Settings
from app.services.cache import clear_cache, get_cached_query, set_cached_query
from app.services.query_engine import Citation, QueryResult


def test_cache_roundtrip():
    clear_cache()
    settings = Settings(query_cache_ttl_seconds=60)
    result = QueryResult(
        answer="Answer from cache",
        citations=[Citation(page_number=2, source="doc.pdf", excerpt="sample excerpt")],
    )

    assert get_cached_query("doc-1", "What is the warranty?", settings) is None

    set_cached_query("doc-1", "What is the warranty?", result, settings)
    cached = get_cached_query("doc-1", "What is the warranty?", settings)

    assert cached is not None
    assert cached.answer == "Answer from cache"
    assert cached.cached is True
    assert cached.citations[0].page_number == 2
    clear_cache()


def test_cache_key_is_case_insensitive():
    clear_cache()
    settings = Settings()
    result = QueryResult(answer="Same", citations=[])

    set_cached_query("doc-1", "Hello World", result, settings)
    cached = get_cached_query("doc-1", "hello world", settings)
    assert cached is not None
    assert cached.answer == "Same"
    clear_cache()
