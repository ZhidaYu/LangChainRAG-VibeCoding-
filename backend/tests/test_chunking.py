"""Tests for Chinese text chunking strategy."""
from app.rag.chunking import get_text_splitter, CHINESE_SEPARATORS


class TestTextSplitter:
    """RecursiveCharacterTextSplitter configuration tests."""

    def test_default_splitter_created(self):
        """Should create a splitter with default settings."""
        splitter = get_text_splitter()
        assert splitter is not None
        assert splitter._chunk_size == 500
        assert splitter._chunk_overlap == 100

    def test_custom_chunk_size(self):
        """Should respect custom chunk_size and overlap."""
        splitter = get_text_splitter(chunk_size=300, chunk_overlap=50)
        assert splitter._chunk_size == 300
        assert splitter._chunk_overlap == 50

    def test_product_data_uses_smaller_chunks(self):
        """Product data should use smaller chunks."""
        splitter = get_text_splitter(is_product_data=True)
        assert splitter._chunk_size == 300
        assert splitter._chunk_overlap == 50

    def test_split_chinese_text(self):
        """Should split Chinese text on sentence boundaries."""
        splitter = get_text_splitter(chunk_size=100, chunk_overlap=20)
        text = "这是第一句话。这是第二句话。这是第三句话。"
        chunks = splitter.split_text(text)
        assert len(chunks) >= 1

    def test_separators_prioritize_chinese(self):
        """Chinese sentence enders (。！？) should be before English ones."""
        cn_end_idx = CHINESE_SEPARATORS.index("。")
        en_period_idx = CHINESE_SEPARATORS.index(".")
        assert cn_end_idx < en_period_idx
