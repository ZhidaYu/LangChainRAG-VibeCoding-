"""Chinese-optimized text chunking strategy."""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings

# Chinese-optimized separators: paragraph -> sentence -> clause -> word -> char
CHINESE_SEPARATORS = [
    "\n\n", "\n",
    "。", "！", "？",
    "；",
    "，", "、",
    " ", ".", "!", "?",
    "",
]


def get_text_splitter(
    chunk_size: int = None,
    chunk_overlap: int = None,
    is_product_data: bool = False,
) -> RecursiveCharacterTextSplitter:
    """Create a Chinese-optimized text splitter."""
    if chunk_size is None:
        chunk_size = settings.chunk_size
    if chunk_overlap is None:
        chunk_overlap = settings.chunk_overlap

    if is_product_data:
        chunk_size = 300
        chunk_overlap = 50

    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=CHINESE_SEPARATORS,
        keep_separator=True,
    )
