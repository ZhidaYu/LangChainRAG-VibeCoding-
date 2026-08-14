"""Tests for utility functions: cache, chunk IDs, text cleaner."""
from app.utils.chunk_id import generate_chunk_id
from app.utils.text_cleaner import clean_text
from app.utils.cache import LRUCache


class TestChunkId:
    """Deterministic chunk ID generation tests."""

    def test_same_input_same_id(self):
        """Same input should produce the same chunk ID."""
        id1 = generate_chunk_id("test.txt", 0, "hello world")
        id2 = generate_chunk_id("test.txt", 0, "hello world")
        assert id1 == id2

    def test_different_content_different_id(self):
        """Different content should produce different IDs."""
        id1 = generate_chunk_id("test.txt", 0, "content A")
        id2 = generate_chunk_id("test.txt", 0, "content B")
        assert id1 != id2

    def test_different_index_different_id(self):
        """Different chunk index should produce different IDs."""
        id1 = generate_chunk_id("test.txt", 0, "same content")
        id2 = generate_chunk_id("test.txt", 1, "same content")
        assert id1 != id2

    def test_different_file_different_id(self):
        """Different source file should produce different IDs."""
        id1 = generate_chunk_id("a.txt", 0, "same")
        id2 = generate_chunk_id("b.txt", 0, "same")
        assert id1 != id2


class TestTextCleaner:
    """Chinese text cleaning tests."""

    def test_removes_excess_whitespace(self):
        """Should normalize multiple spaces."""
        result = clean_text("hello     world")
        assert "    " not in result

    def test_normalizes_newlines(self):
        """Should collapse excessive newlines."""
        result = clean_text("line1\n\n\n\n\nline2")
        assert "\n\n\n\n" not in result

    def test_strips_control_chars(self):
        """Should remove null bytes and other control chars."""
        result = clean_text("hello\x00world")
        assert "\x00" not in result

    def test_empty_string(self):
        """Empty string should return empty."""
        result = clean_text("")
        assert result == ""

    def test_none_input(self):
        """None input should return empty string."""
        result = clean_text(None)
        assert result == ""


class TestLRUCache:
    """LRU cache tests."""

    def test_set_and_get(self):
        """Should store and retrieve values."""
        cache = LRUCache(max_size=10)
        cache.set("key1", {"answer": "hello"})
        result = cache.get("key1")
        assert result is not None
        assert result["answer"] == "hello"

    def test_cache_miss(self):
        """Should return None for missing keys."""
        cache = LRUCache(max_size=10)
        result = cache.get("nonexistent")
        assert result is None

    def test_eviction_when_full(self):
        """Oldest entries should be evicted."""
        cache = LRUCache(max_size=2)
        cache.set("a", {"data": 1})
        cache.set("b", {"data": 2})
        cache.set("c", {"data": 3})  # should evict "a"
        assert cache.get("a") is None
        assert cache.get("b") is not None
        assert cache.get("c") is not None

    def test_lru_moves_to_end(self):
        """Accessing an entry should move it to end (not evicted)."""
        cache = LRUCache(max_size=2)
        cache.set("a", {"data": 1})
        cache.set("b", {"data": 2})
        cache.get("a")  # access "a", moves to end
        cache.set("c", {"data": 3})  # should evict "b" instead
        assert cache.get("a") is not None
        assert cache.get("b") is None
